"""String constants and fixed values shared across the package."""

from enum import StrEnum

PSI_ENDPOINT = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

# Order here is the order of the Scores table and of non-performance action items.
CATEGORIES: tuple[str, ...] = ("performance", "accessibility", "best-practices", "seo")

# Lab metrics shown in the Core Web Vitals section, in display order.
VITAL_AUDIT_IDS: tuple[str, ...] = (
    "largest-contentful-paint",
    "cumulative-layout-shift",
    "total-blocking-time",
    "first-contentful-paint",
    "speed-index",
)

# Audit ref groups that are not actionable: metrics are shown as vitals, hidden ones duplicate
# the visible insight audits.
SKIPPED_GROUPS: frozenset[str] = frozenset({"metrics", "hidden"})

# Score display modes that never represent a failing check.
NON_SCORED_MODES: frozenset[str] = frozenset({"notApplicable", "informative", "manual", "error"})

PASS_SCORE = 0.9
AVERAGE_SCORE = 0.5
MAX_AFFECTED_ITEMS = 10

QUOTA_HTTP_STATUS = 429
EXIT_OK = 0
EXIT_ERROR = 1
EXIT_QUOTA = 2

ENV_API_KEY = "PAGESPEED_API_KEY"
ENV_REPORTS_DIR = "PAGESPEED_REPORTS_DIR"
ENV_TIMEOUT = "PAGESPEED_TIMEOUT"
ENV_LOG_LEVEL = "PAGESPEED_LOG_LEVEL"
ENV_FILE_NAME = ".env"
DEFAULT_REPORTS_DIR = "reports"
DEFAULT_TIMEOUT_SECONDS = 120
DEFAULT_LOG_LEVEL = "INFO"


class Strategy(StrEnum):
    MOBILE = "mobile"
    DESKTOP = "desktop"


class Rating(StrEnum):
    GOOD = "good"
    NEEDS_IMPROVEMENT = "needs-improvement"
    POOR = "poor"
