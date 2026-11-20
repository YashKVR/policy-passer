# Pilot plan

Policy Passer checks one policy copy and one set of claim papers before anyone submits them. The pilot stores each check, decides it, and shows the outcome, the mistakes, and the steps. It does not submit papers, rewrite them, take payment, sign anyone in, or message the person who supplied the papers.

`docs/STATUS.md` describes a hello-world skeleton. Those folders are not in the repo. The npm scripts already expect `backend.main:app`, a Vite app in `dashboard/`, and Playwright in `e2e/`. Phase 1 creates that shell. Later phases fill it in.

## Approach

A check is the only record. It holds the policy copy, the claim papers, the status, the outcome, the mistakes, and the explanation. The spec always looks at one policy copy together with one set of papers, so the pilot does not add customers, plans, or handlers.

The files in `data/` are the business records. On startup the backend loads every check except anything under `data/evals/` into SQLite. The dashboard and the agent read and write only through the API. The agent never opens `data/`.

The API enforces the decision rules. A rejection with no mistakes, or an approval that does not say the papers are ready to submit, is rejected with 422. Putting the rules in the API means a bad model answer cannot be stored. There is no submit route and no pay route.

Each API operation has an `operation_id`, a one-line docstring, and no optional inputs. JSON fields stay in snake_case from the database to the screen.

Tests never call a model. Agent tests pass a stub that returns a fixed series of tool calls. `npm run check` stays green at the end of every phase, including 80% coverage. Scripts stay as `uv run` commands or files the existing npm scripts already call, so the same commands work on Windows.

## Records used throughout

| Id | Status at startup | What it is for |
|---|---|---|
| `CHK-1001` | waiting | Policy period 1 Jun 2026 through 30 Jun 2026. Papers: Maya Chen, emergency treatment on 12 Jun 2026, itemized receipt for $480.00. Section "Emergency medical care" covers treatment inside the period when a receipt is attached. |
| `CHK-1002` | waiting | Same policy. Papers: Luis Ortega, treatment on 5 Jul 2026, no receipt. |
| `CHK-1003` | decided, rejected | Seeded so the screens and end-to-end tests can show a finished check without a model. Section "Baggage". Mistake: no police report for a theft of $300.00. Reason: the policy requires a police report filed within 24 hours. Two activity steps are already stored. |
| `CHK-9001` | not loaded | Lives only in `data/evals/`. The queue, the API, and the agent must not see it. |

`data/instructions.md` tells the agent to read the policy copy and the papers, decide only from that policy, record each step, avoid submitting, name every mistake and why it would cause a rejection, cite the policy section, and on approval say the papers are ready to submit.

## Phase 1: App shell

The scripts, type checks, and tests have nothing to run. This phase makes `npm run dev` and `npm run check` real before any check data exists.

Build:

- `backend/main.py`: FastAPI app and `GET /api/health`, `operation_id` `health`, response `{"status": "ok"}`.
- `dashboard/`: a Vite React page that requests `/api/health` and shows whether the backend is up. Vite proxies `/api` to `http://127.0.0.1:8000`.
- Brand tokens on that page: Instrument Sans, Midnight text, page background `#F0F4F5`, a white panel. Dark-mode tokens are defined and unused. Three routes do not need a router package.
- `e2e/`: one Playwright test that the page shows the backend is up.
- Tool config the npm scripts already call: strict `tsconfig.json`, ESLint, Prettier, Vitest coverage at 80%, and Playwright. Vitest and Playwright start against the Vite app.
- `agent/run.py`: `run(check_id, thread_id)` with one tool that calls `GET /api/health`. The real check tools replace this in Phase 5. The signature takes an id and a thread id, and the id is a check id because that is the record the spec works on.

Success criteria:

- [x] `uv run pytest -q` passes, and the health test gets `{"status": "ok"}`.
- [x] `npm run check` passes.
- [x] With `npm run dev` running, `GET http://127.0.0.1:8000/api/health` returns `200` and `{"status": "ok"}`.
- [x] The Playwright test opens the dashboard and finds the text that the backend is up.
- [x] In the browser, the dashboard page shows that same text on a white panel, Midnight on `#F0F4F5`.

## Phase 2: Records and the queue

The team needs every check, its status, and the papers. This phase loads the files and serves them. Decisions wait until the records are in place.

Build:

- `data/README.md`, `data/instructions.md`, `CHK-1001`, `CHK-1002`, `CHK-1003`, and `data/evals/CHK-9001`.
- SQLite tables for checks and activity steps. Startup loads `data/` and skips `data/evals/`.
- `GET /api/checks`, `operation_id` `list_checks`: id, title, and status, sorted by id.
- `GET /api/checks/{check_id}`, `operation_id` `get_check`: the policy copy, the claim papers, status, outcome, explanation, policy section, and mistakes.
- `GET /api/instructions`, `operation_id` `get_instructions`: the instruction text.
- A missing check returns `404`.

Success criteria:

- [x] `GET /api/checks` returns `CHK-1001` and `CHK-1002` as `waiting`, and `CHK-1003` as `decided`, and does not return `CHK-9001`.
- [x] `GET /api/checks/CHK-1001` returns Maya Chen's policy copy and papers, status `waiting`, and an empty mistake list.
- [x] `GET /api/checks/CHK-1003` returns outcome `rejected`, the baggage mistake, and the reason about the police report.
- [x] `GET /api/checks/CHK-9001` returns `404`.
- [x] `GET /api/instructions` returns the text from `data/instructions.md`.
- [x] A backend test fails if the seed reads `data/evals/`.
- [x] `npm run check` passes.

## Phase 3: Decisions and activity

The queue can be read, and now a check has to move. The rules live here so Phase 5's agent has a safe place to write.

Statuses are `waiting`, `in_progress`, and `decided`.

Build:

- `POST /api/checks/{check_id}/start`, `operation_id` `start_check`, no body. `waiting` becomes `in_progress`. Any other status returns `409`.
- `POST /api/checks/{check_id}/steps`, `operation_id` `add_step`, body `{"message": "..."}`. Accepted only while `in_progress`. The message is required.
- `GET /api/checks/{check_id}/activity`, `operation_id` `list_activity`: steps in the order they were recorded.
- `POST /api/checks/{check_id}/decision`, `operation_id` `record_decision`, body `outcome`, `explanation`, `policy_section`, and `mistakes`. Every field is required. `mistakes` is a list of `mistake` and `reason`.
  - The check must be `in_progress`, or the response is `409`.
  - `rejected` with an empty mistake list, an empty explanation, or an empty policy section returns `422`.
  - `approved` returns `422` unless the explanation says the papers are ready to submit. The mistake list is empty.
  - Success sets status to `decided` and stores the outcome.
- No route submits papers or pays a claim.

Success criteria:

- [ ] `POST /api/checks/CHK-1001/start` returns the check with status `in_progress`. A second start returns `409`.
- [ ] `POST /api/checks/CHK-1001/steps` with a message stores it, and `GET /api/checks/CHK-1001/activity` returns that step after the seeded order.
- [ ] A step posted to `CHK-1003` returns `409`.
- [ ] A decision of `rejected` with no mistakes returns `422`, and the check stays `in_progress`.
- [ ] A decision of `approved` whose explanation does not say the papers are ready to submit returns `422`.
- [ ] A valid `approved` decision on `CHK-1001` returns status `decided`, outcome `approved`, and the ready-to-submit explanation.
- [ ] `GET /api/checks` has no submit or pay operation. The OpenAPI document contains neither.
- [ ] `npm run check` passes.

## Phase 4: Dashboard

The API now has the shapes the team needs to see. The screens come before the agent so the queue, a finished check, and the instructions can be reviewed on seeded data.

Build three pages by reading the path, with no router dependency:

- `/` lists each check and its status. Waiting, in progress, and decided use Sea Green, Marigold, and Coral, darkened enough for text on white.
- `/checks/{check_id}` shows the policy copy, the claim papers, the outcome, each mistake and why it would cause a rejection, the explanation, the policy section, and the activity steps.
- `/instructions` shows the instructions as text. There is no input and no save control.

Fonts are Instrument Sans for the interface, Instrument Serif for the tagline, and JetBrains Mono for check ids. Panels are white and rounded, with no one-sided border and no top rule. Money on a page is written like `$480.00`.

Success criteria:

- [ ] Vitest renders the queue with `CHK-1001` waiting, `CHK-1002` waiting, and `CHK-1003` decided.
- [ ] Vitest renders `CHK-1003` with outcome rejected, the missing police report, the 24-hour reason, and both activity steps.
- [ ] Vitest renders the instructions page with no text field and no button that saves.
- [ ] Playwright opens `/`, `/checks/CHK-1003`, and `/instructions` against `npm run dev` and sees the same facts.
- [ ] In the browser, the queue, the decided check, and the instructions page match the brand: the three status colors, a white panel, and the tagline in Instrument Serif.
- [ ] `npm run check` passes.

## Phase 5: Agent

The screens can show a decision. This phase makes Policy Passer produce one. Tools talk only to the API, so the agent cannot read `data/evals/` or submit papers.

Build:

- `run(check_id, thread_id)` uses LangChain `create_agent` on OpenRouter.
- The model is `openai/gpt-6-luna` with low reasoning effort, or `MODEL_NAME` when that environment variable is set.
- Tools, each a call to the backend: get the check, get the instructions, add a step, record the decision. The tool list has no file tool and no submit tool.
- The run starts the check, lets the stub or model record steps and one decision, and returns the decided check.
- Tests inject a stub model. The stub for `CHK-1002` records one step and a rejection: the treatment is outside the policy period, and the receipt is missing.

Success criteria:

- [ ] A unit test of `run("CHK-1002", "thread-1")` with the stub finishes with status `decided`, outcome `rejected`, and both mistakes stored.
- [ ] The test asserts the stub's tool calls hit the API and that no test opened `data/evals/`.
- [ ] The model factory uses `MODEL_NAME` when it is set, and otherwise `openai/gpt-6-luna` with low reasoning effort. The test does not create a live client.
- [ ] `npm run check` passes without `OPENROUTER_API_KEY`.

## Phase 6: Run a check from the queue

The agent can decide a check in a test. This phase starts that run from the backend and shows it on the check page. End-to-end tests still use the seeded decided check, so Playwright does not call a model.

Build:

- `POST /api/checks/{check_id}/run`, `operation_id` `run_check`, body `{"thread_id": "..."}`. `thread_id` is required. The handler calls `run(check_id, thread_id)`.
- The backend test overrides the agent with the Phase 5 stub.
- The check page shows a Run control for a `waiting` check. While the check is `in_progress`, the page polls `list_activity` and appends steps. The control is absent once the check is `decided`.

Success criteria:

- [ ] `POST /api/checks/CHK-1002/run` with `{"thread_id": "thread-1"}` and the stub returns `decided` and `rejected`, with the two mistakes and at least one new activity step.
- [ ] The same call for `CHK-1003` returns `409`.
- [ ] Vitest shows Run on a waiting check and hides it on `CHK-1003`.
- [ ] Playwright still passes without a model call, using `CHK-1003` for the decided check.
- [ ] In the browser, `CHK-1003` shows its steps in order, and a waiting check shows Run.
- [ ] `npm run check` passes.

## Out of scope

- Submitting papers to an insurer, and any payment.
- Rewriting the papers into a corrected claim.
- Sign-in, and messages to the person who supplied the papers.
- A dark-mode switch. The tokens are set in Phase 1 for a later switch.
- Reading `data/evals/` to grade the agent. Those files stay out of the queue so a later check can use them.
