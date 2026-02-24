from Python.langgraph.graph import compiled_graph

def test_pipeline():
    result = compiled_graph.invoke({
        "user_input": "Completed feature engineering and prepared slides for the meeting.",
        "summary": "",
        "email_text": "",
        "evaluation": "",
        "logs": [],
        "reflection": ""
    })
    print("Final state:", result)
    print("Logs captured:")
    for log in result["logs"]:
        print(log)

if __name__ == "__main__":
    test_pipeline()

