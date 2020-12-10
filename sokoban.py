import argparse
import matplotlib.pyplot as plt
import csv
from pathlib import Path
import numpy as np
import agent
from deepqagent import DeepQAgent
from environment import Environment
import time
iteration_max = 1000 #deadlock by iteration 
import random

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
def train_all():
    '''
    randomly train on the different maps for the given amount of episodes...
    '''
    input_path = Path("inputs/*.txt")

    file_list = list(input_path.glob())

    max_episodes = abs(args.episodes)
    max_iterations = abs(args.iterations)

    walls, boxes, storage, player, xlim, ylim = load(file_list[0])    

    environment = Environment(walls = walls, boxes = boxes, storage = storage, player = player, xlim = xlim, ylim = ylim)
    agent = DeepQAgent(environment = environment, learning_rate=args.learning_rate, discount_factor=0.95, minibatch_size = args.minibatch_size, buffer_size = args.buffer_size, verbose=args.verbose)


    if len(args.command) == 2:
        pretrain_path = Path("sokoban_state.pth")
        if pretrain_path.exists() and pretrain_path.is_file():
            agent.load("sokoban_state.pth")
        elif pretrain_path.exists() and not pretrain_path.is_file():
            raise ValueError("Invalid pytorch file.")
    else:
        pretrain_path = Path(args.command[2])
        if pretrain_path.exists() and pretrain_path.is_file():
            agent.load(args.command[2])
        elif pretrain_path.exists() and not pretrain_path.is_file():
            raise ValueError("Invalid file input.")


    while agent.num_episodes < max_episodes:

        walls, boxes, storage, player, xlim, ylim = random.choice(file_list)  

        environment = Environment(walls = walls, boxes = boxes, storage = storage, player = player, xlim = xlim, ylim = ylim)
        agent.load_environment(environment)

        num_iterations = 0
        while num_iterations < 5000:


            
            goal, iterations = agent.episode(args = False, evaluate = False, max_iterations = max_iterations)

            num_iterations += iterations

        if len(args.command) == 3:
            agent.save(args.command[2])
        else:
            agent.save("sokoban_state.pth")

    if len(args.command) == 3:
            agent.save(args.command[2])
        else:
            agent.save("sokoban_state.pth")


    with open('losses.csv', 'w') as f:
        writer = csv.writer(f, delimiter=',')
        for loss in agent.losses:
            writer.writerow(loss)




def train():
    if len(args.command) < 2:
        raise Exception("Expected filepath input.")
    if args.all:
        train_all()


    # import matplotlib.patches as patches 

    max_episodes = abs(args.episodes)
    max_iterations = abs(args.iterations)

    



    walls, boxes, storage, player, xlim, ylim = load(args.command[1])    

    environment = Environment(walls = walls, boxes = boxes, storage = storage, player = player, xlim = xlim, ylim = ylim)
    agent = DeepQAgent(environment = environment, learning_rate=args.learning_rate, discount_factor=0.95, minibatch_size = args.minibatch_size, buffer_size = args.buffer_size, verbose=args.verbose)


    if len(args.command) == 2:
        pretrain_path = Path("sokoban_state.pth")
        if pretrain_path.exists() and pretrain_path.is_file():
            agent.load("sokoban_state.pth")
        elif pretrain_path.exists() and not pretrain_path.is_file():
            raise ValueError("Invalid pytorch file.")
    else:
        pretrain_path = Path(args.command[2])
        if pretrain_path.exists() and pretrain_path.is_file():
            agent.load(args.command[2])
        elif pretrain_path.exists() and not pretrain_path.is_file():
            raise ValueError("Invalid file input.")


    if args.verbose:
        print(f"{eps:>5s}.{iters:>7s}:")

    while agent.num_episodes < max_episodes:
        # if num_episodes % 500 == 0 and num_episodes > 0: 
        #   iterative_threshold = iterative_threshold*2

        goal, iterations = agent.episode(draw = args.draw, evaluate=False, max_iterations=max_iterations)

        if agent.num_episodes > 0 and agent.num_episodes % 10 == 0:
            goal, iterations = agent.episode(draw = False, evaluate=True, max_iterations=200)

        #num_episodes += 1


    if len(args.command) == 3:
        agent.save(args.command[2])
    else:
        agent.save("sokoban_state.pth")

    episode_iterations = np.array(episode_iterations)

    goal, iterations = agent.episode(draw = True, evaluate=True, max_iterations = 200)

    print("-"*30)
    print("Simulation ended.")
    print(f"episodes   :{agent.num_episodes}")
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


    agent.episode(draw = False, evaluate=True)


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


def time():
    max_episodes = abs(args.episodes)


    if len(args.command) < 3:
        raise Exception("Expected 'time <input file> <output file>' format.")



    walls, boxes, storage, player, xlim, ylim = load(args.command[1])    

    environment = Environment(walls = walls, boxes = boxes, storage = storage, player = player, xlim = xlim, ylim = ylim)
    agent = DeepQAgent(environment = environment, discount_factor=0.95, verbose=args.verbose)


    for i in range(100):
        print(f"{i:5d}.{0:7d}:")
        agent.episode(draw = False, evaluate=False)


    data = zip(range(100), gent.episode_times, agent.training_times)

    with open(args.command[2], 'a') as file:
        writer = csv.writer(file, delimiter=',')
        for datum in data:
            writer.writerow(datum)


def plot():
    data = []

    if len(args.command) < 2:
        raise Exception("Expected 'plot <csv file>' format.")

    with open(args.command[0], 'r') as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:
            data.append([int(row[0]), eval(row[1]), eval(row[2])])

    data = zip(*data)

    print(data)



def main():
    if args.command[0] == "train":
        train()
    elif args.command[0] == "test":
        test()
    elif args.command[0] == "draw":
        draw()
    elif args.command[0] == "evaluate":
        evaluate()
    elif args.command[0] == "time":
        time()
    else:
        print("Unrecognized command. Please use sokoban.py --help for help on usage.")
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Solve a Sokoban game using artificial intelligence.")
    parser.add_argument('--quiet', '-q', action='store_true')
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--episodes', action='store', type=int, default=500)
    parser.add_argument('--iterations', action='store', type=int, default=5000)
    parser.add_argument('--learning_rate', action='store', type=float, default=1e-4)
    parser.add_argument('--buffer_size', action='store', type=int, default=500000)
    parser.add_argument('--minibatch_size', action='store', type=int, default=128)

    parser.add_argument('--output', '-o', type=str)
    parser.add_argument('--save_figure', '-s', action='store_true')
    parser.add_argument('--draw', '-d', action='store_true')
    parser.add_argument('--sequence', type=str)
    parser.add)argument('--all', action='store_true')
    parser.add_argument('command', nargs='*')
    
    args = parser.parse_args()
    main()
