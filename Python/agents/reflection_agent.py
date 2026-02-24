# agents/reflection_agent.py

from Python.agents.logger import LoggingAgent
from Python.llm_client import Phi3Client  # your existing LLM wrapper for Phi-3

class ReflectionAgent:
    """
    Agent that looks at shared logs and provides constructive feedback.
    """
    def __init__(self, model: str = "phi3"):
        self.model = model
        self.client = Phi3Client(model=self.model)

    def reflect(self, logs: list) -> str:
        """
        Generate reflection feedback from logs.
        Args:
            logs (list): List of dicts with keys: agent, input, output
        Returns:
            str: Reflection suggestions
        """
        prompt = "You are a professional reflection agent. Review the following logs and suggest improvements:\n\n"
        for log in logs:
            prompt += f"Agent: {log['agent']}\nInput: {log['input']}\nOutput: {log['output']}\n\n"
        prompt += "Provide concise, actionable, professional suggestions for each step."

        return self.client.run(prompt)
