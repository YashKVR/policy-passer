# Status

The pilot is running.

- `/` lists each check. Waiting is Sea Green, in progress is Marigold, and decided is Coral.
- `/checks/{check_id}` shows the policy copy, the papers, the outcome, the mistakes, and the steps. A waiting check has Run. A decided check does not.
- Run calls `POST /api/checks/{check_id}/run`. The agent reads the policy and the papers through the API and stores the decision. Tests use a stub model.
- A rejection needs mistakes and a reason. An approval must say the papers are ready to submit.
- `CHK-9001` stays in `data/evals/` and is not loaded. Nothing submits the papers.

`npm run dev` serves the dashboard on port 5173 and the backend on port 8000. `npm run check` runs the Python, TypeScript, and Playwright checks.
