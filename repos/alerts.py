from repos.db import as_of, one, rows


def get_alert(alert_id: str):
    return one("SELECT * FROM alerts WHERE alert_id=? AND opened_at<=?", (alert_id, as_of()))


def list_open_alerts():
    return rows("SELECT * FROM alerts WHERE status='open' AND opened_at<=? ORDER BY alert_id", (as_of(),))
