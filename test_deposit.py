from core.storage import _validate_condition
condition = "kind = 'deposit' AND created_at >= date('now', 'start of month', '-1 month') AND created_at < date('now', 'start of month')"
print(_validate_condition(condition))