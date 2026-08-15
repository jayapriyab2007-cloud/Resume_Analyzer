# 🤖 AI Resume Analyzer V2

An AI-powered Resume Analyzer that helps job seekers understand how well their resume matches a job description, identify missing skills, discover suitable job roles, and receive personalized career improvement suggestions.

The application uses **Natural Language Processing (NLP)**, **TF-IDF similarity**, and **Google Gemini AI** to analyze resumes and generate actionable recommendations.

---

## 🚀 Features

### 📄 Resume Upload
Upload your resume in multiple formats:

- PDF
- DOCX
- TXT

The application extracts the resume content automatically for analysis.

### 🧠 Skill Extraction
Identifies relevant technical and professional skills from the uploaded resume.

Examples:

- Python
- Java
- SQL
- Machine Learning
- Data Analysis
- React
- UI/UX
- Communication

### 🎯 Job Match Score
Compares the resume with a given job description and calculates a match score based on the relevance of the resume content.

### 💼 Job Role Recommendations
The system recommends **5+ suitable job roles** based on the candidate's skills and resume profile.

Example roles:

- Data Analyst
- Python Developer
- Machine Learning Engineer
- Software Developer
- Business Analyst
- UI/UX Designer

### 🚨 Skill Gap Analysis
Identifies skills that are required for the target job but are missing or insufficiently represented in the resume.

### 🗺️ AI Career Roadmap
Generates a personalized learning roadmap to help candidates improve their skills and become more suitable for their target roles.

### ✍️ Resume Improvement Suggestions
Provides AI-generated suggestions to improve:

- Skills section
- Project descriptions
- Professional summary
- Keywords
- Resume structure
- Job-specific content

### 📊 Interactive Dashboard
Displays important resume analysis information in an easy-to-understand dashboard.

The dashboard can include:

- Overall match percentage
- Number of detected skills
- Recommended job roles
- Missing skills
- Strengths
- Skill gaps
- Career roadmap

### 📥 Downloadable Report
Allows users to download their resume analysis as a report for future reference.

---

## 🏗️ Project Architecture

```text
                    ┌─────────────────────┐
                    │    Resume Upload    │
                    │   PDF/DOCX/TXT      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Resume Text         │
                    │ Extraction          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Skill Extraction    │
                    │ & Text Processing    │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
          ┌─────────────────┐   ┌─────────────────┐
          │ Job Description │   │ Resume Profile  │
          └────────┬────────┘   └────────┬────────┘
                   │                     │
                   └──────────┬──────────┘
                              ▼
                    ┌─────────────────────┐
                    │ TF-IDF + Cosine     │
                    │ Similarity Analysis │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Gemini AI        │
                    │     Analysis        │
                    └──────────┬──────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
   ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
   │ Match Score │      │ Skill Gaps  │      │ Job Roles   │
   └─────────────┘      └─────────────┘      └─────────────┘
          │                    │                    │
          └────────────────────┼────────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │ AI Career Roadmap   │
                    │ & Suggestions       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Interactive         │
                    │ Dashboard           │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Downloadable Report │
                    └─────────────────────┘