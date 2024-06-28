from typing import Dict, Tuple, List
import json
from agents.agent import Agent

prompt_template = """

You're a manager in a team of optimization experts. The goal of the team is to solve an optimization problem. Your task is to choose the next expert to work on the problem based on the current situation.
- The user has already given us the problem description, the objective function, and the parameters. Only call the user proxy if there is a problem or something ambiguous or missing.

Here's the list of agents in your team:
-----
{agents}
-----

And here's the history of the conversation so far:
-----
{history}
-----


Considering the history, if you think the problem is solved, type DONE. Otherwise, generate a json file with the following format:
{{
    "agent_name": "Name of the agent you want to call next",
    "task": "The task you want the agent to carry out"
}}

to identify the next agent to work on the problem, and also the task it has to carry out.
- If the objective function is not formulated then call the formulator first, then programmer then evaluator.
- If there is a runtime error, ask the the programmer agent to fix it.
- Only generate the json file, and don't generate any other text.
- If the latest message in history says that the code is fixed, ask the evaluator agent to evaluate the code!

"""

class GroupChatManager(Agent):
    def __init__(
        self, agents: List[Agent], max_rounds: int = 12, **kwargs
    ):
        super().__init__(
            name="GroupChatManager",
            description="This is a manager agent that chooses which agent to work on the problem next and organizes the conversation within its team.",
            **kwargs,
        )

        self.agents = agents
        self.conversation_state = {
            "round": 0,
        }
        self.max_rounds = max_rounds
        self.history = []


    def solve(self, state: Dict) -> Tuple[str, Dict]:
        self.history = []

        while True:
            if self.conversation_state["round"] >= self.max_rounds:
                return "The problem is not solved.", state

            print("=" * 20)
            print("=" * 20)
            print("Round", self.conversation_state["round"])

            agents_list = "".join(
                [
                    "-" + agent.name + ": " + agent.description + "\n"
                    for agent in self.agents
                ]
            )

            prompt = prompt_template.format(
                agents=agents_list,
                history="\n".join([json.dumps(item[0]) for item in self.history]),
            )

            cnt = 3
            while True and cnt > 0:
                try:
                    response = self.llm_call_vertexai(prompt=prompt)

                    decision = response.strip()
                    if "```json" in decision:
                        decision = decision.split("```json")[1].split("```")[0]
                    decision = decision.replace("\\", "")

                    if decision == "DONE":
                        print("DONE")
                        return "The problem is solved.", state
                    decision = json.loads(decision)
                    break

                except Exception as e:
                    print(response)
                    print(e)
                    cnt -= 1

                    print("Invalid decision. Trying again ...")
                    if cnt == 0:
                        import traceback

                        err = traceback.format_exc()
                        print(err)

            print(
                "---- History:\n",
                "\n".join([json.dumps(item[0]) for item in self.history]),
            )

            print(f"\n---- Decision:||{decision}||\n")

            if not decision["agent_name"] in [agent.name for agent in self.agents]:
                raise ValueError(
                    f"Decision {decision} is not a valid agent name. Please choose from {self.agents}"
                )
                
            else:
                agent = [
                    agent
                    for agent in self.agents
                    if agent.name == decision["agent_name"]
                ][0]

                message, new_state = agent.generate_reply(
                    task=decision["task"],
                    state=state,
                    sender=self,
                )

                with open(
                    f"{state['log_folder']}/log_{self.conversation_state['round']}.json",
                    "w",
                ) as f:
                    json.dump(state, f, indent=4)

                state = new_state

                decision["result"] = message
                self.history.append((decision, state))
                print("*"*10,"HISTORY","*"*10)
                

                with open(state["log_folder"] + "/selection_log.json", "w") as f:
                    json.dump([d for (d, s) in self.history], f, indent=4)

                if "code" in state:
                    with open(state["log_folder"] + "/code.py", "w") as f:
                        f.write(state["code"])

                self.conversation_state["round"] += 1