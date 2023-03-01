# Author Tacla, UTFPR
# Version 1  fev/2023

import sys
import os
import pygame
import random
import csv
import time
from explorer import Explorer
from physical_agent import PhysAgent


## Class Environment
class Env:
    # class attributes
    # Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    RED = (255, 0, 0)
    CYAN = (0, 255, 255)
    YELLOW = (255, 255, 0)

    # Victim color by injury severity - from the most severe to the least
    VICTIM_COLOR = [(255,51,51), (255,128,0), (255,255,51), (128,255,0)]

    # Index to the gravidade in sinais_vitais.txt (position)
    IDX_SEVERITY = 7

    def __init__(self, data_folder):
        # instance attributes
        self.data_folder = data_folder # folder for the config and data files
        self.dic = {}          # configuration of grid and window
        self.agents = []       # list of running physical agents
        self.walls  = None     # list of walls - 1 for walls, 0 for no walls - inner list is row
                               # explorer agent cannot access this attribute, it has to find!
        self.nb_of_victims = 0 # total number of victims
        self.victims = []      # positional: the coordinates of the victims [(x1,y1), ..., (xn, yn)]
        self.severity = []     # positional: the injury severity for each victim
        self.signals = []      # positional: the vital signals of the victims [[i,s1,...,s5,g,l],...]
        self.found   = [[]]    # positional: Physical agents that found each victim [[ag1] [ag2, ag3], ...] ag1 found vict 0, ag2 and 3, vict 1, ... 
        self.saved   = [[]]    # positional: Physical agents that saved each victim 
        
        # Read the environment config file
        self.__read_config()
        # print(self.dic)

        # Set up the walls - it's a list composed of GRID_WIDTH lists. Each sublist is a column (y=0, 1, ...)
        self.walls = [[0 for y in range(self.dic["GRID_HEIGHT"])] for x in range(self.dic["GRID_WIDTH"])]
        walls_file = os.path.join(self.data_folder,"env_walls.txt")

        with open(walls_file, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                x = int(row[0])
                y = int(row[1])
                self.walls[x][y] = 1
        # print(self.walls)

        # Read and put the victims into the grid

        victims_file = os.path.join(self.data_folder,"env_victims.txt")
        
        with open(victims_file, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                x = int(row[0])
                y = int(row[1])
                self.victims.append((x, y))   # append tuples

        self.nb_of_victims = len(self.victims)

        # Load the vital signals of the victims
        vs_file = os.path.join(self.data_folder,"sinais_vitais.txt")
        
        with open(vs_file, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                self.signals.append(row)
                self.severity.append(int(row[Env.IDX_SEVERITY]))

        if self.nb_of_victims > len(self.signals):
            print("from env: number of victims of env_victims.txt greater than vital signals")
            print("from env: end of execution")
            exit()
            
        if self.nb_of_victims < len(self.signals):
            print("from env: nb of victims of env_victims.txt less than vital signals")
            print("from env: Assuming nb of victims of env_victims.txt")

        # Set up found and saved victims' lists 
        self.found = [[] for v in range(self.nb_of_victims)]
        self.saved = [[] for v in range(self.nb_of_victims)]
                
        # Set up with the trace color of the last physical agent who visited the cell
        self.visited = [[(0,0,0) for y in range(self.dic["GRID_HEIGHT"])] for x in range(self.dic["GRID_WIDTH"])]
        

    
    def __read_config(self):
        """ Read the size of the grid and window and loads into a dictionary """   
        # Open config file
        size_file = os.path.join(self.data_folder, "env_size.txt")
        with open(size_file, "r") as file:
            # Read each line of the file
            for line in file:
                # Split the line into words
                words = line.split()

                # Get the keyword and value
                keyword = words[0]
                raw_value = words[1]

                # casts the value 
                if keyword == "BASE":
                    value = [int(i) for i in raw_value.split(',')]
                elif keyword == "DELAY":
                    value = float(raw_value)
                else:
                    value = int(raw_value)

                self.dic[keyword] = value               

    
    def add_agent(self, mind, state=PhysAgent.ACTIVE):
        """ This public method adds an agent to the simulator.
        It connects the mind to the body (PhysAgent)
        @param self: the environment object
        @param mind: the mind of the agent
        @param state: the state of the physical agent
        @return: an object that is the physical agent"""

        body = PhysAgent(mind, self, self.dic["BASE"][0], self.dic["BASE"][1], state) 
        self.agents.append(body)
        return body

    def __draw(self):
        """ This private method draw the grid and its items """

        # Set cell width and height
        cell_w = self.dic["WINDOW_WIDTH"]/self.dic["GRID_WIDTH"]
        cell_h = self.dic["WINDOW_HEIGHT"]/self.dic["GRID_HEIGHT"]

        # Clear the screen
        self.screen.fill(Env.WHITE)

        # Draw the grid
        for x in range(self.dic["GRID_WIDTH"]):
            for y in range(self.dic["GRID_HEIGHT"]):
                rect = pygame.Rect(x * cell_w, y * cell_h, cell_w, cell_h)
                pygame.draw.rect(self.screen, Env.BLACK, rect, 1)

                if self.walls[x][y] == 1:
                    wall_rect = pygame.Rect(x * cell_w + 1, y * cell_h + 1, cell_w - 2, cell_h - 2)
                    pygame.draw.rect(self.screen, Env.BLACK, wall_rect)                   

                # Paint visited cells
                if self.visited[x][y] != (0,0,0):
                    trace_color = self.visited[x][y]
                    visited_rect = pygame.Rect(x * cell_w + 1, y * cell_h + 1, cell_w - 2, cell_h - 2)
                    pygame.draw.rect(self.screen, trace_color, visited_rect)

        # Draw a marker at the base
        rect = pygame.Rect(self.dic["BASE"][0] * cell_w, self.dic["BASE"][1] * cell_h, cell_w, cell_h)
        pygame.draw.rect(self.screen, Env.CYAN, rect, 4)       

        # Draw the victims
        v=0
        for victim in self.victims:
            victim_rect = pygame.Rect(victim[0] * cell_w + 2, victim[1] * cell_h + 2, cell_w - 4, cell_h - 4)
            c = self.severity[v]-1
            pygame.draw.ellipse(self.screen, Env.VICTIM_COLOR[c], victim_rect)
            if self.saved[v] != []:
                pygame.draw.ellipse(self.screen, self.WHITE, victim_rect, 3)
            elif self.found[v] != []:
                pygame.draw.ellipse(self.screen, self.BLACK, victim_rect, 3)
            v = v + 1

        # Draw the physical agents
        for body in self.agents:
            if body.state == PhysAgent.ACTIVE:
               ag_rect = pygame.Rect(body.x * cell_w, body.y * cell_h, cell_w, cell_h)
               pygame.draw.rect(self.screen, body.mind.COLOR, ag_rect)
               active_idle = True

        # Update the display
        pygame.display.update()
        
                
    def run(self):
        """ This public method is the engine of the simulator. It calls the deliberate
        method of each ACTIVE agent situated in the environment. Then, it updates the state
        of the agents and of the environment"""
        # Set up Pygame
        pygame.init()

        # Create the font object
        self.font = pygame.font.SysFont(None, 24)

        # Create the window
        self.screen = pygame.display.set_mode((self.dic["WINDOW_WIDTH"], self.dic["WINDOW_HEIGHT"]))

        # Draw the environment with items
        self.__draw()
        
        # Create the main loop
        running = True

        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:                  
                    running = False
                    
            # control whether or not there are active or idle agents
            active_or_idle = False

            # ask each agent to deliberate the next action
            for body in self.agents:

                # Asks the agent to choose and to do the next action if it is ACTIVE               
                if body.state == PhysAgent.ACTIVE:
                    active_or_idle = True
                    more_actions_to_do = body.mind.deliberate()

                    # Test if the agent exceeded the time limit
                    if body.end_of_time():
                        body.set_state(PhysAgent.DEAD)
                        print("from env: " + body.mind.NAME + ": time limit reached, no batt, it is dead")
                    elif not more_actions_to_do: # agent do not have more actions to do
                        if body.at_base():
                            print("from env: ag " + body.mind.NAME + " succesfully terminated, it is at the base")
                            body.set_state(PhysAgent.ENDED)
                        else:
                            print("from env: ag " + body.mind.NAME + " lost its mind, not at the base, and asked for termination. Now, it's dead")
                            body.set_state(PhysAgent.DEAD)

                elif body.state == PhysAgent.IDLE:
                    active_or_idle = True

            # Update the grid after the delay
            if self.dic["DELAY"] > 0:
                time.sleep(self.dic["DELAY"])
                
            self.__draw()

            # Show metrics
            if not active_or_idle:
                print("from env: no active or idle agent scheduled for execution... terminating")
                self.print_results()
                print("\n--------------")
                input("from env: Tecle qualquer coisa para encerrar >>")
                running = False
   

        # Quit Pygame
        pygame.quit()

    def __print_victims(self, victims, type_str, sub):
        """ Print either the found or the saved victims list
        @param victims: it is the list to be printed
        @param type_str: it is a string for composing the pring
        @param sub: it is a character representing the metric"""


        if len(victims) > 0:
            print(f"\nList of {type_str} victims followed by the corresponding severity (gravidade)")
            print(victims)
            
            sev = []
            for v in victims:
                sev.append(self.severity[v])
                
            print(sev)

            print("\n")
            print(f"Critical victims {type_str}     (V{sub}1) = {sev.count(1):3d} ")
            print(f"Instable victims {type_str}     (V{sub}2) = {sev.count(2):3d} ")
            print(f"Pot. inst. victims {type_str}   (V{sub}3) = {sev.count(3):3d} ")
            print(f"Stable victims {type_str}       (V{sub}4) = {sev.count(4):3d} ")
            print("--------------------------------------")
            print(f"Total of {type_str} victims     (V{sub})  = {len(sev):3d} ({100*float(len(sev)/self.nb_of_victims):.2f}%)")

            weighted = ((6*sev.count(1) + 3*sev.count(2) + 2*sev.count(3) + sev.count(4))/
            (6*self.severity.count(1)+3*self.severity.count(2)+2*self.severity.count(3)+self.severity.count(1)))

            print(f"Weighted {type_str} victims per severity (V{sub}g) = {weighted:.2f}")

    def print_results(self):
        """ For each agent, print found victims and saved victims by severity
        This is what actually happened in the environment. Observe that the
        beliefs of the agents may be different."""      

        print("\n\n\n*** Numbers of Victims in the Environment ***")
        print(f"Critical victims   (V1) = {self.severity.count(1):3d}")
        print(f"Instable victims   (V2) = {self.severity.count(2):3d}")
        print(f"Pot. inst. victims (V3) = {self.severity.count(3):3d}")
        print(f"Stable victims     (V4) = {self.severity.count(4):3d}")
        print("--------------------------------------")
        print(f"Total of victims   (V)  = {self.nb_of_victims:3d}")
              
        print("\n\n*** Final results per agent ***")
        for body in self.agents:
            print(f"\n[ Agent {body.mind.NAME} ]")
            if body.state == PhysAgent.DEAD:
                print("This agent is dead, you should discard its results, but...")

            # Remaining time
            print("\n*** Used time ***")
            print(f"{body.mind.TLIM - body.rtime} of {body.mind.TLIM}")
        
            # Found victims
            found = body.get_found_victims()
            self.__print_victims(found, "found","e")

            # Saved victims
            saved = body.get_saved_victims()
            self.__print_victims(saved, "saved","s")
 
            


