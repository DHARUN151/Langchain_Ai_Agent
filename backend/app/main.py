import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.tools import (
    analyze_csv,
    calculate_math,
    call_api,
    execute_python_code,
    read_text_file,
    search_web,
    write_text_file,
)

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

app = FastAPI(title="LangChain AI Agent API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
MEMORY_FILE = DATA_DIR / "memory.json"


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


def load_memory() -> List[Dict[str, Any]]:
    if MEMORY_FILE.exists():
        try:
            return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
    return []


def save_memory(messages: List[Dict[str, Any]]) -> None:
    MEMORY_FILE.write_text(json.dumps(messages, indent=2), encoding="utf-8")


def should_clarify(message: str) -> bool:
    lowered = message.strip().lower()
    if not lowered:
        return True
    if len(lowered.split()) < 4:
        return True
    return lowered in {"help", "assist", "do something", "help me"}


def route_to_tool(message: str) -> str | None:
    lowered = message.lower()

    if "calculate" in lowered or "math" in lowered or any(ch in lowered for ch in "+-*/^"):
        try:
            expr = re.search(r"([0-9.+\-*/^()\s]+)", lowered)
            if expr:
                return calculate_math(expr.group(1))
        except Exception:
            return None

    if "read file" in lowered or "open file" in lowered or "read " in lowered and lowered.endswith(".txt"):
        path = lowered.replace("read file", "").replace("open file", "").strip()
        if path:
            return read_text_file(path)

    if "write file" in lowered or "create file" in lowered:
        parts = lowered.split("write file", 1)
        if len(parts) == 2:
            file_name = parts[1].strip().split()[0]
            return write_text_file(file_name, "Created by the assistant")

    if "analyze csv" in lowered or lowered.endswith(".csv"):
        path = lowered.replace("analyze csv", "").strip()
        return analyze_csv(path or "data/sample.csv")

    if "search web" in lowered or "search for" in lowered:
        query = lowered.replace("search web", "").replace("search for", "").strip()
        if query:
            return search_web(query)

    if "call api" in lowered or "fetch" in lowered and "http" in lowered:
        url = re.search(r"https?://\S+", lowered)
        if url:
            return call_api(url.group(0))

    if "execute" in lowered and "python" in lowered:
        code = lowered.split("python", 1)[1].strip()
        return execute_python_code(code)

    return None


def build_reply(message: str, history: List[Dict[str, Any]]) -> str:
    if should_clarify(message):
        return (
            "I can help with research, coding, file work, data analysis, and math. "
            "Could you share a bit more detail about what you want me to do?"
        )

    tool_result = route_to_tool(message)
    if tool_result is not None:
        return f"Tool outcome:\n{tool_result}"

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key or api_key == "your_openai_api_key_here":
        return (
            "OpenAI is not configured yet. Add your API key to the .env file to enable full agent responses. "
            f"I can still help by outlining a plan for: {message}"
        )

    try:
        llm = ChatOpenAI(model=os.getenv("MODEL_NAME", "gpt-4o-mini"), temperature=0.2, api_key=api_key)
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI agent. Interpret ambiguous requests, ask clarifying questions when needed, and use a concise, professional tone.",
                ),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}"),
            ]
        )
        chain = prompt | llm
        history_messages = []
        for item in history[-8:]:
            if item.get("role") == "user":
                history_messages.append(("human", item["content"]))
            elif item.get("role") == "assistant":
                history_messages.append(("ai", item["content"]))

        response = chain.invoke({"history": history_messages, "input": message})
        return response.content.strip()
    except Exception as exc:  # pragma: no cover
        return f"The agent hit an error: {exc}"


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    history = load_memory()
    history.append({"role": "user", "content": req.message})
    reply = build_reply(req.message, history)
    history.append({"role": "assistant", "content": reply})
    save_memory(history)
    return ChatResponse(reply=reply)
