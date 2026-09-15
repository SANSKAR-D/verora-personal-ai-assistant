from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from tools.read_file import read_file
from tools.tail_log import tail_log

llm = ChatOllama(model="qwen3.5-verora")

agent = create_react_agent(
    model=llm,
    tools=[read_file, tail_log],
)