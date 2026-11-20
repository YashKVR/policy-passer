# Status

A check can move from waiting to decided, and the API enforces the decision rules.

- `POST /api/checks/{check_id}/start` moves a waiting check to in progress.
- `POST /api/checks/{check_id}/steps` records a step only while the check is in progress.
- `GET /api/checks/{check_id}/activity` returns those steps in order.
- `POST /api/checks/{check_id}/decision` stores an approval or a rejection. A rejection needs mistakes, an explanation, and a policy section. An approval must say the papers are ready to submit.
- There is no route that submits papers or pays a claim.
- The queue is still loaded from `data/`. `CHK-9001` stays out of it.
- The dashboard shows whether the backend is up.

The screens for the queue, a check, and the instructions are not built yet.
