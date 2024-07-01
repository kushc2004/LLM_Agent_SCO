
import json
import numpy as np
import math

import gurobipy as gp
from gurobipy import GRB

 # Define model
model = gp.Model('model')




NumManuf = 5
NumWarehouses = 3
NumDistributors = 8
CostPerKm = 6
ManufToWarehouseDist = [[501.9, 1433.2, 875.3], [1758.4, 327.4, 2180.4], [1942.4, 1838.2, 1481.8], [580.2, 839.2, 1364.6], [819.2, 917.2, 708.7]]
WarehouseToDistDist = [[1153.7, 1586.3, 1428.5, 692.3, 1085.5, 449.2, 430.7, 2086.9], [1923.6, 2356.2, 578.9, 1503.3, 2006.4, 1372.0, 1298.4, 654.3], [216.2, 339.5, 1492.2, 826.0, 250.2, 1120.5, 977.7, 2460.4]]

# Define model
model = gp.Model('model')

SelectManuf = model.addVars(NumManuf, vtype=gp.GRB.BINARY, name="SelectManuf")
ManufToWarehouseFlow = model.addVars(NumManuf, NumWarehouses, vtype=gp.GRB.BINARY, name="ManufToWarehouseFlow")
WarehouseToDistFlow = model.addVars(NumWarehouses, NumDistributors, vtype=gp.GRB.BINARY, name="WarehouseToDistFlow")

model.addConstr(gp.quicksum(SelectManuf[m] for m in range(NumManuf)) == 2, name='SelectTwoManufs')

for m in range(NumManuf):
    for w in range(NumWarehouses):
        model.addConstr(ManufToWarehouseFlow[m, w] <= SelectManuf[m], name="ManufToWarehouseFlow_constraint")

for w in range(NumWarehouses):
    model.addConstr(gp.quicksum(ManufToWarehouseFlow[m, w] for m in range(NumManuf)) == 1, name=f"Each_warehouse_one_manufacturer_{w+1}")

for d in range(NumDistributors):
    model.addConstr(gp.quicksum(WarehouseToDistFlow[w, d] for w in range(NumWarehouses)) == 1, name="DistSupplyConstraint_" + str(d + 1))

model.setObjective(gp.quicksum(gp.quicksum(ManufToWarehouseFlow[m, w] * ManufToWarehouseDist[m][w] * CostPerKm for w in range(NumWarehouses)) for m in range(NumManuf)) + gp.quicksum(gp.quicksum(WarehouseToDistFlow[w, d] * WarehouseToDistDist[w][d] * CostPerKm for d in range(NumDistributors)) for w in range(NumWarehouses)), gp.GRB.MINIMIZE)

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

