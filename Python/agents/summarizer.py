from Python.llm_client import OllamaClient

class SummarizerAgent:
    """
    Agent responsible for summarizing daily work logs
    """

    def __init__(self, model: str = "llama3.1"):
        self.client = OllamaClient(model=model)

    def run(self, user_worklog: str) -> str:
        system_prompt = (
            "You are a professional corporate assistant. "
            "Summarize the user's daily work in a concise, "
            "clear, professional tone suitable for a manager."
        )

        user_prompt = f"""
Daily work log:
\"\"\"
{user_worklog}
\"\"\"

Return:
- A short paragraph (4–6 lines)
- Professional tone
- No bullet points
"""

        return self.client.generate(
            prompt=user_prompt,
            system=system_prompt,
            temperature=0.2
        )

