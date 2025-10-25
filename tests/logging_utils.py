import logging
import re
import os
from pathlib import Path
import json


def sanitize_nodeid(nodeid: str, max_len: int = 200) -> str:
    """Return a filesystem-safe filename for a pytest nodeid.

    Examples:
        tests/unit/test_foo.py::test_bar -> tests-unit-test_foo.py__test_bar
    """
    # Replace path separators and parameter markers
    s = nodeid.replace("::", "__")
    s = s.replace("/", "-")
    # Remove characters that are unsafe for filenames
    s = re.sub(r"[^A-Za-z0-9._\-__]", "_", s)
    if len(s) > max_len:
        # keep head and tail
        head = s[: int(max_len * 0.6)]
        tail = s[-int(max_len * 0.4) :]
        s = head + "__" + tail
    return s


def ensure_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def default_log_dir(repo_root: str | None = None) -> str:
    if repo_root:
        base = Path(repo_root)
    else:
        base = Path.cwd()
    return str(base / "test-logs")


def get_worker_id(config) -> str:
    # xdist sets workerinput on config when running in a worker process
    try:
        wi = getattr(config, "workerinput", None)
        if wi and isinstance(wi, dict):
            return wi.get("workerid", "gw0")
    except Exception:
        pass
    # Fallback to environment variable used by xdist
    return os.getenv("PYTEST_XDIST_WORKER", os.getenv("PYTEST_WORKER", "gw0"))


def redact(text: str, patterns: list[str] | None = None) -> str:
    """Redact sensitive patterns from text.

    Default patterns: emails, long hex tokens, bearer tokens, file paths that
    include user home (~ or C:\\Users\\), and basic-looking secrets.
    Returns the redacted string.
    """
    if not text:
        return text

    pats = patterns or [
        r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',  # email
        r'bearer\s+[A-Za-z0-9\-_.=]+',  # bearer tokens
        r'[A-Fa-f0-9]{20,}',  # long hex-like tokens
        r'~\\[^"\n]+',  # unix home paths starting with ~\
        r'[A-Za-z]:\\\\Users\\\\[A-Za-z0-9_.-]+\\\\[^"\n]+',  # Windows user paths
    ]

    out = text
    for p in pats:
        try:
            out = re.sub(p, "<REDACTED>", out, flags=re.IGNORECASE)
        except re.error:
            continue

    return out


class JsonFormatter(logging.Formatter):
    """Emit JSON lines with useful fields. Expects `record` to have
    `nodeid` and `worker` attributes if available (added by a logging Filter).
    """

    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        data = {
            "ts": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Optional fields
        if hasattr(record, "nodeid"):
            data["nodeid"] = getattr(record, "nodeid")
        if hasattr(record, "worker"):
            data["worker"] = getattr(record, "worker")
        if record.exc_info:
            data["exc"] = self.formatException(record.exc_info)

        return json.dumps(data, ensure_ascii=False)


class RedactingFormatter(logging.Formatter):
    """Formatter that redacts the formatted message using provided patterns.

    If `inner` is provided, it will be used to produce the formatted string
    before redaction. This allows wrapping JSON formatters as well as
    plain-text formatters.
    """

    def __init__(self, fmt: str | None = None, redaction_patterns: list[str] | None = None, inner: logging.Formatter | None = None):
        super().__init__(fmt)
        self._patterns = redaction_patterns
        self._inner = inner

    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        if self._inner is not None:
            s = self._inner.format(record)
        else:
            s = super().format(record)
        return redact(s, self._patterns)

