from Python.llm_client import OllamaClient 



class EmailAgent:
    """
    Agent responsible for converting a summary into a professional email.
    """

    def __init__(self, model: str = "llama3.1"):
        self.client = OllamaClient(model=model)

    def run(self, summary_text: str, recipient_name: str = "Manager") -> str:
        """
        Generates a professional email based on the summary.

        Args:
            summary_text (str): Text from SummarizerAgent
            recipient_name (str): Name/title of the recipient

        Returns:
            str: Fully written email text
        """
        system_prompt = (
            """You are a corporate communication assistant.

Your task:
- Convert the provided summary into a professional email update to a manager

Rules:
- Use a clear subject line
- Maintain a polite, professional tone
- Avoid slang or informal phrases
- Do NOT add new tasks or claims
- End with a polite closing

Format:
Subject: ...
Email body
"""
        )

        user_prompt = f"""
Recipient: {recipient_name}
Summary of daily work:
\"\"\"
{summary_text}
\"\"\"

Write a professional email to the recipient:
- Polite greeting
- Clear summary of completed work
- Short and concise
- No emojis
- Sign off politely
"""

        return self.client.generate(
            prompt=user_prompt,
            system=system_prompt,
            temperature=0.2
        )
