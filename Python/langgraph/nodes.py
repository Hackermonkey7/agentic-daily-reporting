from Python.agents.summarizer import SummarizerAgent
from Python.agents.email_agent import EmailAgent
from Python.agents.evaluator import EvaluatorAgent
from Python.agents.logger import LoggingAgent
from Python.agents.reflection_agent import ReflectionAgent
class SummarizerNode:
    def __init__(self, model="llama3.1"):
        self.agent = SummarizerAgent(model=model)

    def run(self, input_text):
        return self.agent.run(input_text)


class EmailNode:
    def __init__(self, model="llama3.1"):
        self.agent = EmailAgent(model=model)

    def run(self, summary_text):
        return self.agent.run(summary_text)


class EvaluatorNode:
    def __init__(self, model="phi3"):
        self.agent = EvaluatorAgent(model=model)

    def run(self, email_text):
        return self.agent.run(email_text)


class LoggerNode:
    def __init__(self, db_path="db/logs.db"):
        self.agent = LoggingAgent(db_path=db_path)

    def log(self, agent_name, input_data, output_data):
        self.agent.log_step(agent_name, input_data, output_data)
        
class ReflectionNode:
    def __init__(self, model="phi3", db_path="db/logs.db"):
        self.agent = ReflectionAgent(model=model)
        self.logger = LoggingAgent(db_path=db_path)

    def run(self, logs):
        reflection_text = self.agent.reflect(logs)
        self.logger.log_step(
            agent_name="ReflectionNode",
            input_data=str(logs),
            output_data=reflection_text
        )
        return reflection_text