# FairSight AI ⚖️

**Empowering Ethical AI through Deterministic Fairness Auditing.**

FairSight AI is a premium fairness auditing platform designed to detect, explain, and mitigate bias in machine learning datasets. Built for the **AI Fairness Hackathon 2024**, it provides a zero-code interface for data scientists and compliance officers to ensure their models are equitable across diverse demographic groups.

## 🚀 Key Features

- **Automated Bias Scanning**: Instantly detect disparities in selection rates and outcomes.
- **Domain-Aware Attribute Selection**: Tailored analysis that suggests primary protected attributes (Gender, Race, Age) based on the application domain (Hiring, Banking, Healthcare, Legal).
- **Deterministic Narrative Engine**: Get human-readable summaries of audit findings without relying on external AI APIs.
- **Professional PDF Reporting**: Generate comprehensive audit reports ready for regulatory review.
- **Multi-Domain Support**: Specialized logic for Hiring, Banking, Healthcare, Legal, and General use cases.

## 🛠️ Tech Stack

- **Core Engine**: Python 3.10+
- **Frontend**: Streamlit (Custom Premium Theme)
- **Data Science**: Pandas, NumPy, Scikit-learn
- **Fairness Metrics**: Fairlearn
- **Visuals**: Plotly Express
- **Reporting**: FPDF2
- **Persistence**: JSON-based secure local storage

## 💻 Getting Started

### Prerequisites
- Python 3.9 or higher
- Pip package manager

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/prerana-aiml2024/fairsight-ai.git
   cd fairsight-ai
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Running the App:
   ```bash
   streamlit run app.py
   ```

Access the dashboard at `http://localhost:8501`.

---
*Developed for the AI Fairness Hackathon 2024.*
