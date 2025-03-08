from z3 import *

# Declare integer variables
length = Int('length')
i_0 = Int('i_0')
count_0 = Int('count_0')
n_0 = Int('n_0')
i_1 = Int('i_1')
count_1 = Int('count_1')
n_1 = Int('n_1')
i_2 = Int('i_2')
count_2 = Int('count_2')
n_2 = Int('n_2')
i_3 = Int('i_3')
count_3 = Int('count_3')

# Create a solver
solver = Solver()

# Add constraints
solver.add(length == 3)
solver.add(i_0 == 0)
solver.add(count_0 == 0)
solver.add(n_0 > 0)
solver.add(count_1 == count_0 + If(n_0 > 0, 1, 0))
solver.add(i_1 == i_0 + 1)
solver.add(n_1 > 0)
solver.add(count_2 == count_1 + If(n_1 > 0, 1, 0))
solver.add(i_2 == i_1 + 1)
solver.add(n_2 > 0)
solver.add(count_3 == count_2 + If(n_2 > 0, 1, 0))
solver.add(i_3 == i_2 + 1)
solver.add(count_3 == i_3)

# Check satisfiability and print the model
if solver.check() == sat:
    model = solver.model()
    for var in [length, i_0, count_0, n_0, i_1, count_1, n_1, i_2, count_2, n_2, i_3, count_3]:
        print(f"{var} = {model[var]}")
    print("AllPositive")
else:
    print("Unsatisfiable")
