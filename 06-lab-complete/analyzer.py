"""Single-model analysis helpers for the MVP app."""
import io
import json
from pathlib import Path

import pypdf
from openai import OpenAI

from config import settings


BASE_DIR = Path(__file__).parent
MOCK_CV_DIR = BASE_DIR / "mock_data" / "cvs"
MOCK_JD_DIR = BASE_DIR / "mock_data" / "jds"


def load_mock_options(directory: Path) -> list[str]:
    return sorted(file.stem for file in directory.glob("*.json"))


def load_mock_text(directory: Path, item_id: str) -> str:
    with open(directory / f"{item_id}.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    return json.dumps(data, ensure_ascii=False, indent=2)


def extract_text(uploaded_file, max_upload_size_mb: int) -> str:
    if hasattr(uploaded_file, "getvalue"):
        content = uploaded_file.getvalue()
        file_name = uploaded_file.name.lower()
    else:
        content = uploaded_file.read()
        file_name = getattr(uploaded_file, "filename", "").lower()
    if not content:
        raise ValueError("File is empty.")
    if len(content) > max_upload_size_mb * 1024 * 1024:
        raise ValueError(f"File exceeds {max_upload_size_mb} MB.")

    if file_name.endswith(".pdf"):
        reader = pypdf.PdfReader(io.BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    if file_name.endswith(".json"):
        return json.dumps(json.loads(content.decode("utf-8")), ensure_ascii=False, indent=2)
    return content.decode("utf-8")


def build_messages(cv_text: str, jd_text: str, num_questions: int, difficulty: str, language: str) -> list[dict]:
    language_name = "Vietnamese" if language == "vi" else "English"
    return [
        {
            "role": "system",
            "content": (
                "You are an interview coach for junior IT candidates. "
                "Analyze a CV against a JD and return only valid JSON. "
                "Be specific, useful, and concise."
            ),
        },
        {
            "role": "user",
            "content": f"""
Analyze this CV and JD.

Return exactly one JSON object:
{{
  "insight": {{
    "matching_skills": ["skill"],
    "missing_skills": ["skill"],
    "experience_gap": "short paragraph",
    "strengths": ["strength"],
    "weaknesses": ["weakness"],
    "overall_fit_score": 0
  }},
  "questions": [
    {{
      "question": "text",
      "category": "technical|behavioral|situational",
      "difficulty": "easy|medium|hard",
      "intent": "text",
      "suggested_answer_points": ["point"]
    }}
  ]
}}

Rules:
- Output language: {language_name}
- Generate exactly {num_questions} questions
- Target difficulty: {difficulty}
- Candidate may be fresher or junior
- No markdown, no code fences, no extra explanation

CV:
{cv_text}

JD:
{jd_text}
""".strip(),
        },
    ]


def analyze_cv_jd(cv_text: str, jd_text: str, num_questions: int, difficulty: str, language: str) -> dict:
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is missing. Add it to .env.local or Railway variables.")

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model=settings.openai_model,
        response_format={"type": "json_object"},
        temperature=0.3,
        messages=build_messages(cv_text, jd_text, num_questions, difficulty, language),
    )

    content = response.choices[0].message.content or "{}"
    result = json.loads(content)
    result.setdefault("insight", {})
    result.setdefault("questions", [])
    return result
