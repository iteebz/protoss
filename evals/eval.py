"""Evaluation runner - module interface + CLI."""

import asyncio
import json
import sys
from datetime import datetime

from protoss.lib.paths import Paths  # Import Paths from protoss.lib.paths

from .config import config
from .generate import (
    coding,
    continuity,
    conversation,
    integrity,
    reasoning,
    research,
    security,
)
from .runner import (
    evaluate_protoss_scenario,
)  # Removed protoss_eval_config import


async def run(category=None, samples=None):
    """Run evaluation category or full suite."""
    samples = samples or config.sample_size

    # Adapt category mapping to use config and new scenario structure
    # For now, we'll use a simplified mapping and assume generate.py will be adapted
    # to return scenarios suitable for evaluate_protoss_scenario
    if category == "reasoning":
        # This will need to be adapted to generate Protoss-specific scenarios
        return await _run_category("reasoning", reasoning, samples)
    if category == "conversation":
        return await _run_category("conversation", conversation, samples)
    if category == "continuity":
        return await _run_category("continuity", continuity, samples)
    if category == "coding":
        return await _run_category("coding", coding, samples)
    if category == "research":
        return await _run_category("research", research, samples)
    if category == "security":
        return await _run_category("security", security, samples)
    if category == "integrity":
        return await _run_category("integrity", integrity, samples)
    return await _run_all(samples)


async def _run_category(name, generator, samples):
    """Execute single category evaluation."""
    print(f"🧠 {name.capitalize()} Evaluation")
    print("=" * 40)

    # Override config temporarily
    original_size = config.sample_size  # Use config
    config.sample_size = samples

    try:
        # Generate scenarios (assuming generator is adapted for Protoss scenarios)
        scenarios = generator(config.sample_size)
        results = []
        for i, scenario in enumerate(scenarios):
            scenario["test_id"] = f"{name}_{i:02d}"
            result = await evaluate_protoss_scenario(scenario)
            results.append(result)

        # Aggregate results for the category
        passed_count = len([r for r in results if r.get("passed") is True])
        total_count = len(results)
        rate = passed_count / total_count if total_count else 0

        category_result = {
            "category": name,
            "passed": passed_count,
            "total": total_count,
            "rate": rate,
            "results": results,
        }

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_id = f"{timestamp}_{config.judge}"  # Use config.judge

        run_dir = Paths.evals(f"runs/{run_id}")  # Use Paths from protoss.lib.paths
        run_dir.mkdir(parents=True, exist_ok=True)
        config_data = {
            "judge": config.judge,
            "sample_size": samples,
            "seed": config.seed,
            "timestamp": datetime.now().isoformat(),
        }

        with open(Paths.evals(f"runs/{run_id}/config.json"), "w") as f:
            json.dump(config_data, f, indent=2)

        with open(Paths.evals(f"runs/{run_id}/{name}.json"), "w") as f:
            json.dump(category_result, f, indent=2)
        latest_link = Paths.evals("latest")
        if latest_link.exists() or latest_link.is_symlink():
            latest_link.unlink()
        latest_link.symlink_to(f"runs/{run_id}")

        print(f"Results: {category_result.get('passed', 0)}/{category_result['total']}")
        print(f"Saved: {run_dir}")

        return category_result

    finally:
        config.sample_size = original_size


async def _run_all(samples):
    """Execute full evaluation suite."""
    print("🧠 Protoss Evaluation Suite")  # Updated name
    print("=" * 50)

    categories = {
        "reasoning": reasoning,
        "conversation": conversation,
        "continuity": continuity,
        "coding": coding,
        "research": research,
        "security": security,
        "integrity": integrity,
    }

    # Override config temporarily
    original_size = config.sample_size
    config.sample_size = samples

    try:
        results = []
        for name, generator in categories.items():
            category_result = await _run_category(name, generator, samples)
            results.append(category_result)

        total = sum(r["total"] for r in results)
        passed = sum(r.get("passed", 0) for r in results if r.get("passed") is not None)
        rate = passed / total if total else 0

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_id = f"{timestamp}_{config.judge}"

        run_dir = Paths.evals(f"runs/{run_id}")
        run_dir.mkdir(parents=True, exist_ok=True)
        config_data = {
            "judge": config.judge,
            "sample_size": samples,
            "seed": config.seed,
            "timestamp": datetime.now().isoformat(),
        }

        with open(Paths.evals(f"runs/{run_id}/config.json"), "w") as f:
            json.dump(config_data, f, indent=2)

        summary = {
            "run_id": run_id,
            "version": "Protoss Eval v1.0",  # Updated version
            "total": total,
            "passed": passed,
            "rate": f"{rate:.1%}",
            "categories": {r["category"]: r for r in results},
        }

        with open(Paths.evals(f"runs/{run_id}/summary.json"), "w") as f:
            json.dump(summary, f, indent=2)

        for result in results:
            with open(
                Paths.evals(f"runs/{run_id}/{result['category']}.json"), "w"
            ) as f:
                json.dump(result, f, indent=2)

        # Update latest symlink
        latest_link = Paths.evals("latest")
        if latest_link.exists() or latest_link.is_symlink():
            latest_link.unlink()
        latest_link.symlink_to(f"runs/{run_id}")

        print(f"Overall: {summary['rate']}")
        for result in results:
            rate = f"{result.get('rate', 0):.1%}" if result.get("rate") else "Raw"
            print(f"{result['category'].capitalize()}: {rate}")
        print(f"Latest: {run_dir}")

        return summary

    finally:
        config.sample_size = original_size


def latest():
    """Get latest evaluation summary."""
    latest_link = Paths.evals("latest")
    if latest_link.exists():
        summary_file = latest_link / "summary.json"
        if summary_file.exists():
            with open(summary_file) as f:
                return json.load(f)
    return None


def logs(test_id):
    """Get debug logs for specific test."""
    # TODO: Implement test-specific log extraction
    return f"Debug logs for {test_id} - not yet implemented"


async def cli():
    """CLI entry point."""
    args = sys.argv[1:]

    samples = config.sample_size  # Use config

    if "--samples" in args:
        idx = args.index("--samples")
        samples = int(args[idx + 1])
        args = [a for i, a in enumerate(args) if i not in [idx, idx + 1]]

    if "--seed" in args:
        idx = args.index("--seed")
        config.seed = int(args[idx + 1])  # Use config
        args = [a for i, a in enumerate(args) if i not in [idx, idx + 1]]
        print(f"🎲 Using seed: {config.seed}")

    if "--mode" in args:
        idx = args.index("--mode")
        config.mode = args[idx + 1]  # Use config
        args = [a for i, a in enumerate(args) if i not in [idx, idx + 1]]
        if config.mode == "resume":
            print("🔄 Resume mode - strict WebSocket, no fallback")
        elif config.mode == "replay":
            print("🔁 Replay mode - HTTP only")
        elif config.mode == "auto":
            print("🤖 Auto mode - WebSocket with HTTP fallback")

    if "--concurrency" in args:
        idx = args.index("--concurrency")
        config.max_concurrent_tests = int(args[idx + 1])  # Use config
        args = [a for i, a in enumerate(args) if i not in [idx, idx + 1]]
        print(f"⚡ Concurrency: {config.max_concurrent_tests} parallel tests")

    if "--llm" in args:
        idx = args.index("--llm")
        llm_choice = args[idx + 1]
        args = [a for i, a in enumerate(args) if i not in [idx, idx + 1]]

        # Auto-configure cross-model judging
        if llm_choice == "gemini":
            config.judge = "openai"  # Cross-judge with OpenAI
            print("🧠 Gemini agent + OpenAI judge")
        elif llm_choice == "openai":
            config.judge = "gemini"  # Cross-judge with Gemini
            print("🤖 OpenAI agent + Gemini judge")
        else:
            print(f"⚠️  Unknown LLM: {llm_choice}, using default")
            llm_choice = "gemini"

        # The config.agent override logic is removed as we are now using config
        # and the agent deployment is handled within evaluate_protoss_scenario

    # Remove dangerous --no-sandbox option
    # Security tests always run in sandbox for safety
    # Tool traces show what agent WOULD have done

    category = args[0] if args else None
    await run(category, samples)


if __name__ == "__main__":
    asyncio.run(cli())
