import streamlit as st
import os
import io
import fitz  # PyMuPDF
import google.generativeai as genai
from dotenv import load_dotenv
import google.api_core.exceptions
import time

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# Helper function to extract text from PDF
def extract_text_from_pdf(uploaded_file):
    try:
        if uploaded_file.name.lower().endswith(".pdf"):
             doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
             text = ""
             for page_num in range(len(doc)):
                 page = doc.load_page(page_num)
                 text += page.get_text("text")
             if not text.strip():  # Check if extracted text is empty
                 st.error("The uploaded PDF is empty.")
                 return None
             return text
        else:
              st.error("Uploaded file is not a PDF. Please upload a PDF document.")
              return None
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None


# AI model function with error handling
def get_gemini_response(input_text, pdf_content, prompt):
    if not input_text or not pdf_content:
        st.warning("Please enter job description and upload resume.")
        return None
    model = genai.GenerativeModel('gemini-1.5-pro')
    #time.sleep(1) # No need for time.sleep
    try:
        with st.spinner("Processing..."):  # Show a Streamlit loading spinner
             response = model.generate_content([prompt, f"Job Description: {input_text}", f"Resume: {pdf_content}"])
             return response.text
    except google.api_core.exceptions.ResourceExhausted:
        st.error("The service is temporarily unavailable due to high demand. Please try again after a few moments.")
        return None
    except google.api_core.exceptions.GoogleAPICallError as e:
        st.error(f"An error occurred with the AI service: {e}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
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
        [data-testid="stAppViewContainer"] {
        background-image: url('https://images.unsplash.com/photo-1642355008521-236f1d29d0a8?q=80&w=1932&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D');
        background-size: cover;
        background-position: center;
        height: 100%;
        padding-top: 50px;
    }

    .app-background {
        background-color: #EEEEEE;
        color: #FFFFFF;
    }

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

    .upload-area {
        border: 2px dashed #28a745;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        color: white;
    }

    .stTextInput input, textarea {
        background-color: #F0F0F0;
        color: white;
        border-radius: 10px;
        border: 1px solid #ccc;
        padding: 10px;
        width: 100%;
    }

    .stSubheader {
        color: white;
        font-size: 22px;
        font-weight: 600;
    }

    .footer {
        font-size: 14px;
        color: white;
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
uploaded_file = st.file_uploader("Upload Resume", type=["pdf"])

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
input_prompt1 = "You are an experienced Technical Human Resource Manager, your task is to review the provided resume against the job description. Please share your professional evaluation on whether the candidate's profile aligns with the role. Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements."
input_prompt3 = "You are an skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality, your task is to evaluate the resume against the provided job description. give me the percentage of match if the resume matches the job description (ats score). First the output should come as percentage and then keywords missing and last final thoughts."
input_prompt_cover_letter = """
    You are a professional resume writer. Based on the job description and the provided resume, please create a professional cover letter.
    Make sure you output cover letter in the following format:
    
    [First Paragraph]: Should include a sentence mentioning the job role. How and where did the applicant find the opportunity.
    
    [Second Paragraph]: Should include applicant's skills, experience, and accomplishments that align with the job description.
    
    [Third Paragraph]: Should include expression of the applicant's enthusiasm for the role. The closing should thank the recruiters for their time, and excitement for the next stages of the hiring process and sincerely followed by applicant's name.
    
    Make sure the output you are providing follows the format given above.
    """
input_prompt_resume = """
    You are a professional resume writer. Based on the job description and the provided resume, please create a tailored resume.
    Make sure you output resume in the following format:
    
    [Skills]: Should list the skills relevant to the job description.
    
    [Experience]: Should list experiences with the job description (make sure to include bullet points for each experience)
    
    Make sure the output you are providing follows the format given above.
    """

# Analysis & Response - Ensure buttons are working independently and not preventing others
pdf_text = None
if uploaded_file:
    pdf_text = extract_text_from_pdf(uploaded_file)

# Button actions (more robust handling of user interactions)
if analyze_button:
     if pdf_text:
        response = get_gemini_response(input_text, pdf_text, input_prompt1)
        if response:
           st.subheader("Resume Analysis")
           st.write(response)
     else:
          st.warning("Please upload a resume to analyze.")

if match_button:
     if pdf_text:
        response = get_gemini_response(input_text, pdf_text, input_prompt3)
        if response:
           st.subheader("Match Percentage & Recommendations")
           st.write(response)
     else:
          st.warning("Please upload a resume to check ATS Score.")

if generate_cover_letter_button:
    if pdf_text:
        cover_letter = get_gemini_response(input_text, pdf_text, input_prompt_cover_letter)
        if cover_letter:
           st.subheader("Tailored Cover Letter")
           st.write(cover_letter)
    else:
          st.warning("Please upload a resume to generate cover letter.")

if generate_resume_button:
    if pdf_text:
        tailored_resume = get_gemini_response(input_text, pdf_text, input_prompt_resume)
        if tailored_resume:
           st.subheader("Tailored Resume")
           st.write(tailored_resume)
    else:
         st.warning("Please upload a resume to generate tailored resume.")

# Footer with credits and links
st.markdown("""
    <div class='footer'>
        Developed by <strong>Gayatri Thakre</strong> |
        <a href='https://www.linkedin.com/in/gaytri-thakre-19124b232/' target='_blank'>LinkedIn</a> |
        <a href='https://github.com/Gaytri-Thakre' target='_blank'>GitHub</a>
    </div>
""", unsafe_allow_html=True)