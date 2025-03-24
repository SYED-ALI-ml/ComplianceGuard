from compliance_monitor import ComplianceMonitor
import os

def main():
    # Get API key from environment variable for security
    api_key = 'AIzaSyAUNX0gJyu0aP6bSWf1zwYjJ7KeGtHJX2w'
    
    if not api_key:
        print("Please set the GEMINI_API_KEY environment variable")
        return
    
    monitor = ComplianceMonitor(api_key)
    
    # Get document path from user
    document_path = input("Enter the path to your compliance document: ")
    
    if not os.path.exists(document_path):
        print("Error: Document not found")
        return
    
    # Generate and display report
    report = monitor.generate_compliance_report(document_path)
    
    if 'error' in report:
        print(f"Error: {report['error']}")
    else:
        print("\n=== Compliance Analysis Report ===")
        print(f"Generated at: {report['timestamp']}")
        print("\nAnalysis:")
        print(report['analysis'])

if __name__ == "__main__":
    main() 