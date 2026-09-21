from enum import StrEnum


class ActionType(StrEnum):
    CLOSE = "close"
    WATCH = "watch"
    FREEZE = "freeze"
    FILE_COMPLIANCE = "file_compliance"


class RiskHint(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DeskRole(StrEnum):
    FRAUD = "fraud"
    CARE = "care"


class AlertStatus(StrEnum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    WAITING_HUMAN = "waiting_human"
    CLOSED = "closed"


class ActionStatus(StrEnum):
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"


class CaseType(StrEnum):
    FIRST_CREDIT_DRAIN = "first_credit_drain"
    NIGHT_BILL_CAMOUFLAGE = "night_bill_camouflage"
    SHARED_PAYEE = "shared_payee"
    LOYAL_ODD = "loyal_odd"
    WATCHLIST_REPEAT = "watchlist_repeat"
    DUPLICATE_DEBIT = "duplicate_debit"
