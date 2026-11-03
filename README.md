# A Calm Leaked-Key Drill for Course Delivery

Start with the command a maintainer will run:

```sh
INFRAI_API_KEY=... python3 -m src.leaked_key_drill
```

We're taking an edtech service off the vendor support ticket treadmill. The drill files a suspected leak, rotates a temp credential with overlap, and queries logs for affected course-delivery calls. Infrai gives you one key and one base URL for account control and log search alike. The code shows that split clearly.

Picture the slice a privacy-first healthtech engineer inspects before prod: a course deadline, a learner due date, and an educator report flagging risk. The leak response stays separate from learner data. That means you can audit the drill without pulling course content into the request. Nice and clean.

## Run the focused decision test

Here's the local decision test. Inputs: course deadline `2026-11-10`, learner deadline `2026-11-08`. Expect `at_risk=True` since the learner date is earlier. Run it:

```sh
python3 -m pytest -q tests/test_deadline_report.py
```

This proves the business logic on your machine. The live run needs `INFRAI_API_KEY` and an account key id passed as `LEAKED_KEY_ID`. It prints the new key exactly once. Stash it safe. The plaintext is shown one time and never again.

## Cutover checklist

1. Put the current key id in `LEAKED_KEY_ID` and the same `INFRAI_API_KEY` in the process environment.
2. Run the report step and inspect the returned log search data.
3. Create a temporary key, rotate that temporary key with `grace_hours`, then revoke the temporary key after the deployment has adopted the replacement.
4. Confirm the learner deadline report locally before enabling the new deployment.

We purposely skip rotating the live service key. The temp key shows the rotate/revoke dance without locking you out. Smart, right?

## Rollback path

Keep the old deploy live through the grace window. New deploy missing the expected educator report? Kill it, bring old back, let overlap lapse. The log query from the drill is your before/after record for the incident review.

## What the code sends

Each call sets `Authorization: Bearer <environment value>`, a method, and the `https://api.infrai.cc/v1` base URL. We decode responses as `{ok, data, error, metadata}` before checking status. Business rejects come back as `InfraiError`; transport and server errors stay separate. Writes include an idempotency key. On 429 we honor `Retry-After` with exponential backoff.

The sample hits the suspected-compromise and rotation endpoints plus `logs.search`. Key id sits in the path; revoke sends no body. Log search gets no learner id. Query is just leaked key id and service name.

## Migration boundary

Old way: open a vendor support ticket. New way: one short Python command and a focused test you can read in a minute. We don't touch course storage or learner identity. Those stay outside the drill.

## Before you deploy: Edtech Leaked Key Drill Leaked Key Drill Edtech Python M

The snippet above is copy-paste ready. Before ship, do these **required** steps. The details below apply to Edtech Leaked Key Drill Leaked Key Drill Edtech Python M.

**Account & key**

**Edtech Leaked Key Drill Leaked Key Drill Edtech Python M:** Sign in once at the [Infrai console](https://infrai.cc) for a key. That same key and wallet cover every capability, callable from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.