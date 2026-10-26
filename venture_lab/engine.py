"""Bounded multi-role research cycle. No model output is executed."""
from __future__ import annotations

import json
import re
from typing import Any

from .db import Store
from .llm import generate


DIRECTOR_PROMPT = """You are the venture director for a cautious AI venture lab.
Create a concise plan for the goal. Separate verified facts from assumptions.
Do not invent market evidence, prices, customers, citations, or revenue.
Do not propose illegal activity, spam, collecting sensitive personal data, or bypassing access controls.
Return plain text with: objective, 3-5 research questions, success metric, stop condition.
Goal: {goal}
"""

RESEARCH_PROMPT = """You are a sceptical market researcher. You have no web access in this initial version.
Do not claim that you searched the internet or verified current market facts.
For the goal below, list hypotheses to validate, likely buyer/user, the problem, alternatives,
what evidence would falsify the idea, and the cheapest lawful validation step.
Clearly label all claims as hypotheses where not evidenced.
Goal: {goal}
Director plan:
{plan}
"""

CRITIC_PROMPT = """You are an independent critic. Identify unsupported assumptions, failure modes,
hidden costs, privacy/regulatory risks and ways this plan could fool itself.
Do not agree merely to be helpful. Return a concise risk review and the 3 most important checks.
Goal: {goal}
Plan: {plan}
Research hypotheses: {research}
"""

PROPOSAL_PROMPT = """Propose exactly one small process-level improvement to the agent workflow.
Do not propose unrestricted self-modification, removing safeguards, spending money, contacting people,
deploying code, or changing evaluator rules. It must be reversible and testable.
Return valid JSON with keys: title, rationale, change_type, validation_plan.
All values must be strings. If no useful improvement is supported, propose a documentation or evaluation improvement.
Goal: {goal}
Critic review: {critic}
Research hypotheses: {research}
"""


def parse_proposal(text: str) -> dict[str, str]:
    """Parse a JSON object from model output, rejecting malformed or unsafe proposals."""
    candidate = text.strip()
    match = re.search(r"\{.*\}", candidate, flags=re.DOTALL)
    if not match:
        raise ValueError("Improvement proposal was not valid JSON.")
    obj: Any = json.loads(match.group(0))
    keys = ("title", "rationale", "change_type", "validation_plan")
    if not isinstance(obj, dict) or any(not isinstance(obj.get(k), str) for k in keys):
        raise ValueError("Proposal must contain string fields: " + ", ".join(keys))
    blocked = ("disable safety", "remove guard", "exfiltrat", "steal credential", "bypass permission")
    joined = " ".join(obj[k].lower() for k in keys)
    if any(term in joined for term in blocked):
        raise ValueError("Proposal rejected by the deterministic safety filter.")
    return {k: obj[k].strip()[:4000] for k in keys}


def run_cycle(store: Store, config: dict[str, object], goal: str) -> int:
    if not goal.strip():
        raise ValueError("Goal cannot be empty.")
    if store.count_runs_today() >= int(config["max_cycles_per_day"]):
        raise RuntimeError("Daily cycle cap reached. Increase it deliberately in .env if appropriate.")

    run_id = store.create_run(goal.strip())
    base_url = str(config["ollama_base_url"])
    model = str(config["ollama_model"])
    timeout = int(config["ollama_timeout_seconds"])
    try:
        plan = generate(base_url, model, DIRECTOR_PROMPT.format(goal=goal), timeout)
        store.event(run_id, "director", "plan", plan)

        research = generate(
            base_url, model, RESEARCH_PROMPT.format(goal=goal, plan=plan), timeout
        )
        store.event(run_id, "researcher", "hypotheses", research)

        critic = generate(
            base_url, model,
            CRITIC_PROMPT.format(goal=goal, plan=plan, research=research), timeout
        )
        store.event(run_id, "critic", "review", critic)

        raw_proposal = generate(
            base_url, model,
            PROPOSAL_PROMPT.format(goal=goal, critic=critic, research=research), timeout
        )
        try:
            proposal = parse_proposal(raw_proposal)
            proposal_id = store.add_proposal(run_id, proposal)
            store.event(run_id, "evaluator", "proposal_pending_review", {
                "proposal_id": proposal_id, **proposal
            })
            summary = f"Completed research cycle. Improvement proposal #{proposal_id} awaits human review."
        except (ValueError, json.JSONDecodeError) as exc:
            store.event(run_id, "evaluator", "proposal_rejected", str(exc))
            summary = "Research completed; proposal could not be safely parsed and was not saved."
        store.finish_run(run_id, "completed", summary)
        return run_id
    except Exception as exc:
        store.event(run_id, "system", "error", f"{type(exc).__name__}: {exc}")
        store.finish_run(run_id, "failed", f"{type(exc).__name__}: {exc}")
        raise
