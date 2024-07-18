import json

with open("/home/jiosaavn9/LLM_Agent_SCO/Modelv9/data/problem_4" + "/input.json", "r") as f:
    update = f.read()
update = json.loads(update, strict=False)
print(update)