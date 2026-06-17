import streamlit as st
from google import genai
import PyPDF2
import os
from dotenv import load_dotenv
import time

# ------------------ LOAD API KEY ------------------
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("❌ API key not found. Please check your .env file.")
    st.stop()

# ------------------ GEMINI CLIENT ------------------
from google import genai
client = genai.Client(api_key=api_key)

# Model
MODEL_NAME = "gemini-2.5-flash"  

# ------------------ PDF TEXT EXTRACTION ------------------
def extract_text_from_pdf(uploaded_file):
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    except Exception as e:
        st.error(f"❌ Error reading PDF: {e}")
    return text

# ------------------ STREAMLIT UI ------------------
st.set_page_config(page_title="ATS Resume Checker", page_icon="📄")

st.title("📄 ATS Resume Checker")
st.markdown("### 🚀 Check your resume ATS score instantly")
st.write("Upload your resume and paste job description to analyze match score.")

# 🔍 MODEL CHECK BUTTON (NEW ADD)
if st.button("🔍 Check Available Models"):
    try:
        models = client.models.list()
        st.write("✅ Available Models:")
        for m in models:
            st.write(m.name)
    except Exception as e:
        st.error(f"❌ Error fetching models: {e}")

# Upload resume
uploaded_file = st.file_uploader("📂 Upload Resume (PDF)", type=["pdf"])

# Job description input
job_description = st.text_area("📝 Paste Job Description")

# action button
if st.button("🔍 Check ATS Score"):

    if uploaded_file is None or not job_description:
        st.warning("⚠️ Please upload resume and enter job description.")
    
    else:
        resume_text = extract_text_from_pdf(uploaded_file)

        if not resume_text:
            st.warning("⚠️ Could not extract text from PDF. Try another file.")
        
        else:
            prompt = f"""
You are a professional ATS (Applicant Tracking System).

Analyze the resume against the job description.

Resume:
{resume_text}

Job Description:
{job_description}

Provide:
1. ATS Score (out of 100)
2. Matching Percentage
3. Missing Keywords
4. Strengths
5. Weaknesses
6. Improvement Suggestions
"""

            try:
                with st.spinner("⏳ Analyzing resume... Please wait"):

                    # 🔁 Retry system (for rate limit error 429)
                    for attempt in range(3):
                        try:
                            response = client.models.generate_content(
                                model=MODEL_NAME,  # Use the updated model
                                contents=prompt
                            )
                            break
                        except Exception as e:
                            if "429" in str(e) and attempt < 2:
                                time.sleep(20)
                            else:
                                raise e
                            break
                        except Exception as e:
                            if "429" in str(e) and attempt < 2:
                                time.sleep(20)
                            else:
                                raise e

                st.success("✅ Analysis Completed Successfully!")
                st.subheader("📊 ATS Analysis Result")

                result_text = response.text

                if result_text:
                    st.markdown(result_text)
                else:
                    st.warning("⚠️ No response text received. Try again.")

            except Exception as e:
                st.error(f"❌ Error generating response: {e}")
                st.write("🔍 Available Models:")

try:
    models = client.models.list()
    for m in models:
        st.write(m.name)
except Exception as e:
    st.error(f"Error fetching models: {e}")