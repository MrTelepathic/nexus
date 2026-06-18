"""AI Orchestrator — LangGraph multi-agent coordination.

Defines the agent graph:
  User Message → Router → [Sales | Support | Analyst | Moderator] → Response

Key design decisions:
- StateGraph for visual, debuggable agent flow
- Checkpointing for conversation recovery
- Human-in-the-loop for financial actions
- Loop prevention via max_iterations guard

SECURITY: Agent tools are allowlisted. Only registered tools can be called.
"""

from typing import Annotated, Literal, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages


# --- State definition ---
class AgentState(TypedDict):
    """Shared state across all agents."""

    messages: Annotated[list, add_messages]
    tenant_id: str
    user_id: int
    conversation_id: str
    current_agent: str
    iteration_count: int
    should_escalate: bool
    context: dict


# --- Agent nodes (stubs for MVP) ---
async def router_node(state: AgentState) -> dict:
    """Route to the appropriate agent based on message content.

    Uses simple keyword matching for MVP.
    In production: use LLM-based classification or embeddings.
    """
    last_message = state["messages"][-1].content if state["messages"] else ""

    # Simple routing rules (production: use LLM classifier)
    keywords = {
        "sales": ["buy", "purchase", "price", "order", "product", "subscribe"],
        "support": ["help", "issue", "problem", "bug", "error", "not working"],
        "analyst": ["stats", "analytics", "report", "data", "metrics"],
        "moderator": ["report", "abuse", "spam", "inappropriate"],
    }

    text_lower = str(last_message).lower()
    scores = {}
    for agent, words in keywords.items():
        scores[agent] = sum(1 for w in words if w in text_lower)

    # Default to support if no clear match
    best_agent = max(scores, key=scores.get) if any(scores.values()) else "support"

    return {
        "current_agent": best_agent,
        "iteration_count": state.get("iteration_count", 0) + 1,
    }


async def sales_agent(state: AgentState) -> dict:
    """Sales agent: product recommendations, order placement."""
    # TODO: Integrate with LLM + tools
    response = "I'd love to help you find the perfect plan! What are you looking for?"
    return {"messages": [{"role": "assistant", "content": response}]}


async def support_agent(state: AgentState) -> dict:
    """Support agent: FAQ, troubleshooting, escalation."""
    # TODO: RAG retrieval from knowledge base
    response = "I'm here to help! Could you describe the issue you're experiencing?"
    return {"messages": [{"role": "assistant", "content": response}]}


async def analyst_agent(state: AgentState) -> dict:
    """Analyst agent: data queries, report generation."""
    response = "Let me pull up those analytics for you. What time period are you interested in?"
    return {"messages": [{"role": "assistant", "content": response}]}


async def moderator_agent(state: AgentState) -> dict:
    """Moderator agent: content moderation, abuse detection."""
    response = "I've flagged this for review. Our team will look into it shortly."
    return {"messages": [{"role": "assistant", "content": response}], "should_escalate": True}


def should_continue(state: AgentState) -> Literal["end", "continue"]:
    """Guard: prevent infinite loops.

    Max 10 iterations per conversation turn.
    If exceeded, route to human escalation.
    """
    if state.get("iteration_count", 0) >= 10:
        return "end"
    if state.get("should_escalate"):
        return "end"
    return "continue"


def route_to_agent(state: AgentState) -> str:
    """Route to the selected agent node."""
    agent = state.get("current_agent", "support")
    return f"{agent}_agent"


# --- Build the graph ---
def create_orchestrator() -> StateGraph:
    """Create the LangGraph agent orchestration graph.

    Graph structure:
        START → router → [sales_agent | support_agent | analyst_agent | moderator_agent]
                       → (continue? → router | end)
    """
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("router", router_node)
    graph.add_node("sales_agent", sales_agent)
    graph.add_node("support_agent", support_agent)
    graph.add_node("analyst_agent", analyst_agent)
    graph.add_node("moderator_agent", moderator_agent)

    # Entry point
    graph.set_entry_point("router")

    # Router branches to agents
    graph.add_conditional_edges(
        "router",
        route_to_agent,
        {
            "sales_agent": "sales_agent",
            "support_agent": "support_agent",
            "analyst_agent": "analyst_agent",
            "moderator_agent": "moderator_agent",
        },
    )

    # All agents loop back to router (with guard)
    for agent in ["sales_agent", "support_agent", "analyst_agent", "moderator_agent"]:
        graph.add_conditional_edges(
            agent,
            should_continue,
            {
                "continue": "router",
                "end": END,
            },
        )

    return graph.compile(checkpointer=MemorySaver())


# Singleton orchestrator instance
orchestrator = create_orchestrator()


async def process_message(
    tenant_id: str,
    user_id: int,
    conversation_id: str,
    user_message: str,
) -> str:
    """Process a user message through the multi-agent orchestrator.

    Returns the final agent response text.
    """
    result = await orchestrator.ainvoke(
        {
            "messages": [{"role": "user", "content": user_message}],
            "tenant_id": tenant_id,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "current_agent": "",
            "iteration_count": 0,
            "should_escalate": False,
            "context": {},
        },
        config={"configurable": {"thread_id": conversation_id}},
    )

    # Extract the last assistant message
    messages = result.get("messages", [])
    for msg in reversed(messages):
        if hasattr(msg, "role") and msg.role == "assistant":
            return msg.content
        if isinstance(msg, dict) and msg.get("role") == "assistant":
            return msg.get("content", "")

    return "I'm sorry, I couldn't process your request. Let me connect you with a human agent."
