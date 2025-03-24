import os
from flask import Flask, render_template, request, flash
from compliance_monitor import ComplianceMonitor
from werkzeug.utils import secure_filename
import logging
import tempfile
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for flash messages

# Configure upload folder - use /tmp for Render
UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = {'txt', 'pdf'}

# Ensure upload directory exists with proper permissions
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    logger.info(f"Created upload directory: {UPLOAD_FOLDER}")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

def parse_analysis_text(text: str) -> dict:
    """Parse the analysis text from Gemini into structured data"""
    try:
        # Initialize default structure
        data = {
            'score': 0,
            'regulations': [],
            'violations': []
        }
        
        # Split text into sections
        sections = text.split('\n\n')
        current_section = None
        
        for section in sections:
            if not section.strip():
                continue
                
            # Parse compliance score
            if '%' in section and any(char.isdigit() for char in section):
                # Extract first number followed by % in the text
                import re
                score_match = re.search(r'(\d+)%', section)
                if score_match:
                    data['score'] = int(score_match.group(1))
                    
            # Parse regulations
            elif 'Compliant' in section:
                lines = section.strip().split('\n')
                for line in lines:
                    if '-' in line or '•' in line:
                        parts = line.replace('-', '').replace('•', '').strip().split(':')
                        if len(parts) >= 2:
                            name = parts[0].strip()
                            status = parts[1].strip()
                            data['regulations'].append({
                                'name': name,
                                'status': status
                            })
                            
            # Parse violations
            elif any(severity in section.lower() for severity in ['high', 'medium', 'low']):
                lines = section.strip().split('\n')
                violation = {}
                
                for line in lines:
                    if 'high' in line.lower():
                        violation['severity'] = 'High'
                    elif 'medium' in line.lower():
                        violation['severity'] = 'Medium'
                    elif 'low' in line.lower():
                        violation['severity'] = 'Low'
                        
                    if 'title:' in line.lower():
                        violation['title'] = line.split('title:')[1].strip()
                    elif 'description:' in line.lower():
                        violation['description'] = line.split('description:')[1].strip()
                    elif 'remediation:' in line.lower():
                        violation['remediation'] = line.split('remediation:')[1].strip()
                
                if violation:
                    # Ensure all required fields exist
                    violation.setdefault('title', 'Unnamed Violation')
                    violation.setdefault('description', 'No description provided')
                    violation.setdefault('remediation', 'No remediation steps provided')
                    violation.setdefault('severity', 'Medium')
                    data['violations'].append(violation)
        
        return data
        
    except Exception as e:
        print(f"Error parsing analysis text: {str(e)}")
        # Return default structure if parsing fails
        return {
            'score': 0,
            'regulations': [
                {'name': 'Environmental Protection Standards', 'status': 'Unknown'},
                {'name': 'Safety Regulations', 'status': 'Unknown'},
                {'name': 'Grid Reliability Standards', 'status': 'Unknown'},
                {'name': 'Emissions Reporting', 'status': 'Unknown'},
                {'name': 'Renewable Portfolio Standards', 'status': 'Unknown'}
            ],
            'violations': []
        }

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return render_template('index.html', error='No file part')
        
        file = request.files['file']
        
        if file.filename == '':
            return render_template('index.html', error='No selected file')
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            try:
                file.save(filepath)
                api_key = 'AIzaSyAUNX0gJyu0aP6bSWf1zwYjJ7KeGtHJX2w'
                monitor = ComplianceMonitor(api_key)
                result = monitor.generate_compliance_report(filepath)
                
                if os.path.exists(filepath):
                    os.remove(filepath)
                
                if 'error' in result:
                    return render_template('index.html', error=result['error'])
                
                # Just pass the raw analysis text to the template
                return render_template('index.html', result=result['analysis'])
                
            except Exception as e:
                if os.path.exists(filepath):
                    os.remove(filepath)
                return render_template('index.html', error=f'Error processing file: {str(e)}')
        
        return render_template('index.html', error='Invalid file type')
        
    except Exception as e:
        return render_template('index.html', error=f'Upload failed: {str(e)}')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port) 
from flask import Flask, render_template, request, flash
import os
from compliance_monitor import ComplianceMonitor
from werkzeug.utils import secure_filename
import logging
import tempfile
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for flash messages

# Configure upload folder - use /tmp for Render
UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = {'txt', 'pdf'}

# Ensure upload directory exists with proper permissions
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    logger.info(f"Created upload directory: {UPLOAD_FOLDER}")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

def parse_analysis_text(text: str) -> dict:
    """Parse the analysis text from Gemini into structured data"""
    try:
        # Initialize default structure
        data = {
            'score': 0,
            'regulations': [],
            'violations': []
        }
        
        # Split text into sections
        sections = text.split('\n\n')
        current_section = None
        
        for section in sections:
            if not section.strip():
                continue
                
            # Parse compliance score
            if '%' in section and any(char.isdigit() for char in section):
                # Extract first number followed by % in the text
                import re
                score_match = re.search(r'(\d+)%', section)
                if score_match:
                    data['score'] = int(score_match.group(1))
                    
            # Parse regulations
            elif 'Compliant' in section:
                lines = section.strip().split('\n')
                for line in lines:
                    if '-' in line or '•' in line:
                        parts = line.replace('-', '').replace('•', '').strip().split(':')
                        if len(parts) >= 2:
                            name = parts[0].strip()
                            status = parts[1].strip()
                            data['regulations'].append({
                                'name': name,
                                'status': status
                            })
                            
            # Parse violations
            elif any(severity in section.lower() for severity in ['high', 'medium', 'low']):
                lines = section.strip().split('\n')
                violation = {}
                
                for line in lines:
                    if 'high' in line.lower():
                        violation['severity'] = 'High'
                    elif 'medium' in line.lower():
                        violation['severity'] = 'Medium'
                    elif 'low' in line.lower():
                        violation['severity'] = 'Low'
                        
                    if 'title:' in line.lower():
                        violation['title'] = line.split('title:')[1].strip()
                    elif 'description:' in line.lower():
                        violation['description'] = line.split('description:')[1].strip()
                    elif 'remediation:' in line.lower():
                        violation['remediation'] = line.split('remediation:')[1].strip()
                
                if violation:
                    # Ensure all required fields exist
                    violation.setdefault('title', 'Unnamed Violation')
                    violation.setdefault('description', 'No description provided')
                    violation.setdefault('remediation', 'No remediation steps provided')
                    violation.setdefault('severity', 'Medium')
                    data['violations'].append(violation)
        
        return data
        
    except Exception as e:
        print(f"Error parsing analysis text: {str(e)}")
        # Return default structure if parsing fails
        return {
            'score': 0,
            'regulations': [
                {'name': 'Environmental Protection Standards', 'status': 'Unknown'},
                {'name': 'Safety Regulations', 'status': 'Unknown'},
                {'name': 'Grid Reliability Standards', 'status': 'Unknown'},
                {'name': 'Emissions Reporting', 'status': 'Unknown'},
                {'name': 'Renewable Portfolio Standards', 'status': 'Unknown'}
            ],
            'violations': []
        }

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return render_template('index.html', error='No file part')
        
        file = request.files['file']
        
        if file.filename == '':
            return render_template('index.html', error='No selected file')
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            try:
                file.save(filepath)
                api_key = 'AIzaSyAUNX0gJyu0aP6bSWf1zwYjJ7KeGtHJX2w'
                monitor = ComplianceMonitor(api_key)
                result = monitor.generate_compliance_report(filepath)
                
                if os.path.exists(filepath):
                    os.remove(filepath)
                
                if 'error' in result:
                    return render_template('index.html', error=result['error'])
                
                # Just pass the raw analysis text to the template
                return render_template('index.html', result=result['analysis'])
                
            except Exception as e:
                if os.path.exists(filepath):
                    os.remove(filepath)
                return render_template('index.html', error=f'Error processing file: {str(e)}')
        
        return render_template('index.html', error='Invalid file type')
        
    except Exception as e:
        return render_template('index.html', error=f'Upload failed: {str(e)}')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port) 