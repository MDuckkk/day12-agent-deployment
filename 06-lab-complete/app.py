"""Streamlit MVP for CV/JD interview analysis."""
import json

import streamlit as st

from analyzer import MOCK_CV_DIR, MOCK_JD_DIR, analyze_cv_jd, extract_text, load_mock_options, load_mock_text
from config import settings


st.set_page_config(page_title=settings.app_name, page_icon="🎯", layout="wide")


def render_result(result: dict):
    insight = result.get("insight", {})
    questions = result.get("questions", [])

    st.success("Analysis complete")
    left, right = st.columns([1, 1])
    with left:
        st.metric("Match Score", f"{insight.get('overall_fit_score', 0)}/100")
    with right:
        st.caption(f"Model: {settings.openai_model}")

    overview_tab, skills_tab, questions_tab = st.tabs(["Overview", "Skills", "Questions"])

    with overview_tab:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Strengths")
            for item in insight.get("strengths", []):
                st.write(f"- {item}")
        with col2:
            st.subheader("Weaknesses")
            for item in insight.get("weaknesses", []):
                st.write(f"- {item}")
        st.subheader("Experience Gap")
        st.info(insight.get("experience_gap", "No summary provided."))

    with skills_tab:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Matching Skills")
            for item in insight.get("matching_skills", []):
                st.write(f"- {item}")
        with col2:
            st.subheader("Missing Skills")
            for item in insight.get("missing_skills", []):
                st.write(f"- {item}")

    with questions_tab:
        for index, question in enumerate(questions, start=1):
            title = question.get("question", "Untitled question")
            with st.expander(f"Question {index}: {title}", expanded=index == 1):
                st.write(f"Category: {question.get('category', 'n/a')}")
                st.write(f"Difficulty: {question.get('difficulty', 'n/a')}")
                st.write(f"Intent: {question.get('intent', 'n/a')}")
                st.write("Suggested answer points:")
                for point in question.get("suggested_answer_points", []):
                    st.write(f"- {point}")

    st.download_button(
        "Download JSON Result",
        data=st.session_state.result_json,
        file_name="devcoach_mvp_result.json",
        mime="application/json",
        use_container_width=True,
    )


st.title("🎯 DevCoach MVP")
st.caption("MVP version: Streamlit only, one small model, deploy-ready.")

if not settings.openai_api_key:
    st.warning("OPENAI_API_KEY is not configured yet.")

with st.sidebar:
    st.header("Settings")
    input_mode = st.radio("Input mode", ["Upload files", "Use mock data"])
    num_questions = st.slider("Questions", min_value=3, max_value=10, value=5)
    difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard"], index=1)
    language = st.selectbox("Language", ["vi", "en"], index=0)
    st.caption(f"Upload limit: {settings.max_upload_size_mb} MB per file")

cv_text = ""
jd_text = ""
cv_file = None
jd_file = None

if input_mode == "Upload files":
    col1, col2 = st.columns(2)
    with col1:
        cv_file = st.file_uploader("Upload CV", type=["pdf", "txt", "json"], key="cv")
    with col2:
        jd_file = st.file_uploader("Upload JD", type=["pdf", "txt", "json"], key="jd")
else:
    col1, col2 = st.columns(2)
    with col1:
        cv_id = st.selectbox("Mock CV", load_mock_options(MOCK_CV_DIR), index=None, placeholder="Select a mock CV")
    with col2:
        jd_id = st.selectbox("Mock JD", load_mock_options(MOCK_JD_DIR), index=None, placeholder="Select a mock JD")
    if cv_id:
        cv_text = load_mock_text(MOCK_CV_DIR, cv_id)
    if jd_id:
        jd_text = load_mock_text(MOCK_JD_DIR, jd_id)

run_clicked = st.button("Analyze CV vs JD", type="primary", use_container_width=True)

if run_clicked:
    has_input = bool(cv_file and jd_file) if input_mode == "Upload files" else bool(cv_text and jd_text)
    if not has_input:
        st.error("Please provide both CV and JD.")
    else:
        try:
            with st.spinner("Analyzing..."):
                if input_mode == "Upload files":
                    cv_text = extract_text(cv_file, settings.max_upload_size_mb)
                    jd_text = extract_text(jd_file, settings.max_upload_size_mb)
                result = analyze_cv_jd(
                    cv_text=cv_text,
                    jd_text=jd_text,
                    num_questions=num_questions,
                    difficulty=difficulty,
                    language=language,
                )
            st.session_state.result_json = json.dumps(result, ensure_ascii=False, indent=2)
            render_result(result)
        except Exception as exc:
            st.error(str(exc))

if "result_json" in st.session_state and not run_clicked:
    try:
        render_result(json.loads(st.session_state.result_json))
    except Exception:
        pass
