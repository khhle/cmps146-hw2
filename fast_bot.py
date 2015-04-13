
import random
from math import *
import time

THINK_DURATION = 1
def think(state, quip):

    num = UCT(rootstate = state, itermax = 2000, verbose = False)
    return num



def UCT(rootstate, itermax, verbose = False):
    """ Conduct a UCT search for itermax iterations starting from rootstate.
        Return the best move from the rootstate.
        Assumes 2 alternating players (player 1 starts), with game results in the range [0.0, 1.0]."""

    rootnode = Node(state = rootstate)
    t_start = time.time()
    t_deadline = t_start + THINK_DURATION
    iterations = 0

    while True:
    #for i in range(itermax):
        node = rootnode
        state = rootstate.copy()

        # Select
        while node.untriedMoves == [] and node.childNodes != []: # node is fully expanded and non-terminal
            node = node.UCTSelectChild()
            state.apply_move(node.move)

        # Expand
        if node.untriedMoves != []: # if we can expand (i.e. state/node is non-terminal)
            m = random.choice(node.untriedMoves)
            state.apply_move(m)
            node = node.AddChild(m,state) # add child and descend tree

        rolloutCount = 0
        # Rollout - this can often be made orders of magnitude quicker using a state.GetRandomMove() function
        while state.get_moves() != [] and rolloutCount < 5: # while state is non-terminal
            state.apply_move(random.choice(state.get_moves()))
            rolloutCount += 1

        # Backpropagate
        while node != None: # backpropagate from the expanded node and work back to the root node

            if node.parentNode is None:
                node.score = 0
            else:
                node.score = compute_score_from_perspective(state.get_score(),node.parentNode.who)

            node.visits += 1
            node = node.parentNode

        iterations += 1
        t_now = time.time()
        if t_now > t_deadline:
            break


    sample_rate = float(iterations)/(t_now - t_start)
    print str(get_opposite(rootstate.get_whos_turn())) + " rollout rate: " + str(sample_rate)
    return sorted(rootnode.childNodes, key = lambda c: c.visits)[-1].move # return the move that was most visited

class Node:
    """ A node in the game tree. Note wins is always from the viewpoint of playerJustMoved.
        Crashes if state not specified.
    """
    def __init__(self, move = None, parent = None, state = None):
        self.move = move # the move that got us to this node - "None" for the root node
        self.parentNode = parent # "None" for the root node
        self.childNodes = []
        self.wins = 0
        self.visits = 0
        self.untriedMoves = state.get_moves() # future child nodes
        #self.playerJustMoved = state.get_whos_turn() # the only part of the state that the Node needs later

        self.who = state.get_whos_turn()
        self.score = 0



    def UCTSelectChild(self):
        """ Use the UCB1 formula to select a child node. Often a constant UCTK is applied so we have
            lambda c: c.wins/c.visits + UCTK * sqrt(2*log(self.visits)/c.visits to vary the amount of
            exploration versus exploitation.
        """
        s = sorted(self.childNodes, key = lambda c: (float(c.score)/c.visits ) + sqrt(2*log(self.visits)/c.visits))[-1]
        return s

    def AddChild(self, m, s):
        """ Remove m from untriedMoves and add a new child node for this move.
            Return the added child node
        """
        n = Node(move = m, parent = self, state = s)
        self.untriedMoves.remove(m)
        self.childNodes.append(n)
        return n

    def Update(self, result):
        """ Update this node - one additional visit and result additional wins. result must be from the viewpoint of playerJustmoved.
        """
        self.visits += 1
        #self.score = result
        self.wins += result

    def __repr__(self):
        return "[M:" + str(self.move) + " W/V:" + str(self.wins) + "/" + str(self.visits) + " U:" + str(self.untriedMoves) + "]"

    def TreeToString(self, indent):
        s = self.IndentString(indent) + str(self)
        for c in self.childNodes:
             s += c.TreeToString(indent+1)
        return s

    def IndentString(self,indent):
        s = "\n"
        for i in range (1,indent+1):
            s += "| "
        return s

    def ChildrenToString(self):
        s = ""
        for c in self.childNodes:
             s += str(c) + "\n"
        return s

def compute_score_from_perspective(score_dict, which_player):
    score1 = score_dict[which_player]
    if which_player == "red":
        score2 = score_dict["blue"]
    elif which_player == "blue":
        score2 = score_dict["red"]
    else:
        score2 = 0
        print "Error"
    return score1 - score2

def get_opposite(which_player):
    if which_player == "red":
        return "blue"
    elif which_player == "blue":
        return "red"
    else:
        return "error"