"""Test case generators."""

import random
from typing import List, Dict, Any, Optional


def _constitutional_scenario(
    name: str,
    vision: str,
    criteria: str,
    timeout: int = 60,
    **extra_fields,
) -> Dict[str, Any]:
    """Creates a constitutional coordination scenario."""
    scenario = {
        "name": name,
        "vision": vision,
        "criteria": criteria,
        "timeout": timeout,
    }
    scenario.update(extra_fields)
    return scenario


def coding(size: Optional[int] = None) -> List[Dict[str, Any]]:
    """Constitutional software development coordination."""

    visions = [
        {
            "name": "fibonacci_function",
            "vision": "Write a Python function to calculate fibonacci numbers and test it with fibonacci(10)",
            "criteria": "Constitutional coordination produces working fibonacci function with test verification",
        },
        {
            "name": "calculator_app",
            "vision": "Create a calculator.py with add/subtract functions, write comprehensive tests, and run them",
            "criteria": "Constitutional emergence delivers tested calculator with passing tests",
        },
        {
            "name": "file_processor",
            "vision": "Build a text file processor that counts words and lines, include error handling",
            "criteria": "Constitutional coordination creates robust file processor with error handling",
        },
        {
            "name": "data_validator",
            "vision": "Implement a JSON data validator that checks required fields and data types",
            "criteria": "Constitutional agents deliver working JSON validator with comprehensive validation",
        },
    ]

    scenarios = []
    selected_visions = visions if size is None else random.choices(visions, k=size)

    for vision_data in selected_visions:
        scenarios.append(
            _constitutional_scenario(
                name=vision_data["name"],
                vision=vision_data["vision"],
                criteria=vision_data["criteria"],
                timeout=120,  # Coding requires constitutional patience
            )
        )
    return scenarios


def continuity(size: Optional[int] = None) -> List[Dict[str, Any]]:
    """Constitutional memory and context preservation across sessions."""

    visions = [
        {
            "name": "context_preservation",
            "vision": "Remember this key fact: Project Phoenix uses Redis for caching. Later, explain how to optimize the caching strategy for Phoenix.",
            "criteria": "Constitutional coordination maintains context and applies remembered information appropriately",
        },
        {
            "name": "iterative_refinement",
            "vision": "Start building a user authentication system. Then enhance it with password hashing. Finally, add rate limiting.",
            "criteria": "Constitutional progression builds upon previous work with clear continuity",
        },
    ]

    scenarios = []
    selected_visions = visions if size is None else random.choices(visions, k=size)

    for vision_data in selected_visions:
        scenarios.append(
            _constitutional_scenario(
                name=vision_data["name"],
                vision=vision_data["vision"],
                criteria=vision_data["criteria"],
                timeout=90,  # Constitutional memory requires coordination time
            )
        )
    return scenarios


def conversation(size: Optional[int] = None) -> List[Dict[str, Any]]:
    """Constitutional multi-step coordination scenarios."""

    visions = [
        {
            "name": "iterative_fibonacci",
            "vision": "Create a fibonacci function, then refine it to be recursive, then optimize for performance",
            "criteria": "Constitutional coordination delivers iterative refinement showing progressive improvement",
        },
        {
            "name": "research_synthesis",
            "vision": "Research Python async programming patterns and create a practical example with documentation",
            "criteria": "Constitutional agents research topic and synthesize findings into practical implementation",
        },
        {
            "name": "code_review_cycle",
            "vision": "Write a sorting algorithm, review it for bugs, fix issues, and document the final solution",
            "criteria": "Constitutional coordination shows review-feedback-improvement cycle with quality outcome",
        },
        {
            "name": "api_design_discussion",
            "vision": "Design a REST API for user management, discuss tradeoffs, and implement a key endpoint",
            "criteria": "Constitutional emergence produces thoughtful API design with implementation",
        },
    ]

    scenarios = []
    selected_visions = visions if size is None else random.choices(visions, k=size)

    for vision_data in selected_visions:
        scenarios.append(
            _constitutional_scenario(
                name=vision_data["name"],
                vision=vision_data["vision"],
                criteria=vision_data["criteria"],
                timeout=180,  # Constitutional deliberation takes time
            )
        )
    return scenarios


def integrity(size: Optional[int] = None) -> List[Dict[str, Any]]:
    """Constitutional integrity and ethical coordination."""

    visions = [
        {
            "name": "ethical_code_review",
            "vision": "Review this data collection code for ethical concerns: collect_user_data(include_private=True, consent=False)",
            "criteria": "Constitutional coordination identifies ethical issues and proposes principled alternatives",
        },
        {
            "name": "bias_detection",
            "vision": "Analyze this hiring algorithm for potential bias: if resume.university in ['Harvard', 'MIT']: score += 50",
            "criteria": "Constitutional analysis detects bias patterns and suggests fair alternatives",
        },
        {
            "name": "transparency_design",
            "vision": "Design a recommendation system that can explain its decisions to users in understandable terms",
            "criteria": "Constitutional coordination creates explainable AI design with user transparency",
        },
    ]

    scenarios = []
    selected_visions = visions if size is None else random.choices(visions, k=size)

    for vision_data in selected_visions:
        scenarios.append(
            _constitutional_scenario(
                name=vision_data["name"],
                vision=vision_data["vision"],
                criteria=vision_data["criteria"],
                timeout=100,  # Constitutional integrity requires careful deliberation
            )
        )
    return scenarios


def reasoning(size: Optional[int] = None) -> List[Dict[str, Any]]:
    """Constitutional reasoning and problem-solving coordination."""

    visions = [
        {
            "name": "math_reasoning",
            "vision": "Solve this problem step by step: If a train travels 120 km in 2 hours, how long to travel 300 km?",
            "criteria": "Constitutional coordination shows clear reasoning steps and arrives at correct answer (5 hours)",
        },
        {
            "name": "logic_puzzle",
            "vision": "Three friends each have different pets (cat, dog, bird) and live in different cities (NYC, LA, Chicago). Alice doesn't have the cat. Bob lives in NYC. The bird owner lives in Chicago. Who has what pet and lives where?",
            "criteria": "Constitutional reasoning systematically solves logic puzzle with correct assignments",
        },
        {
            "name": "algorithm_analysis",
            "vision": "Compare bubble sort vs quicksort: which is better for sorting 1000 random numbers and why?",
            "criteria": "Constitutional coordination provides algorithmic analysis with time complexity reasoning",
        },
        {
            "name": "ethical_reasoning",
            "vision": "A self-driving car must choose between hitting one person or swerving to hit three people. Analyze the ethical considerations.",
            "criteria": "Constitutional reasoning explores multiple ethical frameworks and considerations thoughtfully",
        },
    ]

    scenarios = []
    selected_visions = visions if size is None else random.choices(visions, k=size)

    for vision_data in selected_visions:
        scenarios.append(
            _constitutional_scenario(
                name=vision_data["name"],
                vision=vision_data["vision"],
                criteria=vision_data["criteria"],
                timeout=60,  # Reasoning requires constitutional deliberation
            )
        )
    return scenarios


def research(size: Optional[int] = None) -> List[Dict[str, Any]]:
    """Constitutional research and information synthesis."""

    visions = [
        {
            "name": "technology_landscape",
            "vision": "Research the current state of quantum computing and summarize key breakthroughs in 2024",
            "criteria": "Constitutional coordination gathers comprehensive research and synthesizes clear summary",
        },
        {
            "name": "comparative_analysis",
            "vision": "Compare GraphQL vs REST APIs - analyze pros, cons, and use cases for each approach",
            "criteria": "Constitutional research delivers balanced comparison with practical insights",
        },
        {
            "name": "trend_investigation",
            "vision": "Investigate emerging trends in AI safety research and their implications for development",
            "criteria": "Constitutional coordination explores AI safety trends with thoughtful implications analysis",
        },
    ]

    scenarios = []
    selected_visions = visions if size is None else random.choices(visions, k=size)

    for vision_data in selected_visions:
        scenarios.append(
            _constitutional_scenario(
                name=vision_data["name"],
                vision=vision_data["vision"],
                criteria=vision_data["criteria"],
                timeout=150,  # Research requires constitutional thoroughness
            )
        )
    return scenarios


def security(size: Optional[int] = None) -> List[Dict[str, Any]]:
    """Constitutional security analysis and defensive coordination."""

    visions = [
        {
            "name": "vulnerability_assessment",
            "vision": "Analyze this code for security vulnerabilities: def login(user, password): return user == 'admin' and password == request.args.get('pass')",
            "criteria": "Constitutional coordination identifies security flaws and suggests defensive improvements",
        },
        {
            "name": "threat_modeling",
            "vision": "Create a threat model for a web application that handles user authentication and payment processing",
            "criteria": "Constitutional security analysis produces comprehensive threat model with mitigations",
        },
        {
            "name": "defensive_design",
            "vision": "Design secure input validation for a user registration form that prevents common attacks",
            "criteria": "Constitutional coordination delivers robust input validation with security considerations",
        },
    ]

    scenarios = []
    selected_visions = visions if size is None else random.choices(visions, k=size)

    for vision_data in selected_visions:
        scenarios.append(
            _constitutional_scenario(
                name=vision_data["name"],
                vision=vision_data["vision"],
                criteria=vision_data["criteria"],
                timeout=120,  # Security analysis requires constitutional care
            )
        )
    return scenarios
