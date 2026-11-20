import { useEffect, useState } from "react";
import { getJson } from "./api";
import type { Check, Step } from "./types";

export function CheckPage({ id }: { id: string }) {
  const [check, setCheck] = useState<Check | null>(null);
  const [steps, setSteps] = useState<Step[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    void getJson<Check>(`/api/checks/${id}`)
      .then((body) => {
        setCheck(body);
      })
      .catch(() => {
        setError("Check not found.");
      });
    void getJson<Step[]>(`/api/checks/${id}/activity`)
      .then((body) => {
        setSteps(body);
      })
      .catch(() => {
        setSteps([]);
      });
  }, [id]);

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
