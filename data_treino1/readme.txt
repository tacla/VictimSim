To run the simulator with these configuration files, you have to pass the data
folder name in the command line: python main.py data_treino1

Optionnally, replace the __planner method of the rescuer.py to see the rescuer walking:

    def __planner(self):
        """ A private method that calculates the walk actions to rescue the
        victims. Further actions may be necessary and should be added in the
        deliberation method"""

        # This is a off-line trajectory plan, each element of the list is
        # a pair dx, dy that do the agent walk in the x-axis and/or y-axis

        # go
        self.plan.extend([[0,1],[0,1],[0,1],[0,1],[0,1]])
        self.plan.extend([[1,-1],[0,-1],[1,0],[1,0],[1,0],[1,0]])

        # go back
        reverse_list = list(reversed(self.plan))
        reverse_list = [[-1*item for item in sublist] for sublist in reverse_list]
        self.plan.extend(reverse_list)
