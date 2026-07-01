import os
import sys
import json
from models.model_client import get_client_and_model
from mcp_impl.bridge import mcp_session, discover_openai_tools, call_mcp_tool
from agent_graph.state import DevPulseState

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

client, MODEL, BACKEND = get_client_and_model()

PERSONA = (
    "You are the Documentation Agent. Use get_documentation_audit to inspect the README file, "
    "identify missing crucial sections (Installation, Usage, Contributing, License), and suggest specific README improvements."
)

ALLOWED_TOOLS = {"get_documentation_audit"}

async def run(state: DevPulseState) -> DevPulseState:
    async with mcp_session() as session:
        all_tools = await discover_openai_tools(session)
        scoped_tools = [t for t in all_tools if t["function"]["name"] in ALLOWED_TOOLS]

        context_str = f" The active repository in focus is: {state['current_repo']}" if state.get('current_repo') else ""
        system_prompt = PERSONA + context_str

        messages = [{"role": "system", "content": system_prompt}] + state["history"] + [
            {"role": "user", "content": state["query"]}
        ]

        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=scoped_tools, tool_choice="auto"
        )
        msg = response.choices[0].message

        if response.choices[0].finish_reason == "tool_calls" and msg.tool_calls:
            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments)
                if "owner" not in args or "repo" not in args:
                    if state.get("current_repo") and "/" in state["current_repo"]:
                        owner, repo = state["current_repo"].split("/", 1)
                        if "owner" not in args:
                            args["owner"] = owner
                        if "repo" not in args:
                            args["repo"] = repo
                
                print(f" [documentation_agent] executing tool: {tc.function.name}({args})")
                tool_result = await call_mcp_tool(session, tc.function.name, args)
                state["tool_calls_made"].append(
                    {"tool": tc.function.name, "result": tool_result}
                )

            follow_up = (
                messages
                + [
                    {
                        "role": "assistant",
                        "content": msg.content,
                        "tool_calls": [tc.model_dump() for tc in msg.tool_calls],
                    }
                ]
                + [
                    {"role": "tool", "tool_call_id": tc.id, "content": call["result"]}
                    for tc, call in zip(
                        msg.tool_calls, state["tool_calls_made"][-len(msg.tool_calls):]
                    )
                ]
            )

            final = client.chat.completions.create(model=MODEL, messages=follow_up)
            state["answer"] = final.choices[0].message.content
        else:
            state["answer"] = msg.content

    return state
