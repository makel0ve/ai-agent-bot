import asyncio
import json
import time

from app.agent.loop import agent_loop
from app.database import async_session
from app.llm.factory import get_llm_provider
from app.repositories.conversation import create_conversation
from app.repositories.user import get_user
from app.tools.setup import create_registry


async def run_scenario(scenario: dict, llm_provider, session) -> dict:
    first_tool_call = None
    first_tool_args = {}
    steps = 0
    success = True

    start = time.monotonic()

    user = await get_user(session=session, telegram_id=123456)
    conversation = await create_conversation(session=session, user_id=user.id)
    registy = create_registry(session=session, user_id=user.id)

    async for event in agent_loop(
        session=session,
        user_message=scenario["input"],
        conversation_id=conversation.id,
        llm_provider=llm_provider,
        registry=registy,
    ):
        if event.type == "tool_call" and first_tool_call is None:
            first_tool_call = event.data["name"]
            first_tool_args = event.data["arguments"]
            steps += 1

        if event.type == "error":
            success = False

        if event.type == "chat_stream":
            steps += 1

    await session.commit()

    elapsed = time.monotonic() - start

    return {
        "input": scenario["input"],
        "expected_tool": scenario.get("expected_tool"),
        "actual_tool": first_tool_call,
        "expected_args": scenario.get("expected_args_contain", {}),
        "actual_args": first_tool_args,
        "steps": steps,
        "latency": elapsed,
        "success": success,
    }


async def evaluate_provider(provider_name: str, scenarios: list) -> dict:
    results = []

    async with async_session() as session:
        for scenario in scenarios:
            result = await run_scenario(
                scenario=scenario,
                llm_provider=get_llm_provider(provider_name=provider_name),
                session=session,
            )

            results.append(result)

    total = len(results)

    tool_correct = sum(1 for r in results if r["expected_tool"] == r["actual_tool"])

    args_correct = sum(
        1
        for r in results
        if all(r["actual_args"].get(k) == v for k, v in r["expected_args"].items())
        if r["expected_args"]
    )

    avg_latency = sum(r["latency"] for r in results) / total

    return {
        "provider": provider_name,
        "total": total,
        "tool_selection_accuracy": round(tool_correct / total * 100, 1),
        "argument_accuracy": round(args_correct / total * 100, 1),
        "avg_latency": round(avg_latency, 2),
        "results": results,
    }


def write_results(provider_data: dict):
    provider = provider_data["provider"]

    with open(f"eval/results_{provider}.md", "w", encoding="utf-8") as f:
        f.write(f"# Eval Results: {provider}\n\n")
        f.write(f"- Total scenarios: {provider_data['total']}\n")
        f.write(
            f"- Tool selection accuracy: {provider_data['tool_selection_accuracy']}%\n"
        )
        f.write(f"- Argument accuracy: {provider_data['argument_accuracy']}%\n")
        f.write(f"- Avg latency: {provider_data['avg_latency']}s\n\n")

        f.write("## Детали\n\n")
        f.write("| Input | Expected | Actual | Latency |\n")
        f.write("|-------|----------|--------|---------|\n")

        for r in provider_data["results"]:
            f.write(
                f"| {r['input'][:50]} | {r['expected_tool'] or 'none'} | {r['actual_tool'] or 'none'} | {round(r['latency'], 2)}s |\n"
            )


async def main():
    with open("eval/scenarios.json") as f:
        scenarios = json.load(f)

    providers = [
        # "gigachat",
        # "yandexgpt",
        "ollama",
    ]

    for provider_name in providers:
        results = await evaluate_provider(provider_name, scenarios)
        write_results(provider_data=results)


if __name__ == "__main__":
    asyncio.run(main())
