
import json
import numpy as np
import math

import gurobipy as gp
from gurobipy import GRB

 # Define model
model = gp.Model('model')




Manuf = 5
Warehouses = 3
Distributor = 8
DistManufWare = [[501.9, 1433.2, 875.3], [1758.4, 327.4, 2180.4], [1942.4, 1838.2, 1481.8], [580.2, 839.2, 1364.6], [819.2, 917.2, 708.7]]
DistWareDist = [[1153.7, 1586.3, 1428.5, 692.3, 1085.5, 449.2, 430.7, 2086.9], [1923.6, 2356.2, 578.9, 1503.3, 2006.4, 1372.0, 1298.4, 654.3], [216.2, 339.5, 1492.2, 826.0, 250.2, 1120.5, 977.7, 2460.4]]
TransportCost = 6
ManuSelected = 2

# Define model
model = gp.Model('model')

Z = model.addVars(Manuf, vtype=gp.GRB.BINARY, name="Z")
X = model.addVars(Manuf, Warehouses, vtype=gp.GRB.BINARY, name="X")
Y = model.addVars(Warehouses, Distributor, vtype=gp.GRB.BINARY, name="Y")

model.addConstr(gp.quicksum(Z[m] for m in range(Manuf)) == ManuSelected, name="manu_selected")

for m in range(Manuf):
    for w in range(Warehouses):
        model.addConstr(X[m, w] <= Z[m], name="constraint_manufacturer_supply")

for w in range(Warehouses):
    model.addConstr(gp.quicksum(X[m, w] for m in range(Manuf)) >= 1, name="Each_Warehouse_supplied_by_atleast_one_Manufacturer")

for d in range(Distributor):
    model.addConstr(gp.quicksum(Y[w, d] for w in range(Warehouses)) >= 1, name=f"Distributor_Supplied_{d}")

for m in range(Manuf):
    model.addConstr(gp.quicksum(X[m, w] for w in range(Warehouses)) <= Manuf * Z[m], name="manuf_to_warehouses")

model.addConstr(gp.quicksum(Z[m] for m in range(Manuf)) == ManuSelected, name="selected_manufacturers")

model.setObjective(gp.quicksum(gp.quicksum(TransportCost * DistManufWare[m][w] * X[m, w] for w in range(Warehouses)) for m in range(Manuf)) + gp.quicksum(gp.quicksum(TransportCost * DistWareDist[w][d] * Y[w, d] for d in range(Distributor)) for w in range(Warehouses)), gp.GRB.MINIMIZE)

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

