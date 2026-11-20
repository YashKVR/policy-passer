import { spawnSync } from "node:child_process";
import { delimiter } from "node:path";

const env = { ...process.env };
delete env.PYTHONPATH;
env.PATH = `node_modules/.bin${delimiter}${env.PATH ?? ""}`;

function run(command, args) {
  const executable = process.platform === "win32" ? `${command}.cmd` : command;
  const result = spawnSync(executable, args, {
    stdio: "inherit",
    env,
    shell: process.platform === "win32",
  });
  if (result.status !== 0) {
    process.exit(result.status ?? 1);
  }
}

run("uv", ["run", "ruff", "format", "--check"]);
run("uv", ["run", "ruff", "check"]);
run("pyright", []);
run("uv", ["run", "pytest", "-q"]);
