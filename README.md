# AutoHire AI Venture Lab

A local-first, safety-gated multi-agent experimentation framework being added to AutoHire.

**Status:** initial scaffold / developer preview. It is not yet an autonomous business operator. It records research and improvement proposals; it does not deploy software, contact people, spend money, or change its own production code.

## Design goals
- Local model support through Ollama; no paid API required for the initial path.
- Persistent SQLite memory for runs, experiments, events and improvement proposals.
- Clear agent roles: director, researcher, builder, critic and evaluator.
- Recurring experiment cycles with explicit limits.
- Human approval before external actions or promoting self-modifications.
- Safe defaults: no shell-command execution from model output, no automatic deployment, no autonomous purchases or outreach.

## Requirements
- Windows 11
- Python 3.11+
- Ollama (optional, but required for model-generated work)
- Git recommended
- Docker recommended for later sandboxed coding; this initial scaffold does not execute generated code.

## Quick start (PowerShell)
```powershell
cd path\to\gptautohire
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
Copy-Item .env.example .env
```

Install Ollama from https://ollama.com/download/windows, then download a model that fits your GPU/VRAM. Example:
```powershell
ollama pull qwen3:8b
ollama serve
```
Model tags and memory requirements change; choose a smaller model if you hit VRAM/RAM limits. You can test the database without Ollama.

Initialise and inspect:
```powershell
venture-lab init
venture-lab status
venture-lab cycle --goal "Find and evaluate a small, low-cost B2B service opportunity"
venture-lab proposals
python -m unittest discover -s tests -v
```

Set `OLLAMA_MODEL` in `.env` to a model you actually installed. The CLI loads environment variables from `.env`.

## Budget controls
- The initial implementation calls only the local Ollama endpoint.
- No external model API keys are supported in this scaffold.
- The daily cycle cap is configured by `MAX_CYCLES_PER_DAY`.
- Any business spend, paid ads, customer contact, production deployment or handling of sensitive data requires a separate human-approved workflow. Do not add unattended credentials to agent environments.

## Recursive improvement loop
1. Execute a bounded research/planning cycle.
2. Persist the outputs and evidence.
3. Generate an improvement proposal.
4. Keep it pending for human review.
5. Add repeatable, independent tests before considering promotion.

This is process-level improvement (memory, prompts, tools and workflows), not automatic improvement of the underlying model weights. Model-generated confidence is not treated as proof.

## Repository layout
- `venture_lab/`: application
- `tests/`: deterministic tests
- `.env.example`: local configuration template
- `SECURITY.md`: boundaries and threat model

## Next milestones
1. Run the scaffold locally and confirm Python/Ollama versions and GPU memory.
2. Add an independent benchmark suite and regression gates.
3. Add a Docker-based coding worker with read-only mounts and network disabled by default.
4. Add a local dashboard and structured venture scorecards.
5. Add human-approved market validation workflows before any customer-facing automation.

See `SECURITY.md` before enabling tools or connecting accounts.
