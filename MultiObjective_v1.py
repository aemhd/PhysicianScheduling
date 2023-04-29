import gurobipy as gp
from gurobipy import GRB

import pandas as pd

import matplotlib.pyplot as plt

# shiftRequirements(s)∈N : This parameter represents the number of physicians required at each shift s∈shifts.


# Number of physicians required for each shift.
shifts, shiftRequirements = gp.multidict({
    "Mon0": 8,
    "Tue1": 10,
    "Wed2": 11,
    "Thu3": 11,
    "Fri4": 11,
    "Sat5": 12,
    "Sun6": 14,
    "Mon7": 8,
    "Tue8": 10,
    "Wed9": 11,
    "Thu10": 11,
    "Fri11": 11,
    "Sat12": 12,
    "Sun13": 14})


physicians={}
physicians = {
    "A","B", "C","D", "E","F","G", "H","I","J","K", "L", "M","N","O", "Q", "P", "R", "S","T"
}
physicians = sorted(physicians)
#physician availability: defines on which day each employed physician is available.

availability = gp.tuplelist([
    ('A', 'Tue1'), ('A', 'Wed2'), ('A', 'Thu10'), ('A', 'Sun6'),
    ('A', 'Tue8'), ('A', 'Wed9'), ('A', 'Thu3'), ('A', 'Fri4'),('A', 'Sat5'),
    ('B', 'Mon0'), ('B', 'Tue1'),('B', 'Fri4'), ('B', 'Wed2'),('B', 'Sat5'),
    ('B', 'Thu3'),('C', 'Mon0'), ('C', 'Thu3'), ('C', 'Fri4'),('C', 'Sat5'),
    ('C', 'Sun6'), ('C', 'Mon7'),('C', 'Tue8'), ('C', 'Wed9'),
    ('C', 'Thu10'), ('C', 'Fri11'), ('C', 'Sat12'),('D', 'Tue2'),('D', 'Sat5'),
    ('D', 'Thu10'), ('D', 'Fri11'), ('D', 'Mon7'), ('D', 'Tue8'),('D', 'Sun6'),
    ('D', 'Sat12'),('D', 'Sun13'),('E', 'Mon0'), ('E', 'Tue1'), ('E', 'Thu3'),('E', 'Sat5'),
    ('E', 'Fri4'), ('E', 'Sun6'), ('E', 'Mon7'), ('E', 'Tue8'),
    ('F', 'Mon7'),('F', 'Tue8'), ('F', 'Fri11'), ('F', 'Sat12'),('F', 'Sat5'),
    ('F', 'Sun13'),('F', 'Sun6'),('G', 'Mon0'), ('G', 'Tue1'), ('G', 'Wed2'),
    ('G', 'Wed9'), ('G', 'Thu10'), ('G', 'Fri11'), ('G', 'Sat12'),('G', 'Sat5'),
    ('H', 'Sun13'),('H', 'Wed2'),('H', 'Thu3'), ('H', 'Fri4'),('H', 'Sat5'),
    ('H', 'Sun6'),('I', 'Thu3'),('I', 'Fri4'),('I', 'Mon7'),('I', 'Sat5'),
    ('I', 'Wed9'),('I', 'Sun13'),('J', 'Mon0'),('J', 'Mon7'),('J', 'Sat5'),
    ('J', 'Thu3'),('J', 'Sun6'), ('J', 'Thu10') , ('J', 'Sun13'),
    ('K', 'Mon0'), ('K', 'Tue1'), ('K', 'Wed2'), ('K', 'Thu3'),
    ('K', 'Thu10'), ('K', 'Fri11'), ('K', 'Sat12'), ('K', 'Sun6'),
    ('K', 'Sun13'),('L', 'Mon0'), ('L', 'Wed2'), ('L', 'Thu1'), 
    ('L', 'Sun6'), ('L', 'Tue8'), ('L', 'Sat12'), ('L', 'Sun13'),
    ('L', 'Wed9'), ('L', 'Thu3'), ('M', 'Mon0'), ('M', 'Wed2'), 
    ('M', 'Tue8'), ('M', 'Wed9'),('M', 'Thu10'),('M', 'Fri11'), 
    ('M', 'Sun13'), ('N', 'Tue1'),('N', 'Wed2'), ('N', 'Mon7'), 
    ('N', 'Wed9'), ('N', 'Thu3'),('N', 'Fri4'), ('N', 'Sat12'),
    ('N', 'Sun6'),('N', 'Sun13'), ('N', 'Sat5'),('O', 'Thu3'), 
    ('O', 'Thu10'), ('O', 'Sat5'),('O', 'Fri4'), ('O', 'Fri11'), 
    ('O', 'Sat12'), ('O', 'Sun6'), ('O', 'Tue1'), ('O', 'Mon7'),
    ('O', 'Wed9'),('P', 'Thu10'),  ('P', 'Fri4'), ('P', 'Fri11'),  
    ('P', 'Tue1'), ('P', 'Wed9'), ('P', 'Sun13'),('Q', 'Thu10'),
    ('Q', 'Fri11'), ('Q', 'Tue8'), ('Q', 'Wed9'), ('Q', 'Sat12'), 
    ('Q', 'Sun13'),('R', 'Thu10'),('R', 'Fri4'), ('R', 'Fri11'), 
    ('R', 'Tue1'), ('R', 'Wed2'), ('R', 'Tue8'), ('R', 'Wed9'),  
    ('R', 'Sat12'), ('R', 'Sun6'), ('R', 'Sun13'),('S', 'Thu10'), 
    ('S', 'Fri11'), ('S', 'Tue1'), ('S', 'Wed2'),('S', 'Tue8'),('S', 'Sat12'), 
    ('S', 'Sun6'),  ('S', 'Sun13'),('T', 'Wed2'), ('T', 'Thu3'), ('T', 'Fri4'), 
    ('T', 'Sat12'),  ('T', 'Sun6'),  ('T', 'Sun13')])

# Create initial model.
m = gp.Model("workforce5")

# Initialize assignment decision variables.

x = m.addVars(availability, vtype=GRB.BINARY, name="x")

# Slack decision variables determine the number of extra workers required to satisfy the requirements
# of each shift
slacks = m.addVars(shifts, name="Slack")

# Auxiliary variable totSlack to represent the total number of extra workers required to satisfy the
# requirements of all the shifts.
totSlack = m.addVar(name='totSlack')

# Auxiliary variable totShifts counts the total shifts worked by each employed physicians
totShifts = m.addVars(physicians, name="TotShifts")

# Constraint: All shifts requirements most be satisfied.

shift_reqmts = m.addConstrs((x.sum('*', s) + slacks[s] == shiftRequirements[s] for s in shifts),
                            name='shiftRequirement')

# Constraint: set the auxiliary variable (totSlack) equal to the total number of extra physicians
# required to satisfy shift requirements

num_temps = m.addConstr(totSlack == slacks.sum(), name='totSlack')

# Constraint: compute the total number of shifts for each physicians

num_shifts = m.addConstrs((totShifts[w] == x.sum(w, '*') for w in physicians), name='totShifts')

# Auxiliary variables.
# minShift is the minimum number of shifts allocated to physicians
# maxShift is the maximum number of shifts allocated to physicians

minShift = m.addVar(name='minShift')

maxShift = m.addVar(name='maxShift')

# Constraint:
# The addGenConstrMin() method of the model object m adds a new general constraint that
# determines the minimum value among a set of variables.
# The first argument is the variable whose value will be equal to the minimum of the other variables,
# minShift in this case.
# The second argument is the set variables over which the minimum will be taken, (totShifts) in
# this case.
# Recall that the totShifts variable is defined over the set of physicians and determines the number of
# shifts that an employed physicians will work. The third argument is the name of this constraint.

min_constr = m.addGenConstrMin(minShift, totShifts, name='minShift')

# Constraint:
# Similarly, the addGenConstrMax() method of the model object m adds a new general
# constraint that determines the maximum value among a set of variables.

max_constr = m.addGenConstrMax(maxShift, totShifts, name='maxShift')

# Set global sense for ALL objectives.
# This means that all objectives of the model object m are going to be minimized
m.ModelSense = GRB.MINIMIZE

# Set up primary objective.

# The setObjectiveN() method of the model object m allows to define multiple objectives.
# The first argument is the linear expression defining the most important objective, called primary
# objective, in this case it is the minimization of extra physicians required to satisfy shift requirements.
# The second argument is the index of the objective function, we set the index of the primary objective to be equal to 0.
# The third argument is the priority of the objective.
# The fourth argument is the relative tolerance to degrade this objective when a lower priority objective is optimized.
# The fifth argument is the name of this objective.
# A hierarchical or lexicographic approach assigns a priority to each objective, and optimizes
# for the objectives in decreasing priority order.
# For this problem, we have two objectives, and the primary objective has the highest priority
# which is equal to 2.
# When the secondary objective is minimized, since the relative tolerance is 0.2, we can only
# increase the minimum number of extra physicians up to 20%.
# For example if the minimum number extra physicians is 10, then when optimizing the secondary objective
# we can have up to 12 extra physicians.

m.setObjectiveN(totSlack, index=0, priority=2, reltol=0.2, name='TotalSlack')

# Set up secondary objective.

# The secondary objective is called fairness and its goal is to balance the workload assigned
# to the employed workers.
# To balance the workload assigned to the employed workers, we can minimize the difference
# between the maximum number of shifts assigned to an employed physicians and the minimum number
# of shifts assigned to an employed physicians.

m.setObjectiveN(maxShift - minShift, index=1, priority=1)

# Save model formulation for inspection

m.write('workforce.lp')

# Optimize
# This method runs the optimization engine to solve the MIP problem in the model object m
m.optimize()


# Print total slack and the number of shifts worked for each physicians
    # The KPIs for this optimization number is the number of extra worked required to satisfy
    # demand and the number of shifts that each employed physicians is working.

solution = {}
shifts_sol = {}
solution['Total slack required'] = str(totSlack.X)
assignments_all = {}
gant = {}
assignments = dict()

for [w, s] in availability:
    if x[w, s].x == 1:
        if w in assignments:
            assignments[w].append(s)
        else:
            assignments[w] = [s]

print(pd.DataFrame.from_records(list(solution.items()), columns=['KPI', 'Value']))
print('-' * 50)

for w in physicians:
    shifts_sol[w] = totShifts[w].X
    assignments_all[w] = assignments.get(w, [])

print('Shifts')
print(pd.DataFrame.from_records(list(shifts_sol.items()), columns=['Physician', 'Number of shifts']))

y_pos = pd.np.arange(len(shifts_sol.keys()))
plt.bar(y_pos, shifts_sol.values(), align='center')
plt.xticks(y_pos, shifts_sol.keys())
plt.show()

print('-' * 50)

for w in assignments_all:
    gant[w] = [w]
    for d in shifts:
        gant[w].append('*' if d in assignments_all[w] else '-')

print('Assignments')
print('Symbols: \'-\': not working, \'*\': working')
pd.set_option('display.width', 3000)
pd.set_option('display.max_columns',20)
print(pd.DataFrame.from_records(list(gant.values()), columns=['physicians'] + shifts))




