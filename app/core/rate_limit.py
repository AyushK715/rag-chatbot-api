import time
from collections import defaultdict, deque

from fastapi import Depends, HTTPException, status

from app.core.config import get_settings
from app.core.security import get_current_user_email

_request_log: dict[str, deque[float]] = defaultdict(deque)


def rate_limit(email: str = Depends(get_current_user_email)) -> str:
    """Sliding-window rate limiter keyed by user email."""
    settings = get_settings()
    now = time.monotonic()
    window_start = now - settings.rate_limit_window_seconds
    log = _request_log[email]

    while log and log[0] < window_start:
        log.popleft()

    if len(log) >= settings.rate_limit_requests:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again shortly.",
        )
    log.append(now)
    return email
