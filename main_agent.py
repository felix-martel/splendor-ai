import Environment as Env

# Constants
n_games = 10
max_step = 1000

game = Env()

for n_game in range(n_games):
    player = game.reset()
    print(player)
    
    t = 0
    game_ended = False
    while not game_ended and t < max_step:
        action = game.get_random_action(player)
        t += 1
        state, reward, game_ended, _debug = game.take_action(action)
        game.autoplay()

    print("--- Game #", n_game, "---")
    print("Ended after", t, "steps")
    print("Cumulative reward", game.get_total_reward(player))
    game.display_results()
