import os
import json
from utils.misc import *
import re

prompt_templates = [
"""
You are an optimization expert with a focus on Mixed-Integer Linear Programming (MILP) problems. Your task is to interpret a given MILP problem description, understand its nuances, and convert it into a structured standard form.

Upon receiving a problem description (with parameters marked as \\param{{param_name}} and variables marked as \\var{{var_name}}), you should:

1. Carefully analyze and comprehend the problem.
2. Clearly define the background and context of the problem.
3. Identify and list all constraints, including any implicit ones like non-negativity.
* Only generate the necessary constraints. Understand the supply chain problem first, then generate the constraints carefully. Don't generate repetitive constraints.
* Should not assume any information or constraints by yourself. Example If it is not mentioned in the question that each manufacturer is supplying to how many warehouses then don't assume constraint that each manufacturer will supply to only one warehouse.
4. Determine the primary objective of the problem.
5. Identify the input format of the problem.
6. Identify the output format of the problem.
7. If any ambiguities exist in the description, note them specifically.
8. Preferences are not constraints. Do not include them in the list of constraints.
9. Statements that simply define exact values of parameters are not constraints. Do not include them in the list of constraints (e.g., "The cost of producing an X is Y", or "Each X has a size of Y").
10. Statements that define bounds are constraints. Include them in the list of constraints (e.g., "The cost of producing an X is at most Y", or "Each X has a size of at least Y").
11. Only use available variables and parameters. If new variables are needed, define them explicitly.

Produce a JSON file encapsulating this information in the following format:

{{
    "background": "String detailing the problem's background",
    "constraints": ["List", "Of", "All", "Constraints"],
    "objective": [{{"description": "The primary objective to be achieved", "status": "not_formulated"}}],
    "input_format": "The format of the input data",
    "output_format": "The format of the output data"
}}

In case of ambiguities, use this format:

{{
    "ambiguities": ["List", "Of", "Identified", "Ambiguities"]
}}

Remember to keep each constraint separate and explicit. Do not merge different constraints into a single line.

Here is an example 1 to illustrate:

*** Input ***

An office supply company manufactures two types of printers: color and black and white. Each type is produced by separate teams. The color printer team can produce up to \\param{{MaxColor}} units per day, while the black and white team can produce up to \\param{{MaxBW}} units per day. Both teams use a common machine for installing paper trays, which has a maximum daily capacity of \\param{{MaxTotal}} printers. Each color printer yields a profit of \\param{{ProfitColor}}, and each black and white printer yields a profit of \\param{{ProfitBW}}. Determine the optimal production mix to maximize profit.

*** Output ***

{{
    "background": "An office supply company manufactures color and black and white printers, each by different teams using a shared resource.",
    "constraints": [
        "Number of color printers is non-negative",
        "Number of black and white printers is non-negative",
        "Up to MaxColor color printers can be produced per day",
        "Up to MaxBW black and white printers can be produced per day",
        "A total of up to MaxTotal printers can be produced per day"
    ],
    "objective": [{{"description": "Maximize the company's profit from printer production", "status": "not_formulated"}}],
    "input_format": "Number of color printers, number of black and white printers, maximum daily capacity of the common machine, profit per color printer, profit per black and white printer.",
    "output_format": "Optimal number of color and black and white printers to produce."
}}

Here is an example 2 to illustrate:

*** Input ***
A protein powder supply chain consists of Contract Manufacturer, Warehouse and Distributor. The flow is Contract Manufacturer to Warehouse to Distributor. Warehouses are at locations - Bhiwandi, Bangalore and Delhi. The Distributors are located at Agra, Ludhiana, Hyderabad, Indore, Jaipur, Surat, Vadodara and Tirunelveli. The Manufactures who have applied to be selected as Contract Manufacturers are at locations - Ahemdabad, Chennai, Kolkata, Pune and Bhopal. Only 2 manufactures would be selected from these. Optimise the supply chain network and select the two best manufacturers that would minimise the transportation cost. It should also tell which manufacturer is supplying to which warehouse and which warehouse is supplying to which distributor. The cost of transportation per km is \\param{{TransportCost}}. The distances are specified below.\n\nManufacturer to Warehouse Distances (km)\nManufacturer\tBhiwandi\tBengaluru\tDelhi\nAhemdabad\t\\param{{DistanceCMW}}_{{Ahemdabad, Bhiwandi}}\t\\param{{DistanceCMW}}_{{Ahemdabad, Bengaluru}}\t\\param{{DistanceCMW}}_{{Ahemdabad, Delhi}}\nChennai\t\\param{{DistanceCMW}}_{{Chennai, Bhiwandi}}\t\\param{{DistanceCMW}}_{{Chennai, Bengaluru}}\t\\param{{DistanceCMW}}_{{Chennai, Delhi}}\nKolkata\t\\param{{DistanceCMW}}_{{Kolkata, Bhiwandi}}\t\\param{{DistanceCMW}}_{{Kolkata, Bengaluru}}\t\\param{{DistanceCMW}}_{{Kolkata, Delhi}}\nPune\t\\param{{DistanceCMW}}_{{Pune, Bhiwandi}}\t\\param{{DistanceCMW}}_{{Pune, Bengaluru}}\t\\param{{DistanceCMW}}_{{Pune, Delhi}}\nBhopal\t\\param{{DistanceCMW}}_{{Bhopal, Bhiwandi}}\t\\param{{DistanceCMW}}_{{Bhopal, Bengaluru}}\t\\param{{DistanceCMW}}_{{Bhopal, Delhi}}\n\nWarehouse to Distributor Distances (km)\nWarehouse\tAgra\tLudhiana\tHyderabad\tIndore\tJaipur\tSurat\tVadodara\tTirunelveli\nBhiwandi\t\\param{{DistanceWHD}}_{{Bhiwandi, Agra}}\t\\param{{DistanceWHD}}_{{Bhiwandi, Ludhiana}}\t\\param{{DistanceWHD}}_{{Bhiwandi, Hyderabad}}\t\\param{{DistanceWHD}}_{{Bhiwandi, Indore}}\t\\param{{DistanceWHD}}_{{Bhiwandi, Jaipur}}\t\\param{{DistanceWHD}}_{{Bhiwandi, Surat}}\t\\param{{DistanceWHD}}_{{Bhiwandi, Vadodara}}\t\\param{{DistanceWHD}}_{{Bhiwandi, Tirunelveli}}\nBengaluru\t\\param{{DistanceWHD}}_{{Bengaluru, Agra}}\t\\param{{DistanceWHD}}_{{Bengaluru, Ludhiana}}\t\\param{{DistanceWHD}}_{{Bengaluru, Hyderabad}}\t\\param{{DistanceWHD}}_{{Bengaluru, Indore}}\t\\param{{DistanceWHD}}_{{Bengaluru, Jaipur}}\t\\param{{DistanceWHD}}_{{Bengaluru, Surat}}\t\\param{{DistanceWHD}}_{{Bengaluru, Vadodara}}\t\\param{{DistanceWHD}}_{{Bengaluru, Tirunelveli}}\nDelhi\t\\param{{DistanceWHD}}_{{Delhi, Agra}}\t\\param{{DistanceWHD}}_{{Delhi, Ludhiana}}\t\\param{{DistanceWHD}}_{{Delhi, Hyderabad}}\t\\param{{DistanceWHD}}_{{Delhi, Indore}}\t\\param{{DistanceWHD}}_{{Delhi, Jaipur}}\t\\param{{DistanceWHD}}_{{Delhi, Surat}}\t\\param{{DistanceWHD}}_{{Delhi, Vadodara}}\t\\param{{DistanceWHD}}_{{Delhi, Tirunelveli}}\n\nCount and add the number of each stakeholders that is Contract manufacturer, warehouse, distributor. Any manufacturer can supply to any number of warehouses and any warehouse can supply to any number of Distributors.\nDo not consider the flow quantity while formulating the objective function. only consider the cost associated with distance.

*** Output ***
{{
    {{
    "background": "A protein powder supply chain consists of Contract Manufacturers (CM), Warehouses (WH), and Distributors (Dist). The flow is from CM to WH to Dist. There are {{NumCM}} potential CMs, {{NumWH}} WHs, and {{NumDist}} Dist. Only {{Select2CM}} CMs will be selected. The objective is to minimize the total transportation cost. The cost of transportation per km is {{TransportCost}}.  The distances between each CM and WH, and each WH and Dist are given in matrices {{DistanceCMW}} and {{DistanceWHD}} respectively.",
    "constraints": [
        "Exactly two contract manufacturers should be selected.",
        "All the warehouses should be utilised.",
        "All the distributors should be utilised.",
    ],
    "objective": [{{description": "Minimize the total transportation cost in the supply chain network", "status": "not_formulated"}}],
    "input_format": "Number of contract manufacturers, number of warehouses, number of distributors, distance between each pair of manufacturers and warehouses, distance between each pair of warehouses and distributors, transportation cost per km.",
    "output_format": "Selected Contract Manufacturers, Assignment of each selected manufacturer to warehouses, Assignment of each warehouse to distributors"
    }}
}}

** STRICT INSTRUCTIONS **
- Take a deep breath and approach this task methodically, step by step. To formulate the cosntraints and objective function only use the symbols of parameters or variables that mentioned in the description.
- First, read and understand the problem description carefully. Then, generate the JSON file. Do not generate anything after the JSON file.
- Note that I'm going to use python json.loads() function to parse the json file, so please make sure the format is correct (don't add ',' before enclosing '}}' or ']' characters).

Here is the problem description: 
{description}

Below are the parameters with symbols:
{parameters}

Below are the variables with symbols:
{variables}

""",
"""
You are an optimization expert. I have this problem description:

{description}

Below are the parameters with symbols:
{parameters}

Below are the variables with symbols:
{variables}

Someone has extracted the following list of constraints from the description:

{constraints_json}

Your task is to go through the extracted constraints, and for each one of them, do the following:

1. If the statement is not actually a constraint or objective, mark it as "invalid".
2. Otherwise, find the relevant section of the problem description that the statement is referring to.
3. While generating refer to the symbols of varibales and parameters and use them only. 

Generate a json file with the following structure:

{{
    "constraints": [
        {{
            "description": "[Definition of the constraint]",
            "formulation": "Generate a latex equation of the constraint so that it can be shown in the frontend and written in summation form. Use '(double slashes)' \\\\textup{{}} only when writing variables or parameters in constraints. For example (\\\\sum_{{i=1}}^{{N}} \\\\textup{{ItemsSold}}_{{i}} instead of \\\\sum_{{i=1}}^{{N}} ItemsSold_{{i}})" . The symbols should be enclosed in single barckets only.,
            "reasoning": "[Explanation of why the constraint is valid/invalid]",
            "status": "formulated" | "not_formulated (if formulation is not formulated)",
            "relevant_section": "[Section of the problem description that the constraint is referring to, or 'none' if the constraint is invalid]"
        }}
        ...
    ]
}}

** STRICT INSTRUCTIONS **

- Statements that simply define exact values of parameters are not constraints (e.g., "The cost of producing an X is Y", or "Each X has a size of Y").
- Statements that define bounds are constraints (e.g., "The cost of producing an X is at most Y", or "Each X has a size of at least Y").
- Preferences are not constraints.
- If the same constraint is mentioned multiple times (even in different words), mark all but one of them as "redundant".
- Only use available variables and parameters. If new variables are needed, define them explicitly.

Only generate the json file and do not generate anything else. Take a deep breath and approach this task methodically, step by step.
Note that I'm going to use python json.loads() function to parse the json file, so please make sure the format is correct (don't add ',' before enclosing '}}' or ']' characters).

"""
]


def generate_constraints(folder_dir: str):
    """Extract targets for the LPWP instance in the given folder and update the input.json file.

    Args:
        folder_dir (str): the folder that contains the LPWP instance
    """
    # Read input.json
    with open(folder_dir + "/input.json", "r") as f:
        input_json = json.load(f, strict=False)

    desc = input_json.get("description", "")
    # if not description:
    #     description = get_user_input(
    #         "Description is missing. Please provide a detailed description of the problem, including the context and main objectives: "
    #     )
    #     input_json["description"] = description

    # Main extraction
    # print(prompt_templates[0])
    prompt = prompt_templates[0].format(description=desc, 
                                        parameters=input_json.get("parameters", ""), 
                                        variables=input_json.get("variables", "") )
    
    model = gemini_client_pro()
    
    output = model.generate_content(prompt)
    output = output.text

    print("-=" * 10)
    print(output)
    print("-=" * 10)

    output = output.replace(" \\param", " \\\\\\\\param")

    pattern = r"```json(.*?)```"
    match = re.search(pattern, output, re.DOTALL)

    if match:
        output = match.group(1).strip()

    # Update the input_json with new parameters from the output
    output_data = json.loads(output, strict=False)
    input_json["background"] = output_data.get("background", "")
    input_json["objective"] = output_data.get("objective", "")
    input_json["input_format"] = output_data.get("input_format", "")
    input_json["output_format"] = output_data.get("output_format", "")
    
    constraints = output_data.get("constraints", [])

    # Convert the constraints to the required format for the next prompt
    constraints_json = json.dumps(constraints, indent=4)

    # Sanity check
    prompt = prompt_templates[1].format(
        description=desc,
        constraints_json=constraints_json,
        parameters=input_json.get("parameters", ""), 
        variables=input_json.get("variables", "")
    )

    model = gemini_client_pro()
    
    output = model.generate_content(prompt)
    output = output.text

    # print("-=" * 10)
    # print(output)
    # print("-=" * 10)

    output = output.replace(" \\\\param", " \\\\\\\\param")
    output = output.replace(" \\param", " \\\\\\\\param")
    
    
    pattern = r"```json(.*?)```"
    match = re.search(pattern, output, re.DOTALL)

    if match:
        output = match.group(1).strip()

    
    output_data = json.loads(output, strict=False)

    constraints = output_data.get("constraints", [])
    input_json["constraints"] = constraints

    print(output)

    # checked_update = json.loads(output, strict=False)

    # # Update constraints in input_json
    # valid_constraints = [
    #     x["definition"] for x in checked_update["constraints"] if x["status"] == "valid"
    # ]
    # input_json["constraints"] = valid_constraints

    # Save the updated input.json
    with open(folder_dir + "/input_wc.json", "w") as f:
        json.dump(input_json, f, indent=4)
