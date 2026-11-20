# Status

The dashboard shows the queue, a check, and the instructions.

- `/` lists each check and its status. Waiting is Sea Green, in progress is Marigold, and decided is Coral.
- `/checks/{check_id}` shows the policy copy, the claim papers, the outcome, the mistakes, the explanation, and the activity.
- `/instructions` shows the instructions as text, with no editor.
- The API still loads the queue from `data/`, moves a check from waiting to decided, and keeps `CHK-9001` out of the queue.
- `npm run dev` serves the dashboard on port 5173 and the backend on port 8000.

Policy Passer does not yet decide a check. The screens use the records already stored.
