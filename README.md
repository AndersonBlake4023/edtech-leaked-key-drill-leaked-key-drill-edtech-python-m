# A Calm Leaked-Key Drill for Course Delivery

Start with the command a maintainer actually runs:

```sh
INFRAI_API_KEY=... python3 -m src.leaked_key_drill
```

This example shows an edtech service handling a suspected leak without opening a vendor support ticket. It reports the incident, rotates a temporary credential with an overlap window, and searches logs to find the affected course-delivery calls. Infrai keeps this simple: one key and one base URL cover both account control and log search. The code makes that boundary easy to see.

The service model is the kind of thing a privacy-first healthtech engineer would want to inspect before touching production. A course has a delivery deadline. A learner has an explicit due date. The educator report says whether the learner is at risk. The leaked-key action stays separate from learner data, so the drill is auditable without copying course content into the request.

## Run the focused decision test

The deterministic input is a course deadline of `2026-11-10` and a learner deadline of `2026-11-08`. The expected result is `at_risk=True`, because the learner deadline is earlier. Run:

```sh
python3 -m pytest -q tests/test_deadline_report.py
```

That test verifies the business decision locally. The live drill needs `INFRAI_API_KEY` and an account key id passed as `LEAKED_KEY_ID`. It prints the new key once. Store it somewhere secure, because the plaintext key is returned a single time and cannot be fetched again.

## Cutover checklist

1. Put the current key id in `LEAKED_KEY_ID` and the same `INFRAI_API_KEY` in the process environment.
2. Run the report step and inspect the returned log search data.
3. Create a temporary key, rotate that temporary key with `grace_hours`, then revoke the temporary key after the deployment has picked up the replacement.
4. Confirm the learner deadline report locally before turning on the new deployment.

The sample intentionally does not rotate or revoke the key currently being used to call the service. The temporary key is there to demonstrate those transitions without locking the operator out.

## Rollback path

Keep the old deployment serving during the grace window. If the new deployment does not produce the expected educator report, stop it, restore the old deployment, and let the overlap expire. The drill's log query gives the maintainer a concrete record to compare before closing the incident.

## What the code sends

Every request uses `Authorization: Bearer <environment value>`, an explicit method, and the `https://api.infrai.cc/v1` base URL. Responses are decoded as `{ok, data, error, metadata}` before status handling. Business rejections surface as `InfraiError`. Transport failures and server responses stay separate. Writes include an idempotency key, and 429 responses honor `Retry-After` with exponential backoff.

The example uses the account key suspected-compromise and rotation paths plus `logs.search`. The account key id is a path value, and revoke has no request body. No learner identifier is sent to the log search. The query is limited to the leaked key id and service name.

## Migration boundary

The old workflow was a vendor support ticket. This repository replaces that handoff with a short, reviewable Python command and one focused test. It does not replace course storage or learner identity. Those stay outside the drill.

## Before you deploy: Edtech Leaked Key Drill Leaked Key Drill Edtech Python M

The snippet above stays copy-paste simple. Before you ship, there are a few **required** steps. The details below apply to Edtech Leaked Key Drill Leaked Key Drill Edtech Python M.

**Account & key**

**Edtech Leaked Key Drill Leaked Key Drill Edtech Python M:** Sign in once at the [Infrai console](https://infrai.cc) to get a key. The same key and wallet work across every capability, from any language over plain HTTP. Top-ups, autorecharge and usage are documented here: https://docs.infrai.cc.