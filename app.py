"""Root Flask entrypoint for Vercel."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


PROJECT_DIR = Path(__file__).resolve().parent / "06-lab-complete"
MODULE_PATH = PROJECT_DIR / "api" / "index.py"
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

spec = spec_from_file_location("lab_complete_vercel_app", MODULE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load Vercel app from {MODULE_PATH}")

module = module_from_spec(spec)
spec.loader.exec_module(module)
app = module.app
