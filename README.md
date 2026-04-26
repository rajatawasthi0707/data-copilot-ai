# ✦ DataCopilot – Autonomous Data Analyst AI

An AI-powered data agent that can **analyze, visualize, and model datasets using natural language**.

Built using **Streamlit, Gemini API, scikit-learn, and Plotly**, this tool acts like your personal data scientist.

---

## 🚀 Features

- 📊 Automatic EDA (Exploratory Data Analysis)
- 📈 Smart visualizations (histograms, heatmaps, scatter plots)
- 🔍 Natural Language → SQL-style queries
- 🤖 Machine Learning (classification & regression)
- 📝 Executive summary reports
- ⚡ Agent-based tool calling system

---

## 🖥️ Demo

Upload any CSV and ask questions like:

- “Show correlation heatmap”
- “Average fare by class”
- “Predict Survived column”
- “Give executive summary”

---

## 🛠️ Tech Stack

- Python
- Streamlit
- Gemini API (Google GenAI)
- scikit-learn
- Pandas / NumPy
- Plotly

---

## 📂 Project Structure
agents/ → Core agent logic
tools/ → Data + ML tools
ui/ → Streamlit frontend


---

## ⚙️ Setup Instructions

### 1. Clone repo
```bash
git clone https://github.com/YOUR_USERNAME/data-copilot-ai.git
cd data-copilot-ai
### 2. Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
3. Install dependencies
pip install -r requirements.txt
4. Add API Key
GOOGLE_API_KEY=your_key_here
5. Run app
streamlit run ui/app.py
🎯 Use Cases
Data analysis without coding
Business insights generation
Quick ML prototyping
Demo for AI/ML interviews
📌 Future Improvements
Multi-file support
Dashboard export
LLM switching (OpenAI, Claude)
Cloud deployment
🙌 Author

Rajat Awasthi
Data Scientist | AI Engineer
