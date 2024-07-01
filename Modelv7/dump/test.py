import json
import numpy as np
import math

import gurobipy as gp

 # Define model
model = gp.Model('model')




MintUnitsDemo1 = 10
ActiveIngredientUnitsDemo1 = 20
MintyFoamUnitsDemo1 = 25
MintUnitsDemo2 = 12
ActiveIngredientUnitsDemo2 = 15
MintyFoamUnitsDemo2 = 18
BlackTarUnitsDemo1 = 5
BlackTarUnitsDemo2 = 3
MintUnitsTotal = 120
ActiveIngredientUnitsTotal = 100
BlackTarUnitsMax = 50
Demo1Times = model.addVar(vtype=gp.GRB.INTEGER, name="Demo1Times")
Demo2Times = model.addVar(vtype=gp.GRB.INTEGER, name="Demo2Times")

model.addConstr(Demo1Times >= 0, name="Demo1Times_non_negative")

model.addConstr(Demo2Times >= 0, name="Demo2Times_nonnegative")

model.addConstr(Demo1Times * MintUnitsDemo1 + Demo2Times * MintUnitsDemo2 <= MintUnitsTotal, name="MintUnitsConstraint")

model.addConstr(ActiveIngredientUnitsDemo1 * Demo1Times + ActiveIngredientUnitsDemo2 * Demo2Times <= ActiveIngredientUnitsTotal, name="ActiveIngredientUnitsConstraint")

model.addConstr(BlackTarUnitsDemo1 * Demo1Times + BlackTarUnitsDemo2 * Demo2Times <= BlackTarUnitsMax, name="BlackTarUnitsMaxConstraint")

model.addConstr(MintUnitsDemo1 * Demo1Times + MintUnitsDemo2 * Demo2Times <= MintUnitsTotal, name='MintUnitsConstraint')

model.addConstr(ActiveIngredientUnitsDemo1 * Demo1Times + ActiveIngredientUnitsDemo2 * Demo2Times <= ActiveIngredientUnitsTotal, name="ActiveIngredientLimit")

model.addConstr(BlackTarUnitsDemo1 * Demo1Times + BlackTarUnitsDemo2 * Demo2Times <= BlackTarUnitsMax, name="BlackTarProductionLimit")

model.setObjective(MintyFoamUnitsDemo1 * Demo1Times + MintyFoamUnitsDemo2 * Demo2Times, gp.GRB.MAXIMIZE)

# Optimize model
model.optimize()



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

print(obj_val)