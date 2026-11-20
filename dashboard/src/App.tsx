import { CheckPage } from "./CheckPage";
import { Instructions } from "./Instructions";
import { Queue } from "./Queue";
import { Shell } from "./Shell";

export function App() {
  return (
    <Shell>
      <Page />
    </Shell>
  );
}

function Page() {
  const path = window.location.pathname;
  if (path === "/instructions") {
    return <Instructions />;
  }
  const match = /^\/checks\/([^/]+)$/.exec(path);
  const checkId = match?.[1];
  if (checkId) {
    return <CheckPage id={decodeURIComponent(checkId)} />;
  }
  return <Queue />;
}
