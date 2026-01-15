# Python/test_email_agent.py
from Python.agents.summarizer import SummarizerAgent
from Python.agents.email_agent import EmailAgent

# Step 1: Sample work log
worklog = """
Completed feature engineering for sales data,
fixed pipeline bugs,
met with stakeholders,
and prepared slides for tomorrow.
"""

# Step 2: Summarize
summarizer = SummarizerAgent()
summary = summarizer.run(worklog)

# Step 3: Generate Email
email_agent = EmailAgent()
email_text = email_agent.run(summary)

print("=== SUMMARY ===")
print(summary)
print("\n=== EMAIL ===")
print(email_text)