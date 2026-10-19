import configparser
import json
import mimetypes
import os
import shutil
import subprocess
import sys
from openai import OpenAI

sys.stdout.reconfigure(encoding="utf-8")

cfg = configparser.ConfigParser()
cfg.read("config.ini", encoding="utf-8")
s = cfg["llm"]
client = OpenAI(base_url=s["base_url"], api_key=s["api_key"])


def getDate():
    out = subprocess.run("date /t & time /t", shell=True, capture_output=True, text=True)
    return out.stdout.strip()


def isLeapYear(year):
    return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0


def getcwd():
    return os.getcwd()


def list_dir(path):
    lines = []
    for e in sorted(os.listdir(path)):
        full = os.path.join(path, e)
        lines.append(("[DIR] " if os.path.isdir(full) else "[FILE] ") + e)
    return "\n".join(lines) or "(empty)"


def get_file_type(path):
    mime, _ = mimetypes.guess_type(path)
    ext = os.path.splitext(path)[1] or "(no extension)"
    return f"extension: {ext}, mime: {mime or 'unknown'}"


def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        return "error: not a plain text file"


def create_file(directory, filename):
    path = os.path.join(directory, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write("")
    return f"created: {path}"


def edit_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"saved: {path}"


def mkdir(path):
    os.makedirs(path, exist_ok=True)
    return f"created dir: {path}"


def delete_dir(path):
    shutil.rmtree(path)
    return f"deleted dir: {path}"


def delete_file(path):
    os.remove(path)
    return f"deleted file: {path}"


def rename(path, new_name):
    if os.path.dirname(new_name):
        new_path = new_name
    else:
        new_path = os.path.join(os.path.dirname(path), new_name)
    os.rename(path, new_path)
    return f"renamed: {path} -> {new_path}"


TOOLS = [
    ("getDate", "获取当前电脑的日期和时间", {"type": "object", "properties": {}}),
    ("isLeapYear", "判断指定年份是否是闰年",
     {"type": "object", "properties": {"year": {"type": "integer"}}, "required": ["year"]}),
    ("getcwd", "获取当前工作目录", {"type": "object", "properties": {}}),
    ("list_dir", "列出指定目录下所有文件和子目录",
     {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}),
    ("get_file_type", "获取指定文件的文件类型（扩展名和MIME类型）",
     {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}),
    ("read_file", "获取指定纯文本文件的内容",
     {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}),
    ("create_file", "根据指定的目录和文件名创建新文件",
     {"type": "object", "properties": {"directory": {"type": "string"},
                                        "filename": {"type": "string"}},
      "required": ["directory", "filename"]}),
    ("edit_file", "编辑指定纯文本文件的内容（整体覆盖写入）",
     {"type": "object", "properties": {"path": {"type": "string"},
                                        "content": {"type": "string"}},
      "required": ["path", "content"]}),
    ("mkdir", "创建新目录",
     {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}),
    ("delete_dir", "删除目录（含非空目录及其所有内容）",
     {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}),
    ("delete_file", "删除文件",
     {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}),
    ("rename", "重命名文件或目录（new_name为新名字，也可为新路径）",
     {"type": "object", "properties": {"path": {"type": "string"},
                                        "new_name": {"type": "string"}},
      "required": ["path", "new_name"]}),
]

tools = [{"type": "function",
          "function": {"name": n, "description": d, "parameters": p}}
         for n, d, p in TOOLS]
handlers = {n: globals()[n] for n, _, _ in TOOLS}

while True:
    prompt = input("please input your prompt:")
    print("---")
    messages = [{"role": "user", "content": prompt}]
    while True:
        resp = client.chat.completions.create(
            model=s["model"], messages=messages, tools=tools)
        msg = resp.choices[0].message
        if not msg.tool_calls:
            print(msg.content)
            break
        messages.append(msg)
        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments or "{}")
            try:
                result = str(handlers[tc.function.name](**args))
            except Exception as e:
                result = f"error: {e}"
            print(f"[{tc.function.name}] {result[:200]}")
            messages.append({"role": "tool", "tool_call_id": tc.id,
                             "content": result})
