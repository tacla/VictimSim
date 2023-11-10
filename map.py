

class Map:
    def __init__(self, path_priorities):
        self.coord_x = 0 
        self.coord_y = 0
        self.coordinates_map = {'SE': [1,1], 'S': [1,0], 'SW': [1,-1], 'W': [0,-1], 'NW': [-1,-1], 'N': [-1,0], 'NE': [-1,1], 'E': [0,1]}
        self.path_priorities = path_priorities
        self.position = Position(self.path_priorities)
        self.last_position = Position(self.path_priorities)
        self.last_action = ''
        self.backtracking = False
        self.map = {(0,0)}
        self.map = {(0, 0): self.position}

    def get_action(self):
        self.backtracking = False
        mov = (0,0)
        action = ''
        while (self.coord_x+mov[1],self.coord_y+mov[0]) in self.map and action is not None:
            action = self.position.pop_untried()
            if action is not None:
                mov = self.coordinates_map[action]
                self.last_action = action 
        if action is None:
            action = self.get_opposite_action(self.position.last_action)
            mov = self.coordinates_map[action] 
            self.backtracking = True
            self.last_action = action 
        return mov  
    
    def get_opposite_action(self,action):
        if action == 'E':
            return 'W'
        elif action == 'NE':
            return 'SW'
        elif action == 'N':
            return 'S'
        elif action == 'NW':
            return 'SE'
        elif action == 'W':
            return 'E'
        elif action == 'SW':
            return 'NE'
        elif action == 'S':
            return 'N'
        elif action == 'SE':
            return 'NW'
        else:
            return
    
    def update_agent_position(self, dx, dy):
        self.coord_x = self.coord_x + dx
        self.coord_y = self.coord_y + dy
        if (self.coord_x,self.coord_y) not in self.map:
            pos = Position(self.path_priorities)
            pos.coord_x = self.coord_x
            pos.coord_y = self.coord_y
            self.map[(self.coord_x,self.coord_y)] = pos
            pos.last_action = self.last_action
        else:
            pos = self.map[(self.coord_x,self.coord_y)]
            if self.backtracking is not True:
                pos.last_action = self.last_action
        self.position.set_results(self.last_action,pos)
        pos.set_results(self.get_opposite_action(self.last_action),self.position)
        self.last_position = self.position
        self.position = pos
        
    def get_map(self):
        return self.map
    
class Position:
    def __init__(self, path_priorities):
        self.coord_x = 0 
        self.coord_y = 0
        self.results = {'SE': None, 'S': None, 'SW': None, 'W': None, 'NW': None, 'N': None, 'NE': None, 'E': None}
        self.untried = list(path_priorities)
        self.last_action = ''
        
    def pop_untried(self):
        if len(self.untried) != 0:
            return self.untried.pop(0)
        else:
            return 

    def set_results(self,res,pos):
        self.results[(res)] = pos
        