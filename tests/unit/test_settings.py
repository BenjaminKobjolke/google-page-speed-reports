from pathlib import Path

import pytest

from pagespeed_report.settings import PROJECT_ROOT, Settings


def test_env_file_values_and_environment_override(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        '# comment\nPAGESPEED_API_KEY="from-file"\nPAGESPEED_TIMEOUT=30\n', encoding="utf-8"
    )
    settings = Settings.load(env_file, environ={"PAGESPEED_TIMEOUT": "60"})
    assert settings.api_key == "from-file"
    assert settings.timeout_seconds == 60
    assert settings.reports_dir == PROJECT_ROOT / "reports"


def test_defaults_without_env_file(tmp_path: Path) -> None:
    settings = Settings.load(tmp_path / "missing.env", environ={})
    assert settings.api_key is None
    assert settings.timeout_seconds == 120
    assert settings.log_level == "INFO"


def test_invalid_timeout_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="PAGESPEED_TIMEOUT"):
        Settings.load(tmp_path / "missing.env", environ={"PAGESPEED_TIMEOUT": "soon"})
