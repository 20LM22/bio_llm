from lark import Lark, Tree
from lark.visitors import Interpreter
from fastpunct import FastPunct

fastpunct = FastPunct()

# start at the highest level of the grammar: the omega
grammar = """
    ?start: omega
    ?u : gt
        | lt
        | err_bnd
        | d_gt
        | d_lt
        | d_err_bnd
    gt : s "(t)" ">" c
    lt : s "(t)" "<" c 
    err_bnd : "abs(" s "(t)" "-" c ")" "<" e
    d_gt : "d_" s "(t)" ">" D_C
    d_lt : "d_" s "(t)" "<" D_C
    d_err_bnd : "abs(" "d_" s "(t)" "-" D_C ")" "<" e

    ?e : ERROR
        | /[0-9]+/
    ERROR : "e"
    
    c : s "(" t_a ")"
        | C_LOW
        | C_MID
        | C_HIGH
        
    C_LOW : "c(low)"
    C_MID : "c(mid)"
    C_HIGH : "c(high)"
    
    D_C : "0"
        | "d_c(low)"
        | "d_c(high)"
        | "-d_c(low)" 
        | "-d_c(high)"
        
    ?phi : u
        | u_and_phi
        
    ?nu : u | u_implies_u | u_and_phi
    
    u_implies_u : u "→" u | psi "→" psi | psi "→" u | u "→" psi
    u_and_phi : u "^" phi
        
    ?psi : temp_op_fg | temp_op_g | temp_op_f
    
    temp_op_fg : "F" "[" t_a "," t_a "]" "G" "(" nu ")"
    temp_op_f : "F" "[" t_a "," t_a "]" "(" nu ")"
    temp_op_g : "G" "[" t_a "," t_a "]" "(" nu ")"
    
    ?omega : nu # this maybe shouldn't be a ?
        | psi
        | omega "^" omega
        
    t_a : /[0-9]+/
        | /T/
    s : /[a-zA-Z0-9]+/
    d_s : /d_[a-zA-Z0-9]+/

    %import common.WS
    %ignore WS

"""

nl_to_literal_dict = {
    "c(low)": "low",
    "c(mid)": "moderate",
    "c(high)": "high"
}

class Test(Interpreter):
    sentence = []
    F_flag = False
    G_flag = False
    FG_flag = False
    
    def clear(self):
        self.sentence = []
        self.F_flag = False
        self.G_flag = False
        self.FG_flag = False
    
    def omega(self, node):
        for i, child in enumerate(node.children):
            if i != 0:
                self.sentence.append(', and')
            self.visit(child) # visit each child predicate and add 'and' between each one
    
    def u_implies_u(self, node):
        self.sentence.append('if')
        self.visit(node.children[0])
        self.sentence.append('then')
        self.visit(node.children[1])
    
    def u(self, node):
        self.visit(node.children[0])
    
    def u_and_phi(self, node):
        for i, child in enumerate(node.children):
            if i != 0:
                self.sentence.append(', and')
            self.visit(child)

    def u_and_phi(self, node):
        for i, child in enumerate(node.children):
            if i != 0:
                self.sentence.append(', and')
            self.visit(child)
    
    def gt(self, node): # need a repeat of the info from the temporal operators section
        if self.FG_flag:
            self.sentence.append("eventually")
        self.sentence.append("the concentration of")
        self.sentence.append(node.children[0].children[0].value) # name of species --> would need to find and replace using the LLM's dictionary
        self.sentence.append("was")
        if self.G_flag or self.FG_flag:
            self.sentence.append("always")
        if self.F_flag:
            self.sentence.append("eventually")
        self.sentence.append("above")
        if isinstance(node.children[1].children[0], Tree): # len > 1 means further signals to break down for c-threshold
            time = node.children[1].children[1].children[0] # TODO: may be wrong
            if time == 'T':
                self.sentence.append('the final concentration of')
                self.sentence.append(node.children[1].children[0].children[0]) # TODO: may be wrong, supposed to be comparison SPECIES
            else:
                self.sentence.append('the concentration of')
                self.sentence.append(node.children[1].children[0].children[0]) # TODO: may be wrong, comparison SPECIES
                self.sentence.append('at day') # TODO: might want to replace day with dictionary item
                self.sentence.append(time)
        else:
            self.sentence.append('its')
            self.sentence.append(nl_to_literal_dict[node.children[1].children[0]]) # TODO: c-threshold --> take into account c vs. s
            self.sentence.append("levels")

        
    def lt(self, node):
        self.sentence.append("the concentration of")
        self.sentence.append(node.children[0].children[0]) # name of species --> would need to find and replace using the LLM's dictionary
        self.sentence.append("was below its")
        self.sentence.append(nl_to_literal_dict[node.children[1].children[0]]) # TODO: c-threshold --> take into account c vs. s
        self.sentence.append("levels")
        
    def err_bnd(self, node):
        self.sentence.append("the concentration of")
        self.sentence.append(node.children[0].children[0]) # SPECIES
        self.sentence.append("was within")
        self.sentence.append(node.children[2]) # EPSILON
        self.sentence.append("units of its")
        self.sentence.append(nl_to_literal_dict[node.children[1].children[0]]) # c-threshold --> also needs to take into account the difference between s and c
        self.sentence.append("levels")  

    def d_gt(self, node):
        self.sentence.append('the rate of change of the concentration of')
        self.sentence.append(node.children[0].children[0].value) # SPECIES
        match node.children[1]:
            case 'd_c(low)':
                self.sentence.append('was increasing faster than a low rate')
            case 'd_c(high)':
                self.sentence.append('was increasing faster than a high rate')
            case '-d_c(low)':
                self.sentence.append('was decreasing slower than a low rate')
            case '-d_c(high)':
                self.sentence.append('was decreasing slower than a high rate')
            case '0':
                self.sentence.append('was increasing')
        
    def d_lt(self, node):
        self.sentence.append('the rate of change of the concentration of')
        self.sentence.append(node.children[0].children[0].value) # SPECIES
        match node.children[1]:
            case 'd_c(low)':
                self.sentence.append('was increasing slower than a low rate')
            case 'd_c(high)':
                self.sentence.append('was increasing slower than a high rate')
            case '-d_c(low)':
                self.sentence.append('was decreasing faster than a low rate')
            case '-d_c(high)':
                self.sentence.append('was decreasing faster than a high rate')
            case '0':
                self.sentence.append('was decreasing')
        
    def d_err_bnd(self, node):
        self.sentence.append('the rate of change of the concentration of')
        self.sentence.append(node.children[0].children[0].value) # SPECIES
        self.sentence.append('was close to') # Maybe don't put in the value of epsilon because it's assumed to be small?
        match node.children[1]:
            case 'd_c(low)':
                self.sentence.append('a slow, increasing rate')
            case 'd_c(high)':
                self.sentence.append('a fast, increasing rate')
            case '-d_c(low)':
                self.sentence.append('a slow, decreasing rate')
            case '-d_c(high)':
                self.sentence.append('a fast, decreasing rate')
            case '0':
                self.sentence.append('0')
         
    def temp_op_g(self, node): # TODO: parametrize this entire thing to do F, G, FG at the same time
        self.sentence.append('from day') # TODO: change this to an input we get from the LLM's dictionary so it can be adaptable for [days], [was]
        self.sentence.append(node.children[0].children[0].value) # start time interval
        if node.children[1].children[0].value == 'T':
            self.sentence.append('onward')
        else:
            self.sentence.append('to')
            self.sentence.append(node.children[1].children[0].value) # end time interval

        match node.children[2].data: # operator description 
            case 'u_and_phi':
                # turn on G flag 
                self.G_flag = True 
                for i, child in enumerate(node.children[2].children):
                    if i != 0:
                        self.sentence.append(', and')
                    self.visit(child)
                self.G_flag = False
            case 'u_implies_u':
                self.visit(node.children[0])
                self.sentence.append('implies')
                self.visit(node.children[1])
            case "gt" :
                self.sentence.append("the concentration of")
                self.sentence.append(node.children[2].children[0].children[0].value) # name of species --> would need to find and replace using the LLM's dictionary
                self.sentence.append("was always above")
                if len(node.children[2].children[1].children) > 1: # length > 1 means there's further signals to break down 
                    time = node.children[2].children[1].children[1].children[0]
                    if time == 'T':
                        self.sentence.append('the final concentration of')
                        self.sentence.append(node.children[2].children[1].children[0].children[0]) # comparison SPECIES
                    else:    
                        self.sentence.append('the concentration of')
                        self.sentence.append(node.children[2].children[1].children[0].children[0]) # comparison SPECIES
                        self.sentence.append('at day') # TODO: might want to replace day with dictionary item
                        self.sentence.append(time)
                else:
                    self.sentence.append('its')
                    self.sentence.append(nl_to_literal_dict[node.children[2].children[1].children[0]])
                    self.sentence.append("levels")
            case "lt" :
                self.sentence.append("the concentration of")
                self.sentence.append(node.children[2].children[0].children[0].value) # name of species --> would need to find and replace using the LLM's dictionary
                self.sentence.append("was always below")
                if len(node.children[2].children[1].children) > 1: # length > 1 means there's further signals to break down 
                    time = node.children[2].children[1].children[1].children[0]
                    if time == 'T':
                        self.sentence.append('the final concentration of')
                        self.sentence.append(node.children[2].children[1].children[0].children[0]) # comparison SPECIES
                    else:    
                        self.sentence.append('the concentration of')
                        self.sentence.append(node.children[2].children[1].children[0].children[0]) # comparison SPECIES
                        self.sentence.append('at day') # TODO: might want to replace day with dictionary item
                        self.sentence.append(time)
                else:
                    self.sentence.append('its')
                    self.sentence.append(nl_to_literal_dict[node.children[2].children[1].children[0]])
                    self.sentence.append("levels")
            case "err_bnd" :
                self.sentence.append("the concentration of")
                self.sentence.append(node.children[2].children[0].children[0].value) # name of species --> would need to find and replace using the LLM's dictionary
                self.sentence.append("was always close to")
                if len(node.children[2].children[1].children) > 1: # length > 1 means there's further signals to break down 
                    time = node.children[2].children[1].children[1].children[0]
                    if time == 'T':
                        self.sentence.append('the final concentration of')
                        self.sentence.append(node.children[2].children[1].children[0].children[0]) # comparison SPECIES
                    else:    
                        self.sentence.append('the concentration of')
                        self.sentence.append(node.children[2].children[1].children[0].children[0]) # comparison SPECIES
                        self.sentence.append('at day') # TODO: might want to replace day with dictionary item
                        self.sentence.append(time)
                else:
                    self.sentence.append('its')
                    self.sentence.append(nl_to_literal_dict[node.children[2].children[1].children[0]])
                    self.sentence.append("levels")
            case "d_gt" : # s and D_C
                self.sentence.append('the rate of change of the concentration of')
                self.sentence.append(node.children[2].children[0].children[0].value) # SPECIES
                match node.children[2].children[1]: # D_C
                    case 'd_c(low)':
                        self.sentence.append('was always increasing faster than a low rate')
                    case 'd_c(high)':
                        self.sentence.append('was always increasing faster than a high rate')
                    case '-d_c(low)':
                        self.sentence.append('was always decreasing slower than a low rate')
                    case '-d_c(high)':
                        self.sentence.append('was always decreasing slower than a high rate')
                    case '0':
                        self.sentence.append('was always increasing')
            case "d_lt" :
                self.sentence.append('the rate of change of the concentration of')
                self.sentence.append(node.children[2].children[0].children[0].value) # SPECIES
                match node.children[2].children[1]: # D_C
                    case 'd_c(low)':
                        self.sentence.append('was always increasing slower than a low rate')
                    case 'd_c(high)':
                        self.sentence.append('was always increasing slower than a high rate')
                    case '-d_c(low)':
                        self.sentence.append('was always decreasing faster than a low rate')
                    case '-d_c(high)':
                        self.sentence.append('was always decreasing faster than a high rate')
                    case '0':
                        self.sentence.append('was always decreasing')
            case "d_err_bnd" : # s, D_C, e
                self.sentence.append('the rate of change of the concentration of')
                self.sentence.append(node.children[2].children[0].children[0].value) # SPECIES
                self.sentence.append('was always close to') # Maybe don't put in the value of epsilon because it's assumed to be small?
                match node.children[2].children[1]: # D_C
                    case 'd_c(low)':
                        self.sentence.append('a slow, increasing rate')
                    case 'd_c(high)':
                        self.sentence.append('a fast, increasing rate')
                    case '-d_c(low)':
                        self.sentence.append('a slow, decreasing rate')
                    case '-d_c(high)':
                        self.sentence.append('a fast, decreasing rate')
                    case '0':
                        self.sentence.append('0')

    def temp_op_f(self, node): # TODO: parametrize this entire thing to do F, G, FG at the same time
        self.sentence.append('from day') # TODO: change this to an input we get from the LLM's dictionary so it can be adaptable for [days], [was]
        self.sentence.append(node.children[0].children[0].value) # start time interval
        if node.children[1].children[0].value == 'T':
            self.sentence.append('onward')
        else:
            self.sentence.append('to')
            self.sentence.append(node.children[1].children[0].value) # end time interval

        match node.children[2].data: # operator description 
            case 'u_and_phi':
                # turn on F flag 
                self.F_flag = True 
                for i, child in enumerate(node.children[2].children):
                    if i != 0:
                        self.sentence.append(', and')
                    self.visit(child)
                self.F_flag = False
            case 'u_implies_u':
                self.visit(node.children[0])
                self.sentence.append('implies')
                self.visit(node.children[1])
            case "gt" :
                self.sentence.append("the concentration of")
                self.sentence.append(node.children[2].children[0].children[0].value) # name of species --> would need to find and replace using the LLM's dictionary
                self.sentence.append("was eventually above")
                if len(node.children[2].children[1].children) > 1: # length > 1 means there's further signals to break down 
                    time = node.children[2].children[1].children[1].children[0]
                    if time == 'T':
                        self.sentence.append('the final concentration of')
                        self.sentence.append(node.children[2].children[1].children[0].children[0]) # comparison SPECIES
                    else:    
                        self.sentence.append('the concentration of')
                        self.sentence.append(node.children[2].children[1].children[0].children[0]) # comparison SPECIES
                        self.sentence.append('at day') # TODO: might want to replace day with dictionary item
                        self.sentence.append(time)
                else:
                    self.sentence.append('its')
                    self.sentence.append(nl_to_literal_dict[node.children[2].children[1].children[0]])
                    self.sentence.append("levels")
            case "lt" :
                self.sentence.append("the concentration of")
                self.sentence.append(node.children[2].children[0].children[0].value) # name of species --> would need to find and replace using the LLM's dictionary
                self.sentence.append("was eventually below")
                if len(node.children[2].children[1].children) > 1: # length > 1 means there's further signals to break down 
                    time = node.children[2].children[1].children[1].children[0]
                    if time == 'T':
                        self.sentence.append('the final concentration of')
                        self.sentence.append(node.children[2].children[1].children[0].children[0]) # comparison SPECIES
                    else:    
                        self.sentence.append('the concentration of')
                        self.sentence.append(node.children[2].children[1].children[0].children[0]) # comparison SPECIES
                        self.sentence.append('at day') # TODO: might want to replace day with dictionary item
                        self.sentence.append(time)
                else:
                    self.sentence.append('its')
                    self.sentence.append(nl_to_literal_dict[node.children[2].children[1].children[0]])
                    self.sentence.append("levels")
            case "err_bnd" :
                self.sentence.append("the concentration of")
                self.sentence.append(node.children[2].children[0].children[0].value) # name of species --> would need to find and replace using the LLM's dictionary
                self.sentence.append("was eventually close to")
                if len(node.children[2].children[1].children) > 1: # length > 1 means there's further signals to break down 
                    time = node.children[2].children[1].children[1].children[0]
                    if time == 'T':
                        self.sentence.append('the final concentration of')
                        self.sentence.append(node.children[2].children[1].children[0].children[0]) # comparison SPECIES
                    else:    
                        self.sentence.append('the concentration of')
                        self.sentence.append(node.children[2].children[1].children[0].children[0]) # comparison SPECIES
                        self.sentence.append('at day') # TODO: might want to replace day with dictionary item
                        self.sentence.append(time)
                else:
                    self.sentence.append('its')
                    self.sentence.append(nl_to_literal_dict[node.children[2].children[1].children[0]])
                    self.sentence.append("levels")
            case "d_gt" : # s and D_C
                self.sentence.append('the rate of change of the concentration of')
                self.sentence.append(node.children[2].children[0].children[0].value) # SPECIES
                match node.children[2].children[1]: # D_C
                    case 'd_c(low)':
                        self.sentence.append('was eventually increasing faster than a low rate')
                    case 'd_c(high)':
                        self.sentence.append('was eventually increasing faster than a high rate')
                    case '-d_c(low)':
                        self.sentence.append('was eventually decreasing slower than a low rate')
                    case '-d_c(high)':
                        self.sentence.append('was eventually decreasing slower than a high rate')
                    case '0':
                        self.sentence.append('was eventually increasing')
            case "d_lt" :
                self.sentence.append('the rate of change of the concentration of')
                self.sentence.append(node.children[2].children[0].children[0].value) # SPECIES
                match node.children[2].children[1]: # D_C
                    case 'd_c(low)':
                        self.sentence.append('was eventually increasing slower than a low rate')
                    case 'd_c(high)':
                        self.sentence.append('was eventually increasing slower than a high rate')
                    case '-d_c(low)':
                        self.sentence.append('was eventually decreasing faster than a low rate')
                    case '-d_c(high)':
                        self.sentence.append('was eventually decreasing faster than a high rate')
                    case '0':
                        self.sentence.append('was eventually decreasing')
            case "d_err_bnd" : # s, D_C, e
                self.sentence.append('the rate of change of the concentration of')
                self.sentence.append(node.children[2].children[0].children[0].value) # SPECIES
                self.sentence.append('was eventually close to') # Maybe don't put in the value of epsilon because it's assumed to be small?
                match node.children[2].children[1]: # D_C
                    case 'd_c(low)':
                        self.sentence.append('a slow, increasing rate')
                    case 'd_c(high)':
                        self.sentence.append('a fast, increasing rate')
                    case '-d_c(low)':
                        self.sentence.append('a slow, decreasing rate')
                    case '-d_c(high)':
                        self.sentence.append('a fast, decreasing rate')
                    case '0':
                        self.sentence.append('0')

    def temp_op_fg(self, node): # TODO: parametrize this entire thing to do F, G, FG at the same time
        self.sentence.append('from day') # TODO: change this to an input we get from the LLM's dictionary so it can be adaptable for [days], [was]
        self.sentence.append(node.children[0].children[0].value) # start time interval
        if node.children[1].children[0].value == 'T':
            self.sentence.append('onward')
        else:
            self.sentence.append('to')
            self.sentence.append(node.children[1].children[0].value) # end time interval

        match node.children[2].data: # operator description 
            case 'u_and_phi':
                # turn on FG flag 
                self.FG_flag = True 
                for i, child in enumerate(node.children[2].children):
                    if i != 0:
                        self.sentence.append(', and')
                    self.visit(child)
                self.FG_flag = False
            case 'u_implies_u':
                self.visit(node.children[0])
                self.sentence.append('implies')
                self.visit(node.children[1])
            case "gt" :
                self.sentence.append("eventually the concentration of")
                self.sentence.append(node.children[2].children[0].children[0].value) # name of species --> would need to find and replace using the LLM's dictionary
                self.sentence.append("was always above")
                if len(node.children[2].children[1].children) > 1: # length > 1 means there's further signals to break down 
                    time = node.children[2].children[1].children[1].children[0]
                    if time == 'T':
                        self.sentence.append('the final concentration of')
                        self.sentence.append(node.children[2].children[1].children[0].children[0]) # comparison SPECIES
                    else:    
                        self.sentence.append('the concentration of')
                        self.sentence.append(node.children[2].children[1].children[0].children[0]) # comparison SPECIES
                        self.sentence.append('at day') # TODO: might want to replace day with dictionary item
                        self.sentence.append(time)
                else:
                    self.sentence.append('its')
                    self.sentence.append(nl_to_literal_dict[node.children[2].children[1].children[0]])
                    self.sentence.append("levels")
            case "lt" :
                self.sentence.append("eventually the concentration of")
                self.sentence.append(node.children[2].children[0].children[0].value) # name of species --> would need to find and replace using the LLM's dictionary
                self.sentence.append("was always below")
                if len(node.children[2].children[1].children) > 1: # length > 1 means there's further signals to break down 
                    time = node.children[2].children[1].children[1].children[0]
                    if time == 'T':
                        self.sentence.append('the final concentration of')
                        self.sentence.append(node.children[2].children[1].children[0].children[0]) # comparison SPECIES
                    else:    
                        self.sentence.append('the concentration of')
                        self.sentence.append(node.children[2].children[1].children[0].children[0]) # comparison SPECIES
                        self.sentence.append('at day') # TODO: might want to replace day with dictionary item
                        self.sentence.append(time)
                else:
                    self.sentence.append('its')
                    self.sentence.append(nl_to_literal_dict[node.children[2].children[1].children[0]])
                    self.sentence.append("levels")
            case "err_bnd" :
                self.sentence.append("eventually the concentration of")
                self.sentence.append(node.children[2].children[0].children[0].value) # name of species --> would need to find and replace using the LLM's dictionary
                self.sentence.append("was always close to")
                if len(node.children[2].children[1].children) > 1: # length > 1 means there's further signals to break down 
                    time = node.children[2].children[1].children[1].children[0]
                    if time == 'T':
                        self.sentence.append('the final concentration of')
                        self.sentence.append(node.children[2].children[1].children[0].children[0]) # comparison SPECIES
                    else:    
                        self.sentence.append('the concentration of')
                        self.sentence.append(node.children[2].children[1].children[0].children[0]) # comparison SPECIES
                        self.sentence.append('at day') # TODO: might want to replace day with dictionary item
                        self.sentence.append(time)
                else:
                    self.sentence.append('its')
                    self.sentence.append(nl_to_literal_dict[node.children[2].children[1].children[0]])
                    self.sentence.append("levels")
            case "d_gt" : # s and D_C
                self.sentence.append('eventually the rate of change of the concentration of')
                self.sentence.append(node.children[2].children[0].children[0].value) # SPECIES
                match node.children[2].children[1]: # D_C
                    case 'd_c(low)':
                        self.sentence.append('was always increasing faster than a low rate')
                    case 'd_c(high)':
                        self.sentence.append('was always increasing faster than a high rate')
                    case '-d_c(low)':
                        self.sentence.append('was always decreasing slower than a low rate')
                    case '-d_c(high)':
                        self.sentence.append('was always decreasing slower than a high rate')
                    case '0':
                        self.sentence.append('was always increasing')
            case "d_lt" :
                self.sentence.append('eventually the rate of change of the concentration of')
                self.sentence.append(node.children[2].children[0].children[0].value) # SPECIES
                match node.children[2].children[1]: # D_C
                    case 'd_c(low)':
                        self.sentence.append('was always increasing slower than a low rate')
                    case 'd_c(high)':
                        self.sentence.append('was always increasing slower than a high rate')
                    case '-d_c(low)':
                        self.sentence.append('was always decreasing faster than a low rate')
                    case '-d_c(high)':
                        self.sentence.append('was always decreasing faster than a high rate')
                    case '0':
                        self.sentence.append('was always decreasing')
            case "d_err_bnd" : # s, D_C, e
                self.sentence.append('eventually the rate of change of the concentration of')
                self.sentence.append(node.children[2].children[0].children[0].value) # SPECIES
                self.sentence.append('was always close to') # Maybe don't put in the value of epsilon because it's assumed to be small?
                match node.children[2].children[1]: # D_C
                    case 'd_c(low)':
                        self.sentence.append('a slow, increasing rate')
                    case 'd_c(high)':
                        self.sentence.append('a fast, increasing rate')
                    case '-d_c(low)':
                        self.sentence.append('a slow, decreasing rate')
                    case '-d_c(high)':
                        self.sentence.append('a fast, decreasing rate')
                    case '0':
                        self.sentence.append('0')

p = Lark(grammar)

# input_stl = 'G[1,14] (tnf(t) < c(mid) ^ abs(tnf(t) - c(mid)) < 3)'
# input_stl = 'G[1,14] (tnf(t) < c(mid)) ^ G[15,T] (d_tnf(t) < d_c(low))'

input_sentences = ['G[6,7] ( l(t) > c(high) ) ^ G[7,T] ( d_I(t) < 0 )',
'G[6,7] ( l(t) > l(T) ) ^ G[7,T] ( I(t) < c(high) )',
'G[6,7] ( l(t) > c(high) ) ^ F[7,T] G ( I(t) < c(low) )',
'G[1,7] ( b(t) > b(T) ) ^ F[8,14] ( b(t) > c(high) ) ^ G[15,T] ( b(t) < c(mid) )',
'G[1,7] ( d_b(t) > 0 ^ d_r(t) > 0) ^ F[8, 14] ( b(t) > s(7) ^ r(t) > c(high) ) ^ F[15,T] ( b(t) < c(low) ^ r(t) < c(low) )',
'G[1,7] ( a(t) > c(mid) ) ^ G[8,14] (a(t) > c(mid) ) ^ G[15,T] ( a(t) < c(mid) )',
'G[1,14] ( a(t) < c(mid) ) ^ G[15, T] ( d_a(t) < 0 )',
'G[1,14] ( a(t) < c(mid) ) ^ F[15,T] ( a(t) < c(low) )',
'G[1,7] ( I(t) > c(high) ) ^ G[8,14] ( l(t) > c(high) ) ^ G[15, T] ( l(t) > c(high) )',
'G[0,T] ( l(t) > c(high) )',
'G[8,T] ( b(t) > c(mid) ) ^ G[1,7] ( b(t) < c(mid) )',
'G[8,14] ( b(t) > b(0) )',
'F[15,T] ( l(t) > c(high) ) ^ G[1,14] ( l(t) < c(high) )',
'v(t) > c(low) → F[0,1] ( I(t) > c(high) )',
'v(t) > c(low) → F[0,1] ( a(t) > c(high)  ^ b(t) > c(high) )',
'G[14,T] ( v(t) < c(low) ^ l(t) > c(mid) ^ rn(t) > c(mid) )']

tester = Test()
output_sentences = []

for input in input_sentences:
    print(f'Input: {input}')
    tree = p.parse(input)
    # print(tree.pretty())
    tester.clear()
    tester.visit(tree)
    output_sentences.append(" ".join(tester.sentence))
    # print(f'Output: {" ".join(tester.sentence)}\n')
    
output_sentences = fastpunct.punct(output_sentences)
print(output_sentences)