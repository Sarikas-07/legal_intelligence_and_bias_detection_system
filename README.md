 # ⚖️ AI-Powered Legal Intelligence, IPC Recommendation & Bias Detection System

**B.Tech AI & Data Science — Mini / Major Project**

An educational and research demonstration project built using Python and Streamlit.

## 🚀 Live Demo

**[Launch the Legal Intelligence and Bias Detection System](https://legal-intelligence.streamlit.app/)**

## 📌 Project Overview

An AI-powered legal assistance dashboard designed to analyze legal complaints and FIR descriptions, recommend potentially relevant legal sections, summarize complaint text, and detect sentiment and language bias.

The system can:

- Accept legal complaints, FIR descriptions, and uploaded documents.
- Classify crime-related text.
- Recommend potentially applicable IPC/BNS sections with punishment details.
- Generate AI-assisted complaint summaries.
- Perform sentiment analysis and language bias detection.
- Export legal analysis reports.
- Provide role-based access for administrators and users.

> **Disclaimer:** This system generates educational suggestions, not official legal advice. Its outputs may be incomplete or inaccurate and should be verified against authoritative legal sources and by a qualified legal professional.

## 🎯 Key Features

| Feature | Description |
|---|---|
| Authentication | Login and registration with bcrypt password hashing |
| Role-Based Access | Admin and user dashboards |
| Document Input | Enter text or upload PDF/TXT files |
| IPC/BNS Recommendations | TF-IDF and keyword-based legal section matching |
| AI Summarisation | Extractive summarisation; optional transformer-based summarisation |
| Keyword Extraction | Legal keyword and entity extraction |
| Sentiment Analysis | TextBlob polarity and subjectivity analysis |
| Bias Detection | Gender-related, aggressive-language, and emotional-bias indicators |
| Visualisations | Charts and analysis visualisations using Plotly |
| Report Export | Download analysis reports as TXT files |
| Database | SQLite storage for legal sections, user accounts, and reports |

## 🛠️ Technologies Used

| Category | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | Python 3.10+ |
| Database | SQLite3 |
| NLP | NLTK, TextBlob, scikit-learn |
| Summarisation | Extractive summariser / optional Hugging Face Transformers |
| PDF Processing | PyPDF2 |
| Visualisation | Plotly |
| Authentication | bcrypt |

## 📁 Project Structure

```text
legal_ai_project/
├── app.py
├── requirements.txt
├── README.md
├── database/
│   ├── create_database.py
│   └── legal_sections.db
├── modules/
│   ├── database_handler.py
│   ├── pdf_reader.py
│   ├── preprocessing.py
│   ├── summarizer.py
│   ├── keyword_extractor.py
│   ├── sentiment_analysis.py
│   ├── bias_detector.py
│   ├── ipc_recommender.py
│   ├── legal_matcher.py
│   └── visualization.py
├── data/
├── outputs/
├── assets/
└── screenshots/
```

*The structure above describes the expected project layout; optional folders and files may vary in the actual repository.*

## ⚡ Installation and Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/Sarikas-07/legal_intelligence_and_bias_detection_system.git
cd legal_intelligence_and_bias_detection_system
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

On Windows:

```powershell
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialise the database

```bash
python database/create_database.py
```

Run this only when appropriate for your local database setup. Do not overwrite an existing database containing accounts or reports.

### 5. Launch the application

```bash
streamlit run app.py
```

Streamlit will display a local URL, usually `http://localhost:8501`.

## 🔐 Authentication and Security

- Passwords are hashed using bcrypt.
- The application supports administrator and user roles.
- Account availability and administrator setup depend on the configured database and deployment environment.
- Do not publish real passwords, API keys, database files containing personal information, or secret configuration files.
- Configure administrator credentials securely and change any default or publicly exposed password.

## 🧪 Sample Test Cases

These examples illustrate possible test inputs. Actual recommendations depend on the application's matching logic and legal reference data.

### Test 1 — Robbery and Assault

**Input:**

> A man attacked a shopkeeper with an iron rod, injured him, and stole money from the cash register.

**Expected evaluation:** Check whether the system identifies potentially relevant offences involving robbery, theft, and causing hurt.

### Test 2 — Cybercrime

**Input:**

> An individual used a phishing link to access a victim's email account and transfer money from a linked bank account.

**Expected evaluation:** Check for potentially relevant information-technology and financial-fraud provisions.

### Test 3 — Domestic Violence

**Input:**

> A husband repeatedly assaults his wife, demands additional dowry, and threatens her.

**Expected evaluation:** Check whether the system identifies potentially relevant domestic-abuse, dowry-related, and intimidation provisions.

### Test 4 — Kidnapping

**Input:**

> An unknown person abducted a child outside school and demanded a ransom.

**Expected evaluation:** Check for potentially relevant kidnapping and ransom-related provisions.

**Legal accuracy note:** These are illustrative scenarios, not definitive legal classifications. Applicable provisions depend on the facts, jurisdiction, and law in force. IPC and BNS provisions are not interchangeable in every circumstance.

## 📸 Screenshots

Screenshots of the login page, dashboard, legal analysis, bias detection, and report export can be added to the `screenshots/` directory and linked here.

Example:

```markdown
![Login Page](screenshots/login.png)
![Dashboard](screenshots/dashboard.png)
![Legal Analysis](screenshots/analysis.png)
```

Use actual screenshots from the current application.

## 🚀 Future Enhancements

1. AI-powered legal chatbot.
2. Voice-based complaint analysis.
3. Retrieval of updated legal information from authoritative sources.
4. Explainable AI for legal section matching.
5. Multilingual legal text analysis.
6. Mobile application interface.
7. Evidence integrity and audit-history features.

## 👨‍💻 Developer Notes

- The optional transformer summariser may download a model when first used and may require substantial memory and download time.
- Extractive summarisation can be used when transformer summarisation is disabled.
- Legal reference data should be checked against authoritative sources and maintained as laws change.
- SQLite is suitable for local demonstration use, but a hosted persistent database may be more appropriate for a multi-user production deployment.

## 📄 License and Intended Use

This project was developed for educational and research demonstration purposes as part of a B.Tech AI & Data Science curriculum.

It is not a substitute for professional legal advice. Verify all legal outputs independently before relying on them.
