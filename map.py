

class Map:
    def __init__(self):
        self.coord_x = 0 
        self.coord_y = 0
        self.last_action = ''
        self.position = Position()
        self.map = {(0,0)}
        self.map = {(0, 0): self.position}

    def get_action(self):
        mov = [0,0]
        while self.check_position(mov):
            action = self.position.pop_untried()
            if action == 'E':
                mov = [0,1]
                self.last_action = 'E'
            elif action == 'NE':
                mov = [-1,1]
                self.last_action = 'NE'
            elif action == 'N':
                mov = [-1,0]
                self.last_action = 'N'
            elif action == 'NW':
                mov = [-1,-1]
                self.last_action = 'NW'
            elif action == 'W':
                mov = [0,-1]
                self.last_action = 'W'
            elif action == 'SW':
                mov = [1,-1]
                self.last_action = 'SW'
            elif action == 'S':
                mov = [1,0]
                self.last_action = 'S'
            elif action == 'SE':
                mov = [1,1]   
                self.last_action = 'SE' 
        return mov  
    
    def check_position(self,mov) -> bool:  
        if (self.coord_x+mov[1],self.coord_y+mov[0]) in self.map:
            return True
        else:
            return False
           
    def update_agent_position(self, x, y):
        self.coord_x = self.coord_x + x
        self.coord_y = self.coord_y + y
        if (self.coord_x,self.coord_y) not in self.map:
            pos = Position()
            self.map[(self.coord_x,self.coord_y)] = pos
        else:
            pos = self.map[(self.coord_x,self.coord_y)]
        self.position.set_results(self.last_action,pos)
        self.position = pos

    def get_map(self):
        return self.map
    
class Position:
    def __init__(self):
        self.results = {'SE': None, 'S': None, 'SW': None, 'W': None, 'NW': None, 'N': None, 'NE': None, 'E': None}
        self.untried = ['SE','S','SW','W','NW','N','NE','E']
        self.backtracked = False
        
    def pop_untried(self):
        if len(self.untried) != 0:
            return self.untried.pop()
        else:
            return 

    def set_results(self,res,pos):
        self.results[(res)] = pos
        