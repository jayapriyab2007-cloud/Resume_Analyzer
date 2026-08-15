import streamlit as st 
from pypdf import PdfReader 
from docx import Document 
from sklearn.feature_extraction.text import TfidfVectorizer 
from sklearn.metrics.pairwise import cosine_similarity 
import google.generativeai as genai 
 
 
st.set_page_config(page_title="Resume Analyzer") 
 
st.title("AI Resume Analyzer") 
 
st.write("Upload a Resume") 
 
 
# Configure Gemini API Key 
 
genai.configure( 
    api_key=st.secrets["GEMINI_API_KEY"] 
) 
 
 
# Read Uploaded Resume 
 
def read_resume(upload_file): 
 
    file_name = upload_file.name.lower() 
 
    if file_name.endswith(".pdf"): 
 
        pdf_reader = PdfReader(upload_file) 
 
        resume_text = "" 
 
        for page in pdf_reader.pages: 
 
            page_text = page.extract_text() 
 
            if page_text: 
 
                resume_text = resume_text + page_text + "\n" 
 
        return resume_text 
 
    elif file_name.endswith(".docx"): 
 
        document = Document(upload_file) 
 
        resume_text = "" 
 
        for paragraph in document.paragraphs: 
 
            if paragraph.text.strip(): 
 
                resume_text = resume_text + paragraph.text + "\n" 
 
        return resume_text 
 
    elif file_name.endswith(".txt"): 
 
        return upload_file.read().decode("utf-8") 
 
    return "" 
 
 
# Split Resume into Smaller Parts 
 
def create_chunks(resume_text, chunk_size=50): 
 
    words = resume_text.split() 
 
    chunks = [] 
 
    for start in range(0, len(words), chunk_size): 
 
        end = start + chunk_size 
 
        chunk = " ".join(words[start:end]) 
 
        if chunk.strip(): 
 
            chunks.append(chunk) 
 
    return chunks 
 
 
# Find the Most Relevant Resume Sections 
 
def retrieve_chunks(chunks, job_description, top_k=3): 
 
    all_documents = [job_description] + chunks 
 
    # Convert Text into Vectors 
 
    vectorizer = TfidfVectorizer( 
        stop_words="english" 
    ) 
 
    vectors = vectorizer.fit_transform( 
        all_documents 
    ) 
 
    # Separate JD and Resume Vectors 
 
    job_vector = vectors[0:1] 
 
    resume_vectors = vectors[1:] 
 
    # Cosine Similarity Calculation 
 
    similarity_scores = cosine_similarity( 
        job_vector, 
        resume_vectors 
    )[0] 
 
    # Get Top K Indexes 
 
    best_indexes = similarity_scores.argsort()[ 
        -top_k: 
    ][::-1] 
 
    retrieved_results = [] 
 
    for index in best_indexes: 
 
        retrieved_results.append( 
            { 
                "chunk": chunks[index], 
                "score": float( 
                    similarity_scores[index] 
                ) 
            } 
        ) 
 
    return retrieved_results 
 
 
# Generate Final Response Using Gemini 
 
def generate_response( 
    job_description, 
    retrieved_chunks 
): 
 
    context = "" 
 
    for item in retrieved_chunks: 
 
        context += item["chunk"] + "\n\n" 
 
    prompt = f""" 
You are an AI Resume Analyzer. 
 
Job Description: 
 
{job_description} 
 
Relevant Resume Information: 
 
{context} 
 
Tasks: 
 
1. Give a resume match percentage. 
2. Mention candidate strengths. 
3. Mention missing skills. 
4. Suggest improvements. 
""" 
 
    model = genai.GenerativeModel( 
        "gemini-3.6-flash" 
    ) 
 
    response = model.generate_content( 
        prompt 
    ) 
 
    return response.text 
 
 
# Upload Resume 
 
uploaded_file = st.file_uploader( 
    "Upload Resume", 
    type=["pdf", "docx", "txt"] 
) 
 
 
# Enter Job Description 
 
job_description = st.text_area( 
    "Enter Job Description" 
) 
 
 
# Analyze Resume 
 
if st.button("Analyze Resume"): 
 
    if uploaded_file is None: 
 
        st.warning( 
            "Please upload a resume." 
        ) 
 
    elif job_description == "": 
 
        st.warning( 
            "Please enter a job description." 
        ) 
 
    else: 
 
        # Read Resume 
 
        resume_text = read_resume( 
            uploaded_file 
        ) 
 
        # Create Chunks 
 
        chunks = create_chunks( 
            resume_text 
        ) 
 
        # Retrieve Relevant Chunks 
 
        retrieved_chunks = retrieve_chunks( 
            chunks, 
            job_description 
        ) 
 
        # Generate Final Response 
 
        final_response = generate_response( 
            job_description, 
            retrieved_chunks 
        ) 
 
        # Display Result 
 
        st.subheader( 
            "Resume Analysis" 
        ) 
 
        st.write( 
            final_response 
        )