from datetime import datetime, timedelta

MAX_DATETIME = datetime.now()  # noqa: DTZ005
MIN_DATETIME = MAX_DATETIME + timedelta(seconds=1)
