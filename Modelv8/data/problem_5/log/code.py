
import json
import numpy as np
import math

import gurobipy as gp
from gurobipy import GRB

 # Define model
model = gp.Model('model')




ContractManufacturers = 2
Warehouses = 3
Distributors = 8
DistCMB = [[501.9, 1433.2, 875.3], [1758.4, 327.4, 2180.4]]
DistBWD = [[1153.7, 1586.3, 1428.5, 692.3, 1085.5, 449.2, 430.7, 2086.9], [1923.6, 2356.2, 578.9, 1503.3, 2006.4, 1372.0, 1298.4, 654.3], [216.2, 339.5, 1492.2, 826.0, 250.2, 1120.5, 977.7, 2460.4]]
TransportCost = 6

# Define model
model = gp.Model('model')

FlowCMB = model.addVars(ContractManufacturers, Warehouses, name='FlowCMB')
FlowBWD = model.addVars(Warehouses, Distributors, name="FlowBWD")

for c in range(ContractManufacturers):
    model.addConstr(gp.quicksum(FlowCMB[c, w] for w in range(Warehouses)) == 1, name="sum_of_flow_from_CMB")

for d in range(Distributors):
    model.addConstr(gp.quicksum(FlowBWD[w, d] for w in range(Warehouses)) == 1, name="FlowBWD_sum_constraint_" + str(d))

model.setObjective(gp.quicksum(gp.quicksum(FlowCMB[c, w] * DistCMB[c][w] * TransportCost for w in range(Warehouses)) for c in range(ContractManufacturers)) + gp.quicksum(gp.quicksum(FlowBWD[w, d] * DistBWD[w][d] * TransportCost for d in range(Distributors)) for w in range(Warehouses)), gp.GRB.MINIMIZE)

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
    print("The optimal solution is", obj_val)

