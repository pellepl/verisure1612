#!/usr/bin/python

import sys
from string import strip

tokens = {
    'verisure', 
    'door', 
    'lock', 
    'locked', 
    'unlock', 
    'unlocked',
    'disarm', 
    'disarmed', 
    'arm', 
    'armed', 
    'open', 
    'closed', 
    'lamp',
    'lamps', 
    'kitchen', 
    'bedroom', 
    'temperature', 
    'humidity',
    'are', 
    'is', 
    'get', 
    'what', 
    'the', 
    'it', 
    'switch',
    'turn',
    'system', 
    'please', 
    'hello',
    'on',
    'off',
    'in',
    'out',
    'up',
    'down'
    }

rules = {
    'GET_TEMP':           'is | what | what is | get , (the) , temperature',
    'GET_HUMI':           'is | what | what is | get , (the) , humidity',
    'IS_DOOR_OPEN':       'is , (the) , door , open',
    'IS_DOOR_CLOSED':     'is , (the) , door , closed',
    'IS_DOOR_LOCKED':     'is , (the) , door , locked | lock',
    'GET_ARM_STATE':      'is | what | what is | get , (the) , system , armed | disarmed',
    'IS_DOOR_UNLOCKED':   'is , (the) , door , unlocked | unlock',
    'LAMP_ON_BEDROOM':    'turn | switch , on , (the) , bedroom , lamp',
    'LAMP_ON_BEDROOM2':   '(turn) , (switch) , (the) , bedroom , lamp , on',
    'LAMP_ON_KITCHEN':    'turn | switch , on , (the) , kitchen , lamp',
    'LAMP_ON_KITCHEN2':   '(turn) , (switch) , (the) , kitchen , lamp , on',
    'ARM':                'arm , (the) , system',
    'ARM2':               'system , arm',
    'DISARM':             'disarm , (the) , system',
    'DISARM2':            'system , disarm',
    'HELLO':              'hello',
}

isCompiled = False
compiled = {}

def compileGrammar():
    for rule in rules:
        defs = rules[rule].split()
        cgrammar = []

        branch = []
        seq = []
        for token in defs:
            if token == '|':
                branch.append(seq)
                seq = []
                continue
            if token == ',':
                branch.append(seq)
                cgrammar.append(branch)
                seq = []
                branch = []
                continue
            ut = strip(token, '()')
            opt = len(ut) == len(token) - 2

            if not ut in tokens:
                print 'bad token "' + ut + '" in ' + rule + ' : ' + rules[rule]
                raise Exception('bad token "' + ut + '"')
            word = {'tok': ut, 'opt':opt}
            seq.append(word)
        if len(seq) > 0:
            branch.append(seq)
        if len(branch) > 0:
            cgrammar.append(branch)
        compiled[rule] = cgrammar
    pass


_dbg = False #True

def matchSequence(words, wordIx, sequence):
    if _dbg: print '    SEQ ' + str(sequence)
    seqIx = 0
    while seqIx < len(sequence) and wordIx < len(words):
        gword = sequence[seqIx]
        if _dbg: print '      ' + words[wordIx] + ' == ' + gword['tok'] + \
        '   seq:' + str(seqIx) + '/' + str(len(sequence)) + \
        '   inp:' + str(wordIx) + '/' + str(len(words))
        if words[wordIx] == gword['tok']:
            if _dbg: print '    ok'
            wordIx += 1
            seqIx += 1
        elif gword['opt']:
            if _dbg: print '    pass'
            seqIx += 1
        else:
            if _dbg: print '    fail'
            break
    if seqIx == len(sequence) or wordIx == len(words) and sequence[-1]['opt']:
        if _dbg: print '    SEQUENCE MATCH'
        return {'match':True, 'wordIx':wordIx}
    else:
        if _dbg: print '    SEQUENCE FAIL'
        return {'match':False, 'wordIx':0}
    pass

def matchBranch(words, wordIx, branches, branchIx, match):
    if branchIx >= len(branches) or match['match']: 
        if _dbg: print '  BRANCH MATCH'
        match['match'] = True
        return
    if _dbg: print '  BRANCH ' + str(branches[branchIx])
    for sequence in branches[branchIx]:
        res = matchSequence(words, wordIx, sequence)
        if res['match'] and not match['match']:
            matchBranch(words, res['wordIx'], branches, branchIx + 1, match)
    if _dbg: print '  BRANCH FAIL'

def matchRule(words, wordIx, branches, branchIx):
    match = {'match':False}
    matchBranch(words, wordIx, branches, branchIx, match)
    if match['match']:
        if _dbg: print 'RULE MATCH'
        return True
    else:
        if _dbg: print 'RULE FAIL'
        return False


def interpret(speech):
    global isCompiled
    if not isCompiled:
        compileGrammar()
        isCompiled = True
    words = speech.split()
    
    # remove all 'please'
    words = [x for x in words if x != 'please']
    if len(words) == 0:
        return None
    if not words[0] == 'verisure':
        return None
    if _dbg: print "MATCH " + str(words[1:])
    for rule in compiled:
        if _dbg: print "RULE " + str(rule)
        if matchRule(words[1:], 0, compiled[rule], 0):
            print rule
            return rule
    print '?'
    return None

# <COMMAND> :
# rule[
#   branch[
#     seq: [ ord{ tok: <TOKEN> opt: True|False } ] /seq
#   ] /branch
# ] /rule
#

def dump():
    for c in compiled:
        rule = compiled[c]
        print 'COMMAND: ' + c
        for branch in rule:
            for sequence in branch:
                for word in sequence:
                    print '      ' + word["tok"]
                print '   OR'
            print '  AND'

if __name__ == "__main__":
    compileGrammar()
    #dump()
    interpret(sys.argv[1])
