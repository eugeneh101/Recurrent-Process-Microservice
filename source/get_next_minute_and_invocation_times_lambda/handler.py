from datetime import datetime, timedelta
from typing import Union

from aws_lambda_powertools.utilities.typing import LambdaContext

INTERVAL_IN_SECONDS = 2  # hard coded

def lambda_handler(event: None, context: LambdaContext) -> dict[str, Union[str, list[str]]]:
    now = datetime.utcnow()
    delta = timedelta(minutes=1)
    next_minute = (now + delta).replace(second=0, microsecond=0)
    num_intervals = 60 // INTERVAL_IN_SECONDS
    invocation_times = []
    for ith_interval in range(1, num_intervals + 1):
        invocation_time = next_minute + timedelta(seconds=INTERVAL_IN_SECONDS) * ith_interval
        invocation_times.append(invocation_time.strftime("%Y-%m-%dT%H:%M:%SZ"))
    return {
        "next_minute": next_minute.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "invocation_times": invocation_times,
    }
