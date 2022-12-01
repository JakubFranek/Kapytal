from datetime import timedelta, timezone

timezone_offset = +1.0  # Central European Time (CET = UTC+01:00)
tzinfo = timezone(timedelta(hours=timezone_offset))
