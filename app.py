import streamlit as st
from PyPDF2 import PdfReader
from fpdf import FPDF
import io

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(page_title="Resume Analyzer", page_icon="📄")
st.title("📄 Smart Resume Analyzer")
st.write("Upload or paste resume to get ATS Score, Missing Keywords & Suggestions (Downloadable PDF)")
st.divider()

# ----------------------------
# PDF Upload
# ----------------------------
uploaded_file = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])
resume = ""

def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    return text

if uploaded_file is not None:
    resume = extract_text_from_pdf(uploaded_file)
    st.success("✅ PDF uploaded successfully!")
else:
    resume = st.text_area("📌 Paste Your Resume", height=200)

# ----------------------------
# Role Selection
# ----------------------------
role = st.selectbox(
    "🎯 Target Role",
    sorted([
        "AI Engineer",
        "Cloud Engineer",
        "Cybersecurity",
        "Data Analyst",
        "Data Scientist",
        "Full Stack Developer",
        "Game Developer",
        "IoT / Robotics",
        "Python Developer",
        "Software Engineer"
    ])
)

# ----------------------------
# Role-based keywords
# ----------------------------
def get_role_keywords(role):
    keywords = {
        "Data Analyst": ["python","sql","pandas","numpy","data visualization","power bi","tableau","excel","statistics","data cleaning"],
        "Software Engineer": ["java","dsa","oop","system design","api","backend","frontend","react","database","algorithms"],
        "AI Engineer": ["machine learning","deep learning","nlp","tensorflow","pytorch","model deployment","llm","transformers","python","data"],
        "Data Scientist": ["python","machine learning","statistics","data analysis","pandas","numpy","scikit-learn","visualization","modeling"],
        "Cybersecurity": ["network security","osint","penetration testing","ethical hacking","firewalls","encryption","threat analysis","linux","security tools"],
        "Full Stack Developer": ["react","node.js","express","mongodb","frontend","backend","api","javascript","html","css"],
        "Cloud Engineer": ["aws","azure","gcp","docker","kubernetes","cloud computing","devops","ci/cd","infrastructure"],
        "Game Developer": ["unity","unreal engine","c#","c++","game physics","3d modeling","animation","game design"],
        "IoT / Robotics": ["arduino","raspberry pi","embedded systems","sensors","robotics","iot","microcontrollers","python","c++"],
        "Python Developer": ["python","django","flask","api","backend","automation","scripting","sql","debugging"]
    }
    return keywords.get(role, [])

# ----------------------------
# ATS Analysis
# ----------------------------
def analyze_resume(resume, role):
    role_keywords = get_role_keywords(role)
    resume_lower = resume.lower()
    present = []
    missing = []
    for word in role_keywords:
        if word in resume_lower:
            present.append(word)
        else:
            missing.append(word)
    score = int((len(present)/len(role_keywords))*100)
    return score, missing

# ----------------------------
# Keyword Suggestions
# ----------------------------
def keyword_suggestions(missing_keywords):
    suggestions = []
    for word in missing_keywords:
        if word in ["python","sql","pandas","numpy"]:
            suggestions.append(f"Add projects using {word}")
        elif word in ["power bi","tableau","data visualization"]:
            suggestions.append(f"Include dashboards using {word}")
        elif word in ["machine learning","deep learning"]:
            suggestions.append(f"Add ML projects using {word}")
        elif word in ["api","backend"]:
            suggestions.append("Include backend/API development experience")
        elif word in ["aws","azure","gcp"]:
            suggestions.append(f"Add cloud experience ({word})")
        elif word in ["docker","kubernetes"]:
            suggestions.append(f"Mention DevOps tools like {word}")
        elif word in ["react","frontend"]:
            suggestions.append("Include frontend projects")
        elif word in ["statistics"]:
            suggestions.append("Highlight statistics or analysis work")
        else:
            suggestions.append(f"Try to include {word} in your resume")
    return suggestions

# ----------------------------
# Remove Suggestions
# ----------------------------
def removal_suggestions(resume, role):
    suggestions = []
    res = resume.lower()
    if role == "Data Analyst":
        if "java" in res: suggestions.append("Reduce focus on Java")
        if "c++" in res: suggestions.append("Avoid highlighting C/C++ too much")
    elif role == "Software Engineer":
        if "tableau" in res: suggestions.append("Tableau is less relevant")
        if "power bi" in res: suggestions.append("Reduce BI tools focus")
    elif role == "AI Engineer":
        if "excel" in res: suggestions.append("Excel is not important for AI roles")
    return suggestions

# ----------------------------
# PDF Creation (Unicode-safe)
# ----------------------------
def create_pdf(resume_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    
    # Replace unsupported chars with ?
    safe_text = resume_text.encode('latin-1', 'replace').decode('latin-1')
    
    for line in safe_text.split("\n"):
        pdf.multi_cell(0, 8, line)
    
    # Return as BytesIO
    pdf_bytes = pdf.output(dest='S').encode('latin-1')  # <-- S = return string
    return io.BytesIO(pdf_bytes)

# ----------------------------
# Analyze Button
# ----------------------------
if st.button("🚀 Analyze Resume"):
    if resume.strip() == "":
        st.warning("⚠️ Provide resume text or upload PDF")
    else:
        st.divider()
        # ATS
        score, missing = analyze_resume(resume, role)
        st.subheader("📊 ATS Score")
        st.write(f"{score} / 100")
        st.divider()

        # Missing Keywords
        st.subheader("❌ Missing Keywords")
        if missing:
            for m in missing:
                st.write("•", m)
        else:
            st.write("All major keywords present 🎯")

        # Suggestions
        if missing:
            st.subheader("💡 Suggestions to Improve")
            sugg = keyword_suggestions(missing)
            for s in sugg:
                st.write("•", s)

        # Remove / Reduce
        st.subheader("⚠️ Remove / Reduce")
        remove = removal_suggestions(resume, role)
        if remove:
            for r in remove:
                st.write("•", r)
        else:
            st.write("No major issues 👍")

        st.divider()
        # PDF Download
        pdf_file = create_pdf(resume)
        st.download_button(
            label="📥 Download Corrected Resume as PDF",
            data=pdf_file,
            file_name="improved_resume.pdf",
            mime="application/pdf"
        )