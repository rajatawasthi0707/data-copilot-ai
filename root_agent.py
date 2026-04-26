"""
Root Agent – Orchestrator
Uses google-generativeai (old style) which works with your installed version.
API key loaded from .env file.
"""

import json
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Configure with API key from .env
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

from config.settings import MODEL_NAME
from tools.data_ingestion  import data_ingestion_tool
from tools.eda_tool        import eda_tool
from tools.sql_tool        import sql_tool
from tools.viz_tool        import viz_tool
from tools.ml_tool         import ml_tool
from tools.summarizer_tool import summarizer_tool

TOOLS = [
    {
        "function_declarations": [
            {
                "name": "data_ingestion_tool",
                "description": "Load a CSV file into memory. Always call this first.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "source_type": {"type": "string", "description": "use 'csv'"},
                        "source_path": {"type": "string", "description": "full file path to csv"}
                    },
                    "required": ["source_type", "source_path"]
                }
            },
            {
                "name": "eda_tool",
                "description": "Run full EDA: shape, nulls, stats, correlations, distributions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "columns_filter": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "optional list of columns to analyse"
                        }
                    }
                }
            },
            {
                "name": "sql_tool",
                "description": "Answer a data question using SQL on the loaded CSV.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string", "description": "natural language question"},
                        "use_bigquery": {"type": "boolean", "description": "always False for CSV"}
                    },
                    "required": ["question"]
                }
            },
            {
                "name": "viz_tool",
                "description": "Generate a chart. Types: bar, line, scatter, histogram, box, heatmap, pie, area.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "chart_type":   {"type": "string", "description": "bar|line|scatter|histogram|box|heatmap|pie|area"},
                        "x_column":     {"type": "string", "description": "x-axis column name"},
                        "y_column":     {"type": "string", "description": "y-axis column name (optional)"},
                        "color_column": {"type": "string", "description": "color grouping column (optional)"},
                        "title":        {"type": "string", "description": "chart title"}
                    },
                    "required": ["chart_type", "x_column"]
                }
            },
            {
                "name": "ml_tool",
                "description": "Train a ML model to predict a target column.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target_column":   {"type": "string", "description": "column to predict"},
                        "task_type":       {"type": "string", "description": "auto|classification|regression"},
                        "algorithm":       {"type": "string", "description": "random_forest|gradient_boosting|logistic|linear|ridge"},
                        "feature_columns": {"type": "array", "items": {"type": "string"}, "description": "feature columns (optional)"}
                    },
                    "required": ["target_column"]
                }
            },
            {
                "name": "summarizer_tool",
                "description": "Generate a Markdown insight report from all results. Call this last.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_question": {"type": "string", "description": "original user question"},
                        "extra_context": {"type": "string", "description": "extra context (optional)"}
                    },
                    "required": ["user_question"]
                }
            }
        ]
    }
]

_eda_cache = None
_ml_cache  = None
_sql_cache = []


def _dispatch(fn_name, fn_args):
    global _eda_cache, _ml_cache, _sql_cache
    if fn_name == "data_ingestion_tool":
        return data_ingestion_tool(**fn_args)
    elif fn_name == "eda_tool":
        r = eda_tool(**fn_args)
        _eda_cache = r
        return r
    elif fn_name == "sql_tool":
        r = sql_tool(**fn_args)
        _sql_cache.append(r)
        return r
    elif fn_name == "viz_tool":
        return viz_tool(**fn_args)
    elif fn_name == "ml_tool":
        r = ml_tool(**fn_args)
        _ml_cache = r
        return r
    elif fn_name == "summarizer_tool":
        return summarizer_tool(
            eda_result  = _eda_cache,
            ml_result   = _ml_cache,
            sql_results = _sql_cache if _sql_cache else None,
            **fn_args
        )
    return {"status": "error", "message": f"Unknown tool: {fn_name}"}


SYSTEM_INSTRUCTION = """You are an autonomous Data Science Agent.

You have these tools: data_ingestion_tool, eda_tool, sql_tool, viz_tool, ml_tool, summarizer_tool.

Rules:
1. Always call data_ingestion_tool first if a file is mentioned.
2. Run eda_tool right after loading data.
3. Use viz_tool to show charts and distributions.
4. Use sql_tool for aggregation questions like averages and counts.
5. Use ml_tool when user wants predictions.
6. Always end with summarizer_tool for full analyses.

Briefly explain what you are about to do before each tool call."""


def run_agent(user_message, history=None):
    global _sql_cache
    _sql_cache = []

    model = genai.GenerativeModel(
        model_name         = MODEL_NAME,
        tools              = TOOLS,
        system_instruction = SYSTEM_INSTRUCTION,
    )

    messages = list(history or [])
    messages.append({"role": "user", "parts": [user_message]})

    tool_calls_log   = []
    tool_results_log = []
    charts           = []

    for _ in range(10):
        response  = model.generate_content(messages)
        candidate = response.candidates[0]

        fn_calls = [
            p.function_call
            for p in candidate.content.parts
            if hasattr(p, "function_call") and p.function_call.name
        ]

        if not fn_calls:
            final_text = "".join(
                p.text for p in candidate.content.parts
                if hasattr(p, "text") and p.text
            )
            return {
                "text":         final_text,
                "tool_calls":   tool_calls_log,
                "tool_results": tool_results_log,
                "charts":       charts,
            }

        fn_parts = []
        for fc in fn_calls:
            args = dict(fc.args)
            tool_calls_log.append({"name": fc.name, "args": args})

            result = _dispatch(fc.name, args)
            tool_results_log.append(result)

            if fc.name == "viz_tool" and result.get("chart_json"):
                charts.append(result["chart_json"])

            safe = {k: v for k, v in result.items() if k != "dataframe"}

            fn_parts.append(
                genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name     = fc.name,
                        response = {"result": json.dumps(safe, default=str)},
                    )
                )
            )

        messages.append({"role": "model",    "parts": candidate.content.parts})
        messages.append({"role": "function", "parts": fn_parts})

    return {
        "text":         "Analysis complete.",
        "tool_calls":   tool_calls_log,
        "tool_results": tool_results_log,
        "charts":       charts,
    }