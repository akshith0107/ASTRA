import logging
import io
from fpdf import FPDF
from app.database.models import Report

logger = logging.getLogger(__name__)

class ReportExportService:
    def generate_pdf(self, report: Report, threat_summary: str, recommendations: list[str]) -> bytes:
        """
        Generates a PDF byte stream for a specific intelligence report.
        """
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # Header
            pdf.set_font("helvetica", "B", 16)
            pdf.cell(0, 10, "SentinelX - Threat Intelligence Report", ln=True, align="C")
            pdf.ln(10)
            
            # Report Meta
            pdf.set_font("helvetica", "B", 12)
            pdf.cell(0, 10, f"Report ID: {report.id}", ln=True)
            pdf.cell(0, 10, f"Scam Type: {report.scam_type or 'Unknown'}", ln=True)
            pdf.cell(0, 10, f"Risk Level: {report.risk_level}", ln=True)
            pdf.cell(0, 10, f"Risk Score: {report.risk_score:.2f}", ln=True)
            pdf.ln(5)
            
            # Threat Summary
            pdf.set_font("helvetica", "B", 14)
            pdf.cell(0, 10, "Threat Summary", ln=True)
            pdf.set_font("helvetica", "", 12)
            pdf.multi_cell(0, 10, threat_summary)
            pdf.ln(5)
            
            # Indicators
            pdf.set_font("helvetica", "B", 14)
            pdf.cell(0, 10, "Indicators of Compromise (IoCs)", ln=True)
            pdf.set_font("helvetica", "", 12)
            if report.indicators:
                for ind in report.indicators:
                    pdf.cell(0, 10, f"- {ind.type}: {ind.value}", ln=True)
            else:
                pdf.cell(0, 10, "No specific indicators detected.", ln=True)
            pdf.ln(5)
            
            # Recommendations
            pdf.set_font("helvetica", "B", 14)
            pdf.cell(0, 10, "Security Recommendations", ln=True)
            pdf.set_font("helvetica", "", 12)
            for rec in recommendations:
                pdf.multi_cell(0, 10, f"- {rec}")
            pdf.ln(5)
            
            # Transcript
            pdf.set_font("helvetica", "B", 14)
            pdf.cell(0, 10, "Original Transcript", ln=True)
            pdf.set_font("helvetica", "I", 11)
            pdf.multi_cell(0, 10, f'"{report.text_content}"')
            
            return pdf.output()
            
        except Exception as e:
            logger.error(f"Failed to generate PDF: {e}")
            raise

report_export_service = ReportExportService()
