from langchain_ollama import ChatOllama
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatOllama(
    model=os.getenv("QWEN_3_5"),
    temperature=0,
    reasoning=False
)