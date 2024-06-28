import json
import numpy as np
import math

import gurobipy as gp
from gurobipy import GRB

 # Define model
model = gp.Model('model')




N = 6
V = 3
Capacity = [50, 60, 55]
Demand = [10, 15, 20, 25, 30, 35]
StartTime = [8.0, 9.0, 10.0, 11.0, 12.0, 13.0]
EndTime = [10.0, 11.0, 12.0, 13.0, 14.0, 15.0]
Latitude = [40.712776, 40.73061, 40.749825, 40.758896, 40.748817, 40.741895]
Longitude = [-74.005974, -73.935242, -73.987963, -73.98513, -73.985428, -73.989308]
ServiceTime = [0.25, 0.33, 0.42, 0.5, 0.58, 0.67]
Visit = model.addVars(V, N, vtype=gp.GRB.BINARY, name="Visit")
ArrivalTime = model.addVars(V, N, name="ArrivalTime")
DepartureTime = model.addVars(V, N, name="DepartureTime")
# PreviousCustomer = model.addVars(V, N, vtype=gp.GRB.INTEGER, name="PreviousCustomer")

for v in range(V):
    for c in range(N):
        model.addConstr(Visit[v, c] <= 1, name="Visit_binary")
        model.addConstr(Visit[v, c] >= 0, name="Visit_binary")

for v in range(V):
    for c in range(N):
        model.addConstr(ArrivalTime[v, c] >= StartTime[c], name="arrival_time_constraint")

for v in range(V):
    for c in range(N):
        model.addConstr(ArrivalTime[v, c] <= EndTime[c], name="arrival_time_constraint")

for v in range(V):
    for c in range(N):
        model.addConstr(DepartureTime[v, c] == ArrivalTime[v, c] + ServiceTime[c], name=f"DepartureTime_{v}_{c}")

for c in range(N):
    model.addConstr(gp.quicksum(Visit[v, c] for v in range(V)) <= 1, name="visit_once")

for v in range(V):
    model.addConstr(gp.quicksum(Visit[v, c] * Demand[c] for c in range(N)) <= Capacity[v], name=f"capacity_constraint_{v}")

obj = gp.quicksum(gp.quicksum(Visit[v,c] * math.sqrt((Latitude[c] - Latitude[c_prime])**2 + (Longitude[c] - Longitude[c_prime])**2) for c in range(N) for c_prime in range(N)) for v in range(V))
model.setObjective(obj, gp.GRB.MINIMIZE)

model.optimize()
print(model.status)
if model.status == GRB.OPTIMAL:
    print("Optimal Solution:")
    for var in model.getVars():
             print(f"{var.varName} = {var.x}")

    print(f"Objective Value = {model.objVal}")