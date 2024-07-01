import pandas as pd
import gurobipy as gp
from gurobipy import GRB, quicksum
import io
model = gp.Model()
N = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]  #Set of Customers
Np = [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]
Ns = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]
Nt = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,0]
Depot = 0
b=4
Nb= [0,1,2,3,4]
Na= [1,2,3,4]
Nd=[1,2,3,4,0]
L= [1,2,3,4]   #Set of Drones
Rl = [1,1,1,1] #Set of boats
q = [1,5,2,3,4,2,1,5,12,24,12,12,13,15,12,16,1,2]
tau = pd.read_excel("Drone_Times.xlsx", sheet_name=0)
tau = tau.to_numpy()
#print(tau)
#Total time required for a boat to deliver from i to j
t = pd.read_excel("boat.xlsx", sheet_name=0)
t = t.to_numpy()
#print(t)
M=1000
A = [(i, j) for i in Ns for j in Nt if i != j]  #Matrix of all possible routes
Sa = [(i, j) for i in Nb for j in Nd if i != j]
#decision variables
x = {}
h = {}
#v = {}
w = {}
#y = {}
#q = {}
for i in Ns:
    for j in Nt:
        if i!=j:
            x[i, j] = model.addVar(lb=0, ub=1, vtype=GRB.CONTINUOUS, name=f'x_{i}_{j}')   #Adding the values of decesion variable x

#for i in N:
 #  v[i] = model.addVar(vtype=GRB.INTEGER, name=f'v_{i}')                 #Adding the visiting order of the nodes

#for j in N:
  #  v[j] = model.addVar(vtype=GRB.INTEGER, name=f'v_{j}')

for i in Ns:
    for j in Nt:
        if i !=j:
           for l in L:
               h[i, j, l] = model.addVar(vtype=GRB.BINARY, name=f'h_{i}{j}{l}')  #Adding the variable

for i in Ns:
    w[i] = model.addVar(vtype=GRB.CONTINUOUS, name=f'w_{i}')            #waiting time of the trucks
# Set up the objective function
model.ModelSense = GRB.MINIMIZE
model.setObjective(quicksum(t[i][j]*x[i,j] for i,j in A)+quicksum(w[i] for i in Ns))


#v[0] = 0
#constraints
model.addConstr(quicksum(x[0, j] for j in N) == 2)
#model.addConstr(quicksum(x[0, j] for j in N) >= 0.3)
model.addConstr(quicksum(x[i, 0] for i in N) == 2)
#model.addConstr(quicksum(x[i, 0] for i in N) >= 0.3)
model.addConstrs(quicksum(x[i, j] for j in Nt if j != i) == quicksum(x[j, i] for j in Ns if j != i) for i in N)
#model.addConstrs(v[i]-v[j]+ M*x[i,j]<=M-1 for i,j in A if j !=Depot)
model.addConstrs(quicksum(x[i,j] for i in Ns if i != j) + quicksum(h[i,j,l] for i in Ns for l in L if i !=j)== 1 for j in N)
model.addConstrs(M*(quicksum(x[i,j] for j in Nt if j != i)) >= quicksum(h[i,j,l] for j in N for l in L if j != i) for i in Ns)
model.addConstrs(w[i] >= quicksum(tau [i][j] * h[i,j,l] for j in N if j != i) for i in Ns for l in L)

# suppose each vehicle has capacity 100
Q = 20

# suppose each demand point has demand 20
q = [0,10,12,10,8]
# q[0] =0
# q[1]=10
# q[2]=12
# q[3]=10
# q[4]=8
# q={i:10 for i in Na}

#Constraints due to cut
# model.addConstr(x[0,1]+x[2,1]+x[3,1]>=1)

# Add the MTZ variables and constraints, and solve
u = model.addVars( Nb, name=f'u_{i}_{j}' )

u[Depot].LB = 0
u[Depot].UB = 0

for i in Na:
    u[i].LB = q[i]
    u[i].UB = Q

c = model.addConstrs( u[i] - u[j] + Q * x[i,j] <= Q - q[j] for i,j in Sa if j != Depot )

model.optimize()
print(model.status)

model.write("DRONE_exactt.lp")

if model.status == GRB.OPTIMAL:
    print("Optimal Solution:")
    for var in model.getVars():
             print(f"{var.varName} = {var.x}")

    print(f"Objective Value = {model.objVal}")

else:
    print("No solution found.")
model.write("out.JSON")