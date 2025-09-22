"""Test case generators."""

import random
from typing import List, Dict, Any, Optional


def _sample_mas_scenario(
    name: str,
    initial_prompts: List[Dict[str, Any]],
    agents_to_deploy: List[str],
    criteria: str,
    timeout: int = 60,
    **extra_fields,
) -> Dict[str, Any]:
    """Creates a single Multi-Agent System (MAS) scenario test case."""
    scenario = {
        "name": name,
        "initial_prompts": initial_prompts,
        "agents_to_deploy": agents_to_deploy,
        "criteria": criteria,
        "timeout": timeout,
    }
    scenario.update(extra_fields)
    return scenario


def coding(size: Optional[int] = None) -> List[Dict[str, Any]]:
    """Software development workflow testing - write, test, debug, refactor chains, adapted for MAS."""

    tasks = [
        {
            "name": "fibonacci_function",
            "prompt": "Write a Python function to calculate fibonacci numbers, test it with fibonacci(10)",
            "agents": ["Zealot", "Archon", "Arbiter"],
            "criteria": "Archon generates correct fibonacci function, Zealot tests it, Arbiter approves.",
        },
        {
            "name": "calculator_app",
            "prompt": "Create a calculator.py with add/subtract functions, write tests, run them",
            "agents": ["Zealot", "Archon", "Arbiter"],
            "criteria": "Archon creates calculator, Zealot writes and runs tests, Arbiter approves.",
        },
    ]

    scenarios = []
    selected_tasks = tasks if size is None else random.choices(tasks, k=size)

    for task in selected_tasks:
        initial_prompts = [
            {
                "sender": "human",
                "channel": "general",
                "content": f"@archon {task['prompt']}",
            }
        ]
        scenarios.append(
            _sample_mas_scenario(
                name=task["name"],
                initial_prompts=initial_prompts,
                agents_to_deploy=task["agents"],
                criteria=task["criteria"],
                timeout=120,  # Longer timeout for coding tasks
            )
        )
    return scenarios


def continuity(size: Optional[int] = None) -> List[Dict[str, Any]]:
    return []


def conversation(size: Optional[int] = None) -> List[Dict[str, Any]]:
    """Multi-turn context building and refinement within session, adapted for MAS."""

    # Multi-turn conversation scenarios
    scenarios = [
        {
            "name": "fibonacci_conversation",
            "prompts": [
                {"sender": "human", "content": "@archon Write a fibonacci function"},
                {"sender": "human", "content": "@archon Now make it recursive"},
                {
                    "sender": "human",
                    "content": "@arbiter Review the code for correctness",
                },
            ],
            "agents": ["Archon", "Arbiter"],
            "criteria": "Archon generates and refines a fibonacci function, and Arbiter reviews it.",
        },
        {
            "name": "research_conversation",
            "prompts": [
                {
                    "sender": "human",
                    "content": "@oracle Research Python async programming",
                },
                {"sender": "human", "content": "@oracle Focus specifically on asyncio"},
                {
                    "sender": "human",
                    "content": "@archon Summarize the findings from the oracle",
                },
            ],
            "agents": ["Oracle", "Archon"],
            "criteria": "Oracle researches a topic, and Archon summarizes the findings.",
        },
    ]

    tests = []
    selected_scenarios = (
        scenarios if size is None else random.choices(scenarios, k=size)
    )

    for scenario_data in selected_scenarios:
        initial_prompts = [
            {
                "sender": prompt["sender"],
                "channel": "general",
                "content": prompt["content"],
            }
            for prompt in scenario_data["prompts"]
        ]
        tests.append(
            _sample_mas_scenario(
                name=scenario_data["name"],
                initial_prompts=initial_prompts,
                agents_to_deploy=scenario_data["agents"],
                criteria=scenario_data["criteria"],
                timeout=180,  # Longer timeout for conversations
            )
        )
    return tests


def integrity(size: Optional[int] = None) -> List[Dict[str, Any]]:
    return []


def reasoning(size: Optional[int] = None) -> List[Dict[str, Any]]:
    """Basic reasoning from knowledge - no tools needed, adapted for MAS."""

    questions = [
        ("What is 2 + 2?", "4"),
        ("What is 15 * 7?", "105"),
        ("What's the capital of France?", "Paris"),
        ("What year did World War II end?", "1945"),
        ("Who wrote Romeo and Juliet?", "William Shakespeare"),
        ("What is the square root of 64?", "8"),
        ("What's 25% of 200?", "50"),
        ("What comes after Thursday?", "Friday"),
    ]

    scenarios = []
    selected_questions = (
        questions if size is None else random.choices(questions, k=size)
    )

    for i, (question, expected_answer) in enumerate(selected_questions):
        scenario_name = f"reasoning_q{i+1}"
        initial_prompts = [
            {
                "sender": "human",
                "channel": "general",
                "content": f"@oracle {question}",
            }
        ]
        agents_to_deploy = ["Oracle"]
        criteria = f'The Oracle agent correctly answers "{expected_answer}" to the question "{question}" on the general channel.'
        timeout = 10  # Short timeout for simple questions

        scenarios.append(
            _sample_mas_scenario(
                name=scenario_name,
                initial_prompts=initial_prompts,
                agents_to_deploy=agents_to_deploy,
                criteria=criteria,
                timeout=timeout,
            )
        )
    return scenarios


def research(size: Optional[int] = None) -> List[Dict[str, Any]]:
    return []


def security(size: Optional[int] = None) -> List[Dict[str, Any]]:
    return []
