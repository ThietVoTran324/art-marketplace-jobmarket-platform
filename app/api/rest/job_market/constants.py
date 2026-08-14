CV_MAX_COUNT = 3
CV_MAX_BYTES = 5 * 1024 * 1024  # 5 MiB

CV_ALLOWED_CONTENT_TYPES = {
    "application/pdf": ".pdf",
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
}

CV_ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}

# ---- Sprint2 KYC ----

DEFAULT_REGISTRATION_AUTHORITY = "NATIONAL"
DEFAULT_TERMS_VERSION = "hiring-rights-kyc-v1"
ENGLISH_LANGUAGE = "en"

KYC_MAX_BYTES = 15 * 1024 * 1024  # 15 MiB
KYC_MAX_FILES_PER_TYPE = 5
KYC_MAX_FILES_PER_REQUEST = 15

KYC_ALLOWED_CONTENT_TYPES = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
}

KYC_ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}

KYC_DOC_TYPES = frozenset(
    {
        "business_registration_document",
        "tax_registration_document",
        "authorization_evidence",
        "identity_document",
        "document_translation",
    }
)

COMPANY_STATUSES = frozenset(
    {
        "pending_verification",
        "active",
        "rejected",
        "suspended",
        "soft_deleted",
    }
)

REQUEST_STATUSES = frozenset({"pending", "need_more_info", "approved", "rejected"})

SUPERSEDED_REJECTION_REASON = "superseded_by_other_approval"

# ---- Sprint3 JD ----

SALARY_MODE_LOVE_IT = "love_it"
SALARY_MODE_RANGE = "range"
SALARY_MODES = frozenset({SALARY_MODE_LOVE_IT, SALARY_MODE_RANGE})

CURRENCY_VND = "VND"
CURRENCY_USD = "USD"
CURRENCIES = frozenset({CURRENCY_VND, CURRENCY_USD})
DEFAULT_CURRENCY = CURRENCY_VND

JOB_STATUS_ACTIVE = "active"
JOB_STATUS_CLOSED = "closed"
JOB_STATUSES = frozenset({JOB_STATUS_ACTIVE, JOB_STATUS_CLOSED})

# ---- Sprint4 applications ----

APP_STATUS_SUBMITTED = "submitted"
APP_STATUS_VIEWED = "viewed"
APP_STATUS_REJECTED = "rejected"
APP_STATUS_PASSED = "passed"
APP_STATUSES = frozenset(
    {
        APP_STATUS_SUBMITTED,
        APP_STATUS_VIEWED,
        APP_STATUS_REJECTED,
        APP_STATUS_PASSED,
    }
)
APP_NON_TERMINAL = frozenset({APP_STATUS_SUBMITTED, APP_STATUS_VIEWED})
APP_TERMINAL = frozenset({APP_STATUS_REJECTED, APP_STATUS_PASSED})

CV_SOURCE_TAB = "tab"
CV_SOURCE_ONESHOT = "oneshot"
CV_SOURCES = frozenset({CV_SOURCE_TAB, CV_SOURCE_ONESHOT})

COVER_NOTE_MAX_LEN = 4000

UPDATE_TYPE_APPLICATION_RECEIVED = "job_application_received"
UPDATE_TYPE_APPLICATION_VIEWED = "job_application_viewed"
UPDATE_TYPE_APPLICATION_REJECTED = "job_application_rejected"
UPDATE_TYPE_APPLICATION_PASSED = "job_application_passed"

UPDATE_TYPE_WORK_EXP_PENDING = "work_exp_pending"
UPDATE_TYPE_WORK_EXP_APPROVED = "work_exp_approved"
UPDATE_TYPE_WORK_EXP_REJECTED = "work_exp_rejected"

UPDATE_TYPE_COMPANY_SUSPENDED = "company_suspended"
UPDATE_TYPE_COMPANY_UNSUSPENDED = "company_unsuspended"

# ---- Sprint6 reports ----

REPORT_REASON_SPAM = "spam"
REPORT_REASON_SCAM = "scam"
REPORT_REASON_INAPPROPRIATE = "inappropriate"
REPORT_REASON_OTHER = "other"
REPORT_REASONS = frozenset(
    {
        REPORT_REASON_SPAM,
        REPORT_REASON_SCAM,
        REPORT_REASON_INAPPROPRIATE,
        REPORT_REASON_OTHER,
    }
)

REPORT_STATUS_OPEN = "open"
REPORT_STATUS_DISMISSED = "dismissed"
REPORT_STATUS_ACTIONED = "actioned"
REPORT_STATUSES = frozenset(
    {REPORT_STATUS_OPEN, REPORT_STATUS_DISMISSED, REPORT_STATUS_ACTIONED}
)
