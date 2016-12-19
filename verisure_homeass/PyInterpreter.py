#!/usr/bin/python

import sys
from string import strip

tokens = {
    'veryshor', 
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
    'hall', 
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
    'off'
    }

sentences = {
    'GET_TEMP':           'is | what | what is | get , (the) , temperature',
#    'GET_HUMI':           'is | what | what is | get , (the) , humidity',
##    'IS_DOOR_OPEN':       'is , (the) , door , open',
#    'IS_DOOR_CLOSED':     'is , (the) , door , closed',
#    'IS_DOOR_LOCKED':     'is , (the) , door , locked | lock',
#    'GET_ARM_STATE':      'is | what | what is | get , (the) , system , armed | disarmed',
#    'IS_DOOR_UNLOCKED':   'is , (the) , door , unlocked | unlock',
#    'LAMP_ON_HALL':       'turn | switch , on , (the) , hall , lamp',
#    'LAMP_ON_HALL2':      '(the) , hall , lamp , on',
#    'LAMP_ON_KITCHEN':    'turn | switch , on , (the) , kitchen , lamp',
#    'LAMP_ON_KITCHEN2':   '(the) , kitchen , lamp , on',
}

compiled = {}

def compileGrammar():
    for cmd in sentences:
        defs = sentences[cmd].split()
        csentence = []
        
        branch = []
        seq = []
        for t in defs:
            if t == '|':
                branch.append(seq)
                seq = []
                continue
            if t == ',':
                branch.append(seq)
                csentence.append(branch)
                seq = []
                branch = []
                continue
            ut = strip(t, '()')
            opt = len(ut) == len(t) - 2
            
            if not ut in tokens:
                print 'bad token "' + ut + '" in ' + cmd + ' : ' + sentences[cmd]
                raise Exception('bad token "' + ut + '"')
            word = {'tok': ut, 'opt':opt}
            seq.append(word)
        if len(seq) > 0:
            branch.append(seq)
        if len(branch) > 0:
            csentence.append(branch)
        compiled[cmd] = csentence
    pass


_dbg = True
def matchSentence(words, sentence):
    if _dbg: print "MATCH " + str(words) + " AGAINST " + str(sentence)
    wordIx = 0
    for branch in sentence:
        if _dbg: print '  BRANCH ' + str(branch)
        curWordIx = wordIx
        branchMatch = False
        for sequence in branch:
            if _dbg: print '    SEQ ' + str(sequence)
            seqIx = 0
            while seqIx < len(sequence):
                gword = sequence[seqIx]
                if _dbg: print '      ' + gword['tok'] + ' == ' + words[curWordIx] + '   seq:' + str(seqIx) + 'of' + str(len(sequence)) + '  in:' + str(curWordIx) + 'of' + str(len(words))
                if words[curWordIx] == gword['tok']:
                    if _dbg: print '    ok'
                    curWordIx += 1
                    seqIx += 1
                elif gword['opt']:
                    if _dbg: print '    pass'
                    seqIx += 1
                else:
                    if _dbg: print '    fail'
                    break
                
            if seqIx == len(sequence):
                if _dbg: print '    SEQUENCE MATCH'
                wordIx = curWordIx
                branchMatch = True
                break
            else:
                if _dbg: print '    SEQUENCE FAIL'
        if not branchMatch:
            return False
            
            
    return True
                

def interpret(speech):
    words = speech.split()
    if not words[0] == 'veryshor':
        return 
    for c in compiled:
        if matchSentence(words[1:], compiled[c]):
            print c
            return
    print '?'
    
    
# <COMMAND> : 
# sentence[
#   branch[
#     seq: [ ord{ tok: <TOKEN> opt: True|False } ] /seq
#   ] /branch
# ] /sentence
#

def dump():
    for c in compiled:
        sentence = compiled[c]
        print 'COMMAND: ' + c
        for branch in sentence:
            for sequence in branch:
                for word in sequence:
                    print '      ' + word["tok"]
                print '   OR'
            print '  AND'

if __name__ == "__main__":
    compileGrammar()
    interpret(sys.argv[1])
    
