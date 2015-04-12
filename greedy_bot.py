import random

def think(state, quip):
    
    topScore = 0
    primeMove = random.choice(state.get_moves())

    player = state.get_shows_turn()
    score = state.get_score()[player]
    
    for move in state.get_move():
      tempState = state.copy()
      tempState.apply_move(move)
      if(tempState.get_score()[player] + score) > topScore:
         topScore = tempState.get_score()[player] +score
         primeMove = move
         
    return primeMove