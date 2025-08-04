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
        STL2literal('','')

    def omega(self, node):
        print(f'node.children: {node.children}')
        if node.children[0] == psi_and_psi:
            print("psi and psi")
        elif node.children[0] == nu:
            print("nu")
        elif node.children[0] == psi:
            print("psi")
        elif node.children[0] == omega_and_omega:
            print("omega and omega")
        else:
            print("wrong")
        """
        for i, child in enumerate(node.children):
            if i != 0:
                self.sentence.append(', and')
            self.visit(child) # visit each child predicate and add 'and' between each one
        """
    
    def start(self, node):
        print("start located")

    def u_implies_u(self, node):
        self.sentence.append('if')
        self.visit(node.children[0])
        self.sentence.append('then')
        self.visit(node.children[1])
    
    def u(self, node):
        self.visit(node.children[0])
    
    def u_and_u(self, node):
        for i, child in enumerate(node.children):
            if i != 0:
                self.sentence.append(', and')
            self.visit(child)
    
    def gt(self, node): # need a repeat of the info from the temporal operators section
        if self.FG_flag:
            self.sentence.append("eventually")
        # self.sentence.append("the concentration of")
        self.sentence.append(node.children[0].children[0].value) # name of species --> would need to find and replace using the LLM's dictionary
        self.sentence.append("was")
        if self.G_flag or self.FG_flag:
            self.sentence.append("always")
        if self.F_flag:
            self.sentence.append("eventually")
        self.sentence.append("above")
        if isinstance(node.children[1].children[0], Tree): # len > 1 means further signals to break down for c-threshold
            time = node.children[1].children[1].children[0] # TODO: may be wrong
            if time == '∞':
                self.sentence.append('the final level of')
                self.sentence.append(node.children[1].children[0].children[0]) # TODO: may be wrong, supposed to be comparison SPECIES
            else:
                # self.sentence.append('the concentration of')
                self.sentence.append(node.children[1].children[0].children[0]) # TODO: may be wrong, comparison SPECIES
                self.sentence.append('at day') # TODO: might want to replace day with dictionary item
                self.sentence.append(time)
        else:
            self.sentence.append('its')
            self.sentence.append(nl_to_literal_dict[node.children[1].children[0]]) # TODO: c-threshold --> take into account c vs. s
            self.sentence.append("levels")

        
    def lt(self, node):
        # self.sentence.append("the concentration of")
        # print("inside lt")
        # print(f'node.children[0]: {node.children[0]}')
        # print(f'node.children[0].children: {node.children[0].children}')

        self.sentence.append(node.children[0].children[0]) # name of species --> would need to find and replace using the LLM's dictionary
        self.sentence.append("was below its")
        self.sentence.append(nl_to_literal_dict[node.children[1].children[0]]) # TODO: c-threshold --> take into account c vs. s
        self.sentence.append("levels")
        
    def eq(self, node):
        # self.sentence.append("the concentration of")
        self.sentence.append(node.children[0].children[0]) # SPECIES
        self.sentence.append("was close to")
        # self.sentence.append("was within")
        # self.sentence.append(node.children[2]) # EPSILON
        # self.sentence.append("units of its")
        self.sentence.append("its")
        self.sentence.append(nl_to_literal_dict[node.children[1].children[0]]) # c-threshold --> also needs to take into account the difference between s and c
        self.sentence.append("levels")  

    def d_gt(self, node):
        self.sentence.append("the rate of change of")
        # self.sentence.append('the rate of change of the concentration of')
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
        # self.sentence.append('the rate of change of the concentration of')
        self.sentence.append('the rate of change of')
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
        
    def d_eq(self, node):
        # self.sentence.append('the rate of change of the concentration of')
        self.sentence.append('the rate of change of')
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
        if node.children[1].children[0].value == '∞':
            self.sentence.append('onward')
        else:
            self.sentence.append('to')
            self.sentence.append(node.children[1].children[0].value) # end time interval

        match node.children[2].data: # operator description 
            case 'u_and_u':
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
            case _:
                self.visit(node.children[2])
    
    def temp_op_f(self, node): # TODO: parametrize this entire thing to do F, G, FG at the same time
        self.sentence.append('from day') # TODO: change this to an input we get from the LLM's dictionary so it can be adaptable for [days], [was]
        self.sentence.append(node.children[0].children[0].value) # start time interval
        if node.children[1].children[0].value == '∞':
            self.sentence.append('onward')
        else:
            self.sentence.append('to')
            self.sentence.append(node.children[1].children[0].value) # end time interval

        match node.children[2].data: # operator description 
            case 'u_and_u':
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
            case _:
                self.visit(node.children[2])
 
    def temp_op_fg(self, node): # TODO: parametrize this entire thing to do F, G, FG at the same time
        self.sentence.append('from day') # TODO: change this to an input we get from the LLM's dictionary so it can be adaptable for [days], [was]
        self.sentence.append(node.children[0].children[0].value) # start time interval
        if node.children[1].children[0].value == '∞':
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
            case _:
                self.visit(node.children[2])

species_dict = {
'IL-6': 'IL6',
'IL-12': 'IL12',
'IL-1β': 'IL1β',
'IL-1Ra': 'IL1Ra',
'TNF-α': 'TNFα',
'IL-8': 'IL8',
'IFN-α': 'IFNα',
'IFN-β': 'IFNβ',
'SARS-CoV-2': 'SARSCoV2',
'IL1RN': 'IL1RN',
'IL1RA': 'IL1Ra'
}

def STL2literal(input_sentence, grammar):
    # TODO: remove this grammar
    grammar = "?start: omega\n?u: gt | lt | eq | d_gt | d_lt | d_eq\ngt: s \"(t)\" \">\" c\nlt: s \"(t)\" \"<\" c\neq: s \"(t)\" \"=\" c\nd_gt: \"d_\" s \"(t)\" \">\" D_C\nd_lt: \"d_\" s \"(t)\" \"<\" D_C\nd_eq: \"d_\" s \"(t)\" \"=\" D_C\nc: s \"(\" t_a \")\" | C_LOW | C_MID | C_HIGH\nC_LOW: \"c(low)\"\nC_MID: \"c(mid)\"\nC_HIGH: \"c(high)\"\nD_C : \"0\" | \"d_c(low)\" | \"d_c(high)\" | \"-d_c(low)\" | \"-d_c(high)\"\n?nu : u | u_implies_u | u_and_u\nu_implies_u: u \"implies\" u\nu_and_u: u \"and\" u\n?psi: temp_op_fg | temp_op_g | temp_op_f\ntemp_op_fg: \"eventually\" \"[\" t_a \",\" t_a \"]\" \"globally\" \"(\" nu \")\"\ntemp_op_f: \"eventually\" \"[\" t_a \",\" t_a \"]\" \"(\" nu \")\"\ntemp_op_g: \"globally\" \"[\" t_a \",\" t_a \"]\" \"(\" nu \")\"\nomega: nu | psi | omega_and_omega | psi_implies_psi\nomega_and_omega: omega \"and\" omega\npsi_implies_psi: psi \"implies\" psi\nt_a: /[0-9]+/ | \"inf\" | /∞/\ns: /[\\w]+/\nd_s: /d_[\\w]+/\n%import common.WS\n%ignore WS"

    p = Lark(grammar) # TODO: this is also slow, improve if possible

    # TODO: remove this once done testing
    input_sentence = 'globally[1,2](d_IL6(t)>d_c(high))implieseventually[3,4](IL8(t)>c(high))'
    
    tree = p.parse(input_sentence)
    # print(f'this is what the tree looks like: {tree}')
    tester = Test() # TODO: this is redundant, see if this can be improved
    tester.visit(tree)

    # print(f'the tree is: {tree}')

    tester.sentence = ' '.join(tester.sentence)

    for key in species_dict:
        tester.sentence = tester.sentence.replace(species_dict[key], key)

    tester.sentence = tester.sentence.replace(' ,',',')
    tester.sentence += '.'
    tester.sentence = tester.sentence.capitalize()

    return tester.sentence

if __name__ == "__main__":
    m = Test()

