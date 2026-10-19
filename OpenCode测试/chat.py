from configparser import ConfigParser
from openai import OpenAI

c = ConfigParser()
c.read("config.ini", encoding="utf-8")
s = c["llm"]
client = OpenAI(base_url=s["base_url"], api_key=s["api_key"])

history = []
while True:
    prompt = input("please input your prompt:")
    print("---")
    history.append({"role": "user", "content": prompt})
    stream = client.chat.completions.create(
        model=s["model"],
        messages=history,
        stream=True,
    )
    reply = ""
    for chunk in stream:
        if delta := chunk.choices[0].delta.content:
            reply += delta
            print(delta, end="", flush=True)
    print()
    history.append({"role": "assistant", "content": reply})
