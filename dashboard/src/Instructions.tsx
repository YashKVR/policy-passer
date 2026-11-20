import { useEffect, useState } from "react";
import { getJson } from "./api";

export function Instructions() {
  const [text, setText] = useState("");

  useEffect(() => {
    void getJson<{ instructions: string }>("/api/instructions")
      .then((body) => {
        setText(body.instructions);
      })
      .catch(() => {
        setText("Instructions are unavailable.");
      });
  }, []);

  return (
    <>
      <h2>Instructions</h2>
      <p className="instructions">{text}</p>
    </>
  );
}
