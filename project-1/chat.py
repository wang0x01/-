import configparser
from openai import OpenAI

cfg = configparser.ConfigParser()
cfg.read("config.ini", encoding="utf-8")
s = cfg["llm"]
client = OpenAI(base_url=s["base_url"], api_key=s["api_key"])

prompt = input("please input your prompt:")
print("---")
print(client.chat.completions.create(
    model=s["model"],
    messages=[{"role": "user", "content": prompt}]
).choices[0].message.content)
