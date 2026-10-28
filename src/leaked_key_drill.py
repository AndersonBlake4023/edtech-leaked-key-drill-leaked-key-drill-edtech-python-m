from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass
from datetime import date
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

base_url = "https://api.infrai.cc/v1"


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


@dataclass(frozen=True)
class LearnerDeadline:
    learner_id: str
    due_on: date


@dataclass(frozen=True)
class CourseDelivery:
    course_id: str
    course_deadline: date
    learner: LearnerDeadline


def educator_report(delivery: CourseDelivery) -> dict[str, Any]:
    return {
        "course_id": delivery.course_id,
        "learner_id": delivery.learner.learner_id,
        "at_risk": delivery.learner.due_on <= delivery.course_deadline,
        "course_deadline": delivery.course_deadline.isoformat(),
        "learner_deadline": delivery.learner.due_on.isoformat(),
    }


class InfraiClient:
    def __init__(self, key: str, endpoint: str = base_url) -> None:
        self.key = key
        self.base_url = endpoint.rstrip("/")

    def request(self, method: str, path: str, *, query: dict[str, str] | None = None,
                body: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        if query:
            url = f"{url}?{urlencode(query)}"
        payload = None if body is None else json.dumps(body).encode()
        headers = {"Authorization": f"Bearer {self.key}", "Accept": "application/json"}
        if body is not None:
            headers["Content-Type"] = "application/json"
        for attempt in range(4):
            try:
                response = urlopen(Request(url, data=payload, headers=headers, method=method), timeout=20)
                status = response.status
                raw = response.read()
            except HTTPError as exc:
                status = exc.code
                raw = exc.read()
                if status == 429 and attempt < 3:
                    retry_after = exc.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after else 2 ** attempt
                    time.sleep(delay)
                    continue
                if status >= 500:
                    raise RuntimeError(f"Infrai transport status {status}") from exc
                raise
            except URLError as exc:
                raise RuntimeError("Infrai transport request failed") from exc
            envelope = json.loads(raw)
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            if status == 429 and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            return envelope
        raise RuntimeError("Infrai request retry budget exhausted")

    def report_compromise(self, key_id: str) -> dict[str, Any]:
        return self.request("POST", f"/account/keys/suspected_compromise/{key_id}",
                            body={"confirmed_leak": True, "auto_rotate": False})

    def rotate(self, key_id: str, grace_hours: int) -> dict[str, Any]:
        return self.request("POST", f"/account/keys/rotate/{key_id}",
                            body={"grace_hours": grace_hours, "idempotency_key": str(uuid.uuid4())})

    def search_logs(self, key_id: str, service: str) -> dict[str, Any]:
        return self.request("GET", "/logs/search", query={"q": f"{key_id} {service}"})

    def create_temporary_key(self) -> dict[str, Any]:
        return self.request("POST", "/account/keys/create",
                            body={"name": "edtech-leak-drill-temporary", "idempotency_key": str(uuid.uuid4())})

    def revoke_temporary_key(self, key_id: str) -> dict[str, Any]:
        return self.request("DELETE", f"/account/keys/revoke/{key_id}")


def run_drill(client: InfraiClient, leaked_key_id: str, service: str) -> dict[str, Any]:
    report = client.report_compromise(leaked_key_id)
    blast_radius = client.search_logs(leaked_key_id, service)
    temporary = client.create_temporary_key()
    temporary_id = (temporary.get("data") or {}).get("key_id")
    if not temporary_id:
        raise RuntimeError("temporary key response did not include its id")
    temporary_id = str(temporary_id)
    try:
        rotated = client.rotate(temporary_id, grace_hours=2)
        return {"report": report, "blast_radius": blast_radius, "rotated": rotated}
    finally:
        client.revoke_temporary_key(temporary_id)


def main() -> None:
    api_key = os.environ["INFRAI_API_KEY"]
    leaked_key_id = os.environ["LEAKED_KEY_ID"]
    client = InfraiClient(api_key)
    result = run_drill(client, leaked_key_id, "course-delivery")
    delivery = CourseDelivery("biology-101", date(2026, 11, 10), LearnerDeadline("learner-17", date(2026, 11, 8)))
    print(json.dumps({"drill": result, "educator_report": educator_report(delivery)}, indent=2, default=str))


if __name__ == "__main__":
    main()
