import json

with open("/home/ckushj/LLM_Agent_SCO/Modelv8/data/problem_4" + "/input.json", "r") as f:
    update = f.read()
update = json.loads(update, strict=False)
print(update)