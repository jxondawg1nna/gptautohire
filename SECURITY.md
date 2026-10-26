# Security and autonomy boundaries

This project is an experimental agent framework, not a hardened security product.

## Safe defaults
- Model output is untrusted data.
- Never execute commands, scripts or code copied from a model response.
- Never provide agents with passwords, API keys, browser cookies, personal files or unrestricted account access.
- Do not allow agents to change spending caps, their own permissions, evaluator rules or deployment policy.
- Do not run generated code on the host. Any future coding worker must use an isolated container/VM, non-root user, resource limits, read-only source mounts where possible, and network disabled by default.
- Keep human approval for publishing, sending messages, purchases, paid APIs, customer-data access and production changes.
- Do not collect sensitive personal information or send unsolicited marketing messages.

## Threat model
Potential failures include prompt injection from web pages/files, data exfiltration, destructive code, runaway loops, misleading self-evaluation, excessive compute use and false business claims. SQLite logs and model critique do not eliminate these risks.

## Before expanding autonomy
- Add tests that do not depend on the same model that generated a change.
- Run tests against held-out cases and previous successful tasks.
- Use code review and version control; preserve rollback points.
- Restrict filesystem access and network egress.
- Add real hard limits at the process/orchestrator level, not just in prompts.
- Verify applicable privacy, spam, consumer and financial-services obligations before any commercial outreach or lead generation.
