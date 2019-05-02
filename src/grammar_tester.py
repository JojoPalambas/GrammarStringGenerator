#!/bin/python3

# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 18:01:25 2018

@author: gabri
"""

import random
import time
import tiger

start = time.time()

"""

Data structure storing the grammar: list <tuple <string, list <list <bool, string>>>>
Example:
    [("operation",  [[(True, "operation"), (True, "operator"), (True, "operation")]]),
     ("operator",   [[(False, "+")],
                    [(False, "-")],
                    [(False, "*")],
                    [(False, "/")]])]

The data structure is a list, corresponding to the list of all the expendable tokens and their rules.
Each element of the list is a tuple:
    - The first element is a string, being the name of the current expandable token
    - The second element is the list of all the rules to expand the token.
      Each element is a list, being the list of words composing the rule.
      Each word of the rule is a tuple:
          - The first element is a bool, True if the word is an expandable token, else False
          - The second one is a string, the word itself

"""

"""
===============================================================================
============================ LIST MANAGEMENT ==================================
===============================================================================
"""

"""
Merges the two lists of strings and returns the merged list as follows:
    merge_list(["a", "b", "c"], ["1", "2"]) = ["a1", "a2", "b1", "b2", "c1", "c2"]
"""


def merge_list(l1, l2):
    if not l1:
        return l2
    if not l2:
        return l1
    ret = []
    for i in l1:
        for j in l2:
            ret.append(i + j)
    return ret


""" Otputs the content of the list, one element per line """


def out_list(l):
    for e in l:
        print(e)


"""
===============================================================================
=================== COMPLETE GRAMMAR POSSIBILITIES CHECK ======================
===============================================================================
"""

""" Returns the list of rules for the given token, None if the token matches no rule """


def get_rules(grammar, token):
    for e in grammar:
        if e[0] == token:
            return e[1]
    return None


""" Adds a token expansion to the histogram """


def histogram_add(histogram, token):
    cpy = histogram.copy()
    for i in range(len(cpy)):
        if cpy[i][0] == token:
            cpy[i] = (cpy[i][0], cpy[i][1] + 1)
            return cpy
    cpy.append((token, 1))
    return cpy


""" Checks if any value in the histogram is over the max value """


def histogram_check(histogram, max_value):
    for e in histogram:
        if e[1] > max_value:
            return True
    return False


""" Expands the given token with the grammar, and returns a list of all the possible strings """


def expand(grammar, token, histogram=[], max_depth=2):
    if histogram_check(histogram, max_depth):
        return None
    rules = get_rules(grammar, token)
    if not rules:
        print("Rules not found for", token)
        return None
    ret = []
    for rule in rules:
        sub = subexpand_rule(grammar, rule, histogram, max_depth)
        if sub:
            ret += sub
    return ret


""" Expands the given rule with the grammar, and returns a list of all the possible strings """


def subexpand_rule(grammar, rule, histogram, max_depth):
    ret = []
    for word in rule:
        sub = subexpand_couple(grammar, word, histogram, max_depth)
        if not sub:
            return None
        ret = merge_list(ret, sub)
    return ret


""" Expands the given word with the grammar, and returns a list of all the possible strings """


def subexpand_couple(grammar, couple, histogram, max_depth):
    if not couple[0]:
        return [couple[1]]
    return expand(grammar, couple[1], histogram_add(histogram, couple[1]), max_depth)


"""
===============================================================================
=========================== FULL RULES CHECK ==================================
===============================================================================
"""

global_todolist = []

""" Returns the bool associated with the token in global_todolist """


def tok_to_bool(token):
    global todolist
    for (b, tok) in global_todolist:
        if token == tok:
            return b
    print("Token \"", token, "\" not found!", sep="")
    return False


"""
Expands the current token by making sure that all the rules are used at least
once
To do this:
    - If the global todolist is empty, it is built using the grammar as
      follows: [(True, "exp"), (True, "op"), (True, "value")]
    - If the current token is marked with True, it is marked as False, all
      its rules are expanded and added to the result list
    - Else, the rule is chosen in the fastpass list

BE CAREFUL:
    This function can be a RAM bomb if not enough rules are terminal.
    The best use is to give to every token at least one terminal, like an
    example of what the expansion of the token can generate.
"""


def expand_all_rules(grammar, token):
    global global_todolist
    if not global_todolist:
        # Builds the global todolist
        global_todolist = []
        for (tok, tmp) in grammar:
            global_todolist.append((True, tok))
    # Gets the rules of the current token
    rules = get_rules(grammar, token)
    ret = []
    # If the current token is marked as true
    if tok_to_bool(token):
        # Marks the current token as True
        for i in range(len(global_todolist)):
            if global_todolist[i][1] == token:
                global_todolist[i] = (False, global_todolist[i][1])
        # Expands all the rules
        for rule in rules:
            ret += subexpand_rule_all_rules(grammar, rule)
    else:
        # Chooses a (if possible) terminal rule and expands it
        rule = choose_rule(rules, 3, 2)
        ret = subexpand_rule_all_rules(grammar, rule)
    return ret


""" Same as subexpand_rule but with different arguments """


def subexpand_rule_all_rules(grammar, rule):
    ret = []
    for word in rule:
        sub = subexpand_couple_all_rules(grammar, word)
        if not sub:
            return None
        ret = merge_list(ret, sub)
    return ret


""" Same as subexpand_couple but with different arguments """


def subexpand_couple_all_rules(grammar, couple):
    if not couple[0]:
        return [couple[1]]
    return expand_all_rules(grammar, couple[1])


"""
===============================================================================
========================= RANDOM GRAMMAR CHECK ================================
===============================================================================
"""

""" Picks a number between 0 and the given number, 0 included and the given number excluded """


def pick_index(n):
    if not n:
        return 0
    return random.randint(0, n - 1)


""" Picks a random rule is max_depth is not reached, else tries to find the best rule to finish the work fast """


def choose_rule(rules, depth, max_depth):
    # Puts terminal rules in term and non-terminal ones in nterm
    term = []
    nterm = []
    for rule in rules:
        x = False
        for (b, s) in rule:
            x = x or b
        if not x:
            term.append(rule)
        else:
            nterm.append(rule)
    if depth <= max_depth and nterm:
        return nterm[pick_index(len(nterm))]
    if depth > max_depth and term:
        return term[pick_index(len(term))]
    if not term:
        return nterm[pick_index(len(nterm))]
    return term[pick_index(len(term))]


""" Expands the token by picking random rules in the grammar """


def random_expand(grammar, token, depth=0, max_depth=5):
    rules = get_rules(grammar, token)
    if not rules:
        return None
    rule = choose_rule(rules, depth, max_depth)
    ret = ""
    for (b, s) in rule:
        if not b:
            ret += s
        else:
            ret += random_expand(grammar, s, depth + 1, max_depth)
    return ret


"""
===============================================================================
============================= FILE WRITERS ====================================
===============================================================================
"""


def expand_all_rules_to_file(filename, grammar, rule):
    f = open(filename, "w")
    to_write = expand_all_rules(grammar, rule)
    for s in to_write:
        f.write(s + '\n')
    f.close()


def random_rules_to_file(filename, grammar, rule, nb_tests):
    current_second = time.time()
    f = open(filename, "w")
    print("Generating tests: 0%")
    for i in range(nb_tests):
        if time.time() - current_second >= 1:
            print("Generating tests: ", i, " / ", nb_tests, " = ", int(i * 100 / nb_tests), "%", sep="")
            current_second = time.time()
        f.write(random_expand(grammar, "program") + "\n")
    print("Generating tests: 100%")
    print("Tests wrote in ", time.time() - start, " seconds.", sep="")
    f.close()


"""
print("Generating tests...")
f = open("tiger_tests", "a")
code_list = expand_all_rules(tiger, "program")
for code in code_list:
    f.write(code + "\n")
"""
"""
current_second = time.time()
nb_tests = 1000
print("Generating tests: 0%")
for i in range(nb_tests):
    if time.time() - current_second >= 1:
        print("Generating tests: ", i, " / ", nb_tests, " = ", int(i * 100 / nb_tests), "%", sep = "")
        current_second = time.time()
    f.write(random_expand(tiger, "program") + "\n")
print("Generating tests: 100%")
print("Tests wrote in ", time.time() - start, " seconds.", sep = "")
f.close()
"""

"""
===============================================================================
============================= PROGRAM BODY ====================================
===============================================================================
"""

expand_all_rules_to_file("../all.txt", tiger.grammar, "program")
random_rules_to_file("../random.txt", tiger.grammar, "program", 10000)
