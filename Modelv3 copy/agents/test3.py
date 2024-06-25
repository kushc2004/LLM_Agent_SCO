import json
import numpy as np
import math

import gurobipy as gp

 # Define model
model = gp.Model('model')




D = 2
Mint = [10, 12]
ActiveIngredient = [20, 15]
MintyFoam = [25, 18]
BlackTar = [5, 3]
TotalMint = 120
TotalActiveIngredient = 100
MaxBlackTar = 50
NDemonstrations = model.addVars(D, vtype=gp.GRB.INTEGER, name="NDemonstrations")

model.addConstr(NDemonstrations[D] >= 0, name="NDemonstrations_D1_nonnegative")