import js from "@eslint/js";
import vitest from "@vitest/eslint-plugin";
import prettier from "eslint-config-prettier";
import jsxA11y from "eslint-plugin-jsx-a11y-x";
import playwright from "eslint-plugin-playwright";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import sonarjs from "eslint-plugin-sonarjs";
import globals from "globals";
import tseslint from "typescript-eslint";

export default tseslint.config(
  { ignores: ["node_modules", "dist", "coverage", ".venv"] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  jsxA11y.configs.recommended,
  sonarjs.configs.recommended,
  {
    files: ["dashboard/**/*.{ts,tsx}"],
    plugins: {
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
      vitest,
    },
    languageOptions: {
      globals: globals.browser,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      "react-refresh/only-export-components": "error",
      ...vitest.configs.recommended.rules,
    },
  },
  {
    files: ["e2e/**/*.ts"],
    ...playwright.configs["flat/recommended"],
  },
  prettier,
);
