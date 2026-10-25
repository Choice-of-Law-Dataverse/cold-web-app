@AGENTS.md

## Claude Code

- Delegate a security pass to the `security-reviewer` subagent when a diff touches auth, API keys,
  presigned storage URLs, raw SQL or CORS.
- When compacting, keep the list of modified files and every check you ran with its result.
