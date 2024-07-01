import json
import os
import sys
import re
from utils.misc import gemini_client
import google.generativeai as genai
from agents.agent import *
import re

prompt_template = """
You are an expert in optimization problems, including Linear Programming (LP) and Mixed-Integer Linear Programming (MILP). Your task is to read a given optimization problem, identify its type, and re-write it in a text-book format.
Remember to analyze everything, follow the strict instructions and output only the json file.
Here is the problem:

-----
{description}
-----

You should:
1. Identify the type of the problem (e.g., LP, MILP).
2. Identify the objective of the problem.
3. Identify the input format of the problem.
4. Identify the output format of the problem.
5. If there is a new line in description then instead of typing new line include a new line \\n character as the json file does not recognize a new line. 
6. Go through the statements one by one, and identify and separate the parameters and variables of the problem, and put them in a json file and a string in this format:
7. Use '```json' and '```' to enclose the json file.
8. Note that I'm going to use python json.loads() function to parse the json file, so please make sure the format is correct (don't add ',' before enclosing '}}' or ']' characters).


=====
{{
    "problem_type": "LP" | "MILP" | "Other",
    "description": *updated description* with new line replaced by 'single slash n' \\n character, parameters are replaced by 'dobule slash param{{}}' \\\\param{{}}  and variables replaced by 'dobule slash var{{}}' \\\\var{{}},
    "problem_info": "str",
    "input_format": "str",
    "output_info": "str",
    "output_format": "str",
    "parameters": [
        {{
            "definition": "str",
            "symbol": "str",
            "value": "number",
            "shape": ["str"]
        }}
    ],
    "variables": [
        {{
            "definition": "str",
            "symbol": "str",
            "type": "continuous" | "integer" | "binary",
            "shape": ["str"]
        }}
    ],
    "data": [
        {{
            "<parameter_name>": "matrix or array"
        }}
    ],
    "path": "{folder_dir}"
}}
=====
*updated description*
=====


Where:
- "problem_type" is the type of the problem.
- "problem_info" is a brief description of the problem.
- "input_format" is the format of the input data.
- "output_info" is a brief description of the output.
- "output_format" is the format of the output data.
- "definition" is the definition of the parameter or variable.
- "symbol" is the mathematical symbol you want to use to represent the parameter or variable.
- "value" is a float or int, representing the numerical value of the parameter (use 0.33 instead of 1/3.0). For variables, this field can be omitted.
- "type" is the type of the variable: continuous, integer, or binary.
- "shape" is a possibly empty list of strings representing the dimensions of the parameter or variable in terms of other parameters or variables. 
- The symbol in the shape should be the symbol of a parameters without the brackets {{}}. Do not define shape which is not a symbol of any parameter. 
- Before defining every shape check all the parameter symbols and then only define the shape.
- "data" is the numerical values of the data given in the problem description. Express it in the form of dictionaru with key as tuples and values as the value associated with it which you can decide by checking the shape of the parameter. Include the data of all the parameters or variables mentioned in the problem. 
- Keep the symbols related to the definition, not just letters so that they are easily understandable.
- Keep the symbols generated as LaTeX expression.
- Very important step: *updated description* is the original description of the problem with its numbers replaced with the corresponding variable or parameter symbols in the \\param{{<name}} format. use double slash for writing this instead of single slash as json will give error if you write double slash.

Here is an example:

*** input ***

A factory produces two products using three machines. Each product requires a certain amount of time on each machine. The factory has a limited amount of time available on each machine per day. The goal is to determine the number of each product to produce to maximize profit. The profit per unit of each product is known. Latitude of machine m is 40.543.

*** output ***
```json
=====
{{
    "problem_type": "LP",
    "description": "A factory produces two products using three machines. Each product requires a certain amount of time on each machine. The factory has a limited amount of time available on each machine per day. The goal is to determine the number of each product to produce to maximize profit. The profit per unit of each product is known.",
    "problem_info": "A factory produces products using machines with limited time.",
    "input_format": "Number of products, number of machines, time available on each machine, time required for each product on each machine, profit per unit of each product.",
    "output_info": "Optimal number of each product to produce.",
    "output_format": "Number of units of each product to produce.",
    "parameters": [
        {{
            "definition": "Number of products",
            "symbol": "{{Products}}",
            "value": 2,
            "shape": [],
            "status": "formulated"
        }},
        {{
            "definition": "Number of machines",
            "symbol": "{{Machines}}",
            "value": 3,
            "shape": [],
            "status": "formulated"
        }},
        {{
            "definition": "Time available on machine m",
            "symbol": "{{T}}_m",
            "value": "",
            "shape": ["Machines"],
            "status": "formulated"
        }},
        {{
            "definition": "Time required for product p on machine m",
            "symbol": "{{TimeReq}}_pm",
            "value": "",
            "shape": ["Products", "Machines"],
            "status": "formulated"
        }},
        {{
            "definition": "Profit per unit of product p",
            "symbol": "{{Profit}}_p",
            "value": "",
            "shape": ["Products"],
            "status": "formulated"
        }},
        {{
            "definition": "Latitude of machine m",
            "symbol": "{{LatitudeMachine}}_m",
            "value": 40.543,
            "shape": ["Machines"],
            "status": "formulated"
        }}
    ],
    "variables": [
        {{
            "definition": "Number of units of product p to produce",
            "symbol": "{{NUnits}}_p",
            "type": "integer",
            "shape": ["Products"],
            "status": "formulated"
        }}
        {{
            "definition": "Number of units of machine m used",
            "symbol": "{{MUnits}}_m",
            "type": "integer",
            "shape": ["Machines"],
            "status": "formulated"
        }}
    ],
    "data": [
        {{
            "{{Machines}}": 3    
        }},
        {{
            "{{Products}}": 2
        }},
        {{
            "{{T}}_m": [5, 10, 4]
        }},
        {{
            "{{TimeReq}}_pm": {{
                                (1,2): 2.5, (1,2): 3.0, (1,3): 1.5,  # Time required for Product 1 on Machine 1, 2, and 3 (only for your understanding, dont include in your output)
                                (2,1): 4.0, (2,2): 2.5, (2,3): 3.5   # Time required for Product 2 on Machine 1, 2, and 3 (only for your understanding, dont include in your output)
                            }}
        }},
        {{
            "{{Profit}}_p": [100, 245]
        }},
        {{
            "{{LatitudeMachine}}_m": [40.543, 40.543, 40.543]
        }}
    ],
    "path": "path/data/problem_x"
}}
=====
A factory produces \\\\param{{Products}} products using \\\\param{{Machines}} machines. Each product requires \\\\param{{R_pm}} time on each machine. The factory has \\\\param{{T_m}} time available on each machine per day. The goal is to determine the number of \\\\param{{NUnits}} to produce to maximize profit. The profit per unit of each product is \\\\param{{Profit}}.
=====
```

**Instructions**
- Only generate the json file and the updated description, and do not generate anything else.
- Include the ===== lines in the output.
- Don't pass any comments in the json file.
- Before defining every shape check all the parameter symbols and then only define the shape.
- Avoid using fractions and use floating point numbers instead (0.2 instead of 1/5).
- Note that indices are not separate parameters or variables.
- Strictly follow this instruction. When writing the variables or parameters in the description write with double slash param like \\\\param{{}} because if you write single slash param{{}} the json recognizes single slash p{{}} as a character and gives error. Example: "A factory produces 2 products using 3 machines." is translated to "A factory produces \\\\param{{Products}} products using \\\\param{{Machines}} machines."
- Do not generate any data by yourself.
- Feel free to define new symbols for parameters or variables that do not have a symbol.
- Whenever you define a parameter or a variable and if you define its symbol then set its status as formulated. 
    Example {{
            "definition": "Number of units of product p to produce",
            "symbol": "{{NUnits}}_p",
            "type": "integer",
            "shape": ["P"],
            "status": "formulated"
        }}
- Use CamelCase and full words for symbols, and don't include the indices (e.g., MaxColor instead of maxColor or max_color or maxcolor or MaxCol or MaxColor_i or MaxColor_{{i}}).
- Use single capital letters for symbols that represent dimensions for indices of other parameters or variables (e.g., N, M, etc.).
- Note that parameters are known values upon which the model is built, and they do not change during the optimization process. Variables are the unknowns that the optimization process seeks to solve.
- Make sure you include all the parameters and variables in the updated problem description.
- Keep the symbols generated as LaTeX expression.
- Values of each and every parameter should be included in the "data".
- If you are able to combine the given data such as distances or latitudes, longitudes in a matrix/list form then do it so that you have to define less parameters.
    Example: 
    The locations (latitude and longitude) of the customers are as follows:
    Customer 1: Latitude 40.712776, Longitude -74.005974
    Customer 2: Latitude 40.730610, Longitude -73.935242
    Customer 3: Latitude 40.749825, Longitude -73.987963
    Customer 4: Latitude 40.758896, Longitude -73.985130
    Customer 5: Latitude 40.748817, Longitude -73.985428
    Customer 6: Latitude 40.741895, Longitude -73.989308
    If above data is given then try to combine it and write it as single parameter like
    {{
                "definition": "Latitude of Customer i",
                "symbol": "{{Latitude}}_i",
                "value": {{ 1: 40.712776, 2: 40.73061, 3: 40.749825, 4: 40.758896, 5: 40.748817, 6: 40.741895 }},
                "shape": ["NumCustomers"],
                "status": "formulated"
            }}
    {{
                "definition": "Longitude of Customer i",
                "symbol": "{{Longitude}}_i",
                "value": {{1: -74.005974, 2: -73.935242, 3: -73.987963, 4: -73.98513, 5: -73.985428, 6: -73.989308}},
                "shape": ["NumCustomers"],
                "status": "formulated"
            }}

Take a deep breath and tackle the problem step by step.
"""



prompt_template1 = """
You are an expert in optimization problems, including Linear Programming (LP) and Mixed-Integer Linear Programming (MILP). Your task is to read a given optimization problem, identify its type, and re-write it in a text-book format.
Remember to analyze everything, follow the strict instructions and output only the json file.
Here is the problem:

-----
{description}
-----

You should:
1. Identify the type of the problem (e.g., LP, MILP).
2. Identify the objective of the problem.
3. Identify the input format of the problem.
4. Identify the output format of the problem.
5. If there is a new line in description then instead of typing new line include a new line \\n character as the json file does not recognize a new line. 
6. Go through the statements one by one, and identify and separate the parameters and variables of the problem, and put them in a json file and a string in this format:
7. Use '```json' and '```' to enclose the json file.
8. Note that I'm going to use python json.loads() function to parse the json file, so please make sure the format is correct (don't add ',' before enclosing '}}' or ']' characters).


=====
{{
    "problem_type": "LP" | "MILP" | "Other",
    "description": *updated description* with new line replaced by 'single slash n' \\n character, parameters are replaced by 'dobule slash param{{}}' \\\\param{{}}  and variables replaced by 'dobule slash var{{}}' \\\\var{{}},
    "problem_info": "str",
    "input_format": "str",
    "output_info": "str",
    "output_format": "str",
    "parameters": [
        {{
            "definition": "str",
            "symbol": "str",
            "value": "number",
            "shape": ["str"]
        }}
    ],
    "variables": [
        {{
            "definition": "str",
            "symbol": "str",
            "type": "continuous" | "integer" | "binary",
            "shape": ["str"]
        }}
    ],
    "data": [
        {{
            "<parameter_name>": "matrix or array"
        }}
    ],
    "path": "{folder_dir}"
}}
=====
*updated description*
=====


Where:
- "problem_type" is the type of the problem.
- "problem_info" is a brief description of the problem.
- "input_format" is the format of the input data.
- "output_info" is a brief description of the output.
- "output_format" is the format of the output data.
- "definition" is the definition of the parameter or variable.
- "symbol" is the mathematical symbol you want to use to represent the parameter or variable.
- "value" is a float or int, representing the numerical value of the parameter (use 0.33 instead of 1/3.0). For variables, this field can be omitted.
- "type" is the type of the variable: continuous, integer, or binary.
- "shape" is a possibly empty list of strings representing the dimensions of the parameter or variable in terms of other parameters or variables. 
- The symbol in the shape should be the symbol of a parameters without the brackets {{}}. Do not define shape which is not a symbol of any parameter. 
- Before defining every shape check all the parameter symbols and then only define the shape.
- "data" is the numerical values of the data given in the problem description. Express it in the matrix or array form which you can decide by checking the shape of the parameter. Include the data of all the parameters or variables mentioned in the problem. 
- Keep the symbols related to the definition, not just letters so that they are easily understandable.
- Keep the symbols generated as LaTeX expression.
- Very important step: *updated description* is the original description of the problem with its numbers replaced with the corresponding variable or parameter symbols in the \\param{{<name}} format. use double slash for writing this instead of single slash as json will give error if you write double slash.

Here is an example:

*** input ***

A factory produces two products using three machines. Each product requires a certain amount of time on each machine. The factory has a limited amount of time available on each machine per day. The goal is to determine the number of each product to produce to maximize profit. The profit per unit of each product is known. Latitude of machine m is 40.543.

*** output ***
```json
=====
{{
    "problem_type": "LP",
    "description": "A factory produces two products using three machines. Each product requires a certain amount of time on each machine. The factory has a limited amount of time available on each machine per day. The goal is to determine the number of each product to produce to maximize profit. The profit per unit of each product is known.",
    "problem_info": "A factory produces products using machines with limited time.",
    "input_format": "Number of products, number of machines, time available on each machine, time required for each product on each machine, profit per unit of each product.",
    "output_info": "Optimal number of each product to produce.",
    "output_format": "Number of units of each product to produce.",
    "parameters": [
        {{
            "definition": "Number of products",
            "symbol": "{{Products}}",
            "value": 2,
            "shape": [],
            "status": "formulated"
        }},
        {{
            "definition": "Number of machines",
            "symbol": "{{Machines}}",
            "value": 3,
            "shape": [],
            "status": "formulated"
        }},
        {{
            "definition": "Time available on machine m",
            "symbol": "{{T}}_m",
            "value": "",
            "shape": ["Machines"],
            "status": "formulated"
        }},
        {{
            "definition": "Time required for product p on machine m",
            "symbol": "{{TimeReq}}_pm",
            "value": "",
            "shape": ["Products", "Machines"],
            "status": "formulated"
        }},
        {{
            "definition": "Profit per unit of product p",
            "symbol": "{{Profit}}_p",
            "value": "",
            "shape": ["Products"],
            "status": "formulated"
        }},
        {{
            "definition": "Latitude of machine m",
            "symbol": "{{LatitudeMachine}}_m",
            "value": 40.543,
            "shape": ["Machines"],
            "status": "formulated"
        }}
    ],
    "variables": [
        {{
            "definition": "Number of units of product p to produce",
            "symbol": "{{NUnits}}_p",
            "type": "integer",
            "shape": ["Products"],
            "status": "formulated"
        }}
        {{
            "definition": "Number of units of machine m used",
            "symbol": "{{MUnits}}_m",
            "type": "integer",
            "shape": ["Machines"],
            "status": "formulated"
        }}
    ],
    "data": [
        {{
            "{{Machines}}": 3    
        }},
        {{
            "{{Products}}": 2
        }},
        {{
            "{{T}}_m": [5, 10, 4]
        }},
        {{
            "{{TimeReq}}_pm": [
                                [2.5, 3.0, 1.5],  # Time required for Product 1 on Machine 1, 2, and 3 (only for your understanding, dont include in your output)
                                [4.0, 2.5, 3.5]   # Time required for Product 2 on Machine 1, 2, and 3 (only for your understanding, dont include in your output)
                            ]
        }},
        {{
            "{{Profit}}_p": [100, 245]
        }},
        {{
            "{{LatitudeMachine}}_m": [40.543, 40.543, 40.543]
        }}
    ],
    "path": "path/data/problem_x"
}}
=====
A factory produces \\\\param{{Products}} products using \\\\param{{Machines}} machines. Each product requires \\\\param{{R_pm}} time on each machine. The factory has \\\\param{{T_m}} time available on each machine per day. The goal is to determine the number of \\\\param{{NUnits}} to produce to maximize profit. The profit per unit of each product is \\\\param{{Profit}}.
=====
```

**Instructions**
- Only generate the json file and the updated description, and do not generate anything else.
- Include the ===== lines in the output.
- Don't pass any comments in the json file.
- Before defining every shape check all the parameter symbols and then only define the shape.
- Avoid using fractions and use floating point numbers instead (0.2 instead of 1/5).
- Note that indices are not separate parameters or variables.
- Strictly follow this instruction. When writing the variables or parameters in the description write with double slash param like \\\\param{{}} because if you write single slash param{{}} the json recognizes single slash p{{}} as a character and gives error. Example: "A factory produces 2 products using 3 machines." is translated to "A factory produces \\\\param{{Products}} products using \\\\param{{Machines}} machines."
- Do not generate any data by yourself.
- Feel free to define new symbols for parameters or variables that do not have a symbol.
- Whenever you define a parameter or a variable and if you define its symbol then set its status as formulated. 
    Example {{
            "definition": "Number of units of product p to produce",
            "symbol": "{{NUnits}}_p",
            "type": "integer",
            "shape": ["P"],
            "status": "formulated"
        }}
- Use CamelCase and full words for symbols, and don't include the indices (e.g., MaxColor instead of maxColor or max_color or maxcolor or MaxCol or MaxColor_i or MaxColor_{{i}}).
- Use single capital letters for symbols that represent dimensions for indices of other parameters or variables (e.g., N, M, etc.).
- Note that parameters are known values upon which the model is built, and they do not change during the optimization process. Variables are the unknowns that the optimization process seeks to solve.
- Make sure you include all the parameters and variables in the updated problem description.
- Keep the symbols generated as LaTeX expression.
- Values of each and every parameter should be included in the "data".
- If you are able to combine the given data such as distances or latitudes, longitudes in a matrix/list form then do it so that you have to define less parameters.
    Example: 
    The locations (latitude and longitude) of the customers are as follows:
    Customer 1: Latitude 40.712776, Longitude -74.005974
    Customer 2: Latitude 40.730610, Longitude -73.935242
    Customer 3: Latitude 40.749825, Longitude -73.987963
    Customer 4: Latitude 40.758896, Longitude -73.985130
    Customer 5: Latitude 40.748817, Longitude -73.985428
    Customer 6: Latitude 40.741895, Longitude -73.989308
    If above data is given then try to combine it and write it as single parameter like
    {{
                "definition": "Latitude of Customer i",
                "symbol": "{{Latitude}}_i",
                "value": [ 40.712776, 40.73061, 40.749825, 40.758896, 40.748817, 40.741895 ],
                "shape": ["NumCustomers"],
                "status": "formulated"
            }}
    {{
                "definition": "Longitude of Customer i",
                "symbol": "{{Longitude}}_i",
                "value": [-74.005974, -73.935242, -73.987963, -73.98513, -73.985428, -73.989308],
                "shape": ["NumCustomers"],
                "status": "formulated"
            }}

Take a deep breath and tackle the problem step by step.
"""


def transform_problem(folder_dir: str):
    """Clean the LPWP instance in the given folder.

    Args:
        folder_dir (str): the folder that contains the LPWP instance
    """

    with open(folder_dir + "/description.txt", "r") as f:
        description = f.read()

    # prompt = prompt_template1.format(description=description)
    prompt = prompt_template1.format(description=description, folder_dir=folder_dir)

    # print(prompt)
    model = gemini_client()
    
    output = model.generate_content(prompt)
    output = output.text
    

    print("-=" * 10)
    print(output)
    print("-=" * 10)

    # if "```json" in output:
    #     # delete until the first '```json'
    #     output = output[output.find("```json") + 7 :]

    #     # delete until the last '```'
    #     output = output[: output.rfind("```")]

    pattern = r"```json(.*?)```"
    match = re.search(pattern, output, re.DOTALL)

    if match:
        output = match.group(1).strip()

    output = output.split("=====")
    output = [x.strip() for x in output if len(x.strip()) > 0]


    output_json = output[0]
    output_desc = output[1]

    if "```json" in output_json:
        # delete until the first '```json'
        output_json = output_json[output_json.find("```json") + 7 :]

        # delete until the last '```'
        output_json = output_json[: output_json.rfind("```")]

    

    print(output_json)
    
    

    with open(folder_dir + "/input.json", "w") as f:
        f.write(output_json)

    update = json.loads(output_json)

    data = update["data"]
    result_data = {}
    for item in data:
        result_data.update(item)
    print("*"*10)
    print(result_data)
    result_dict = json.dumps(result_data, indent=4)

    with open(folder_dir + "/data.json", "w") as f:
        f.write(str(result_dict))

    for param in update["parameters"]:
        if "_" in param["symbol"]:
            new_symbol = param["symbol"].replace("_", "")
            output_desc = output_desc.replace(param["symbol"], new_symbol)
            param["symbol"] = new_symbol

    update["description"] = output_desc

    return update

