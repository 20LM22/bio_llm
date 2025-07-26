from abc import ABC
from lark import Lark
import random

grammar = """
    ?start: omega
    ?u: s "(t)" ">" c | s "(t)" "<" c | "abs(" s "(t)" "-" c ")" "<" e | "d_" s "(t)" ">" d_c | "d_" s "(t)" "<" d_c | "abs(" "d_" s "(t)" "-" d_c ")" "<" e
    
    ?e: "e" | /[0-9]+.[0-9]+/ | /[0-9]+/
    c: s "(" t_a ")" | "c(low)" | "c(mid)" | "c(high)"
    d_c : "0" | "d_c(low)" | "d_c(high)" | "-d_c(low)" | "-d_c(high)"

    ?phi: u | u "^" phi | u "∧" phi
    ?nu : u | u "→" u | u "^" phi | u "∧" phi
    ?psi: temp_op_f | temp_op_g | temp_op_f_g
    temp_op_f_g: "F" "[" t_a "," t_a "]" "G" "(" nu ")"
    temp_op_f: "F" "[" t_a "," t_a "]" "(" nu ")"
    temp_op_g: "G" "[" t_a "," t_a "]" "(" nu ")"
    ?omega: nu | psi | omega "^" omega | omega "∧" omega | psi "→" psi 
    
    t_a: /[0-9]+/ | "infinity" | /∞/
    s: "IL6" | "IL12" | "IL1β" | "IL1Ra" | "TNFα" | "IL8" | "IFNα" | "IFNβ" | "SARSCoV2" | "IL1RN"

    %import common.WS
    %ignore WS
"""

def compute_min_depth(sym, rule_map, min_depth_map, visited):
    if sym in min_depth_map:
        return min_depth_map[sym]

    if sym not in rule_map:
        # Terminal
        min_depth_map[sym] = 1
        return 1

    if sym in visited:
        # Prevent infinite loops (e.g. left recursion)
        return float('inf')

    visited.add(sym)

    min_depth = float('inf')
    for expansion in rule_map[sym]:
        depth = 0
        for t in expansion:
            if not t.is_term:
                depth = max(depth, compute_min_depth(t.name, rule_map, min_depth_map, visited))
            else:
                depth = max(depth, 1)
        min_depth = min(min_depth, depth + 1)

    visited.remove(sym)
    min_depth_map[str(sym)] = min_depth
    return min_depth

class STLBase(ABC):
    def __init__(self):

        self.parser = Lark(grammar, start='omega', parser='lalr')

        rule_map = {}
        # Build map from nonterminal name to list of expansions (each expansion is a list of symbols)
        
        for rule in self.parser.rules:
            print(f"rule is: {rule.origin.name}")
            lhs = rule.origin.name
            if lhs not in rule_map:
                rule_map[lhs] = []
            if lhs.startswith('Token'):
                # add lhs string cutting to only name of rule
                token_value = lhs.split(",")[-1].strip(" )'")
                lhs = token_value
            rule_map[lhs].append(rule.expansion)
        self.rule_map = rule_map

        print(f'rule map: {self.rule_map}')

        min_depth_map = {}
        visited = set()

        for rule in self.rule_map:
            compute_min_depth(rule, self.rule_map, min_depth_map, visited)

        self.rule_depth_map = min_depth_map
        print("depth map:")
        print(self.rule_depth_map)

        anon_map = {}
        for term in self.parser.terminals:
            if term.pattern:
                # Strip the surrounding quotes
                literal = term.pattern.value
                anon_map[term.name] = literal

        self.anon_map = anon_map
        # print(self.sample('omega'))

    def sample(self, sym, depth=0, max_depth=3):
        print("--------------------------------------------------------------inside of SAMPLE---------------------------------------------------------------")
        ids = ["IL6", "IL12", "IL1β", "IL1Ra", "TNFα", "IL8", "IFNα", "IFNβ", "SARSCoV2", "IL1RN"]

        parts = []
        t_a_str = "t_a"

        if sym == "t_a":
            parts.append(str(random.randint(0, 20)))
        elif sym == "s":
            parts.append(random.choice(ids))
        elif sym == "d_s":
            parts.append("d_" + random.choice(ids))
        elif sym == "e":
            parts.append(random.choice([str(random.randint(1, 20) / 20), "e"]))
        elif sym == "c":
            signal = random.choice(ids)
            parts.append(random.choice([f"{signal}_{self.sample(t_a_str)}", "c(low)", "c(mid)", "c(high)"]))
        elif sym == "d_c":
            parts.append(random.choice(["0", "d_c(low)", "d_c(high)", "-d_c(low)", "-d_c(high)"]))
        else:


            if sym in self.rule_map:
                if depth > max_depth:
                    # Try only fully terminal expansions
                    min_depth = 100
                    best_depth_ids = []
                    for idx, sym_temp in enumerate(self.rule_map[sym]):
                        terminal_only = [t for t in sym_temp if t.is_term]
                        if len(terminal_only) == len(sym_temp):
                            best_depth_ids.append(idx)
                            min_depth = 1
                        else:
                            for t in sym_temp:
                                if not t.is_term:
                                    if self.rule_depth_map[t.name] <= min_depth:
                                        best_depth_ids.append(idx)
                                        min_depth = self.rule_depth_map[t.name]
                    expansion = self.rule_map[sym][random.choice(best_depth_ids)]
                    # terminal_only = [e for e in expansion if e.is_term]
                    # if terminal_only:
                    #     expansion = terminal_only
                else:
                    expansion = random.choice(self.rule_map[sym])
                
                parts = []
                for t in expansion:
                    if not t.is_term:
                        if t.name == "t_a":
                            parts.append(str(random.randint(0, 20)))
                        elif t.name == "s":
                            parts.append(random.choice(ids))
                        elif t.name == "d_s":
                            parts.append("d_" + str(random.choice(ids)))
                        elif t.name == "e":
                            parts.append(random.choice([str(random.randint(1, 20) / 20), "e"]))
                        elif t.name == "c":
                            parts.append(random.choice(["c(low)", "c(mid)", "c(high)"]))
                        elif t.name == "d_c":
                            parts.append(random.choice(["0", "d_c(low)", "d_c(high)", "-d_c(low)", "-d_c(high)"]))
                        else:
                            parts.append(self.sample(t.name, depth + 1))
                    else:
                        parts.append(self.anon_map[t.name])  # Use literal if available

            # print(self.parser.parse(''.join(parts))) 
            return ' '.join(parts)

if __name__ == "__main__":
    stl = STLBase()

