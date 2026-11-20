import { useEffect, useState } from "react";
import { getJson, postJson } from "./api";
import type { Check, Step } from "./types";

export function CheckPage({ id }: { id: string }) {
  const [check, setCheck] = useState<Check | null>(null);
  const [steps, setSteps] = useState<Step[]>([]);
  const [error, setError] = useState("");
  const [running, setRunning] = useState(false);
  const [runError, setRunError] = useState("");

  useEffect(() => {
    void getJson<Check>(`/api/checks/${id}`)
      .then((body) => {
        setCheck(body);
      })
      .catch(() => {
        setError("Check not found.");
      });
    void loadActivity(id, setSteps);
  }, [id]);

  useEffect(() => {
    if (!running) {
      return;
    }
    const timer = window.setInterval(() => {
      void loadActivity(id, setSteps);
    }, 1000);
    return () => window.clearInterval(timer);
  }, [id, running]);

  async function onRun() {
    setRunning(true);
    setRunError("");
    try {
      const decided = await postJson<Check>(`/api/checks/${id}/run`, {
        thread_id: `web-${id}`,
      });
      setCheck(decided);
    } catch {
      setRunError("The check could not be run.");
    } finally {
      setRunning(false);
    }
  }

  if (error) {
    return <p>{error}</p>;
  }
  if (!check) {
    return <p>Loading the check.</p>;
  }
  return (
    <>
      <p className="id">{check.id}</p>
      <h2>{check.title}</h2>
      {check.status === "waiting" && !running ? (
        <button type="button" onClick={() => void onRun()}>
          Run check
        </button>
      ) : null}
      {running ? <p>Running the check.</p> : null}
      {runError ? <p>{runError}</p> : null}
      <p>
        Outcome:{" "}
        <span className={`status ${check.status}`}>
          {check.outcome || "not decided"}
        </span>
      </p>
      <h2>Policy</h2>
      <p>{check.policy_copy}</p>
      {check.policy_section ? <p>Section: {check.policy_section}</p> : null}
      <h2>Papers</h2>
      <p>{check.claim_papers}</p>
      <h2>Mistakes</h2>
      {check.mistakes.length === 0 ? (
        <p>No mistakes.</p>
      ) : (
        <ul>
          {check.mistakes.map((item) => (
            <li key={item.mistake}>
              <p>{item.mistake}</p>
              <p>{item.reason}</p>
            </li>
          ))}
        </ul>
      )}
      {check.explanation ? <p>{check.explanation}</p> : null}
      <h2>Activity</h2>
      <ol>
        {steps.map((step) => (
          <li key={step.message}>{step.message}</li>
        ))}
      </ol>
    </>
  );
}

function loadActivity(
  id: string,
  setSteps: (steps: Step[]) => void,
): Promise<void> {
  return getJson<Step[]>(`/api/checks/${id}/activity`)
    .then((body) => {
      setSteps(body);
    })
    .catch(() => {
      setSteps([]);
    });
}
