Always run before committing:

```bash
pnpm run check
```

This runs: Prettier (writes), ESLint with `--fix`, vue-tsc type check, Vitest tests.

Use `pnpm run check:ci` for the read-only equivalent (`format:check`, `lint` without
`--fix`). This is what CI runs, so prefer it when you only need a pass/fail answer.

All checks must pass. No console.log in production code.
