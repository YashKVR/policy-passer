# Status

Policy Passer can decide a check. The dashboard does not start that review yet.

- `run(check_id, thread_id)` reads the check and the instructions through the API, records each step, and stores one decision.
- The model is `openai/gpt-6-luna` with low reasoning effort, or `MODEL_NAME` when that is set.
- Tests use a stub model. They do not call OpenRouter, and they do not open `data/evals/`.
- The dashboard lists the queue, shows a check, and shows the instructions.
- There is still no route that submits papers or pays a claim.

`npm run dev` serves the dashboard on port 5173 and the backend on port 8000.
