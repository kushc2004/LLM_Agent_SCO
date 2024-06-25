from typing import Dict, Tuple
from agents.agent import Agent
import json
import traceback
import re
import ast

main_prompt_templates = [
    """
You're an expert evaluator in a team of optimization experts. The goal of the team is to solve an optimization problem. Your responsibility is to run the code and evaluate the performance and correctness of the code.
"""
]


prep_code = """
import json
import numpy as np
import math

{solver_prep_code}



"""

post_code = """

# Get model status
status = model.status

obj_val = None
# check whether the model is infeasible, has infinite solutions, or has an optimal solution
if status == gp.GRB.INFEASIBLE:
    obj_val = "infeasible"
elif status == gp.GRB.INF_OR_UNBD:
    obj_val = "infeasible or unbounded"
elif status == gp.GRB.UNBOUNDED:
    obj_val = "unbounded"
elif status == gp.GRB.OPTIMAL:
    obj_val = model.objVal
    print("The optimal solution is", obj_val)
"""


class Evaluator(Agent):
    def __init__(self, client: None, solver="gurobipy", **kwargs):
        super().__init__(
            name="Evaluator",
            description="This is an evaluator agent that is an expert in running optimization codes, identifying the bugs and errors, ane evaluating the performance and correctness of the code.",
            client=client,
            **kwargs,
        )
        self.solver = solver

    def generate_reply(self, task: str, state: Dict, sender: Agent) -> Tuple[str, Dict]:
        print("- Evaluator agent is called!")

        res = self._run_code(state=state)

        if not res["success"]:
            state["solution_status"] = "runtime_error"
            state["error_message"] = res["error_message"]
            state["prep_code"] = prep_code.format(
                solver_prep_code=self.get_solver_prep_code(),
            )

            if not res["bogus_context"]:
                return f"Bad model! Print DONE to finish the execution.", state

            res["bogus_context"]["status"] = "runtime_error"
            
            state["solver_output_status"] = res["bogus_context"]["status"]

            return (
                f"There was an error in running the code! {res['error_message']}",
                state,
            )

        else:
            state["solution_status"] = "solved"
            state["solver_output_status"] = res["status"]
            state["obj_val"] = res["obj_val"]
            state["code"] = res["code"]
            return ("Evaluation Done! The problem is solved.", state)
    
    def take_input(self, p):
        print(f""" Defintion: {p["definition"]} \n
                        Symbol: {p["symbol"]} \n
                        Shape: {p["shape"]}""")
        
        if len(p["shape"]) == 0:
            result_list = int(input("Enter Value: "))
            return result_list
        
        else: 
            input_string = input("Enter Value in Matrix(List) form: ")
            t=1
            while (t>0):
                try:
                    # Evaluate the input string as a Python expression
                    result_list = ast.literal_eval(input_string)
                    # Check if the input is a valid list
                    if isinstance(result_list, list):
                        t=0
                        return result_list
                    else:
                        print("The input is not a valid, Try again...")
                        return None
                except (ValueError, SyntaxError):
                    print("Invalid input format. Try again...")
                    return None
                
    def get_parameter_data(self, state: Dict):
        print("="*20)
        print("Enter the values of parameters: \n")

        param = state["parameters"]
        for i in param:
            val = self.take_input(i)
            i["value"] = val


    def _run_code(self, state: Dict):
        local_env = {}
        code = ""
        last_line = ""
        bogus_context = None

        try:
            last_line = prep_code.format(
                solver_prep_code=self.get_solver_prep_code(),
            )
            code += last_line + "\n"
            

            exec(
                last_line,
                local_env,
                local_env,
            )

            self.get_parameter_data(state=state)
            param = state["parameters"]
            for i in param:
                print(i)
                symb = re.search(r'\{(.*?)\}', i["symbol"])
                print(symb)
                symb = symb.group(1)

                last_line = f"{symb} = {i["value"]}"
                code += last_line + "\n"
                exec(last_line, local_env, local_env)



            #GET PARAMETER DATA FROM DATA.JSON FILE
            # with open(state["path"] + "/data.json", "r") as f:
            #     data = f.read()
            # data = json.loads(data)
            # for i in data:
            #     param = re.search(r'\{(.*?)\}', i)
            #     param = param.group(1)
            #     last_line = f"{param} = {data[i]}"
            #     code += last_line + "\n"
            #     exec(last_line, local_env, local_env)

            # for parameter in state["parameters"]:
            #     if not "code" in parameter:
            #         raise Exception(f"Parameter {parameter} is not coded yet!")
            #     last_line = parameter["code"]
            #     code += last_line + "\n"
            #     exec(last_line, local_env, local_env)

            # last_line = f"\n# Define model\nmodel = gp.Model('model')\n"
            # code += last_line + "\n"
            # exec(last_line, local_env, local_env)

            for variable in state["variables"]:
                bogus_context = variable
                last_line = variable["code"]
                code += last_line + "\n"
                exec(last_line, local_env, local_env)
                

            print("\nExecuting Constraints......\n")

            for constraint in state["constraints"]:
                print("got constraint")
                bogus_context = constraint
                last_line = constraint["code"]

                print("\nLast Line:\n", last_line)
                code += "\n" + last_line + "\n"
                exec(last_line, local_env, local_env)

            print("\nExecuting Objective......\n")

            bogus_context = state["objective"][0]
            last_line = state["objective"][0]["code"]
            print(last_line)
            code += "\n" + last_line + "\n"
            exec(last_line, local_env, local_env)

            bogus_context = "OPTIMIZATION CALL"
            last_line = f"\n# Optimize model\nmodel.optimize()\n"
            code += last_line + "\n"
            exec(last_line, local_env, local_env)

            bogus_context = None
            last_line = post_code
            code += last_line + "\n"
            exec(last_line, local_env, local_env)

            return {
                "success": True,
                "error_line": None,
                "code": code,
                "obj_val": local_env["obj_val"],
                "status": local_env["status"],
                "error_message": None,
            }

        except Exception as e:
            # print(local_env)
            print("COOOODE")
            print(code)
            print()
            if not bogus_context:
                error_msg = traceback.format_exc()
                raise Exception(
                    f"Unexpected error in running code at {last_line}: "
                    + "\n"
                    + str(e)
                    + "\n\n\n"
                    + error_msg
                )

            error_msg = traceback.format_exc()
            return {
                "success": False,
                "error_line": last_line,
                "code": code,
                "obj_val": None,
                "status": None,
                "error_message": error_msg,
                "bogus_context": bogus_context,
            }

    def get_solver_prep_code(self):
        if self.solver == "gurobipy":
            return "import gurobipy as gp\nfrom gurobipy import GRB\n\n # Define model\nmodel = gp.Model('model')"
        else:
            raise Exception(f"Solver {self.solver} is not supported yet!")