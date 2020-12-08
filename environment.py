import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from enum import Enum
from collections import namedtuple
import copy
#from actor import State

#import torch



# class MapType(Enum):
#   EMPTY = 0
#   PLAYER = 1
#   BOX = 2
#   WALL = 3

EMPTY = 0
PLAYER = 1
BOX = 2
WALL = 3


UP = np.array([0,1])
DOWN = np.array([0, -1])
LEFT = np.array([-1, 0])
RIGHT = np.array([1, 0])
DIRECTIONS = [UP, RIGHT, DOWN, LEFT]

def direction_to_str(direction):
    if all(direction == UP):
        return "UP"
    elif all(direction == DOWN):
        return "DOWN"
    elif all(direction == LEFT):
        return "LEFT"
    return "RIGHT"


# class Move():

#   def __init__(self, previous_state, previous_scores, action, box_moved = False):
#       self.action = action
#       self.previous_state = previous_state
#       self.previous_scores = previous_scores
#       self.box_moved = box_moved


class Environment():


    def __init__(self, walls, boxes, player, storage, xlim, ylim):

        self.fig = plt.figure()


        self.state = np.zeros((2, xlim+1, ylim+1), dtype=np.double)#torch.zeros(xlim+1, ylim+1, 2)
        self.walls = np.zeros((xlim+1, ylim+1)) #torch.zeros(xlim+1, ylim+1)
        self.xlim = xlim
        self.ylim = ylim

        self.storage = set(storage)


        for wall in walls:
            #print(wall)
            self.walls[wall[0], wall[1]] = 1.
        for box in boxes:
            self.state[1, box[0], box[1]] = 1.

        self.state[0, player[0], player[1]] = 1.

        self.deadlock_table = {}

        self.original_state = copy.deepcopy(self.state)
        
        
        self.state_hash = None



#     def save_state(self):
#         self.saved_map = copy.deepcopy(self.map)
#         self.saved_state = copy.deepcopy(self.state)
#         self.saved_scores = copy.deepcopy(self.has_scored)

#     def reset_to_save(self):
#         if self.saved_map is None:
#             print("NEED TO SAVE BEFORE RESET!")
#         else:
#             self.map = copy.deepcopy(self.saved_map)
#             self.state = copy.deepcopy(self.saved_state)
#             self.has_scored = copy.deepcopy(self.saved_scores)

    def reset(self):
        # print("reset!")
        # print(f"player:{self.state[0]}")
        # print(f"reset_player:{self.original_player}")
        self.state = copy.deepcopy(self.original_state)


#     def reset_map(self):
#         for i in range(self.xlim):
#             for j in range(self.ylim):
#                 if self.map[i, j] == BOX:
#                     self.map[i, j] = EMPTY
        
#         self.map[tuple(self.state[0])] = PLAYER
#         for box in self.state[2:]:
#             self.map[tuple(box)] = BOX


#     def is_goal(self):
#         for place in self.storage:
#             if self.map[place] != BOX:
#                 return False

#         return True

    

    def is_goal_state(self, state):
        for place in self.storage:
            if state[1, place[0], place[1]] != 1:
                return False

        return True

    def get_player(self, state):
        return np.unravel_index(np.argmax(state[0, :, :]), state[0, :, :].shape)
    def get_neighbors(self, location):
        return [location + direction for direction in DIRECTIONS]


    def is_frozen(self, state, location, previous=None):

        if location.tobytes() in self.deadlock_table[self.state_hash]:
          return self.deadlock_table[self.state_hash][location.tobytes()]

        # if not previous:
        #   previous = set([])
        neighbors = self.get_neighbors(location)
        previous.add(tuple(location))
        if tuple(location) not in self.storage:
            for i in range(len(neighbors)):
                neighbor = tuple(neighbors[i])
                next_neighbor = tuple(neighbors[(i+1)%len(neighbors)])

                if self.walls[neighbor] == 1 and self.walls[next_neighbor] == 1:
                    self.deadlock_table[self.state_hash][location.tobytes()] = True

                    #print("case 1")
                    return True
                elif self.walls[neighbor] == 1 and state[1, next_neighbor[0], next_neighbor[1]] == 1:
                    #print("case 2")
                    if next_neighbor in previous:
                        #depndency cycle!
                        self.deadlock_table[self.state_hash][location.tobytes()] = True
                        return True
                    if self.is_frozen(state, np.array(next_neighbor), previous):
                        self.deadlock_table[self.state_hash][location.tobytes()] = True
                        return True
                elif state[1, neighbor[0], neighbor[1]] == 1 and self.walls[next_neighbor] == 1:
                    #print("case 3")

                    if neighbor in previous:
                        #dependency cycle!
                        self.deadlock_table[self.state_hash][location.tobytes()] = True
                        return True

                    if self.is_frozen(state, np.array(neighbor), previous):
                        self.deadlock_table[self.state_hash][location.tobytes()] = True
                        return True
                elif state[1, neighbor[0], neighbor[1]] == BOX and state[1, next_neighbor[0], next_neighbor[1]] == BOX:
                    # print("case 4")
                    # print(neighbor in previous)
                    # print(next_neighbor in previous)
                    if neighbor in previous:
                        frozen_neighbor = True
                    else:
                        frozen_neighbor = self.is_frozen(state, np.array(neighbor), previous)
                    if next_neighbor in previous:
                        frozen_next_neighbor = True
                    else:
                        frozen_next_neighbor = self.is_frozen(state, np.array(next_neighbor), previous)


                    if frozen_neighbor and frozen_next_neighbor:
                        self.deadlock_table[self.state_hash][location.tobytes()] = True
                        return True

        previous.remove(tuple(location))
        self.deadlock_table[self.state_hash][location.tobytes()] = False

        return False


    def is_deadlock(self, state):
        # if not self.frozen_nodes:
        #   self.frozen_nodes = set([])
        self.state_hash = state.tobytes()

        if self.state_hash not in self.deadlock_table:
            self.deadlock_table[self.state_hash] = {}
        for i in range(state.shape[1]):
            for j in range(state.shape[2]):
                if state[1, i,j] == 1:
                    box = np.array([i, j])
                    if box.tobytes() in self.deadlock_table[self.state_hash] and self.deadlock_table[self.state_hash][box.tobytes()]:
                        return True
                    elif self.is_frozen(state, box, previous=set([])):

                        #self.frozen_nodes = None
                        return True


        #self.frozen_nodes = None
        return False

    # def undo(self):
    #   if self.previous_move is None:
    #       self.reset() ##no previous move? reset
    #   else:   

    #       self.state = copy.deepcopy(self.previous_move.previous_state)
    #       #print(self.state)
    #       self.has_scored = copy.deepcopy(self.previous_move.previous_scores)

    #       #undo movement
    #       self.map[tuple(self.state[0])] = PLAYER
    #       # if self.previous_move.box_moved:
    #       #   self.map[tuple(self.state[0] + self.previous_move.action)] = BOX
    #       #   self.map[tuple(self.state[0] + 2*self.previous_move.action)] = EMPTY
    #       self.reset_map()




        # for box in self.state[2:]:
        #   if not self.map[tuple(box)] == BOX:
        #       print(f"state:{self.state[0]}")
        #       print(f"previous_state:{self.previous_move.previous_state[0]}")

        #       assert self.map[tuple(box)] == BOX, f"{box} is not in MAP relative to {self.state[0]}"


    def next_state(self, state, action):
        '''
        Returns a copy with the next state.
        '''
        player = self.get_player(state)

        next_position = np.array(player) + action

        next_state = np.copy(state)

        if state[1, next_position[0], next_position[1]] == 1:
            next_box_position = next_position + action

            if state[1, next_box_position[0], next_box_position[1]] == 0 and self.walls[tuple(next_box_position)] == 0:
                next_state[0, player[0], player[1]] = 0
                next_state[0, next_position[0], next_position[1]] = 1
                next_state[1, next_position[0], next_position[1]] = 0

                next_state[1, next_box_position[0], next_box_position[1]] = 1
                
#                 for i in range(len(self.state[2:])):
#                     if (self.state[i+2] == next_position).all():
#                         self.state[i+2] = box_next_position 
#                         if tuple(box_next_position) in self.storage:
#                             self.has_scored[i] = 1.
#                         break
                

        elif self.walls[next_position[0], next_position[1]] == 1:
            pass
        elif state[1, next_position[0], next_position[1]] == 0 and self.walls[next_position[0], next_position[1]] == 0:
            #print("EMPTY")
            next_state[0, player[0], player[1]] = 0
            next_state[0, next_position[0], next_position[1]] = 1
            #return next_position

#         self.state[1,0] = np.sum(self.has_scored)
        return next_state

    # def step(self, evaluate=False):


    #   if not evaluate:
    #       action = self.actor.learn(State(self.state[0], self.state[1:]), self.map)
    #   else:
    #       action = self.actor.evaluate(State(self.state[0], self.state[1:]), self.map)
    #   #print(move)
    #   #print(move)
    #   next_position = action + self.state[0]
    #   #print(next_position)
        






    def draw(self, state, save_figure = False):
        #print(f"num_score:{self.state[1,0]}")
        ax = plt.gca()
        ax.clear()
        #create square boundary
        lim = max(self.xlim, self.ylim)
        plt.xlim(0, lim+1)
        plt.ylim(0, lim+1)
        ax.set_xticks(np.arange(0, lim+1))
        ax.set_yticks(np.arange(0, lim+1))
        plt.grid(alpha=0.2)


        for i in range(self.xlim+1):
            for j in range(self.ylim+1):
                #print((i,j))
                if self.walls[i,j] == 1:
                    rect = patches.Rectangle((i+0.5, j+0.5),-1,-1,linewidth=0.5,edgecolor='slategray',facecolor='slategray')
                    ax.add_patch(rect)

                elif state[0, i,j] == 1:
                    plt.plot(i, j, 'o', color='orange')
                elif state[1, i,j] == 1:  
                    # if self.is_frozen(state, np.array([i, j]), set([])):
                    #     rect = patches.Rectangle((box[0]+0.5, box[1]+0.5), -1, -1, linewidth=0.5, edgecolor='red', facecolor='red')
                    # else:
                    rect = patches.Rectangle((i+0.5, j+0.5), -1, -1, linewidth=0.5, edgecolor='tan', facecolor='tan')
                    ax.add_patch(rect)

        for place in self.storage:
            circle = patches.Circle(place, 0.05, edgecolor='limegreen', facecolor='limegreen')
            ax.add_patch(circle)



        
        #plt.draw()
        #plt.show()
        if save_figure:
            plt.savefig('sokoban.png')
        else:
            plt.show(block=False)
            # background = fig.canvas.copy_from_bbox(ax.bbox)
            # fig.canvas.restore_region(background)
            # fig.canvas.draw()

            plt.pause(0.05)