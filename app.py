import streamlit as st
import pandas as pd
import fitz  # PyMuPDF

# Skill list
COMMON_SKILLS = [
    "python", "java", "c++", "sql", "excel", "tableau", "power bi", "sas",
    "aws", "azure", "gcp", "hadoop", "spark", "pandas", "numpy",
    "machine learning", "deep learning", "data analysis", "nlp",
    "communication", "leadership", "project management"
]

# Skill extractor
def extract_skills(text, skill_list):
    found = []
    text = text.lower()
    for skill in skill_list:
        if skill in text:
            found.append(skill)
    return found

st.title("Resume Skill Matcher")

# Session State to store resumes
if "database" not in st.session_state:
    st.session_state.database = []

# --- Add Resume Section ---
st.header("1. Add a Team Member's Resume")
upload_method = st.radio("Choose input method:", ["Paste text", "Upload PDF"])
name = st.text_input("Employee Name")
resume_text = ""

if upload_method == "Paste text":
    resume_text = st.text_area("Paste Resume Text or Skills")
elif upload_method == "Upload PDF":
    uploaded_file = st.file_uploader("Upload PDF Resume", type=["pdf"])
    if uploaded_file is not None:
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            resume_text = ""
            for page in doc:
                resume_text += page.get_text()
        st.success("PDF text extracted!")

if st.button("Add to Database") and name and resume_text:
    skills = extract_skills(resume_text, COMMON_SKILLS)
    st.session_state.database.append({
        "name": name,
        "resume": resume_text.lower(),
        "skills": ", ".join(skills)
    })
    st.success(f"{name} added to the database with {len(skills)} skills detected.")

# --- Search Section ---
st.header("2. Find Someone With a Skill")
search_skill = st.text_input("What do you need help with?")
if st.button("Search"):
    matches = []
    for record in st.session_state.database:
        if search_skill.lower() in record["resume"]:
            matches.append(record["name"])
    if matches:
        st.write("### Suggested Matches:")
        for match in matches:
            st.write(f"- {match}")
    else:
        st.warning("No matches found.")

# --- View Current Database ---
st.header("3. View All Stored Resumes")
if st.button("Show Database"):
    if st.session_state.database:
        df = pd.DataFrame(st.session_state.database)
        df["resume"] = df["resume"].str.slice(0, 200) + "..."  # Preview only
        st.dataframe(df[["name", "skills", "resume"]])
    else:
        st.info("No resumes added yet.")
