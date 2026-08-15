import streamlit as st
from pypdf import PdfReader
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai


# ----------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------

st.set_page_config(
    page_title="Resume Analyzer",
    page_icon="e:\downloads\noun-chatbot-1596693.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ----------------------------------------------------------------------
# STYLE — soft pink/purple palette, calm and professional
# ----------------------------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --bg:            #F3EDF1;
        --surface:       #FFFFFF;
        --surface-alt:   #F6EFF4;
        --border:        #E9DCE6;
        --text-primary:  #362D3B;
        --text-secondary:#7C6D80;
        --accent:        #A47DB8;   /* muted purple */
        --accent-soft:   #EEE1F1;   /* pale lavender-pink */
        --accent-dark:   #7C5A91;
        --rose:          #D98CA0;   /* dusty pink accent */
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, sans-serif;
        color: var(--text-primary);
    }

    /* ---------- Interesting layered background instead of flat color ---------- */
    .stApp {
        background:
            radial-gradient(circle at 12% 18%, rgba(164, 125, 184, 0.22), transparent 42%),
            radial-gradient(circle at 88% 12%, rgba(217, 140, 160, 0.20), transparent 46%),
            radial-gradient(circle at 50% 100%, rgba(164, 125, 184, 0.18), transparent 55%),
            linear-gradient(180deg, #F6F0F4 0%, var(--bg) 100%);
        background-attachment: fixed;
    }

    /* Hide default Streamlit chrome for a cleaner look */
    #MainMenu, footer, header {visibility: hidden;}

    .block-container {
        max-width: 880px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }

    /* ---------- Header ---------- */
    .app-header {
        text-align: center;
        margin-bottom: 2.25rem;
    }
    .app-header .eyebrow {
        font-size: 0.78rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: var(--accent-dark);
        font-weight: 600;
        margin-bottom: 0.6rem;
    }
    .app-header h1 {
        font-family: 'Fraunces', serif;
        font-weight: 700;
        font-size: 3rem;
        margin: 0 0 0.6rem 0;
        letter-spacing: -0.01em;
        background: linear-gradient(120deg, var(--accent-dark) 0%, var(--accent) 55%, var(--rose) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        display: inline-block;
    }
    .app-header .title-wrap {
        position: relative;
        display: inline-block;
    }
    .app-header .sparkle {
        position: absolute;
        top: -0.2rem;
        right: -1.6rem;
        font-size: 1.4rem;
        -webkit-text-fill-color: initial;
        animation: sparkle-float 2.6s ease-in-out infinite;
    }
    @keyframes sparkle-float {
        0%, 100% { transform: translateY(0) rotate(0deg); opacity: 0.85; }
        50%      { transform: translateY(-6px) rotate(12deg); opacity: 1; }
    }
    .app-header p {
        color: var(--text-secondary);
        font-size: 1rem;
        max-width: 480px;
        margin: 0 auto;
        line-height: 1.55;
    }

    /* ---------- Cards ----------
       Applied to real st.container(key=...) wrappers, so padding/border
       actually enclose their children instead of floating as an empty box. */
    div[class*="st-key-"] > div {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.75rem;
        box-shadow: 0 1px 2px rgba(54, 45, 59, 0.05);
        transition: box-shadow 0.2s ease, transform 0.2s ease, border-color 0.2s ease;
    }
    div[class*="st-key-"]:hover > div {
        box-shadow: 0 10px 24px rgba(164, 125, 184, 0.16);
        border-color: var(--accent-soft);
        transform: translateY(-2px);
    }

    .card-label {
        font-size: 0.78rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-weight: 600;
        color: var(--accent-dark);
        margin-bottom: 0.9rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* ---------- Kill Streamlit's own default widget chrome ---------- */
    [data-testid="stFileUploader"],
    [data-testid="stFileUploader"] section,
    [data-testid="stTextArea"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        box-shadow: none !important;
    }
    [data-testid="stWidgetLabel"] {
        display: none !important;
    }

    /* ---------- Inputs ---------- */
    .stTextArea textarea {
        background: var(--surface-alt) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
        font-size: 0.95rem !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }
    .stTextArea textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px var(--accent-soft) !important;
    }
    .stTextArea textarea::placeholder {
        color: var(--text-secondary) !important;
        opacity: 1 !important;
    }

    [data-testid="stFileUploaderDropzone"] {
        background: var(--surface-alt) !important;
        border: 1.5px dashed var(--border) !important;
        border-radius: 10px !important;
        padding: 1.5rem 1.25rem !important;
        transition: border-color 0.15s ease, background 0.15s ease;
    }
    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: var(--accent) !important;
        background: var(--accent-soft) !important;
    }

    /* Instruction text ("Drag & drop" / size limit) — give it breathing
       room so it doesn't hug the dropzone border, and make it visible */
    [data-testid="stFileUploaderDropzoneInstructions"] {
        margin-top: 0.6rem !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"],
    [data-testid="stFileUploaderDropzoneInstructions"] span,
    [data-testid="stFileUploaderDropzoneInstructions"] small,
    [data-testid="stFileUploaderDropzoneInstructions"] div {
        color: var(--text-secondary) !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] svg {
        fill: var(--accent) !important;
    }

    [data-testid="stFileUploaderDropzone"] button {
        background: var(--surface) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        transition: background 0.15s ease, transform 0.15s ease;
    }
    [data-testid="stFileUploaderDropzone"] button:hover {
        background: var(--accent) !important;
        color: #FFFFFF !important;
        border-color: var(--accent) !important;
        transform: translateY(-1px);
    }
    [data-testid="stFileUploaderDropzone"] button p,
    [data-testid="stFileUploaderDropzone"] button span {
        color: inherit !important;
    }

    [data-testid="stFileUploaderFile"] {
        color: var(--text-primary) !important;
        background: var(--surface) !important;
        border-radius: 8px !important;
    }
    [data-testid="stFileUploaderFileName"] {
        color: var(--text-primary) !important;
    }
    [data-testid="stCaptionContainer"] {
        color: var(--text-secondary) !important;
        margin-top: 0.75rem !important;
    }

    /* ---------- Button ---------- */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent) 0%, var(--rose) 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 999px !important;
        padding: 0.7rem 2.2rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.01em;
        transition: box-shadow 0.2s ease, transform 0.15s ease, filter 0.15s ease;
        box-shadow: 0 4px 14px rgba(164, 125, 184, 0.35);
        width: 100%;
    }
    .stButton > button:hover {
        filter: brightness(1.06);
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(164, 125, 184, 0.45);
    }
    .stButton > button:active {
        transform: translateY(0);
    }

    /* ---------- Reward badge ---------- */
    .score-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1.1rem;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 1.25rem;
        animation: pop-in 0.35s ease;
    }
    .score-badge.tier-excellent { background: #EAF6EE; color: #3F8556; }
    .score-badge.tier-good      { background: var(--accent-soft); color: var(--accent-dark); }
    .score-badge.tier-fair      { background: #FDF1DD; color: #B4791C; }
    .score-badge.tier-low       { background: #FBEAEE; color: #B0506A; }

    @keyframes pop-in {
        0%   { opacity: 0; transform: scale(0.85); }
        100% { opacity: 1; transform: scale(1); }
    }

    /* ---------- Alerts ---------- */
    div[data-testid="stAlert"] {
        border-radius: 10px;
        border: 1px solid var(--border);
    }

    /* ---------- Results ---------- */
    .results-header {
        font-family: 'Fraunces', serif;
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.25rem;
    }
    .results-sub {
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin-bottom: 1.25rem;
    }
    .results-body {
        font-size: 0.96rem;
        line-height: 1.65;
        color: var(--text-primary);
    }
    .results-body h1, .results-body h2, .results-body h3 {
        font-family: 'Fraunces', serif;
        color: var(--accent-dark);
        margin-top: 1.1rem;
    }

    /* ---------- Divider ---------- */
    .soft-divider {
        border: none;
        border-top: 1px solid var(--border);
        margin: 2rem 0;
    }

    /* ---------- Mobile responsiveness ---------- */
    @media (max-width: 640px) {
        .app-header h1 { font-size: 2.1rem; }
        .block-container { padding-left: 1rem; padding-right: 1rem; }
        div[class*="st-key-"] > div { padding: 1.25rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------
# GEMINI CONFIG
# ----------------------------------------------------------------------

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])


# ----------------------------------------------------------------------
# CORE LOGIC (unchanged behavior, same functions)
# ----------------------------------------------------------------------

def read_resume(upload_file):
    file_name = upload_file.name.lower()

    if file_name.endswith(".pdf"):
        pdf_reader = PdfReader(upload_file)
        resume_text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                resume_text += page_text + "\n"
        return resume_text

    elif file_name.endswith(".docx"):
        document = Document(upload_file)
        resume_text = ""
        for paragraph in document.paragraphs:
            if paragraph.text.strip():
                resume_text += paragraph.text + "\n"
        return resume_text

    elif file_name.endswith(".txt"):
        return upload_file.read().decode("utf-8")

    return ""


def create_chunks(resume_text, chunk_size=50):
    words = resume_text.split()
    chunks = []
    for start in range(0, len(words), chunk_size):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
    return chunks


def retrieve_chunks(chunks, job_description, top_k=3):
    all_documents = [job_description] + chunks

    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform(all_documents)

    job_vector = vectors[0:1]
    resume_vectors = vectors[1:]

    similarity_scores = cosine_similarity(job_vector, resume_vectors)[0]
    best_indexes = similarity_scores.argsort()[-top_k:][::-1]

    retrieved_results = []
    for index in best_indexes:
        retrieved_results.append(
            {"chunk": chunks[index], "score": float(similarity_scores[index])}
        )
    return retrieved_results


def extract_score(response_text):
    """Pull the first percentage number out of the model's response,
    for the reward badge. Returns None if nothing is found."""
    import re

    match = re.search(r"(\d{1,3})\s*%", response_text)
    if match:
        return min(int(match.group(1)), 100)
    return None


def score_badge(score):
    """Return (css_tier_class, emoji, label) for a given score."""
    if score is None:
        return "tier-good", "✨", "Analysis Complete"
    if score >= 80:
        return "tier-excellent", "🏆", f"Excellent Match — {score}%"
    if score >= 60:
        return "tier-good", "✅", f"Good Match — {score}%"
    if score >= 40:
        return "tier-fair", "🌱", f"Fair Match — {score}%"
    return "tier-low", "💡", f"Needs Work — {score}%"


def generate_response(job_description, retrieved_chunks):
    context = ""
    for item in retrieved_chunks:
        context += item["chunk"] + "\n\n"

    prompt = f"""
You are an AI Resume Analyzer.

Job Description:

{job_description}

Relevant Resume Information:

{context}

Respond in clean Markdown with these sections, in this order:

## Match Score
State a resume match percentage.

## Strengths
Bullet list of candidate strengths relevant to the role.

## Missing Skills
Bullet list of skills or qualifications the resume is missing.

## Suggestions
Bullet list of concrete improvements the candidate could make.
"""

    model = genai.GenerativeModel("gemini-3.6S-flash")
    response = model.generate_content(prompt)
    return response.text


# ----------------------------------------------------------------------
# UI — HEADER
# ----------------------------------------------------------------------

st.markdown(
    """
    <div class="app-header">
        <div class="eyebrow">AI-Powered Career Tool</div>
        <div class="title-wrap">
            <h1>Resume Analyzer</h1>
            <span class="sparkle">✨</span>
        </div>
        <p>Upload your resume and a job description to get a clear match score,
        key strengths, gaps, and tailored suggestions in seconds.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------
# UI — INPUTS
# Real st.container(key=...) wrappers, so the "card" styling actually
# encloses the label + widget + caption instead of floating empty above them.
# ----------------------------------------------------------------------

col_left, col_right = st.columns(2, gap="medium")

with col_left:
    with st.container(key="resume_card"):
        st.markdown('<div class="card-label">📄 Your Resume</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload Resume",
            type=["pdf", "docx", "txt"],
            label_visibility="collapsed",
        )
        st.caption("Accepted formats: PDF, DOCX, TXT")

with col_right:
    with st.container(key="jd_card"):
        st.markdown('<div class="card-label">🎯 Job Description</div>', unsafe_allow_html=True)
        job_description = st.text_area(
            "Enter Job Description",
            height=150,
            placeholder="Paste the job description here...",
            label_visibility="collapsed",
        )

st.write("")
analyze_clicked = st.button("Analyze Resume")
st.write("")


# ----------------------------------------------------------------------
# UI — ANALYSIS FLOW
# ----------------------------------------------------------------------

if analyze_clicked:

    if uploaded_file is None:
        st.warning("Please upload a resume to continue.")

    elif job_description.strip() == "":
        st.warning("Please enter a job description to continue.")

    else:
        with st.spinner("Reading resume and matching against the job description..."):
            resume_text = read_resume(uploaded_file)
            chunks = create_chunks(resume_text)
            retrieved_chunks = retrieve_chunks(chunks, job_description)
            final_response = generate_response(job_description, retrieved_chunks)

        st.markdown('<hr class="soft-divider">', unsafe_allow_html=True)

        score = extract_score(final_response)
        tier_class, emoji, badge_label = score_badge(score)

        st.markdown(
            f"""
            <div class="results-header">Analysis Results</div>
            <div class="results-sub">Based on the resume sections most relevant to this role</div>
            <div class="score-badge {tier_class}">{emoji} {badge_label}</div>
            """,
            unsafe_allow_html=True,
        )

        with st.container(key="results_card"):
            st.markdown('<div class="results-body">', unsafe_allow_html=True)
            st.markdown(final_response)
            st.markdown("</div>", unsafe_allow_html=True)

        # A small reward for finishing the analysis — bigger celebration
        # for a strong match, a gentler one otherwise.
        if score is not None and score >= 80:
            st.balloons()
        else:
            st.toast("Analysis complete!", icon="✨")