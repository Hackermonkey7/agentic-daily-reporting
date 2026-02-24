from typing import TypedDict

from langgraph.graph import StateGraph, START, END

# Define shared state
class ReportState(TypedDict):
    user_input: str
    summary: str
    email_text: str
    evaluation: str
    logs: list       # stores intermediate node logs
    reflection: str  # optional field for future reflection suggestions

# Node functions live outside classes
def summarize_node(state: ReportState) -> dict:
    from Python.agents.summarizer import SummarizerAgent
    agent = SummarizerAgent()
    summary = agent.run(state["user_input"])
    # Log and store in shared state
    updated_logs = logger_node(state, "SummarizerNode", state["user_input"], summary)["logs"]
    return {"summary": summary, "logs": updated_logs}

def email_node(state: ReportState) -> dict:
    from Python.agents.email_agent import EmailAgent
    agent = EmailAgent()
    email_text = agent.run(state["summary"])
    # Log and store in shared state
    updated_logs = logger_node(state, "EmailNode", state["summary"], email_text)["logs"]
    return {"email_text": email_text, "logs": updated_logs}

def eval_node(state: ReportState) -> dict:
    from Python.agents.evaluator import EvaluatorAgent
    agent = EvaluatorAgent()
    evaluation = agent.run(state["email_text"])
    # Log and store in shared state
    updated_logs = logger_node(state, "EvaluatorNode", state["email_text"], evaluation)["logs"]
    return {"evaluation": evaluation, "logs": updated_logs}

def logger_node(state: ReportState, agent_name: str, input_data: str, output_data: str) -> dict:
    from Python.agents.logger import LoggingAgent
    logger = LoggingAgent(db_path="db/logs.db")
    logger.log_step(agent_name, input_data, output_data)

    # Append to in-memory log
    if "logs" not in state or state["logs"] is None:
        state["logs"] = []
    state["logs"].append({
        "agent": agent_name,
        "input": input_data,
        "output": output_data
    })

    return {"logs": state["logs"]}

def reflection_node(state: ReportState) -> dict:
    """
    Node function to integrate ReflectionAgent into LangGraph.
    Args:
        state (ReportState): shared memory containing 'logs'
    Returns:
        dict: updated state with 'reflection' key populated
    """
    from Python.agents.reflection_agent import ReflectionAgent
    from Python.agents.logger import LoggingAgent

    # Initialize ReflectionAgent
    agent = ReflectionAgent(model="phi3")
    reflection_text = agent.reflect(state.get("logs", []))

    # Log reflection to SQLite via LoggingAgent
    logger = LoggingAgent(db_path="db/logs.db")
    logger.log_step(
        agent_name="ReflectionNode",
        input_data=str(state.get("logs", [])),
        output_data=reflection_text
    )

    # Update shared memory
    state["reflection"] = reflection_text

    return {"reflection": reflection_text, "logs": state.get("logs", [])}



# Build the graph
builder = StateGraph(ReportState)

# 1️⃣ Add nodes
builder.add_node("summarize", summarize_node)
builder.add_node("email", email_node)
builder.add_node("evaluate", eval_node)
builder.add_node("reflection", reflection_node)  # add reflection node BEFORE using in edges

# 2️⃣ Define sequence (edges)
builder.add_edge(START, "summarize")
builder.add_edge("summarize", "email")
builder.add_edge("email", "evaluate")
builder.add_edge("evaluate", "reflection")  # now this works
builder.add_edge("reflection", END)


# Compile
compiled_graph = builder.compile()
