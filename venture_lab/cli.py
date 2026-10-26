"""Command-line interface for the AutoHire AI Venture Lab."""
from __future__ import annotations

import argparse
import json
import sys

from .config import get_config
from .db import Store
from .engine import run_cycle
from .llm import ModelError


def main() -> None:
    parser = argparse.ArgumentParser(prog="venture-lab", description="Local-first AI Venture Lab")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init", help="Create the local database")
    sub.add_parser("status", help="Show recent runs and configuration")
    cycle = sub.add_parser("cycle", help="Run one bounded research/improvement cycle")
    cycle.add_argument("--goal", required=True, help="Goal to investigate")
    proposals = sub.add_parser("proposals", help="List pending improvement proposals")
    proposals.add_argument("--limit", type=int, default=20)

    args = parser.parse_args()
    try:
        config = get_config()
        store = Store(config["db_path"])
        if args.command == "init":
            print(f"Database ready: {config['db_path']}")
        elif args.command == "status":
            print(json.dumps({
                "database": str(config["db_path"]),
                "model": config["ollama_model"],
                "ollama": config["ollama_base_url"],
                "cycles_today_utc": store.count_runs_today(),
                "daily_cycle_cap": config["max_cycles_per_day"],
                "external_actions_enabled": False,
                "recent_runs": store.runs(10),
            }, indent=2, ensure_ascii=False))
        elif args.command == "cycle":
            run_id = run_cycle(store, config, args.goal)
            print(f"Cycle {run_id} completed. Run 'venture-lab proposals' to inspect its proposal.")
        elif args.command == "proposals":
            print(json.dumps(store.proposals(max(1, args.limit)), indent=2, ensure_ascii=False))
    except (ValueError, RuntimeError, ModelError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
