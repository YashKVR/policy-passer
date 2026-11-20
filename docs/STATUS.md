# Status

The pilot shell is running.

- `npm run dev` starts the backend on port 8000 and the dashboard on port 5173.
- `GET /api/health` returns `{"status": "ok"}`.
- The dashboard shows whether the backend is up.
- `agent.run(check_id, thread_id)` calls the health route.
- `npm run check` runs the Python, TypeScript, and Playwright checks.

The check queue is not built yet.
