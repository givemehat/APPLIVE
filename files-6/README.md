# 📊 RiskIQ — AI Investment Risk Profiler

> Know your investment DNA in under 2 minutes.

A production-ready fintech web app that profiles investor risk using Machine Learning and delivers personalized portfolio advice powered by GPT.

---

## 🚀 Features

| Feature | Details |
|---|---|
| 🧠 ML Risk Classification | Logistic Regression on 1,200+ synthetic investor records |
| 📋 7-Question Smart Form | Sliders, dropdowns, radio buttons — no typing needed |
| 📊 4 Interactive Charts | Gauge, Pie, Probability Bar, Profile Comparison |
| 🤖 AI Advice | GPT-3.5 personalized advice (with smart fallback) |
| 📄 PDF Report | Download full report with allocations + AI advice |
| 🗄️ SQLite Database | Stores every profile, viewable in Admin Dashboard |
| 🛠️ Admin Panel | Charts + full data table of all past profiles |

---

## 🗂️ Project Structure

```
ai-risk-profiler/
├── app.py                 # Main Streamlit app (multi-page)
├── model.py               # ML model training + prediction
├── dataset.py             # Synthetic dataset generator (1,200 rows)
├── utils.py               # Charts, DB, AI advice, PDF generation
├── risk_questions.json    # 7 profiling questions with metadata
├── requirements.txt       # All dependencies with pinned versions
├── .env.example           # API key template
└── README.md
```

---

## ⚡ Quickstart

### 1. Clone & Install

```bash
git clone https://github.com/your-username/ai-risk-profiler.git
cd ai-risk-profiler
pip install -r requirements.txt
```

### 2. Set Up API Key (Optional)

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

> **Note:** The app works perfectly without an API key — it uses smart fallback advice.

### 3. Run the App

```bash
streamlit run app.py
```

The app will **automatically**:
- Generate the dataset (`dataset.csv`)
- Train and save the model (`risk_model.pkl`)
- Initialize the database (`profiles.db`)

No manual steps needed.

---

## 🧠 ML Model Details

| Property | Value |
|---|---|
| Algorithm | Logistic Regression (+ Decision Tree fallback) |
| Training Samples | 1,200 synthetic investor profiles |
| Features | Age, Income, Experience, Risk Tolerance, Horizon, Goal, Behavior |
| Target Classes | Conservative / Moderate / Aggressive |
| Encoder | LabelEncoder (for categorical features) |
| Evaluation | Accuracy Score + Classification Report |
| Storage | `joblib` → `risk_model.pkl` |

---

## 📊 Risk Categories

| Profile | Description | Portfolio |
|---|---|---|
| 🟢 Conservative | Prioritizes capital safety | 70% Bonds, 20% ETF, 10% Gold |
| 🟡 Moderate | Balances growth and safety | 50% Stocks, 30% ETF, 20% Bonds |
| 🔴 Aggressive | Maximizes growth potential | 80% Stocks, 15% Crypto, 5% ETF |

---

## 🌐 Deployment

### Streamlit Cloud (Free)
1. Push to GitHub
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
3. Connect repo → Deploy
4. Add `OPENAI_API_KEY` in Secrets

### Hugging Face Spaces
1. Create a new Space → Select Streamlit SDK
2. Upload all files
3. Add API key in Settings → Secrets

---

## ⚠️ Disclaimer

This app is built for educational and hackathon purposes. It does not constitute financial advice. Always consult a SEBI-registered investment advisor before making investment decisions.

---

## 🛠️ Tech Stack

`Python` · `Streamlit` · `Scikit-learn` · `Plotly` · `OpenAI API` · `SQLite` · `FPDF2` · `Pandas` · `NumPy`
