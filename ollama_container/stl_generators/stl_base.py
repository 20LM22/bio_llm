from abc import ABC
from lark import Lark
import random

# u
# removed "t_a"
# t_a:
#        | "t"
# omega
#        | omega" → "omega
# c
#         | "s("t_a")"

grammar = """
    u : s"(t) < "c
        | s"(t) > "c 
        | "abs("s"(t) - "c") < "e
        | d_s"(t) > "d_c
        | d_s"(t) < "d_c
        | "abs("d_s"(t) - "d_c") < "e
    e : "e"
        | /[0-9]+/
    c : "c(low)"
        | "c(mid)"
        | "c(high)"
    d_c : "0" 
        | "d_c(low)"
        | "d_c(high)" 
        | "-d_c(low)" 
        | "-d_c(high)"
    phi : u
        | phi" ^ "phi
        | "( "phi" → "phi" )"
    psi : "F["t_a","t_a"]G("phi")"
        | "G["t_a","t_a"]("phi")"
        | "F["t_a","t_a"]("phi")"
    omega : phi
        | psi
        | omega" ^ "omega
        | "( "omega" → "omega" )"
    t_a : /[0-9]+/
        | "T"
    s : /[a-zA-z0-9]+/
    d_s : "d_"/[a-zA-z0-9]+/
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
    min_depth_map[sym] = min_depth
    return min_depth

class STLBase(ABC):
    def __init__(self):

        self.parser = Lark(grammar, start='omega', parser='lalr')

        rule_map = {}
        # Build map from nonterminal name to list of expansions (each expansion is a list of symbols)
        for rule in self.parser.rules:
            lhs = rule.origin.name
            if lhs not in rule_map:
                rule_map[lhs] = []
            if lhs.startswith('Token'):
                # add lhs string cutting to only name of rule
                token_value = lhs.split(",")[-1].strip(" )'")
                lhs = token_value
            rule_map[lhs].append(rule.expansion)
        self.rule_map = rule_map

        min_depth_map = {}
        visited = set()

        for rule in self.rule_map:
            compute_min_depth(rule, self.rule_map, min_depth_map, visited)

        self.rule_depth_map = min_depth_map

        anon_map = {}
        for term in self.parser.terminals:
            if term.pattern:
                # Strip the surrounding quotes
                literal = term.pattern.value
                anon_map[term.name] = literal

        self.anon_map = anon_map

        #print(self.sample("omega"))
        #print(self.sample("omega"))
        #print(self.sample("omega"))
        #pass

    def sample(self, sym, depth=0, max_depth=3):
        ids = [0, 1, 2,3,4]
        parts = []
        t_a_str = "t_a"

        if sym == "t_a":
            parts.append(random.choice(["T", str(random.randint(0, 10))]))
        elif sym == "s":
            parts.append("s" + str(random.choice(ids)))
        elif sym == "d_s":
            parts.append("d_s" + str(random.choice(ids)))
        elif sym == "e":
            parts.append(str(random.randint(1, 20) / 20))
        elif sym == "c":
            parts.append(random.choice([f"s({self.sample(t_a_str)})", "c(low)", "c(mid)", "c(high)"]))
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
                            parts.append(random.choice(["T", str(random.randint(0, 10))]))
                        elif t.name == "s":
                            parts.append("s" + str(random.choice(ids)))
                        elif t.name == "d_s":
                            parts.append("d_s" + str(random.choice(ids)))
                        elif t.name == "e":
                            parts.append(str(random.randint(1, 20) / 20))
                        elif t.name == "c":
                            parts.append(random.choice(["c(low)", "c(mid)", "c(high)"]))
                        elif t.name == "d_c":
                            parts.append(random.choice(["0", "d_c(low)", "d_c(high)", "-d_c(low)", "-d_c(high)"]))
                        else:
                            parts.append(self.sample(t.name, depth + 1))
                    else:
                        parts.append(self.anon_map[t.name])  # Use literal if available
            return ''.join(parts)

if __name__ == "__main__":
    stl = STLBase()

