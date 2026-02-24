# main.py

from Python.langgraph.graph import compiled_graph


def main():
    user_input = input("Enter your daily work update:\n> ")

    initial_state = {
        "user_input": user_input,
        "summary": "",
        "email_text": "",
        "evaluation": "",
        "logs": [],
        "reflection": ""
    }

    final_state = compiled_graph.invoke(initial_state)

    print("\n===== FINAL OUTPUT =====\n")
    print("📌 Professional Summary:\n", final_state["summary"])
    print("\n📧 Email Draft:\n", final_state["email_text"])
    print("\n🧪 Evaluation:\n", final_state["evaluation"])
    print("\n🪞 Reflection:\n", final_state["reflection"])


if __name__ == "__main__":
    main()
