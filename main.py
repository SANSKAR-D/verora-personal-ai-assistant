from agent.graph import agent

def ask(question: str):
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    return result["messages"][-1].content

if __name__ == "__main__":
    question = "Here's my training log at C:/Users/seths/verora/train.log and my code at C:/Users/seths/verora/train.py. Why is my accuracy stuck? Read both files first."
    print(ask(question))