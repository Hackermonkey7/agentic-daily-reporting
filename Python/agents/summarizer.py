from Python.llm_client import OllamaClient

class SummarizerAgent:
    """
    Agent responsible for summarizing daily work logs
    """

    def __init__(self, model: str = "llama3.1"):
        self.client = OllamaClient(model=model)

    def run(self, user_worklog: str) -> str:
        system_prompt = ("""
You are a professional workplace assistant.

Your task:
- Convert raw, informal task updates into a concise, professional summary
- Maintain a neutral, corporate tone
- Avoid adding information not present in the input

Rules:
- Output should be 2 or 3 sentences
- Do NOT use bullet points
- Do NOT include opinions or suggestions
"""
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

