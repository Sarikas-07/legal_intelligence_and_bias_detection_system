# ⚖️ AI-Powered Legal Intelligence, IPC Recommendation & Bias Detection System

> **B.Tech AI & Data Science — Mini / Major Project**
> For educational and research demonstration purposes only.

---

## 📌 Project Overview

An intelligent, AI-powered legal assistance dashboard built with **Python + Streamlit** that can:

- Accept legal complaints / FIR descriptions / uploaded documents
- Automatically classify the crime type
- Recommend applicable **IPC / BNS legal sections** with punishment details
- Generate an **AI summary** of the complaint
- Perform **sentiment analysis** and **language bias detection**
- Export a complete **PDF/TXT legal analysis report**
- Provide **role-based access** (Admin / User) with secure login

> ⚠️ **DISCLAIMER:** This system provides AI-generated legal suggestions and should NOT be considered official legal advice. It is built purely for educational purposes.

---

## 🎯 Key Features

| Feature | Description |
|---|---|
| 🔐 Authentication | Secure login / registration with bcrypt password hashing |
| 👤 Role-Based Access | Admin and User dashboards |
| 📄 Document Input | Type text, upload PDF or TXT file |
| ⚖️ IPC/BNS Recommendations | TF-IDF + keyword matching against 30+ legal sections |
| 📝 AI Summarisation | Extractive summariser (optional: DistilBART transformer) |
| 🔑 Keyword Extraction | Legal vocabulary boosted frequency analysis |
| 💬 Sentiment Analysis | TextBlob polarity + subjectivity scores |
| 🚨 Bias Detection | Gender, aggressive language, and emotional bias scoring |
| 📊 Visualisations | Gauges, bar charts, pie charts (Plotly) |
| 📤 Export Report | Download full analysis as TXT file |
| 🗄️ SQLite Database | 30+ IPC/BNS sections, user accounts, saved reports |

---

## 🛠️ Technologies Used

| Category | Library / Tool |
|---|---|
| Frontend | Streamlit |
| Backend | Python 3.10+ |
| Database | SQLite3 |
| NLP | NLTK, TextBlob, scikit-learn |
| Summarisation | Extractive (built-in) / HuggingFace Transformers (optional) |
| PDF Processing | PyPDF2 |
| Visualisation | Plotly |
| Auth | bcrypt |

---

## 📁 Project Structure

```
legal_ai_project/
│
├── app.py                        ← Main Streamlit application
├── requirements.txt
├── README.md
│
├── database/
│   ├── create_database.py        ← Run once to create DB
│   └── legal_sections.db         ← Auto-created SQLite database
│
├── modules/
│   ├── database_handler.py       ← All DB read/write operations
│   ├── pdf_reader.py             ← PDF & TXT text extraction
│   ├── preprocessing.py          ← Text cleaning & tokenisation
│   ├── summarizer.py             ← Extractive + transformer summariser
│   ├── keyword_extractor.py      ← Legal keyword & entity extraction
│   ├── sentiment_analysis.py     ← TextBlob sentiment analysis
│   ├── bias_detector.py          ← Gender / aggressive / emotional bias
│   ├── ipc_recommender.py        ← Crime classification + IPC matching
│   ├── legal_matcher.py          ← TF-IDF cosine section matching
│   └── visualization.py          ← Plotly chart generators
│
├── data/                         ← (optional) extra datasets
├── outputs/                      ← Downloaded reports stored here
└── assets/                       ← Images / logos
```

---

## ⚡ Installation Guide

### Step 1 — Clone / Download the project

```bash
# If using git
git clone <your-repo-url>
cd legal_ai_project

# Or just extract the zip and open in VS Code
```

### Step 2 — Create a Python virtual environment (recommended)

```bash
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS / Linux
source venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Download NLTK data (auto on first run, or manually)

```python
python -c "import nltk; nltk.download('all')"
```

### Step 5 — Initialise the database

```bash
python database/create_database.py
```

This creates `database/legal_sections.db` with:
- 30+ IPC / BNS legal sections
- Default admin account: `admin` / `admin123`

### Step 6 — Run the app

```bash
streamlit run app.py
```

Open your browser at: **http://localhost:8501**

---

## 🖥️ VS Code Setup

1. Install the **Python** extension in VS Code
2. Select your virtual environment as the Python interpreter (`Ctrl+Shift+P` → "Python: Select Interpreter")
3. Open a terminal in VS Code (`Ctrl+\``)
4. Follow Steps 2–6 above

---

## 🔐 Default Credentials

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |

> ⚠️ Change the admin password immediately for any production or demo use.

---

## 🧪 Sample Test Cases

### Test 1 — Robbery + Assault
```
Input: "A man attacked the shopkeeper with an iron rod, injured him badly, and stole Rs. 50,000 from the cash register."
Expected: IPC 390 (Robbery), IPC 323 (Assault), IPC 379 (Theft)
```

### Test 2 — Cybercrime
```
Input: "The accused hacked into the victim's email account using a phishing link and transferred money from the linked bank account."
Expected: IT Act 66 (Hacking), IT Act 66D (Cheating by Impersonation), IPC 420 (Fraud)
```

### Test 3 — Domestic Violence
```
Input: "The husband beats his wife every day and demands Rs. 2 lakh more dowry. He has threatened to kill her if she files a complaint."
Expected: IPC 498A (Dowry Harassment), IPC 304B (Dowry Death), IPC 506 (Criminal Intimidation)
```

### Test 4 — Kidnapping
```
Input: "An unknown person forcefully abducted a 10-year-old girl from outside her school and demanded a ransom of Rs. 10 lakh."
Expected: IPC 363 (Kidnapping), IPC 364A (Kidnapping for Ransom)
```

---

## 📸 Screenshots

*(Replace with actual screenshots after running)*

| Screen | Description |
|---|---|
| Login Page | Secure login / register |
| Analyze Page | Input area + sample complaints |
| IPC Sections Tab | Match scores + punishment |
| Bias Detection Tab | Gauge + breakdown chart |
| Export Tab | Report download |

---

## 🚀 Future Enhancements

1. 🤖 **AI Legal Chatbot** — Conversational legal assistant using LLM APIs
2. 🎙️ **Voice Complaint Analysis** — Speech-to-text input
3. 🌐 **Real-Time Legal Search** — Fetch latest amendments from LegalZilla / IndianKanoon
4. 🔍 **Explainable AI** — SHAP / LIME explanations for section matching
5. ⚖️ **Court Judgment Prediction** — Predict likely verdict based on similar cases
6. 🌏 **Multi-Language Support** — Hindi, Tamil, Telugu legal text support
7. 📱 **Mobile App** — React Native / Flutter frontend
8. 🔗 **Blockchain Evidence Chain** — Tamper-proof complaint storage

---

## 👨‍💻 Developer Notes

- The transformer summariser (`sshleifer/distilbart-cnn-12-6`) will download automatically on first use (~500MB). Set `use_transformer=False` in `app.py` to skip.
- For GPU acceleration add `device=0` to the `pipeline()` call in `summarizer.py`.
- The IPC section database can be extended by editing `database/create_database.py` and re-running it.

---

## 📄 License

This project is built for **educational purposes** under the B.Tech AI & Data Science curriculum. Not for commercial use.
