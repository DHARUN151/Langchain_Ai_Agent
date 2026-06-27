import ast
import csv
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[2]


def read_text_file(path: str) -> str:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / path
    if not candidate.exists():
        return f"File not found: {path}"
    return candidate.read_text(encoding="utf-8")


def write_text_file(path: str, content: str) -> str:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / path
    candidate.parent.mkdir(parents=True, exist_ok=True)
    candidate.write_text(content, encoding="utf-8")
    return f"Wrote file: {candidate}"


def calculate_math(expression: str) -> str:
    safe_expression = re.sub(r"[^0-9.+\-*/^()\s]", "", expression)
    if not safe_expression:
        return "No valid math expression found."
    try:
        tree = ast.parse(safe_expression, mode="eval")
        allowed_nodes = (
            ast.Expression,
            ast.BinOp,
            ast.UnaryOp,
            ast.Num,
            ast.Add,
            ast.Sub,
            ast.Mult,
            ast.Div,
            ast.Pow,
            ast.USub,
            ast.UAdd,
        )
        for node in ast.walk(tree):
            if not isinstance(node, allowed_nodes):
                raise ValueError("Unsupported expression")
        result = eval(compile(tree, "<math>", "eval"), {"__builtins__": {}}, {})
        return f"Result: {result}"
    except Exception as exc:
        return f"Math evaluation failed: {exc}"


def analyze_csv(path: str) -> str:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / path
    if not candidate.exists():
        return f"CSV file not found: {path}"
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        rows = list(reader)
    if not rows:
        return "The CSV is empty."
    header = rows[0]
    data_rows = rows[1:]
    return f"CSV loaded with {len(data_rows)} rows and columns: {', '.join(header)}"


def call_api(url: str) -> str:
    try:
        response = requests.get(url, timeout=10)
        snippet = response.text[:400].replace("\n", " ")
        return f"Status {response.status_code}: {snippet}"
    except Exception as exc:
        return f"API request failed: {exc}"


def execute_python_code(code: str) -> str:
    try:
        result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=20, cwd=str(ROOT))
        output = result.stdout.strip() or result.stderr.strip() or "No output"
        return f"Exit code {result.returncode}: {output}"
    except Exception as exc:
        return f"Code execution failed: {exc}"


def search_web(query: str) -> str:
    try:
        response = requests.get("https://duckduckgo.com/html/", params={"q": query}, timeout=10)
        matches = re.findall(r'<a rel="nofollow" class="result__a" href="(.*?)">(.*?)</a>', response.text)
        if matches:
            title, snippet = matches[0]
            return f"Result: {re.sub('<.*?>', '', title)}\n{re.sub('<.*?>', '', snippet)}"
        return f"Search request completed for: {query}"
    except Exception as exc:
        return f"Web search failed: {exc}"
