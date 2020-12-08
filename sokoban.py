import argparse
import matplotlib.pyplot as plt
import csv
from pathlib import Path
import numpy as np
import agent
from deepqagent import DeepQAgent
from environment import Environment
#from environment import DOWN, LEFT, RIGHT, UP
iteration_max = 1000 #deadlock by iteration 

def load(filename):
    filepath = Path(filename)
    #print(args.filename)
    if not filepath.exists():
        raise ValueError("Path does not exist.")
    if not filepath.is_file():
        raise ValueError("Path is not a valid file.")



    with open(filepath, 'r') as file:
        csv_input = csv.reader(file, delimiter=' ')

        for index, row in enumerate(csv_input):

            def unpack(points):

                return [tuple([int(points[index+1]), int(points[index])]) for index in range(1, len(points), 2)]

            #print(index, row)

            if index == 0:
                #sizeH, sizeV

                xlim = int(row[0])
                ylim = int(row[1])
            if index == 1:
                #print(MapType.WALL.value)
                walls = unpack(row)
            elif index == 2:    
                boxes = unpack(row)
            elif index == 3:
                storage = unpack(row)
            elif index == 4:
                player = np.array([int(row[0]), int(row[1])])

    return walls, boxes, storage, player, xlim, ylim
def train():
    # import matplotlib.patches as patches 

    max_episodes = abs(args.episodes)
    max_iterations = abs(args.iterations)

    if len(args.command) < 2:
        raise Exception("Expected filepath input.")



    walls, boxes, storage, player, xlim, ylim = load(args.command[1])    

    environment = Environment(walls = walls, boxes = boxes, storage = storage, player = player, xlim = xlim, ylim = ylim)
    agent = DeepQAgent(environment = environment, discount_factor=0.95, verbose=args.verbose)

    pretrain_path = Path("sokoban_state.pth")
    if pretrain_path.exists() and pretrain_path.is_file():
        agent.load("sokoban_state.pth")


    episode_bookmarks = []
    episode_iterations = []

    num_episodes = 0
    num_iterations = 0
    goals_reached = 0
    iterative_threshold = 10000
    while num_episodes < max_episodes:
        # if num_episodes % 500 == 0 and num_episodes > 0: 
        #   iterative_threshold = iterative_threshold*2

        if num_episodes % 1 == 0:
            print(f"{num_episodes:5d}.{0:7d}:")
        goal, iterations = agent.episode(draw = args.draw, evaluate=False, max_iterations=max_iterations)

        if goal:
            goals_reached += 1
            episode_bookmarks.append(num_episodes)
            episode_iterations.append(iterations)
            #print(f"{num_episodes:5d}:goal reached.")
        


        if num_episodes > 0 and num_episodes % 100 == 0:
            goal, iterations = agent.episode(draw = False, evaluate=True, iterations=200)
            print("-"*20)
            print(f"evaluation:{goal}")
            if goal:
                print(f"iterations:{iterations}")
            print("-"*20)


        num_episodes += 1

    agent.save("sokoban_state.pth")

    episode_iterations = np.array(episode_iterations)

    goal, iterations = agent.episode(draw = True, evaluate=True, max_iterations = 200)

    print("-"*30)
    print("Simulation ended.")
    print(f"episodes   :{num_episodes}")
    print(f"map solved :{goal}")
    print(f"iterations :{iterations}")


def evaluate():
    max_episodes = abs(args.episodes)

    if len(args.command) < 2:
        raise Exception("Expected filepath input.")



    walls, boxes, storage, player, xlim, ylim = load(args.command[1])    

    environment = Environment(walls = walls, boxes = boxes, storage = storage, player = player, xlim = xlim, ylim = ylim)
    agent = DeepQAgent(environment = environment, discount_factor=0.95, verbose=args.verbose)

    pretrain_path = Path("sokoban_state.pth")
    if pretrain_path.exists() and pretrain_path.is_file():
        agent.load("sokoban_state.pth")

    agent.episode(draw = True, evaluate=True)


def test():
    import unittest
    import tests.environmenttest 
    import tests.deepqagenttest

    import logging
    import sys
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromModule(tests.environmenttest))
    suite.addTests(loader.loadTestsFromModule(tests.deepqagenttest))


  
    if args.verbose:
        verbose = 2
    elif args.quiet:
        verbose = 0
    else:
        verbose = 1
    runner = unittest.TextTestRunner(verbosity = verbose)
    result = runner.run(suite)




def draw():
    if len(args.command) < 2:
        raise Exception("Expected a filepath argument.")

    walls, boxes, storage, player, xlim, ylim = load(args.command[1])
    environment = Environment(walls = walls, boxes = boxes, storage = storage, player = player, xlim = xlim, ylim = ylim)


    environment.draw(environment.state)
    for action in [LEFT, DOWN, LEFT, LEFT, RIGHT, DOWN, RIGHT, DOWN, DOWN, LEFT, LEFT, LEFT, UP, LEFT, DOWN, RIGHT, UP, UP, UP, UP, LEFT, UP, RIGHT]:
        environment.state = environment.next_state(environment.state, action)
        environment.draw(environment.state)
    plt.show(block=True)
    #if args.sequence:




def main():
    if args.command[0] == "train":
        train()
    elif args.command[0] == "test":
        test()
    elif args.command[0] == "draw":
        draw()
    elif args.command[0] == "evaluate":
        evaluate()
    else:
        print("Unrecognized command. Please use sokoban.py --help for help on usage.")
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Solve a Sokoban game using artificial intelligence.")
    parser.add_argument('--quiet', '-q', action='store_true')
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--episodes', action='store', type=int, default=500)
    parser.add_argument('--iterations', action='store', type=int, default=5000)

    parser.add_argument('--output', '-o', type=str)
    parser.add_argument('--save_figure', '-s', action='store_true')
    parser.add_argument('--draw', '-d', action='store_true')
    parser.add_argument('--sequence', type=str)
    parser.add_argument('command', nargs='*')
    
    args = parser.parse_args()
    main()
