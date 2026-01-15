# Python/tests/test_evaluator_agent.py
from Python.agents.summarizer import SummarizerAgent
from Python.agents.email_agent import EmailAgent
from Python.agents.evaluator import EvaluatorAgent

worklog = """
Completed feature engineering for sales data,
fixed pipeline bugs,
met with stakeholders,
and prepared slides for tomorrow.
"""

# Summarize
summarizer = SummarizerAgent()
summary = summarizer.run(worklog)

# Generate Email
email_agent = EmailAgent()
email_text = email_agent.run(summary)

# Evaluate Email
evaluator = EvaluatorAgent()
evaluation = evaluator.run(email_text)

print("=== EMAIL ===")
print(email_text)
print("\n=== EVALUATION ===")
print(evaluation)
