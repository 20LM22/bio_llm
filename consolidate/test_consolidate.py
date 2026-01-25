from z3 import *
from lark import Lark, Tree
import json

with open(f'../config/config_nx_2_ny_2_nz_18_prelim_set.json') as f:
    params = json.load(f)
grammar = params['grammar']
parser = Lark(grammar, propagate_positions=True)

def split_outermost(stl_str, parser):
    tree = parser.parse(stl_str)
    pieces = []

    def collect(node, parent=None):
        # Case 1: always split omega_and_omega
        if isinstance(node, Tree) and node.data == "omega_and_omega":
            for child in node.children:
                collect(child, node)
            return

        # Case 2: split u_and_u iff parent is omega
        if (
            isinstance(node, Tree)
            and node.data == "u_and_u"
            and isinstance(parent, Tree)
            and parent.data == "omega"
        ):
            print("we found a u_and_u that needs to be split")
            for child in node.children:
                start = child.meta.start_pos
                end = child.meta.end_pos
                pieces.append(stl_str[start:end])
                # collect(child, node)
            return

        # Case 3: atomic omega
        if isinstance(node, Tree) and node.data == "omega" and node.children[0].data != "omega_and_omega" and node.children[0].data != "u_and_u":
            print("i am inside omega")
            start = node.meta.start_pos
            end = node.meta.end_pos
            pieces.append(stl_str[start:end])
            return

        # Otherwise: recurse (do NOT collect here)
        if isinstance(node, Tree):
            print("i am recursing")
            for child in node.children:
                collect(child, node)

    collect(tree)
    print(f"number of elements in pieces: {len(pieces)}")
    print(f"pieces: {pieces}")
    return [p.strip() for p in pieces]

sentence = "IL1RN(t)=c(high) and IL1RN(t)=c(low)"
# and eventually[15,21](IL1RN(t)=c(high)) and eventually[22,28](IL1RN(t)=c(high))"
tree = parser.parse(sentence)
print(tree)

try:
    stl_pieces = split_outermost(sentence, parser)
    print("stl pieces")
    print(f"{stl_pieces}")
    # print("split!")
except Exception as e:
    print("exception")
    print(f"{e}")

# for piece in stl_pieces:
#     parsed_piece = parser.parse(piece)
#     species_list = get_species_list_STL2literal(parsed_piece)
#     bin_dict[species_list].append({
#         "stl": piece,
#         "absorbed": 0
#     })


# T = 3
# x = [Real(f"x_{t}") for t in range(T)]
# # this creates 6 different variables called x_0, x_1, etc.
# solver = Solver()

# # Encode phi = F[0,3]G(x > 0)
# # "there exists t0 such that for all t>=t0: x[t] > 0"
# t0 = Int("t0")
# phi = And(t0 >= 0, t0 <= T,
#           And([Implies(t >= t0, x[t] > 0) for t in range(T)]))

# # Encode psi = F[0,3](x > -1)
# # "there exists t with x[t] > -1"
# psi = Or([x[t] > -1 for t in range(T+1)])

# encode psi implies psi **draw out the diagram

# # To check phi <=> psi, check Not(phi == psi) --> if not satisfiable then it's because the statements must be the same
# solver.add(Not(phi == psi))

# print(solver.check())
# if solver.check() == sat:
#     print("They are NOT equivalent!:")
#     print(solver.model())
# else:
#     print("They are equivalent!:")

"""
?start: omega
?u: gt | lt | eq | d_gt | d_lt | d_eq
gt: s \"(t)\" \">\" c
lt: s \"(t)\" \"<\" c
eq: s \"(t)\" \"=\" c
d_gt: \"d_\" s \"(t)\" \">\" D_C
d_lt: \"d_\" s \"(t)\" \"<\" D_C
d_eq: \"d_\" s \"(t)\" \"=\" D_C
c: s \"(\" t_a \")\" | C_LOW | C_MID | C_HIGH
C_LOW: \"c(low)\"\nC_MID: \"c(mid)\"
C_HIGH: \"c(high)\"
D_C : \"0\" | \"d_c(low)\" | \"d_c(high)\" | \"-d_c(low)\" | \"-d_c(high)\"
?nu : u | u_implies_u | u_and_u\nu_implies_u: u \"implies\" u
u_and_u: u \"and\" u
?psi: temp_op_fg | temp_op_g | temp_op_f
temp_op_fg: \"eventually\" \"[\" t_a \",\" t_a \"]\" \"globally\" \"(\" nu \")\"
temp_op_f: \"eventually\" \"[\" t_a \",\" t_a \"]\" \"(\" nu \")\"
temp_op_g: \"globally\" \"[\" t_a \",\" t_a \"]\" \"(\" nu \")\"
omega: nu | psi | omega_and_omega | psi_implies_psi
omega_and_omega: omega \"and\" omega
psi_implies_psi: psi \"implies\" psi
TANUM: /[0-9]+/
INFINITY: \"inf\" | \"∞\"
t_a: TANUM | INFINITY
s: /[\\w]+/
d_s: /d_[\\w]+/
"""