import os
import google.generativeai as genai
from typing import Dict
from datetime import datetime
import PyPDF2
import re

class ComplianceMonitor:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        # Using the faster Gemini model
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        print(f"Using model: gemini-2.5-flash")
    
    def read_pdf(self, file_path: str) -> str:
        """
        Reads a PDF file and returns its text content.
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text.strip()
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")

    def analyze_document(self, document_text: str) -> Dict:
        """
        Analyzes a compliance document and returns a structured report.
        """
        prompt = f"""
        You are a financial compliance expert. Analyze the following document and provide a COMPLETE compliance report with NO EMPTY SECTIONS.

        COMPLIANCE_SCORE:
        Calculate a score from 0-100 based on compliance level.
        Score: [number]

        REGULATION_SUMMARY:
        For each regulation, provide AT LEAST 3 specific points:
        1. Environmental Protection Standards:
        • [Point 1]
        • [Point 2]
        • [Point 3]

        2. Safety Regulations:
        • [Point 1]
        • [Point 2]
        • [Point 3]

        3. Grid Reliability Standards:
        • [Point 1]
        • [Point 2]
        • [Point 3]

        4. Emissions Reporting:
        • [Point 1]
        • [Point 2]
        • [Point 3]

        5. Renewable Portfolio Standards:
        • [Point 1]
        • [Point 2]
        • [Point 3]

        DETECTED_VIOLATIONS:
        For each violation:
        Severity: [High/Medium/Low]
        Title: [Title]
        Key Issues:
        • [Issue 1]
        • [Issue 2]
        Impact:
        • [Impact 1]
        • [Impact 2]
        Remediation Steps:
        • [Step 1]
        • [Step 2]

        RECOMMENDATIONS:
        For each recommendation:
        Priority: [High/Medium/Low]
        Title: [Title]
        Objective:
        • [Objective 1]
        • [Objective 2]
        Implementation Steps:
        • [Step 1]
        • [Step 2]
        • [Step 3]
        Timeline: [Timeline]
        Expected Outcomes:
        • [Outcome 1]
        • [Outcome 2]

        Document to analyze:
        {document_text}
        """

        try:
            response = self.model.generate_content(prompt)
            analysis_text = response.text.strip() if hasattr(response, 'text') else str(response)

            # Extract compliance score using regex
            score_match = re.search(r'Score:\s*(\d+)', analysis_text)
            compliance_score = int(score_match.group(1)) if score_match else 0

            return {
                'analysis': analysis_text,
                'compliance_score': compliance_score,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'error': f"Error analyzing document: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }

    def generate_compliance_report(self, document_path: str) -> Dict:
        """
        Reads a document and generates a compliance report.
        """
        try:
            if document_path.lower().endswith('.pdf'):
                document_text = self.read_pdf(document_path)
            else:
                with open(document_path, 'r', encoding='utf-8') as file:
                    document_text = file.read()
            return self.analyze_document(document_text)
        except Exception as e:
            return {
                'error': f"Error processing document: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
