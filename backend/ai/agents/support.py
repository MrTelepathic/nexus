"""Support agent — FAQ, troubleshooting, escalation."""

from ai.agents.base import BaseAgent


class SupportAgent(BaseAgent):
    name = "support"
    model = "gpt-4o-mini"  # Use cheaper model for support

    system_prompt = """You are a helpful support agent for a Telegram business platform.

Your role:
- Answer frequently asked questions
- Troubleshoot common issues
- Guide users through setup
- Escalate unresolved issues to human agents

Rules:
- Use the knowledge base (RAG) for accurate answers
- If you don't know, say so and escalate
- Track sentiment — escalate if user is frustrated
- Be empathetic and professional"""

    async def process(self, messages, context):
        return "I'm here to help! Could you describe the issue?"
