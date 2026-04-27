# FairSight AI ⚖️

**Ensuring Fairness and Detecting Bias in Automated Decisions.**

FairSight AI is a premium, high-performance auditing platform designed to help organizations detect, visualize, and mitigate algorithmic biases in their datasets and machine learning models. Built for transparency and compliance, it provides actionable insights through a sophisticated dark-themed interface.

## 🚀 Key Features

- **Advanced Bias Scanning**: Automatically detects protected attributes and target outcomes to identify disparate impact and selection rate gaps.
- **AI-Driven Narratives**: Generates deterministic and AI-powered audit summaries to explain complex bias metrics in plain business language.
- **Interactive Visualizations**: High-fidelity Plotly charts showing distribution disparities and fairness scores.
- **Audit History**: Persistent tracking of past audits, allowing teams to monitor fairness trends over time.
- **Professional Reporting**: Export comprehensive PDF audit reports containing detailed findings and recommended mitigation actions.
- **User Profiles**: Personalized experience with secure session-based profiles and avatar management.
- **Multi-Domain Support**: Tailored analysis for Hiring, Banking, Healthcare, Legal, and General use cases.

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
   git clone https://github.com/your-repo/fairsight-ai.git
   cd fairsight-ai
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables (optional):
   Create a `.env` file for any external AI integrations (e.g., Gemini API).

### Running the App

```bash
streamlit run app.py
```

Access the dashboard at `http://localhost:8501`.

---
*Developed for the AI Fairness Hackathon 2024.*
