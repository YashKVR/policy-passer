# Status

The check queue is loaded from `data/` and served by the API.

- `GET /api/checks` lists `CHK-1001`, `CHK-1002`, and `CHK-1003`. `CHK-9001` stays in `data/evals/` and is not served.
- `GET /api/checks/{check_id}` returns the policy copy, the claim papers, and any decision already stored.
- `GET /api/instructions` returns the read-only instructions.
- The dashboard shows whether the backend is up.
- `npm run dev` starts the backend on port 8000 and the dashboard on port 5173.

A check cannot move from waiting to decided yet.
