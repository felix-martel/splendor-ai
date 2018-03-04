from Environment import Environment

# Constants
n_games = 10
max_step = 1000
last_debug = {}
game = Environment()
player = game.get_player()

print(player)

t = 0
game_ended = False
while not game_ended and t < max_step:
    action = game.get_random_action(player)
    
    state, reward, game_ended, _debug = game.take_action(action, player)
    last_debug = _debug
    t += 1
    game.autoplay()

if game_ended:
    print("\n\n Game ended after", t, "steps")
    
#print("--- GAME RESULTS---")
#print("Ended after", t, "steps")
#print("Cumulative reward", game.get_total_reward(player))
#game.display_results()
