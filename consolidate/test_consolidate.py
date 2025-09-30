from dreal import *

# Declare time and signal
t1 = Variable("t1")
t2 = Variable("t2")
phi1 = Function("phi1", t1)  # uninterpreted function phi1(t)

# Formula 1: F_[1,5] (phi1 > 0)
phi1_pos = Exists([t1], And(t1 >= 1, t1 <= 5, phi1 > 0))

# Formula 2: F_[2,4] (phi1 > 1)
phi1_gt1 = Exists([t2], And(t2 >= 2, t2 <= 4, phi1 > 1))

# Check redundancy: (φ1 ∧ ¬φ2) satisfiable?
f = And(phi1_pos, Not(phi1_gt1))

# Call dReal delta-solver
result = CheckSatisfiability(f, 0.001)

if result:
    print("SAT with witness:", result)
    print("→ φ2 is NOT redundant (counterexample exists).")
else:
    print("UNSAT")
    print("→ φ2 is redundant given φ1.")