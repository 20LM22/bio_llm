from z3 import *
from lark import Lark, Tree
from lark.visitors import Interpreter

# TODO: when changing species names, they need to be updated here as well
nl_to_literal_dict = {
    "c(low)": "low",
    "c(mid)": "moderate",
    "c(high)": "high"
}

signal_names_dict = {
    "adam17": "ADAM-17",
    "albumin": "albumin",
    "alkp": "ALKP",
    "alt": "ALT",
    "ast": "AST",
    "bcells": "B-cells",
    "cc3": "CC3",
    "ccl2": "CCL2",
    "ccr2": "CCR2",
    "cd107a": "CD107a",
    "cd19": "CD19",
    "cd24": "CD24",
    "cd38": "CD38",
    "crp": "CRP",
    "cpg2216": "CpG 2216",
    "gcsf": "G-CSF",
    "glut1": "GLUT1",
    "glut3": "GLUT3",
    "gmcsf": "GM-CSF",
    "ifn": "IFN",
    "ifnα": "IFN-α",
    "ifnβ": "IFN-β",
    "ifnγ": "IFN-γ",
    "igg": "IgG",
    "igm": "IgM",
    "il1α": "IL-1α",
    "il1β": "IL-1β",
    "il1ra": "IL-1Ra",
    "il1rn": "IL1RN",
    "il10": "IL-10",
    "il12": "IL-12",
    "il15": "IL-15",
    "il17": "IL-17",
    "il18": "IL-18",
    "il2": "IL-2",
    "il27": "IL-27",
    "il4": "IL-4",
    "il5": "IL-5",
    "il6": "IL-6",
    "il8": "IL-8",
    "ip10": "IP-10",
    "lymphocytes": "lymphocytes",
    "mcp": "MCP",
    "mcp1": "MCP-1",
    "mcp2": "MCP-2",
    "mcp3": "MCP-3",
    "mcp4": "MCP-4",
    "merscov": "MERS-CoV",
    "mip1a": "MIP-1α",
    "mip1b": "MIP-1β",
    "monocytes": "monocytes",
    "mx1": "MX1",
    "mx2": "MX2",
    "neopterin": "neopterin",
    "neutrophil": "neutrophils",
    "ns1": "NS1",
    "platelets": "platelets",
    "rantes": "RANTES",
    "reticulocytes": "reticulocytes",
    "sarscov": "SARS-CoV",
    "sarscov2": "SARS-CoV-2",
    "stat1": "STAT-1",
    "stnfri": "sTNFRI",
    "stnfrii": "sTNFRII",
    "tcells": "T-cells",
    "titers": "titers",
    "tnfα": "TNF-α",
    "triglycerides": "triglycerides",
    "virus": "virus",
    "vp40": "VP40",

    "d_adam17": "ADAM-17",
    "d_albumin": "albumin",
    "d_alkp": "ALKP",
    "d_alt": "ALT",
    "d_ast": "AST",
    "d_bcells": "B-cells",
    "d_cc3": "CC3",
    "d_ccl2": "CCL2",
    "d_ccr2": "CCR2",
    "d_cd107a": "CD107a",
    "d_cd19": "CD19",
    "d_cd24": "CD24",
    "d_cd38": "CD38",
    "d_crp": "CRP",
    "d_cpg2216": "CpG 2216",
    "d_gcsf": "G-CSF",
    "d_glut1": "GLUT1",
    "d_glut3": "GLUT3",
    "d_gmcsf": "GM-CSF",
    "d_ifn": "IFN",
    "d_ifnα": "IFN-α",
    "d_ifnβ": "IFN-β",
    "d_ifnγ": "IFN-γ",
    "d_igg": "IgG",
    "d_igm": "IgM",
    "d_il1α": "IL-1α",
    "d_il1β": "IL-1β",
    "d_il1ra": "IL-1Ra",
    "d_il1rn": "IL1RN",
    "d_il10": "IL-10",
    "d_il12": "IL-12",
    "d_il15": "IL-15",
    "d_il17": "IL-17",
    "d_il18": "IL-18",
    "d_il2": "IL-2",
    "d_il27": "IL-27",
    "d_il4": "IL-4",
    "d_il5": "IL-5",
    "d_il6": "IL-6",
    "d_il8": "IL-8",
    "d_ip10": "IP-10",
    "d_lymphocytes": "lymphocytes",
    "d_mcp": "MCP",
    "d_mcp1": "MCP-1",
    "d_mcp2": "MCP-2",
    "d_mcp3": "MCP-3",
    "d_mcp4": "MCP-4",
    "d_merscov": "MERS-CoV",
    "d_mip1a": "MIP-1α",
    "d_mip1b": "MIP-1β",
    "d_monocytes": "monocytes",
    "d_mx1": "MX1",
    "d_mx2": "MX2",
    "d_neopterin": "neopterin",
    "d_neutrophil": "neutrophils",
    "d_ns1": "NS1",
    "d_platelets": "platelets",
    "d_rantes": "RANTES",
    "d_reticulocytes": "reticulocytes",
    "d_sarscov": "SARS-CoV",
    "d_sarscov2": "SARS-CoV-2",
    "d_stat1": "STAT-1",
    "d_stnfri": "TNFRI",
    "d_stnfrii": "TNFRII",
    "d_tcells": "T-cells",
    "d_titers": "titers",
    "d_tnfα": "TNF-α",
    "d_triglycerides": "triglycerides",
    "d_virus": "virus",
    "d_vp40": "VP40"
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
           # print("psi and psi")
            self.sentence.append('if')
            self.visit(node.children[0].children[0])
            self.sentence.append(', then')
            self.visit(node.children[0].children[1])
        elif node.children[0].data == 'nu' or node.children[0].data == 'psi':
            #print("nu")
            self.visit(node.children[0].children[0])
        elif node.children[0].data == "omega_and_omega":
            #print("omega and omega")
            self.visit(node.children[0].children[0])
            self.sentence.append(', and')
            self.visit(node.children[0].children[1])

        else:
            self.visit(node.children[0])
        
    def u_implies_u(self, node):
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
    
    def gt(self, node):
        self.sentence.append(signal_names_dict[node.children[0].children[0].value])
        self.sentence.append("was")
        self.sentence.append("above")
        if isinstance(node.children[1].children[0], Tree):
            # len > 1 means further signals to break down for c-threshold
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
        if isinstance(node.children[1].children[0], Tree):
            # len > 1 means further signals to break down for c-threshold
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
        if isinstance(node.children[1].children[0], Tree):
            # len > 1 means further signals to break down for c-threshold
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
        self.sentence.append('was close to')
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
         
    def temp_op_g(self, node):
        self.sentence.append('from day')
        self.sentence.append(node.children[0].children[0].value) # start time interval
        if node.children[1].children[0].value == '∞' or node.children[1].children[0].value == 'inf':
            self.sentence.append('onward')
        else:
            self.sentence.append('to')
            self.sentence.append(node.children[1].children[0].value) # end time interval

        self.G_flag = True
 
        if node.children[2].data == 'u_implies_u' or node.children[2].data == 'u_and_u':
            self.visit(node.children[2])
        else:
            self.sentence.append('at every point in that interval')
            self.visit(node.children[2])

        self.G_flag = False
         
    def temp_op_f(self, node):
        self.sentence.append('from day')
        self.sentence.append(node.children[0].children[0].value) # start time interval
        if node.children[1].children[0].value == '∞' or node.children[1].children[0].value == 'inf':
            self.sentence.append('onward')
        else:
            self.sentence.append('to')
            self.sentence.append(node.children[1].children[0].value) # end time interval
 
        self.F_flag = True
        
        if node.children[2].data == 'u_implies_u' or node.children[2].data == 'u_and_u':
            self.visit(node.children[2])
        else:
            self.sentence.append('eventually in that interval')
            self.visit(node.children[2])

        self.F_flag = False

    def temp_op_fg(self, node):
        self.sentence.append('from day')
        self.sentence.append(node.children[0].children[0].value) # start time interval
        if node.children[1].children[0].value == '∞' or node.children[1].children[0].value == 'inf':
            self.sentence.append('onward')
        else:
            self.sentence.append('to')
            self.sentence.append(node.children[1].children[0].value) # end time interval
        
        self.FG_flag = True
        if node.children[2].data == 'u_implies_u' or node.children[2].data == 'u_and_u':
            self.visit(node.children[2])
        else:
            self.sentence.append('eventually at every point in that interval')
            self.visit(node.children[2])

        self.FG_flag = False

class DerivativeChecker(Interpreter):
    error = False

    def __init__(self):
        self.error = False

    def eq(self, node):
        if 'd_' in node.children[0].children[0] and node.children[1].data == 'c':
            self.error = True
    def lt(self, node):
        if 'd_' in node.children[0].children[0] and node.children[1].data == 'c':
            self.error = True
    def gt(self, node):
        if 'd_' in node.children[0].children[0] and node.children[1].data == 'c':
            self.error = True

class SpeciesSearch(Interpreter):
    species_list = set()

    def __init__(self):
        self.species_list = set()

    def eq(self, node):
        self.species_list.add(node.children[0].children[0].value)
    def lt(self, node):
        self.species_list.add(node.children[0].children[0].value)
    def gt(self, node):
        self.species_list.add(node.children[0].children[0].value)
    def d_eq(self, node):
        self.species_list.add(f'd_{node.children[0].children[0].value}')
    def d_lt(self, node):
        self.species_list.add(f'd_{node.children[0].children[0].value}')
    def d_gt(self, node):
        self.species_list.add(f'd_{node.children[0].children[0].value}')

class SMTSolver(Interpreter):
    T = 30
    signal_vars = {}
    derivatives_vars = {}
    time_flag = False
    fg_counter = 0
    current_time = 0

    def __init__(self):
        self.T = 30
        self.signal_vars = {}
        self.derivatives_vars = {}
        self.time_flag = False
        self.fg_counter = 0
        self.current_time = 0

    def get_signal_var(self, name, t=None):
        if t is None:
            t = self.current_time
        key = (name, t)
        if key not in self.signal_vars:
            self.signal_vars[key] = Real(f"{name}_{t}")
        return self.signal_vars[key]
    
    def get_derivative_threshold(self, value):
        if value == 'd_c(low)':
            return RealVal(1)
        elif value == 'd_c(high)':
            return RealVal(2)
        elif value == '-d_c(low)':
            return RealVal(-1)
        elif value == '-d_c(high)':
            return RealVal(-2)
        elif value == '0':
            return RealVal(0)
        else:
            raise Exception("Unknown derivative c-value")

    def get_signal_threshold(self, value):
        # print("hellllllooo")
        # print(f"value: {value}")
        if value == 'c(high)':
            return RealVal(3)
        elif value == 'c(mid)':
            return RealVal(2)
        elif value == 'c(low)':
            return RealVal(1)
        else:
            raise Exception("Unknown c-value")

    def omega(self, node):
        if node.children[0].data == 'psi_implies_psi':
            r1 = self.visit(node.children[0].children[0])
            r2 = self.visit(node.children[0].children[1])
            return Implies(r1,r2)
        elif node.children[0].data == 'nu' or node.children[0].data == 'psi':
            return self.visit(node.children[0].children[0])
        elif node.children[0].data == "omega_and_omega":
            r1 = self.visit(node.children[0].children[0])
            r2 = self.visit(node.children[0].children[1])
            return And(r1,r2)
        else:
            return self.visit(node.children[0])

    def u_implies_u(self, node):
        r1 = self.visit(node.children[0])
        r2 = self.visit(node.children[1])
        return Implies(r1,r2)

    def u(self, node):
        return self.visit(node.children[0])

    def u_and_u(self, node):
        r1 = self.visit(node.children[0])
        r2 = self.visit(node.children[1])
        return And(r1,r2)

    def gt(self, node):
        threshold = ""
        try:    
            threshold = self.get_signal_threshold(node.children[1].children[0])
        except Exception as e:
            name = node.children[1].children[0].children[0].value
            time = node.children[1].children[1].children[0].value
            threshold = Real(f"{name}_{time}")

        if self.time_flag:
            t = self.current_time
            return self.get_signal_var(node.children[0].children[0].value, t) > threshold
        else:
            reqs = []
            for t in range(0, self.T + 1):
                var = self.get_signal_var(node.children[0].children[0].value, t)
                reqs.append(var > threshold)
            return And(reqs)

    def lt(self, node):
        threshold = ""
        try:    
            threshold = self.get_signal_threshold(node.children[1].children[0])
        except Exception as e:
            name = node.children[1].children[0].children[0].value
            time = node.children[1].children[1].children[0].value
            threshold = Real(f"{name}_{time}")

        if self.time_flag:
            t = self.current_time
            return self.get_signal_var(node.children[0].children[0].value, t) < threshold
        else:
            reqs = []
            for t in range(0, self.T + 1):
                var = self.get_signal_var(node.children[0].children[0].value, t)
                reqs.append(var < threshold)
            return And(reqs)

    def eq(self, node):
        threshold = ""
        try:
            threshold = self.get_signal_threshold(node.children[1].children[0])
        except Exception as e:
            name = node.children[1].children[0].children[0].value
            time = node.children[1].children[1].children[0].value
            threshold = Real(f"{name}_{time}")

        if self.time_flag:
            t = self.current_time
            return self.get_signal_var(node.children[0].children[0].value, t) == threshold
        else:
            reqs = []
            for t in range(0, self.T + 1):
                var = self.get_signal_var(node.children[0].children[0].value, t)
                reqs.append(var == threshold)
            return And(reqs)

    def d_gt(self, node):
        threshold = self.get_derivative_threshold(node.children[1].value)
        var_name = node.children[0].children[0].value

        if self.time_flag:
            t = self.current_time
            x_t = self.get_signal_var(var_name, t)
            x_t1 = self.get_signal_var(var_name, t + 1)
            derivative = x_t1 - x_t
            return derivative > threshold
        else:
            reqs = []
            for t in range(0, self.T):
                x_t = self.get_signal_var(var_name, t)
                x_t1 = self.get_signal_var(var_name, t+1)
                derivative = x_t1 - x_t
                reqs.append(derivative > threshold)
            return And(reqs)

    def d_lt(self, node):
        threshold = self.get_derivative_threshold(node.children[1].value)
        var_name = node.children[0].children[0].value

        if self.time_flag:
            t = self.current_time
            x_t = self.get_signal_var(var_name, t)
            x_t1 = self.get_signal_var(var_name, t + 1)
            derivative = x_t1 - x_t
            return derivative < threshold
        else:
            reqs = []
            for t in range(0, self.T):
                x_t = self.get_signal_var(var_name, t)
                x_t1 = self.get_signal_var(var_name, t+1)
                derivative = x_t1 - x_t
                reqs.append(derivative < threshold)
            return And(reqs)

    def d_eq(self, node):
        threshold = self.get_derivative_threshold(node.children[1].value)
        var_name = node.children[0].children[0].value

        if self.time_flag:
            t = self.current_time
            x_t = self.get_signal_var(var_name, t)
            x_t1 = self.get_signal_var(var_name, t + 1)
            derivative = x_t1 - x_t
            return derivative == threshold
        else:
            reqs = []
            for t in range(0, self.T):
                x_t = self.get_signal_var(var_name, t)
                x_t1 = self.get_signal_var(var_name, t+1)
                derivative = x_t1 - x_t
                reqs.append(derivative == threshold)
            return And(reqs)

    def temp_op_g(self, node):
        t_a = int(node.children[0].children[0].value)
        t_b = self.T if (node.children[1].children[0].value == '∞' or node.children[1].children[0].value == 'inf') else int(node.children[1].children[0].value)

        self.time_flag = True
        reqs = []
        for t in range(t_a, t_b + 1):
            self.current_time = t
            reqs.append(self.visit(node.children[2]))
        self.time_flag = False
        return And(reqs)

    def temp_op_f(self, node):
        t_a = int(node.children[0].children[0].value)
        t_b = self.T if (node.children[1].children[0].value == '∞' or node.children[1].children[0].value == 'inf') else int(node.children[1].children[0].value)

        self.time_flag = True
        reqs = []
        for t in range(t_a, t_b + 1):
            self.current_time = t
            reqs.append(self.visit(node.children[2]))
        self.time_flag = False
        return Or(reqs)

    def temp_op_fg(self, node):
        t_a = int(node.children[0].children[0].value)
        t_b = self.T if (node.children[1].children[0].value == '∞' or node.children[1].children[0].value == 'inf') else int(node.children[1].children[0].value)

        self.fg_counter += 1

        self.time_flag = True
        reqs = []
        for t_prime in range(t_a, t_b + 1):
            sub_reqs = []
            for t in range(t_prime, t_b + 1):
                self.current_time = t
                sub_reqs.append(self.visit(node.children[2]))
            reqs.append(And(sub_reqs))
        self.time_flag = False
        return Or(reqs)

def STL2literal(input_sentence, grammar):
    p = Lark(grammar)
    tree = p.parse(input_sentence)
    tester = Test()
    tester.visit(tree)

    tester.sentence = ' '.join(tester.sentence)
    tester.sentence = tester.sentence.replace(' ,',',')
    tester.sentence += '.'
    split = tester.sentence.split(' ')
    first_letter = split[0][0]
    first_word = '' if len(split[0]) < 2 else split[0][1:]
    tester.sentence = first_letter.capitalize() + first_word + ' ' + ' '.join(split[1:])

    return tester.sentence

def check_derivative_STL2literal(parsed_input):
    d = DerivativeChecker()
    d.visit(parsed_input)
    return d.error

def get_species_list_STL2literal(parsed_input):
    s = SpeciesSearch()
    s.visit(parsed_input)
    list(s.species_list).sort()
    return '-'.join(s.species_list)

def get_smt(parsed_input):
    # print(f"get smt: {parsed_input}")
    smt = SMTSolver()
    return smt.visit(parsed_input)

if __name__ == '__main__':
    grammar = "?start: omega\n?u: gt | lt | eq | d_gt | d_lt | d_eq\ngt: s \"(t)\" \">\" c\nlt: s \"(t)\" \"<\" c\neq: s \"(t)\" \"=\" c\nd_gt: \"d_\" s \"(t)\" \">\" D_C\nd_lt: \"d_\" s \"(t)\" \"<\" D_C\nd_eq: \"d_\" s \"(t)\" \"=\" D_C\nc: s \"(\" t_a \")\" | C_LOW | C_MID | C_HIGH\nC_LOW: \"c(low)\"\nC_MID: \"c(mid)\"\nC_HIGH: \"c(high)\"\nD_C : \"0\" | \"d_c(low)\" | \"d_c(high)\" | \"-d_c(low)\" | \"-d_c(high)\"\n?nu : u | u_implies_u | u_and_u\nu_implies_u: u \"implies\" u\nu_and_u: u \"and\" u\n?psi: temp_op_fg | temp_op_g | temp_op_f\ntemp_op_fg: \"eventually\" \"[\" t_a \",\" t_a \"]\" \"globally\" \"(\" nu \")\"\ntemp_op_f: \"eventually\" \"[\" t_a \",\" t_a \"]\" \"(\" nu \")\"\ntemp_op_g: \"globally\" \"[\" t_a \",\" t_a \"]\" \"(\" nu \")\"\nomega: nu | psi | omega_and_omega | psi_implies_psi\nomega_and_omega: omega \"and\" omega\npsi_implies_psi: psi \"implies\" psi\nTANUM: /[0-9]+/\nINFINITY: \"inf\" | \"∞\"\nt_a: TANUM | INFINITY\ns: /[\\w]+/\nd_s: /d_[\\w]+/\n%import common.WS\n%ignore WS"
    p = Lark(grammar)
    # input_sentence1 = "eventually[8,18]globally(d_IL1RN(t) > c(high))"
    # input_sentence2 = "d_IL1RN(t) = c(high)"
    input_sentence2 = "eventually[1,7](IL1RN(t)=c(high)) and eventually[15,21](IL1RN(t)=c(high)) and eventually[22,28](IL1RN(t)=c(high))"

    tree = p.parse(input_sentence2)
    # print(check_derivative_STL2literal(tree))
    print(tree)

    # tree1 = p.parse(input_sentence1)
    # print(input_sentence1)
    # print(get_smt(tree1))
    #
    # print('\n')
    # tree2 = p.parse(input_sentence2)
    # print(input_sentence2)
    # print(get_smt(tree2))
#  Tree(Token('RULE', 'd_lt')
#   [Tree(Token('RULE', 's')
#       [Token('__ANON_1', 'IL6')]),
#   Token('D_C', '0')])])])

# Tree(Token('RULE', 'eq'),
#   [Tree(Token('RULE', 's'),
#       [Token('__ANON_1', 'IL6')]),
#    Tree(Token('RULE', 'c'),
#       [Token('C_LOW', 'c(low)')])])])])