from lark import Lark, Tree
from lark.visitors import Interpreter
from fastpunct import FastPunct

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

fastpunct = FastPunct() # TODO: might have to be moved into the function def?

def STL2literal(input_sentence, grammar):
    p = Lark(grammar) # TODO: this is also slow, improve if possible
    tree = p.parse(input)
    tester = Test() # TODO: this is redundant, see if this can be improved
    tester.visit(tree)
    return fastpunct.punct(" ".join(tester.sentence))

#################################################################################################

import ollama, time
from ollama import generate
from lark import Lark
import numpy as np
import os
import pandas
from collections import defaultdict
import pickle
from sentence_transformers import SentenceTransformer
import re
from sklearn.metrics.pairwise import cosine_similarity
from stl2literal import STL2literal

# let's set up some parameters
ollama.base_url = "http://localhost:11434" # this is the default port, can be changed on ollama serve & startup
model_name = "deepseek-r1:1.5b"
num_semantic_attempts = 3 # allow each sentence to get translated 3 times before declaring the translation a failure
num_batch = 6 # when prompting the LLM for a translation, have it produce 6 STL statements, then process them 
regex = '\*\*.*\*\*' # for matching the STL statement in the response returned by the LLM

# first need a bank of sentences to translate
sentences = [
    'In the mild and moderate groups, IL-6 concentrations were at their highest level in the first week after the symptom onset and then exhibited a decreasing trend.',
    'Remarkably, in the mild group, the amount of these cytokines (IL-1β and IL-1Ra) increased at the day 1–7, reached a peak at the day 8–14, and diminished after >14 days.',
    'TNF-α levels elevated at the day 1–7 and 8–14 times intervals, then decreased at the day>14.',
    'We detected that IL-8 was significantly elevated in all COVID-19 subgroups at three studied time intervals compared to the control group.',
    'We found that although there was no difference in the production of IFN-β in all patients with COVID-19 compared to the control group at the day 1–7, IFN-β levels were higher in moderate, severe, and critical subjects at the day 8–14 or >14 compared to the healthy control and themselves at the day 1–7.',
    'IL-12 reached its maximum level at the day>14 in mild patients.',
    'It is reported that in recovered cases, within a few hrs of virus entry, both α and β IFNs (at first day of infection) are rapidly produced and an antiviral state is soon reached [23]',
    'By day 14, we detected no viral reads for SARS-CoV-2, and the observed cytokines returned to baseline, with the exception of IL-6 and IL1RN or IL1RA, which remained elevated, similar to results observed with MERS (Pascal et al., 2015; Figures 3B and 3C).'
] # this can also be replaced with input from the csv file

# for now, let's assume that we use one prompt to go directly from NL to STL
# we can also try to extend this by doing a NL to literal translation, then literal to STL
# not only might that approach have the benefit of being more robust since it decomposes the semantic
# and the syntactic translation, but it also has the benefit of filtering out sentences that
# aren't any good for STL anyways.
core_prompt_1 = """... Translate the following natural language statement into a signal temporal logic (STL) statement:
            ..."""
core_prompt_2 = """          
            ...
            ... It is extremely important to follow these rules:
            ... Rule: The time unit is days.
            ... Rule: You must return the STL statement like this: **your STL response**
            ... Rule: You must accept feedback on your previous responses and amend them if asked to.
            ...
            ... Your response must conform to these rules:
            ... [BEGIN RULES]
            ... u : s"(t) < "c | s"(t) > "c | "abs("s"(t) - "c") < "e | d_s"(t) > "d_c | d_s"(t) < "d_c | "abs("d_s"(t) - "d_c") < "e
            ... e : "e" | [0-9]+
            ... c : "s("t_a")" | "c(low)" | "c(mid)" | "c(high)"
            ... d_c : "0" | "d_c(low)" | "d_c(high)" | "-d_c(low)" | "-d_c(high)"
            ... phi : u | phi" ^ "phi | phi" → "phi
            ... psi : "F["t_a","t_a"]G("phi")" | "G["t_a","t_a"]("phi")" | "F["t_a","t_a"]("phi")"
            ... omega : phi | psi | omega" ^ "omega
            ... t_a : [0-9]+ | "T"
            ... s : [a-zA-z0-9]+
            ... d_s : "d_"[a-zA-z0-9]+
            ... [END RULES]
            ...
            ... The d_s terms represent the derivative of a signal, so you may find those terms helpful for describing how signals increase or decrease. For general statements describing the levels of some species as “high” or “low” for example, you may find comparison statements helpful.
            ...
            ... Here is an example of natural language-signal temporal logic pairs for reference; however, make sure the STL statements you generate are specific to the NL statement you are currently being asked to translate.
            ...
            ... {input: "From 4 to 8 days after infection, IL-6 levels were significantly elevated until day 9, at which point they steadily decreased.", output: "**G[4,8] (IL6(t) > c(high)) ^ G[8,T] (d_IL6(t) < 0)**"}
            ...
"""

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
    
    ?omega : nu
        | psi
        | omega "^" omega
        
    t_a : /[0-9]+/
        | /T/
    s : /[a-zA-Z0-9]+/
    d_s : /d_[a-zA-Z0-9]+/

    %import common.WS
    %ignore WS
"""

output_translations = [['' for _ in range(18)] for _ in range(len(sentences))]

for sentence in sentences:
 # change the prompt for each sentence
    prompt = core_prompt_1 + sentence + core_prompt_2
    # allow each sentence to be translated up n times to get the semantic meaning correct --> n = num_semantic_attempts
    for i in range(num_semantic_attempts):
        # this scope works at the sentence level
        syntactically_correct_responses = []
        # need to produce m translations to STL --> m = num_batch
        for j in range(num_batch):
# for now, let's just use the original prompt without syntactic modification based on the previous responses
            response = ollama.generate(model=model_name, messages=[{"role": "user", "content": prompt}], stream=False).message.content
            # need to extract the **STL** part
            extracted_response = re.search(regex, response)
            # now put the STL through
            if extracted_response is None:
                # TODO: modify prompt to note that response was not included in ****
                i = 2 
            try:
                parsed_STL = grammar.parse(extracted_response)
                # TODO: need to do extra syntactic check: are the intervals correct?
                syntactically_correct_responses.append(parsed_STL)
            except Exception as e:
                # TODO: if not parsed correctly? --> update the prompt with exception information
                print(e)

        # at this point syntactically_correct_responses should be filled with responses
        literal_translations = [] # np.zeroes_like(syntactically_correct_responses)
        for stl in syntactically_correct_responses:
            # TODO: translate these to literal STL --> write the stl2literal function
            literal_translation.append(STL2literal(parsed_STL, grammar))

        # these literal translations need to be evaluated for semantic integrity
        # obtain embeddings of the original sentence and all of the literal translations
        literal_embeddings = [] # np.zeroes_like(literal_translations)
        nl_embedding = np.array(model.encode(sentence, normalize_embeddings=True))
        for i, literal in enumerate(literal_translations):
            embedding_literal = np.array(model.encode(literal_translations[i], normalize_embeddings=True))
            literal_embeddings.append(embedding_literal)
        
        # now compare the embeddings using cosine similarity, take max of the produced array
        sim_matrix = cosine_similarity(np.array(literal_embeddings), np.array(nl_embedding))
        best_stl_id = np.argmax(sim_matrix)

        # only accept what is above similarity threshold
        # the final output is in the form [['nl', 'stl'],['nl', 'stl']]
        if sim_matrix[best_stl_id] < semantic_threshold:
            # reject
            output_translations.append([sentence, None])
        else:
            # accept
            output_translations.append([sentence, syntactically_correct_responses[best_stl_id]])   
