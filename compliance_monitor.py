import os
import google.generativeai as genai
from typing import Dict, List
from datetime import datetime
import PyPDF2
import re

class ComplianceMonitor:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        # Use the gemini-1.5-pro model
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        print(f"Using model: gemini-1.5-pro")
    
    def read_pdf(self, file_path: str) -> str:
        """
        Reads a PDF file and returns its text content
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")

    def analyze_document(self, document_text: str) -> Dict:
        """
        Analyzes a compliance document and returns a structured report
        """
        prompt = f"""
        You are a financial compliance expert. Analyze the following document and provide a COMPLETE compliance report with NO EMPTY SECTIONS.
        
        COMPLIANCE_SCORE:
        Calculate a score from 0-100 based on compliance level.
        Score: [number]
        
        REGULATION_SUMMARY:
        For each regulation, provide AT LEAST 3 specific points:

        1. Environmental Protection Standards:
        • [Specific point about environmental compliance]
        • [Specific point about ESG requirements]
        • [Specific point about sustainable finance]

        2. Safety Regulations:
        • [Specific point about workplace safety]
        • [Specific point about employee protection]
        • [Specific point about safety protocols]

        3. Grid Reliability Standards:
        • [Specific point about business continuity]
        • [Specific point about operational resilience]
        • [Specific point about system reliability]

        4. Emissions Reporting:
        • [Specific point about emissions tracking]
        • [Specific point about carbon footprint]
        • [Specific point about reporting requirements]

        5. Renewable Portfolio Standards:
        • [Specific point about renewable investments]
        • [Specific point about sustainable portfolios]
        • [Specific point about green initiatives]

        DETECTED_VIOLATIONS:
        For each violation found, provide ALL of these details:
        Severity: [High/Medium/Low]
        Title: [Clear violation name]
        Key Issues:
        • [Specific issue 1]
        • [Specific issue 2]
        Impact:
        • [Specific impact 1]
        • [Specific impact 2]
        Remediation Steps:
        • [Specific step 1]
        • [Specific step 2]

        RECOMMENDATIONS:
        For each recommendation, provide ALL of these details:
        Priority: [High/Medium/Low]
        Title: [Clear action item]
        Objective:
        • [Specific objective 1]
        • [Specific objective 2]
        Implementation Steps:
        • [Specific step 1]
        • [Specific step 2]
        • [Specific step 3]
        Timeline: [Specific timeframe]
        Expected Outcomes:
        • [Specific outcome 1]
        • [Specific outcome 2]

        Analyze this document focusing on financial sector compliance:
        {document_text}
        """

        try:
            response = self.model.generate_content(prompt)
            analysis = response.text
            
            # Extract compliance score
            score_match = re.search(r'Score:\s*(\d+)', analysis)
            compliance_score = int(score_match.group(1)) if score_match else 0
            
            return {
                'analysis': analysis,
                'compliance_score': compliance_score,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error generating analysis: {str(e)}")
            return {
                'error': f"Error analyzing document: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }

    def generate_compliance_report(self, document_path: str) -> Dict:
        """
        Reads a document and generates a compliance report
        """
        try:
            if document_path.lower().endswith('.pdf'):
                document_text = self.read_pdf(document_path)
            else:
                with open(document_path, 'r') as file:
                    document_text = file.read()
            return self.analyze_document(document_text)
        except Exception as e:
            return {
                'error': f"Error processing document: {str(e)}",
                'timestamp': datetime.now().isoformat()
            } 