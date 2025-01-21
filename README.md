# Eduveda - Tailored Resume & Cover Letter Generator

A Streamlit web app designed to help users tailor their resumes and generate personalized cover letters. By analyzing job descriptions and resumes, this tool leverages Google's Gemini AI to assess the alignment between the user's profile and the job requirements. It also calculates ATS (Applicant Tracking System) scores to improve job application success.

https://eduveda-ai-resume-fyp-gayu55.streamlit.app/

## Features

- **Job Description Analysis**: Input job descriptions to understand key skills and requirements.
- **Resume Upload**: Upload a PDF resume for analysis.
- **Resume Tailoring**: Generate a tailored resume that matches the job description.
- **ATS Score**: Evaluate the resume's compatibility with job requirements and provide a match percentage along with missing keywords.
- **Cover Letter Generation**: Automatically generate a personalized cover letter based on the job description and resume.

## Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **AI Model**: Google Gemini AI
- **Libraries**:
  - `pdf2image` - To convert PDF resumes to images for AI analysis.
  - `PIL` - For image processing.
  - `google-generativeai` - For interacting with Gemini AI.
  - `dotenv` - For managing environment variables.


