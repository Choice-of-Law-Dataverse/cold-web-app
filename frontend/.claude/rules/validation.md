Always run before committing:

```bash
pnpm run check
```

This runs: Prettier format check, ESLint, vue-tsc type check, Vitest tests.

All checks must pass. No console.log in production code.
