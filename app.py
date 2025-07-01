import json
import os
import streamlit as st
import pandas as pd
import fitz  # PyMuPDF

# ---------- Skill Setup ----------
COMMON_SKILLS = [
    "python", "java", "c++", "sql", "excel", "tableau", "power bi", "sas",
    "aws", "azure", "gcp", "hadoop", "spark", "pandas", "numpy",
    "machine learning", "deep learning", "data analysis", "nlp",
    "communication", "leadership", "project management"
]

def extract_skills(text, skill_list):
    found = []
    text = text.lower()
    for skill in skill_list:
        if skill in text:
            found.append(skill)
    return found

# ---------- App Config ----------
st.set_page_config(page_title="Resume Skill Matcher", layout="wide")

st.markdown("""
    <style>
        html, body, [class*="css"]  {
            font-family: 'Segoe UI', sans-serif;
        }
        .main {
            background-color: #f9f9f9;
            padding: 1.5rem;
        }
        .block-container {
            padding-top: 2rem;
        }
        .stTabs [data-baseweb="tab-list"] {
            justify-content: center;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 1.1rem;
            padding: 1rem 2rem;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <h1 style='text-align: center; font-size: 3em; font-weight: 500; margin-bottom: 0.2em;'>💼 Resume Skill Matcher</h1>
    <p style='text-align: center; font-size: 1.2em; color: #6e6e6e;'>A smart way to connect people to skills across your team.</p>
""", unsafe_allow_html=True)

# ---------- Data Initialization ----------
DATA_FILE = "resume_data.json"
if "database" not in st.session_state:
    st.session_state.database = []

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            st.session_state.database = json.load(f)
        except json.JSONDecodeError:
            st.session_state.database = []

# ---------- Tabs ----------
tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Resume", "🔍 Search Skills", "📋 View Database", "🛠 Manage Resumes"])

# ---------- Tab 1: Add Resume ----------
with tab1:
    st.markdown("### ➕ Add a New Team Member")
    col1, col2 = st.columns([2, 3])

    with col1:
        upload_method = st.radio("Choose input method", ["Paste text", "Upload PDF"])
        name = st.text_input("Employee Name")

    resume_text = ""

    with col2:
        if upload_method == "Paste text":
            resume_text = st.text_area("Paste Resume Text or Skills", height=200)
        elif upload_method == "Upload PDF":
            uploaded_file = st.file_uploader("Upload PDF Resume", type=["pdf"])
            if uploaded_file is not None:
                with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
                    resume_text = ""
                    for page in doc:
                        resume_text += page.get_text()
                st.success("✅ PDF text extracted!")

    st.markdown("")

    if st.button("✅ Add to Database"):
        if not name or not resume_text:
            st.warning("Please fill in both name and resume.")
        elif any(entry["name"].lower() == name.lower() for entry in st.session_state.database):
            st.error("🚫 An entry with this name already exists. Please use a unique name.")
        else:
            skills = extract_skills(resume_text, COMMON_SKILLS)
            entry = {
                "name": name,
                "resume": resume_text.lower(),
                "skills": ", ".join(skills)
            }
            st.session_state.database.append(entry)

            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(st.session_state.database, f, indent=2)

            st.success(f"✅ {name} added with {len(skills)} skills detected.")


# ---------- Tab 2: Search Skills ----------
with tab2:
    st.markdown("### 🔍 Search by Skill")
    st.markdown("Select a skill below to find relevant people.")

    all_skills = []
    for record in st.session_state.database:
        all_skills.extend([s.strip() for s in record["skills"].split(",") if s.strip()])
    unique_skills = sorted(set(all_skills))

    if unique_skills:
        selected_skill = st.selectbox("Select a skill", unique_skills)
        if st.button("🔎 Find Matches"):
            matches = [r["name"] for r in st.session_state.database if selected_skill in r["skills"]]
            if matches:
                st.markdown("### ✅ Suggested Matches")
                for match in matches:
                    st.markdown(f"- **{match}**")
            else:
                st.warning("No matches found.")
    else:
        st.info("⚠️ No skills found yet. Add a resume first.")

# ---------- Tab 3: View Database ----------
with tab3:
    st.markdown("### 📋 All Stored Resumes")
    st.markdown("Browse uploaded team member info and download as CSV.")

    if st.button("📂 Show Database"):
        if st.session_state.database:
            df = pd.DataFrame(st.session_state.database)
            df["resume"] = df["resume"].str.slice(0, 200) + "..."
            st.dataframe(df[["name", "skills", "resume"]])

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name="resume_database.csv",
                mime="text/csv"
            )
        else:
            st.info("⚠️ No resumes added yet.")
# ---------- Tab 4: Manage Resumes ----------
with tab4:
    st.markdown("### 🛠 Manage Resumes")
    st.markdown("Update or delete an existing team member’s resume.")

    if st.session_state.database:
        names = [entry["name"] for entry in st.session_state.database]
        selected_name = st.selectbox("Select Employee", names)

        selected_index = next((i for i, entry in enumerate(st.session_state.database) if entry["name"] == selected_name), None)
        if selected_index is not None:
            current_entry = st.session_state.database[selected_index]

            st.markdown(f"**Current Skills:** {current_entry['skills']}")
            st.markdown("---")

            action = st.radio("Choose Action", ["Update Resume", "Delete Resume"])

            if action == "Update Resume":
                update_method = st.radio("New input method", ["Paste text", "Upload PDF"], key="update_input_method")
                updated_resume = ""

                if update_method == "Paste text":
                    updated_resume = st.text_area("Paste new resume text")
                elif update_method == "Upload PDF":
                    updated_file = st.file_uploader("Upload new PDF", type=["pdf"], key="update_file")
                    if updated_file is not None:
                        with fitz.open(stream=updated_file.read(), filetype="pdf") as doc:
                            updated_resume = ""
                            for page in doc:
                                updated_resume += page.get_text()
                        st.success("✅ New PDF text extracted!")

                if st.button("🔄 Update"):
                    new_skills = extract_skills(updated_resume, COMMON_SKILLS)
                    st.session_state.database[selected_index] = {
                        "name": selected_name,
                        "resume": updated_resume.lower(),
                        "skills": ", ".join(new_skills)
                    }
                    with open(DATA_FILE, "w", encoding="utf-8") as f:
                        json.dump(st.session_state.database, f, indent=2)
                    st.success(f"✅ {selected_name}'s resume was updated with {len(new_skills)} skills.")

            elif action == "Delete Resume":
                confirm_delete = st.checkbox(f"⚠️ I confirm I want to delete {selected_name}'s resume")
                if confirm_delete:
                    if st.button("🗑️ Confirm Delete"):
                        del st.session_state.database[selected_index]
                        with open(DATA_FILE, "w", encoding="utf-8") as f:
                            json.dump(st.session_state.database, f, indent=2)
                        st.success(f"❌ {selected_name}'s resume has been deleted. Refresh the page to update the list.")

        st.info("No resumes available to manage. Add some first.")
