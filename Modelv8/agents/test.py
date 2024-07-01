import json
import numpy as np
import math

import gurobipy as gp
from gurobipy import GRB

 # Define model
model = gp.Model('model')




CM = 5
WH = 3
DIST = 8
Latitude = [19.333111, 12.97675, 28.70406, 22.565571, 21.20351, 18.52076, 26.92098, 23.252319, 27.167641, 30.91317, 17.361719, 22.71867, 22.42055, 8.715, 23.0225, 13.0843]
Longitude = [73.111504, 77.575279, 77.102493, 88.370209, 72.839233, 73.855408, 75.79422, 77.431091, 78.035873, 75.849541, 78.475166, 75.855713, 73.16569, 77.7656, 72.5714, 80.2705]

# Define model
model = gp.Model('model')

Y = model.addVars(CM, vtype=gp.GRB.BINARY, name="Y")
XMW = model.addVars(CM, WH, vtype=gp.GRB.BINARY, name="XMW")
FWD = model.addVars(WH, DIST, vtype=gp.GRB.BINARY, name="FWD")

model.addConstr(gp.quicksum(Y[cm] for cm in CM) <= 1, name="Each_Contract_Manufacturer_Selected_At_Most_Once")
