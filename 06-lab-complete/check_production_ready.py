"""Lightweight deploy readiness check for the MVP Streamlit app."""
import os
import sys


def check(name: str, passed: bool) -> bool:
    icon = "OK" if passed else "FAIL"
    print(f"[{icon}] {name}")
    return passed


def run_checks() -> bool:
    base = os.path.dirname(__file__)
    required_files = [
        "app.py",
        "analyzer.py",
        "config.py",
        "requirements.txt",
        "Dockerfile",
        "railway.toml",
        ".env.example",
    ]
    passed = []

    print("MVP deploy readiness\n")
    for name in required_files:
        passed.append(check(f"{name} exists", os.path.exists(os.path.join(base, name))))

    dockerfile = os.path.join(base, "Dockerfile")
    if os.path.exists(dockerfile):
        content = open(dockerfile, encoding="utf-8").read()
        passed.append(check("Dockerfile runs Streamlit", "streamlit" in content.lower()))

    railway = os.path.join(base, "railway.toml")
    if os.path.exists(railway):
        content = open(railway, encoding="utf-8").read()
        passed.append(check("Railway healthcheck configured", "_stcore/health" in content))

    reqs = os.path.join(base, "requirements.txt")
    if os.path.exists(reqs):
        content = open(reqs, encoding="utf-8").read()
        passed.append(check("Streamlit dependency included", "streamlit" in content.lower()))
        passed.append(check("OpenAI dependency included", "openai" in content.lower()))

    ok = all(passed)
    print(f"\nResult: {'READY' if ok else 'NOT READY'}")
    return ok


if __name__ == "__main__":
    sys.exit(0 if run_checks() else 1)
