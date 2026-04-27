from fpdf import FPDF
import datetime

class FairSightReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'FairSight AI Audit Report', 0, 1, 'C')
        self.ln(10)

def generate_pdf_report(metrics, recommendations):
    # Use A4, unit mm, and explicit margins
    pdf = FairSightReport(orientation='P', unit='mm', format='A4')
    pdf.set_margins(15, 15, 15)
    pdf.add_page()
    
    effective_page_width = pdf.w - 2 * pdf.l_margin
    
    pdf.set_font("Arial", 'B', 12)
    
    # Header Info
    pdf.cell(effective_page_width, 10, txt="Audit Executive Summary", ln=1)
    pdf.set_font("Arial", size=10)
    
    f_score = metrics.get('fairness_score', 0)
    attribute = metrics.get('detailed_explanation', {}).get('attribute', 'Protected Attribute')
    pdf.cell(effective_page_width, 8, txt=f"Fairness Score: {int(f_score)}/100", ln=1)
    pdf.cell(effective_page_width, 8, txt=f"Protected Attribute: {attribute}", ln=1)
    pdf.cell(effective_page_width, 8, txt=f"Generation Date: {datetime.date.today()}", ln=1)
    pdf.ln(5)
    
    # Metrics Table
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(effective_page_width, 10, txt="Subgroup Selection Rates:", ln=1)
    pdf.set_font("Arial", size=9)
    for key, val in metrics.get('selection_rates', {}).items():
        # Ensure key and val are safe strings
        text = f"- {str(key)}: {str(val)}%"
        pdf.multi_cell(effective_page_width, 8, txt=text)
        
    pdf.ln(5)
    
    # Recommendations
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(effective_page_width, 10, txt="Strategic Recommendations:", ln=1)
    pdf.set_font("Arial", size=9)
    for rec in recommendations:
        pdf.multi_cell(effective_page_width, 8, txt=f"- {str(rec)}")
        
    pdf.ln(10)
    
    # Narrative (if exists)
    if 'narrative' in metrics:
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(effective_page_width, 10, txt="Detailed Narrative:", ln=1)
        pdf.set_font("Arial", size=9)
        pdf.multi_cell(effective_page_width, 6, txt=str(metrics['narrative']))
        pdf.ln(10)

    pdf.set_font("Arial", 'I', 8)
    disclaimer = "Disclaimer: This report is generated automatically by FairSight AI based on provided dataset metrics. Results should be validated by human auditors."
    pdf.multi_cell(effective_page_width, 5, txt=disclaimer)

    return bytes(pdf.output())
