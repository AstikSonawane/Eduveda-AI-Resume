import streamlit as st
import base64
import os
import io
import fitz  # PyMuPDF
import google.generativeai as genai
from dotenv import load_dotenv
import time
import google.api_core.exceptions

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Helper function to extract text from PDF
def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text("text")  # Extract text from each page
    return text

# AI model function with error handling
def get_gemini_response(input, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-pro')
    time.sleep(10)
    
    try:
        response = model.generate_content([input, pdf_content, prompt])
        return response.text
    except google.api_core.exceptions.ResourceExhausted:
        st.error("The service is temporarily unavailable due to high demand. Please try again after a few moments.")
        return None
    except google.api_core.exceptions.GoogleAPICallError as e:
        st.error(f"An error occurred with the AI service: {e}")
        return None

# Streamlit App Config with Custom Favicon
st.set_page_config(
    page_title="EDUVEDA",
    page_icon="logo.png",
    layout="centered"
)

# Custom CSS for Modern UI
st.markdown("""
    <style>
    /* App background color */
    body {
        background-color: #EEEEEE;
        color: #000000;
    }

    /* Header and Logo */
    .header-logo img {
        display: block;
        margin: 0 auto;
        width: 150px;
        margin-bottom: 10px;
        border-radius: 10%;
    }

    /* Green button styling */
    .stButton>button {
        background: #28a745;
        color: white;
        border-radius: 8px;
        padding: 12px 20px;
        font-weight: bold;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
        border: none;
        height: 50px;
        width: 100%;
    }

    .stButton>button:hover {
        background-color: white;
        color: black;
    }

    /* File upload area */
    .upload-area {
        border: 2px dashed #28a745;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        color: #333;
    }

    /* Input fields */
    textarea, .stTextInput input {
        background-color: #F0F0F0;
        color: #333;
        border-radius: 10px;
        border: 1px solid #ccc;
        padding: 10px;
        width: 100%;
    }

    /* Subheaders */
    .stSubheader {
        color: #333;
        font-size: 22px;
        font-weight: 600;
    }

    /* Footer */
    .footer {
        font-size: 14px;
        color: #666;
        text-align: center;
        padding: 10px 0;
    }

    .footer a {
        color: #28a745;
        text-decoration: none;
        font-weight: bold;
    }

    .footer a:hover {
        color: #218838;
    }

    .button-column {
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 10px;
    }

    /* Mobile responsive adjustments */
    @media (max-width: 600px) {
        .stButton>button {
            font-size: 14px;
            padding: 10px;
        }

        .stTextInput input, textarea {
            font-size: 14px;
        }

        .upload-area {
            padding: 10px;
        }

        .footer {
            font-size: 12px;
        }

        .button-column {
            flex-direction: column;
        }
    }
    </style>
""", unsafe_allow_html=True)


# Logo Section - Centered Logo
logo_path = "aire.png"
if os.path.exists(logo_path):
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    st.image(logo_path, width=250)
    st.markdown("</div>", unsafe_allow_html=True)

# Job Description Input Section
st.subheader("Job Description")
input_text = st.text_area("Enter the Job Description", placeholder="Paste the job description here...", key="input")

# Resume Upload Section
st.markdown("<div class='upload-area'>Upload your resume (PDF only)</div>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["pdf"])

# Action Buttons (Optimized for Mobile View)
col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
with col1:
    analyze_button = st.button("Analyze Resume")
with col2:
    match_button = st.button("ATS Score")
with col3:
    generate_cover_letter_button = st.button("Generate Cover Letter")
with col4:
    generate_resume_button = st.button("Generate Tailored Resume")

# Prompts
input_prompt1 = " You are an experienced Technical Human Resource Manager,your task is to review the provided resume against the job description. Please share your professional evaluation on whether the candidate's profile aligns with the role. Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements."
input_prompt3 = "You are an skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality, your task is to evaluate the resume against the provided job description. give me the percentage of match if the resume matches the job description (ats score). First the output should come as percentage and then keywords missing and last final thoughts."
input_prompt_cover_letter = "Based on the job description and my uploaded resume, create a professional, three-paragraph cover letter. In the first paragraph, mention the [role] I'm applying for and how I learned about this opportunity. In the second paragraph, highlight my relevant skills, experiences, and accomplishments that align with the job description. In the third and final paragraph, express my enthusiasm for the role, thank the recruiters for their time, and convey my excitement for the next stages of the hiring process and sincerely [name]"
input_prompt_resume = "Using the provided job description and the uploaded resume, create a tailored resume that best fits the requirements of the job. Make sure to highlight the relevant skills, experience (make sure in bullet points), and qualifications from the resume that match the job description. If any areas of improvement or additions are needed, suggest modifications to ensure the resume aligns with the job's key requirements. The tailored resume should showcase the most relevant aspects of the candidate's experience that directly correspond to the role, skills, and qualifications mentioned in the job description."

# Analysis & Response
if analyze_button:
    if uploaded_file is not None:
        pdf_text = extract_text_from_pdf(uploaded_file)
        with st.spinner("Analyzing resume..."):
            response = get_gemini_response(input_text, pdf_text, input_prompt1)
            st.subheader("Resume Analysis")
            st.write(response)
    else:
        st.warning("Please upload your resume to proceed.")

elif match_button:
    if uploaded_file is not None:
        pdf_text = extract_text_from_pdf(uploaded_file)
        with st.spinner("Calculating match percentage..."):
            response = get_gemini_response(input_text, pdf_text, input_prompt3)
            st.subheader("Match Percentage & Recommendations")
            st.write(response)
    else:
        st.warning("Please upload your resume to proceed.")

if generate_cover_letter_button:
    if uploaded_file is not None:
        pdf_text = extract_text_from_pdf(uploaded_file)
        with st.spinner("Generating cover letter..."):
            cover_letter = get_gemini_response(input_text, pdf_text, input_prompt_cover_letter)
            st.subheader("Tailored Cover Letter")
            st.write(cover_letter)
    else:
        st.warning("Please upload your resume to proceed.")

if generate_resume_button:
    if uploaded_file is not None:
        pdf_text = extract_text_from_pdf(uploaded_file)
        with st.spinner("Generating tailored resume..."):
            tailored_resume = get_gemini_response(input_text, pdf_text, input_prompt_resume)
            st.subheader("Tailored Resume")
            st.write(tailored_resume)
    else:
        st.warning("Please upload your resume to proceed.")

# Footer with credits and links
st.markdown("""
    <div class='footer'>
        Developed by <strong>Gayatri Thakre</strong> |
        <a href='https://www.linkedin.com/in/gaytri-thakre-19124b232/' target='_blank'>LinkedIn</a> |
        <a href='https://github.com/Gaytri-Thakre' target='_blank'>GitHub</a>
    </div>
""", unsafe_allow_html=True)
