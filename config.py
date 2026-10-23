import os
from pathlib import Path

ENV_FILE = Path(__file__).with_name(".env")


# Helper: reads KEY=value lines from .env into os.environ (real environment variables take priority).
def load_env_file(path: Path = ENV_FILE) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env_file()

HOME_URL = os.environ.get("DOC_HOME_URL", "https://www.doconcall.com.my/")
LOGIN_URL = os.environ.get("DOC_LOGIN_URL")
MY_ACCOUNT_URL = os.environ.get("DOC_MY_ACCOUNT_URL")
DOC_EMAIL = os.environ.get("DOC_EMAIL")
DOC_PASSWORD = os.environ.get("DOC_PASSWORD")
DOC_COUPON_CODE = os.environ.get("DOC_COUPON_CODE")
DOC_COUPON_AMOUNT = float(os.environ.get("DOC_COUPON_AMOUNT") or 0)
