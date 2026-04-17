"""Flask entrypoint for Vercel deployment."""
import json

from flask import Flask, Response, render_template_string, request

from analyzer import MOCK_CV_DIR, MOCK_JD_DIR, analyze_cv_jd, extract_text, load_mock_options, load_mock_text
from config import settings


app = Flask(__name__)

PAGE_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ app_name }}</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f5efe4;
      --panel: rgba(255, 252, 246, 0.94);
      --text: #1f2937;
      --muted: #6b7280;
      --accent: #c2410c;
      --accent-dark: #9a3412;
      --line: rgba(31, 41, 55, 0.12);
      --ok: #166534;
      --error: #b91c1c;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(251, 191, 36, 0.24), transparent 28%),
        radial-gradient(circle at top right, rgba(194, 65, 12, 0.18), transparent 24%),
        linear-gradient(180deg, #fcf7ef 0%, var(--bg) 100%);
    }
    .shell {
      max-width: 1180px;
      margin: 0 auto;
      padding: 32px 20px 40px;
    }
    .hero {
      margin-bottom: 24px;
      padding: 28px;
      border-radius: 24px;
      background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,244,230,0.88));
      border: 1px solid rgba(194, 65, 12, 0.16);
      box-shadow: 0 18px 45px rgba(148, 95, 46, 0.12);
    }
    .hero h1 {
      margin: 0 0 10px;
      font-size: clamp(2rem, 4vw, 3.2rem);
    }
    .hero p {
      margin: 0;
      max-width: 760px;
      color: var(--muted);
      line-height: 1.6;
    }
    .grid {
      display: grid;
      gap: 24px;
      grid-template-columns: minmax(0, 1.1fr) minmax(0, 0.9fr);
      align-items: start;
    }
    .card {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 22px;
      padding: 22px;
      box-shadow: 0 14px 28px rgba(31, 41, 55, 0.06);
      backdrop-filter: blur(6px);
    }
    h2, h3 { margin-top: 0; }
    .field { margin-bottom: 16px; }
    .field label {
      display: block;
      margin-bottom: 8px;
      font-weight: 600;
    }
    .row {
      display: grid;
      gap: 14px;
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    .row.three {
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }
    input[type="file"], select, button {
      width: 100%;
      border-radius: 14px;
      border: 1px solid rgba(31, 41, 55, 0.14);
      padding: 12px 14px;
      font-size: 0.98rem;
      background: #fffdf9;
    }
    button {
      cursor: pointer;
      background: linear-gradient(135deg, var(--accent), #ea580c);
      color: white;
      font-weight: 700;
      border: none;
      box-shadow: 0 12px 24px rgba(194, 65, 12, 0.24);
    }
    button:hover { background: linear-gradient(135deg, var(--accent-dark), var(--accent)); }
    .mode {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-bottom: 18px;
    }
    .mode label {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 10px 14px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: rgba(255,255,255,0.8);
      font-weight: 600;
    }
    .notice, .error {
      margin-bottom: 18px;
      border-radius: 16px;
      padding: 14px 16px;
      line-height: 1.6;
    }
    .notice {
      background: rgba(22, 101, 52, 0.08);
      border: 1px solid rgba(22, 101, 52, 0.18);
      color: var(--ok);
    }
    .error {
      background: rgba(185, 28, 28, 0.08);
      border: 1px solid rgba(185, 28, 28, 0.18);
      color: var(--error);
    }
    .metric {
      display: inline-flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 18px;
      padding: 14px 16px;
      border-radius: 18px;
      background: linear-gradient(135deg, rgba(194, 65, 12, 0.08), rgba(251, 191, 36, 0.12));
      border: 1px solid rgba(194, 65, 12, 0.14);
    }
    .metric strong {
      font-size: 1.6rem;
    }
    .section + .section {
      margin-top: 22px;
      padding-top: 22px;
      border-top: 1px solid var(--line);
    }
    ul {
      margin: 0;
      padding-left: 18px;
      line-height: 1.7;
    }
    pre {
      margin: 0;
      overflow: auto;
      padding: 16px;
      border-radius: 16px;
      background: #1f2937;
      color: #f9fafb;
      font-size: 0.92rem;
    }
    .question {
      margin-bottom: 14px;
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 14px 16px;
      background: rgba(255,255,255,0.72);
    }
    .muted { color: var(--muted); }
    .download {
      display: inline-block;
      margin-top: 16px;
      text-decoration: none;
      color: white;
      background: #1f2937;
      padding: 11px 16px;
      border-radius: 12px;
      font-weight: 700;
    }
    @media (max-width: 900px) {
      .grid, .row, .row.three { grid-template-columns: 1fr; }
      .shell { padding: 20px 14px 28px; }
      .hero, .card { padding: 18px; }
    }
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <h1>{{ app_name }}</h1>
      <p>Analyze a CV against a JD, get a fit score, identify missing skills, and generate targeted interview questions. This Vercel version keeps the same OpenAI analysis logic as the original Streamlit MVP.</p>
    </section>

    {% if warning %}
      <div class="error">{{ warning }}</div>
    {% endif %}
    {% if error %}
      <div class="error">{{ error }}</div>
    {% endif %}
    {% if result %}
      <div class="notice">Analysis complete. Model: {{ model_name }}</div>
    {% endif %}

    <div class="grid">
      <section class="card">
        <h2>Run Analysis</h2>
        <form method="post" enctype="multipart/form-data">
          <div class="mode">
            <label><input type="radio" name="input_mode" value="upload" {% if form.input_mode == "upload" %}checked{% endif %}> Upload files</label>
            <label><input type="radio" name="input_mode" value="mock" {% if form.input_mode == "mock" %}checked{% endif %}> Use mock data</label>
          </div>

          <div class="row three">
            <div class="field">
              <label for="num_questions">Questions</label>
              <select id="num_questions" name="num_questions">
                {% for value in question_options %}
                  <option value="{{ value }}" {% if form.num_questions == value|string %}selected{% endif %}>{{ value }}</option>
                {% endfor %}
              </select>
            </div>
            <div class="field">
              <label for="difficulty">Difficulty</label>
              <select id="difficulty" name="difficulty">
                {% for value in difficulty_options %}
                  <option value="{{ value }}" {% if form.difficulty == value %}selected{% endif %}>{{ value }}</option>
                {% endfor %}
              </select>
            </div>
            <div class="field">
              <label for="language">Language</label>
              <select id="language" name="language">
                <option value="vi" {% if form.language == "vi" %}selected{% endif %}>vi</option>
                <option value="en" {% if form.language == "en" %}selected{% endif %}>en</option>
              </select>
            </div>
          </div>

          <div class="row">
            <div class="field">
              <label for="cv_file">CV file</label>
              <input id="cv_file" name="cv_file" type="file" accept=".pdf,.txt,.json">
            </div>
            <div class="field">
              <label for="jd_file">JD file</label>
              <input id="jd_file" name="jd_file" type="file" accept=".pdf,.txt,.json">
            </div>
          </div>

          <div class="row">
            <div class="field">
              <label for="cv_id">Mock CV</label>
              <select id="cv_id" name="cv_id">
                <option value="">Select a mock CV</option>
                {% for value in cv_options %}
                  <option value="{{ value }}" {% if form.cv_id == value %}selected{% endif %}>{{ value }}</option>
                {% endfor %}
              </select>
            </div>
            <div class="field">
              <label for="jd_id">Mock JD</label>
              <select id="jd_id" name="jd_id">
                <option value="">Select a mock JD</option>
                {% for value in jd_options %}
                  <option value="{{ value }}" {% if form.jd_id == value %}selected{% endif %}>{{ value }}</option>
                {% endfor %}
              </select>
            </div>
          </div>

          <button type="submit">Analyze CV vs JD</button>
          <p class="muted">Upload limit: {{ upload_limit }} MB per file.</p>
        </form>
      </section>

      <section class="card">
        {% if result %}
          <h2>Result</h2>
          <div class="metric">
            <span class="muted">Match score</span>
            <strong>{{ result.insight.overall_fit_score or 0 }}/100</strong>
          </div>

          <div class="section">
            <h3>Strengths</h3>
            <ul>
              {% for item in result.insight.strengths %}
                <li>{{ item }}</li>
              {% else %}
                <li>No strengths returned.</li>
              {% endfor %}
            </ul>
          </div>

          <div class="section">
            <h3>Weaknesses</h3>
            <ul>
              {% for item in result.insight.weaknesses %}
                <li>{{ item }}</li>
              {% else %}
                <li>No weaknesses returned.</li>
              {% endfor %}
            </ul>
          </div>

          <div class="section">
            <h3>Matching Skills</h3>
            <ul>
              {% for item in result.insight.matching_skills %}
                <li>{{ item }}</li>
              {% else %}
                <li>No matching skills returned.</li>
              {% endfor %}
            </ul>
          </div>

          <div class="section">
            <h3>Missing Skills</h3>
            <ul>
              {% for item in result.insight.missing_skills %}
                <li>{{ item }}</li>
              {% else %}
                <li>No missing skills returned.</li>
              {% endfor %}
            </ul>
          </div>

          <div class="section">
            <h3>Experience Gap</h3>
            <p>{{ result.insight.experience_gap or "No summary provided." }}</p>
          </div>

          <div class="section">
            <h3>Interview Questions</h3>
            {% for question in result.questions %}
              <article class="question">
                <strong>{{ loop.index }}. {{ question.question }}</strong>
                <p class="muted">Category: {{ question.category }} | Difficulty: {{ question.difficulty }}</p>
                <p>{{ question.intent }}</p>
                <ul>
                  {% for point in question.suggested_answer_points %}
                    <li>{{ point }}</li>
                  {% else %}
                    <li>No suggested answer points returned.</li>
                  {% endfor %}
                </ul>
              </article>
            {% else %}
              <p>No questions returned.</p>
            {% endfor %}
          </div>

          <div class="section">
            <h3>Raw JSON</h3>
            <pre>{{ result_json }}</pre>
            <a class="download" href="/api/download?payload={{ download_payload }}">Download JSON Result</a>
          </div>
        {% else %}
          <h2>Ready for Vercel</h2>
          <p>This page is served by Flask so Vercel can deploy it as a Python function. Choose either file uploads or built-in mock data, then run the analysis.</p>
          <p class="muted">Environment variables required: OPENAI_API_KEY, OPENAI_MODEL, APP_NAME, MAX_UPLOAD_SIZE_MB.</p>
        {% endif %}
      </section>
    </div>
  </main>
</body>
</html>
"""


def _default_form() -> dict:
    return {
        "input_mode": "mock",
        "num_questions": "5",
        "difficulty": "medium",
        "language": "vi",
        "cv_id": "",
        "jd_id": "",
    }


def _render_page(result=None, error="", warning="", form=None):
    current_form = _default_form()
    if form:
        current_form.update(form)

    result_json = json.dumps(result, ensure_ascii=False, indent=2) if result else ""
    download_payload = json.dumps(result, ensure_ascii=False) if result else ""
    return render_template_string(
        PAGE_TEMPLATE,
        app_name=settings.app_name,
        model_name=settings.openai_model,
        upload_limit=settings.max_upload_size_mb,
        cv_options=load_mock_options(MOCK_CV_DIR),
        jd_options=load_mock_options(MOCK_JD_DIR),
        difficulty_options=["easy", "medium", "hard"],
        question_options=list(range(3, 11)),
        warning=warning,
        error=error,
        result=result,
        result_json=result_json,
        download_payload=download_payload,
        form=current_form,
    )


@app.route("/", methods=["GET", "POST"])
def home():
    warning = ""
    if not settings.openai_api_key:
        warning = "OPENAI_API_KEY is not configured yet. Add it in Vercel Project Settings before running analysis."

    if request.method == "GET":
        return _render_page(warning=warning)

    form = {
        "input_mode": request.form.get("input_mode", "mock"),
        "num_questions": request.form.get("num_questions", "5"),
        "difficulty": request.form.get("difficulty", "medium"),
        "language": request.form.get("language", "vi"),
        "cv_id": request.form.get("cv_id", ""),
        "jd_id": request.form.get("jd_id", ""),
    }

    try:
        if form["input_mode"] == "upload":
            cv_file = request.files.get("cv_file")
            jd_file = request.files.get("jd_file")
            if not cv_file or not jd_file or not cv_file.filename or not jd_file.filename:
                raise ValueError("Please upload both CV and JD files.")
            cv_text = extract_text(cv_file, settings.max_upload_size_mb)
            jd_text = extract_text(jd_file, settings.max_upload_size_mb)
        else:
            if not form["cv_id"] or not form["jd_id"]:
                raise ValueError("Please choose both a mock CV and a mock JD.")
            cv_text = load_mock_text(MOCK_CV_DIR, form["cv_id"])
            jd_text = load_mock_text(MOCK_JD_DIR, form["jd_id"])

        result = analyze_cv_jd(
            cv_text=cv_text,
            jd_text=jd_text,
            num_questions=int(form["num_questions"]),
            difficulty=form["difficulty"],
            language=form["language"],
        )
        return _render_page(result=result, warning=warning, form=form)
    except Exception as exc:
        return _render_page(error=str(exc), warning=warning, form=form)


@app.route("/api/download")
def download():
    payload = request.args.get("payload", "{}")
    return Response(
        payload,
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=devcoach_mvp_result.json"},
    )
