from lark import Lark, Tree
from lark.visitors import Interpreter
# from fastpunct import FastPunct

nl_to_literal_dict = {
    "c(low)": "low",
    "c(mid)": "moderate",
    "c(high)": "high"
}

signal_names_dict = {
    "IL6": "IL-6",
    "IL12": "IL-12",
    "IL1β": "IL-1β",
    "IL1Ra": "IL-1Ra",
    "TNFα": "TNF-α",
    "IL8": "IL-8",
    "IFNα": "IFN-α",
    "IFNβ": "IFN-β",
    "SARSCoV2": "SARS-CoV-2",
    "IL1RN": "IL1RN"
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

        if node.children[0].data == 'psi_implies_psi':
            print("psi and psi")
            self.sentence.append('if')
            self.visit(node.children[0].children[0])
            self.sentence.append(', then')
            self.visit(node.children[0].children[1])
        elif node.children[0].data == 'nu' or node.children[0].data == 'psi':
            print("nu")
            self.visit(node.children[0].children[0])
        elif node.children[0].data == "omega_and_omega":
            print("omega and omega")
            self.visit(node.children[0].children[0])
            self.sentence.append(', and')
            self.visit(node.children[0].children[1])
        else:
            self.visit(node.children[0])
            # raise Exception("Error in translation")
        
    def u_implies_u(self, node):
        print('located in u implies u')
        
        if self.FG_flag:
            self.sentence.append('if')
            self.visit(node.children[0])
            self.sentence.append('then eventually at every point in that interval')
            self.visit(node.children[1])
        elif self.F_flag:
            self.sentence.append('if')
            self.visit(node.children[0])
            self.sentence.append('then eventually')
            self.visit(node.children[1])
        elif self.G_flag:
            self.sentence.append('if')
            self.visit(node.children[0])
            self.sentence.append('then at every point in that interval')
            self.visit(node.children[1])
        else:
            self.sentence.append('if')
            self.visit(node.children[0])
            self.sentence.append('then')
            self.visit(node.children[1])
    
    def u(self, node):
        print('located in u')

        if self.FG_flag:
            self.sentence.append('eventually at every point in that interval')
            self.visit(node.children[0])
        elif self.F_flag:
            self.sentence.append('eventually in that interval')
            self.visit(node.children[0])
        elif self.G_flag:
            self.sentence.append('at every point in that interval')
            self.visit(node.children[0])
        else:
            self.visit(node.children[0])
    
    def u_and_u(self, node):
        print('located in u and u')

        if self.FG_flag:
            self.sentence.append('eventually at every point in that interval')
            self.visit(node.children[0])
            self.sentence.append('and')
            self.visit(node.children[1])
        elif self.F_flag:
            self.sentence.append('eventually in that interval')
            self.visit(node.children[0])
            self.sentence.append('and')
            self.visit(node.children[1])
        elif self.G_flag:
            self.sentence.append('at every point in that interval')
            self.visit(node.children[0])
            self.sentence.append('and')
            self.visit(node.children[1])
        else:
            self.visit(node.children[0])
            self.sentence.append('and')
            self.visit(node.children[1])
    
    def gt(self, node): # need a repeat of the info from the temporal operators section
        
        self.sentence.append(signal_names_dict[node.children[0].children[0].value]) # name of species --> would need to find and replace using the LLM's dictionary
        self.sentence.append("was")
     
        self.sentence.append("above")
        if isinstance(node.children[1].children[0], Tree): # len > 1 means further signals to break down for c-threshold
            time = node.children[1].children[1].children[0] # TODO: may be wrong
            if time == '∞' or time == 'inf':
                self.sentence.append('the final level of')
                self.sentence.append(node.children[1].children[0].children[0]) # TODO: may be wrong, supposed to be comparison SPECIES
            else:
                self.sentence.append(node.children[1].children[0].children[0]) # TODO: may be wrong, comparison SPECIES
                self.sentence.append('at day') # TODO: might want to replace day with dictionary item
                self.sentence.append(time)
        else:
            try:
                self.sentence.append('its')
                self.sentence.append(nl_to_literal_dict[node.children[1].children[0]]) # TODO: c-threshold --> take into account c vs. s
                self.sentence.append('levels')
            except Exception as e:
                self.sentence.append('the value of')
                self.sentence.append(signal_names_dict[node.children[1].children[0].children[0]]) # TODO: c-threshold --> take into account c vs. s
                self.sentence.append("at day")
                self.sentence.append(node.children[1].children[1].children[0])

    def lt(self, node):

        self.sentence.append(signal_names_dict[node.children[0].children[0].value]) # name of species --> would need to find and replace using the LLM's dictionary
        self.sentence.append("was below")

        if isinstance(node.children[1].children[0], Tree): # len > 1 means further signals to break down for c-threshold
            time = node.children[1].children[1].children[0] # TODO: may be wrong
            if time == '∞' or time == 'inf':
                self.sentence.append('the final level of')
                self.sentence.append(node.children[1].children[0].children[0]) # TODO: may be wrong, supposed to be comparison SPECIES
            else:
                self.sentence.append(node.children[1].children[0].children[0]) # TODO: may be wrong, comparison SPECIES
                self.sentence.append('at day') # TODO: might want to replace day with dictionary item
                self.sentence.append(time)
        else:
            try:
                self.sentence.append('its')
                self.sentence.append(nl_to_literal_dict[node.children[1].children[0]]) # TODO: c-threshold --> take into account c vs. s
                self.sentence.append('levels')
            except Exception as e:
                self.sentence.append('the value of')
                self.sentence.append(signal_names_dict[node.children[1].children[0].children[0]]) # TODO: c-threshold --> take into account c vs. s
                self.sentence.append("at day")
                self.sentence.append(node.children[1].children[1].children[0])
  
    def eq(self, node):
        self.sentence.append(signal_names_dict[node.children[0].children[0].value]) # SPECIES
        self.sentence.append("was close to")

        if isinstance(node.children[1].children[0], Tree): # len > 1 means further signals to break down for c-threshold
            time = node.children[1].children[1].children[0] # TODO: may be wrong
            if time == '∞' or time == 'inf':
                self.sentence.append('the final level of')
                self.sentence.append(node.children[1].children[0].children[0]) # TODO: may be wrong, supposed to be comparison SPECIES
            else:
                self.sentence.append(node.children[1].children[0].children[0]) # TODO: may be wrong, comparison SPECIES
                self.sentence.append('at day') # TODO: might want to replace day with dictionary item
                self.sentence.append(time)
        else:
            try:
                self.sentence.append('its')
                self.sentence.append(nl_to_literal_dict[node.children[1].children[0]]) # TODO: c-threshold --> take into account c vs. s
                self.sentence.append('levels')
            except Exception as e:
                self.sentence.append('the value of')
                self.sentence.append(signal_names_dict[node.children[1].children[0].children[0]]) # TODO: c-threshold --> take into account c vs. s
                self.sentence.append("at day")
                self.sentence.append(node.children[1].children[1].children[0])

    def d_gt(self, node):
        self.sentence.append("the rate of change of")
        self.sentence.append(signal_names_dict[node.children[0].children[0]]) # SPECIES
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
        self.sentence.append('the rate of change of')
        self.sentence.append(signal_names_dict[node.children[0].children[0]]) # SPECIES
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
        self.sentence.append('the rate of change of')
        self.sentence.append(signal_names_dict[node.children[0].children[0]]) # SPECIES
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
        print('located in temp op g')

        self.sentence.append('from day') # TODO: change this to an input we get from the LLM's dictionary so it can be adaptable for [days], [was]
        self.sentence.append(node.children[0].children[0].value) # start time interval
        if node.children[1].children[0].value == '∞':
            self.sentence.append('onward')
        else:
            self.sentence.append('to')
            self.sentence.append(node.children[1].children[0].value) # end time interval

        self.G_flag = True
        self.visit(node.children[2])
        self.G_flag = False
         
    def temp_op_f(self, node): # TODO: parametrize this entire thing to do F, G, FG at the same time
        print('located in temp op f')

        self.sentence.append('from day') # TODO: change this to an input we get from the LLM's dictionary so it can be adaptable for [days], [was]
        self.sentence.append(node.children[0].children[0].value) # start time interval
        if node.children[1].children[0].value == '∞':
            self.sentence.append('onward')
        else:
            self.sentence.append('to')
            self.sentence.append(node.children[1].children[0].value) # end time interval

        self.visit(node.children[2])
        
        self.F_flag = True
        self.visit(node.children[2])
        self.F_flag = False

    def temp_op_fg(self, node): # TODO: parametrize this entire thing to do F, G, FG at the same time
        print('located in temp op fg')

        self.sentence.append('from day') # TODO: change this to an input we get from the LLM's dictionary so it can be adaptable for [days], [was]
        self.sentence.append(node.children[0].children[0].value) # start time interval
        
        if node.children[1].children[0].value == '∞' or node.children[1].children[0].value == 'inf':
            self.sentence.append('onward')
        else:
            self.sentence.append('to')
            self.sentence.append(node.children[1].children[0].value) # end time interval
        
        self.FG_flag = True
        self.visit(node.children[2])
        self.FG_flag = False
        

def STL2literal(input_sentence, grammar):
    # TODO: remove this grammar
    grammar = "?start: omega\n?u: gt | lt | eq | d_gt | d_lt | d_eq\ngt: s \"(t)\" \">\" c\nlt: s \"(t)\" \"<\" c\neq: s \"(t)\" \"=\" c\nd_gt: \"d_\" s \"(t)\" \">\" D_C\nd_lt: \"d_\" s \"(t)\" \"<\" D_C\nd_eq: \"d_\" s \"(t)\" \"=\" D_C\nc: s \"(\" t_a \")\" | C_LOW | C_MID | C_HIGH\nC_LOW: \"c(low)\"\nC_MID: \"c(mid)\"\nC_HIGH: \"c(high)\"\nD_C : \"0\" | \"d_c(low)\" | \"d_c(high)\" | \"-d_c(low)\" | \"-d_c(high)\"\n?nu : u | u_implies_u | u_and_u\nu_implies_u: u \"implies\" u\nu_and_u: u \"and\" u\n?psi: temp_op_fg | temp_op_g | temp_op_f\ntemp_op_fg: \"eventually\" \"[\" t_a \",\" t_a \"]\" \"globally\" \"(\" nu \")\"\ntemp_op_f: \"eventually\" \"[\" t_a \",\" t_a \"]\" \"(\" nu \")\"\ntemp_op_g: \"globally\" \"[\" t_a \",\" t_a \"]\" \"(\" nu \")\"\nomega: nu | psi | omega_and_omega | psi_implies_psi\nomega_and_omega: omega \"and\" omega\npsi_implies_psi: psi \"implies\" psi\nt_a: /[0-9]+/ | \"inf\" | /∞/\ns: /[\\w]+/\nd_s: /d_[\\w]+/\n%import common.WS\n%ignore WS"

    p = Lark(grammar) # TODO: this is also slow, improve if possible

    # TODO: remove this once done testing
    input_sentence = "eventually[0,14](d_IFNα(t)<0impliesIL1Ra(t)<c(low))"
    
    tree = p.parse(input_sentence)
    print(f'input sentence: {input_sentence}')
    print(f'input tree: {tree}')
    tester = Test() # TODO: this is redundant, see if this can be improved
    tester.visit(tree)

    tester.sentence = ' '.join(tester.sentence)

    tester.sentence = tester.sentence.replace(' ,',',')
    tester.sentence += '.'
    split = tester.sentence.split(' ')
    first_letter = split[0][0]
    first_word = '' if len(split[0]) < 2 else split[0][1:]
    tester.sentence = first_letter.capitalize() + first_word + ' ' + ' '.join(split[1:])
    
    print(f'translation: {tester.sentence}')

    return tester.sentence


