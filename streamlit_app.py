import os
import streamlit as st
from compliance_monitor import ComplianceMonitor
import tempfile

# Use tempfile for uploads in Streamlit Cloud
UPLOAD_FOLDER = tempfile.gettempdir()

def main():
    st.set_page_config(
        page_title="ComplianceGuard",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Add custom CSS
    st.markdown("""
        <style>
        .main {
            background-color: #1a1f2e;
            color: #ffffff;
        }
        .stButton>button {
            background-color: #4C63B6;
            color: white;
            border-radius: 0.5rem;
            padding: 0.5rem 2rem;
        }
        .upload-box {
            border: 2px dashed #4C63B6;
            border-radius: 0.5rem;
            padding: 2rem;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h1>ComplianceGuard</h1>
            <p>Upload your document for compliance analysis</p>
        </div>
    """, unsafe_allow_html=True)

    # File upload
    uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'txt'], 
                                   help="Upload PDF or TXT files only")

    if uploaded_file is not None:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            file_path = tmp_file.name

        try:
            # Process the file
            if st.button("Generate Compliance Report"):
                with st.spinner("Analyzing document..."):
                    monitor = ComplianceMonitor()
                    result = monitor.process_document(file_path)

                    if 'error' in result:
                        st.error(result['error'])
                    else:
                        # Display compliance score
                        score = result.get('compliance_score', 0)
                        st.markdown(f"""
                            <div style='text-align: center; margin: 2rem 0;'>
                                <h2>Overall Compliance Score</h2>
                                <div style='font-size: 3rem; font-weight: bold; color: {"#4CAF50" if score >= 70 else "#FFA726" if score >= 40 else "#EF5350"}'>
                                    {score}%
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

                        # Display analysis results in expandable sections
                        with st.expander("Regulation Summary", expanded=True):
                            st.markdown(result['analysis'])

                # Cleanup temporary file
                try:
                    os.unlink(file_path)
                except:
                    pass  # Ignore cleanup errors

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            # Cleanup on error
            try:
                os.unlink(file_path)
            except:
                pass

if __name__ == "__main__":
    main() 