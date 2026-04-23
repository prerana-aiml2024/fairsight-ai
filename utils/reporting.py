from fpdf import FPDF
import datetime

class FairSightReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'FairSight AI Audit Report', 0, 1, 'C')
        self.ln(10)

def generate_pdf_report(metrics, recommendations):
    pdf = FairSightReport()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    
    # Header Info
    pdf.cell(0, 10, txt="Audit Executive Summary", ln=1)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 8, txt=f"Fairness Score: {int(metrics.get('fairness_score', 0))}/100", ln=1)
    pdf.cell(0, 8, txt=f"Generation Date: {datetime.date.today()}", ln=1)
    pdf.ln(5)
    
    # Metrics Table
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 10, txt="Subgroup Selection Rates:", ln=1)
    pdf.set_font("Arial", size=9)
    for key, val in metrics.get('selection_rates', {}).items():
        # Use simple dash to avoid encoding issues with special characters in Arial
        pdf.multi_cell(0, 8, txt=f"- {key}: {val}%", border=0)
        
    pdf.ln(10)
    
    # Recommendations
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 10, txt="Strategic Recommendations:", ln=1)
    pdf.set_font("Arial", size=9)
    for rec in recommendations:
        pdf.multi_cell(0, 8, txt=f"- {rec}", border=0)
        
    pdf.ln(15)
    pdf.set_font("Arial", 'I', 8)
    pdf.multi_cell(0, 5, txt="Disclaimer: This report is generated automatically by FairSight AI based on provided dataset metrics. Results should be validated by human auditors.")

    return bytes(pdf.output())
