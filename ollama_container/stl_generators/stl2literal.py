from lark import Lark, Tree
from lark.visitors import Interpreter
# from fastpunct import FastPunct

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
    
    def __init__(self):
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

# fastpunct = FastPunct() # TODO: might have to be moved into the function def?

def STL2literal(input_sentence, grammar):
    p = Lark(grammar) # TODO: this is also slow, improve if possible
    tree = p.parse(input_sentence)
    tester = Test() # TODO: this is redundant, see if this can be improved
    tester.visit(tree)
    # return fastpunct.punct(" ".join(tester.sentence))
    return ' '.join(tester.sentence)
