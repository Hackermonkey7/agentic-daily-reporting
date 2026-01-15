from Python.agents.summarizer import SummarizerAgent

def main():
    s = SummarizerAgent()

    text = """
    Large language models are neural networks trained on vast corpora of text.
    They are capable of reasoning, summarization, and generation tasks.
    """

    # CALL the correct method
    summary = s.run(text)
    print("\nSUMMARY:\n", summary)

if __name__ == "__main__":
    main()


