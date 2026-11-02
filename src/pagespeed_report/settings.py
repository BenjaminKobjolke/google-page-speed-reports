"""Central settings: the only module that reads environment variables and the .env file."""

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from pagespeed_report.constants import (
    DEFAULT_LOG_LEVEL,
    DEFAULT_REPORTS_DIR,
    DEFAULT_TIMEOUT_SECONDS,
    ENV_API_KEY,
    ENV_FILE_NAME,
    ENV_LOG_LEVEL,
    ENV_REPORTS_DIR,
    ENV_TIMEOUT,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def read_env_file(path: Path) -> dict[str, str]:
    """Parse simple KEY=VALUE lines; blank lines and # comments are ignored."""
    if not path.is_file():
        return {}
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values


@dataclass(frozen=True)
class Settings:
    api_key: str | None
    reports_dir: Path
    timeout_seconds: int
    log_level: str

    @classmethod
    def load(
        cls, env_file: Path | None = None, environ: Mapping[str, str] | None = None
    ) -> "Settings":
        """Real environment variables win over values from the .env file."""
        env = {
            **read_env_file(env_file or PROJECT_ROOT / ENV_FILE_NAME),
            **(os.environ if environ is None else environ),
        }
        reports_dir = Path(env.get(ENV_REPORTS_DIR) or DEFAULT_REPORTS_DIR)
        if not reports_dir.is_absolute():
            reports_dir = PROJECT_ROOT / reports_dir
        timeout = env.get(ENV_TIMEOUT) or str(DEFAULT_TIMEOUT_SECONDS)
        if not timeout.isdigit():
            raise ValueError(f"{ENV_TIMEOUT} must be a whole number of seconds, got {timeout!r}")
        return cls(
            api_key=env.get(ENV_API_KEY) or None,
            reports_dir=reports_dir,
            timeout_seconds=int(timeout),
            log_level=env.get(ENV_LOG_LEVEL) or DEFAULT_LOG_LEVEL,
        )
