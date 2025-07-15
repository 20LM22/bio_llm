from lark import Lark, Visitor
from lark.visitors import Visitor_Recursive

# ## TEST THIS
# start: WORD "hello"
# WORD: /\w+/
# ### --> map the literals to symbols

# start at the highest level of the grammar: the omega
grammar = """
    ?start: omega
    u : s"(t) < "c
        | s"(t) > "c 
        | "abs("s"(t) - "c") < "e
        | d_s"(t) > "d_c
        | d_s"(t) < "d_c
        | "abs("d_s"(t) - "d_c") < "e
    e : "e"
        | /[0-9]+/
    c : "s("t_a")"
        | "c(low)"
        | "c(mid)"
        | "c(high)"
    d_c : "0" 
        | "d_c(low)"
        | "d_c(high)" 
        | "-d_c(low)" 
        | "-d_c(high)"
    ?phi : u
        | phi" ^ "phi
        | phi" → "phi
    psi : "F["t_a","t_a"] G("phi")"
        | "G["t_a","t_a"] ("phi")"
        | "F["t_a","t_a"] ("phi")"
    ?omega : phi
        | psi
        | omega" ^ "omega
    t_a : /[0-9]+/
        | "T"
    s : /[a-zA-z0-9]+/
    d_s : "d_"/[a-zA-z0-9]+/
"""

class Test_Visitor(Visitor_Recursive):
    def u(self, tree): # the methods have to be rules in the grammar
        print(tree.children)
        # assert tree.data == "number"
        # tree.children[0] += 1
    def t_a(self, tree):
        print(tree.children)
        # assert tree.data == "number"
        # tree.children[0] += 1

p = Lark(grammar)

input_stl = 'G[1,14] (tnf(t) < c(mid)) ^ G[15,T] (d_tnf(t) < 0)'
# print(f'type of response is: {type(p.parse(input_stl))}')
# 'type of response is: {type(p.parse(input_stl))}'
# print(p.parse(input_stl).pretty())

res = p.parse(input_stl)

print(res)
# Test_Visitor().visit(tree)