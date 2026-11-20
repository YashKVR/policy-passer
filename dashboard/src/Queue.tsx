import { useEffect, useState } from "react";
import { getJson } from "./api";
import type { CheckSummary } from "./types";

type Health = "loading" | "up" | "down";

const statusLabel: Record<string, string> = {
  waiting: "waiting",
  in_progress: "in progress",
  decided: "decided",
};

export function Queue() {
  const [health, setHealth] = useState<Health>("loading");
  const [checks, setChecks] = useState<CheckSummary[]>([]);
  const [queueError, setQueueError] = useState("");

  useEffect(() => {
    void getJson<{ status: string }>("/api/health")
      .then((body) => {
        setHealth(body.status === "ok" ? "up" : "down");
      })
      .catch(() => {
        setHealth("down");
      });
    void getJson<CheckSummary[]>("/api/checks")
      .then((body) => {
        if (!Array.isArray(body)) {
          throw new Error("Queue was not a list");
        }
        setChecks(body);
      })
      .catch(() => {
        setQueueError("The queue is unavailable.");
      });
  }, []);

  return (
    <>
      <p>{healthMessage(health)}</p>
      {queueError ? <p>{queueError}</p> : null}
      <ul className="check-list">
        {checks.map((check) => (
          <li key={check.id}>
            <a href={`/checks/${check.id}`}>
              <span className="id">{check.id}</span> {check.title}
            </a>
            <span className={`status ${check.status}`}>
              {statusLabel[check.status] ?? check.status}
            </span>
          </li>
        ))}
      </ul>
    </>
  );
}

function healthMessage(health: Health): string {
  if (health === "loading") {
    return "Checking the backend.";
  }
  if (health === "up") {
    return "The backend is up.";
  }
  return "The backend is down.";
}
