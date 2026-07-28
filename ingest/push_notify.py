import json

import psycopg2
from pywebpush import WebPushException, webpush

from .config import DATABASE_URL, VAPID_CLAIM_EMAIL, VAPID_PRIVATE_KEY

TABLE = "push_subscriptions"


def _get_subscriptions() -> list[tuple[str, str, str]]:
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT endpoint, p256dh, auth FROM {TABLE}")
            return cur.fetchall()
    finally:
        conn.close()


def _delete_subscription(endpoint: str) -> None:
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            cur.execute(f"DELETE FROM {TABLE} WHERE endpoint = %s", (endpoint,))
        conn.commit()
    finally:
        conn.close()


def notify_new_items(count: int) -> None:
    if count == 0:
        return
    if not VAPID_PRIVATE_KEY:
        print("No VAPID_PRIVATE_KEY set, skipping push notifications.")
        return

    payload = json.dumps(
        {
            "title": "AI Update Hub",
            "body": f"{count} new item{'s' if count != 1 else ''} just landed",
            "url": "/",
        }
    )

    sent = 0
    for endpoint, p256dh, auth in _get_subscriptions():
        try:
            webpush(
                subscription_info={
                    "endpoint": endpoint,
                    "keys": {"p256dh": p256dh, "auth": auth},
                },
                data=payload,
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={"sub": f"mailto:{VAPID_CLAIM_EMAIL}"},
            )
            sent += 1
        except WebPushException as exc:
            if exc.response is not None and exc.response.status_code in (404, 410):
                _delete_subscription(endpoint)
            else:
                print(f"Push failed for {endpoint}: {exc}")

    print(f"Sent {sent} push notifications.")
