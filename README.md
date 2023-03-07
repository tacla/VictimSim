# VictimSim
A simulator for testing search algorithms in rescue scenarios.
The simulator is using in the course on Artificial Intelligence at UTFPR, Curitiba.
VictimSim simulates catastrophic scenarios with a simple grid 2D environment where artificial agents search for victims and try to save them.

Some features of the simulator:
- allows one or more agents, each agent has its own color configurable by the config files (in data folder)
- detects colision of the agents with the walls and with the end of the grid (BUMPED perception)
- controls the scheduling of each agent by its state: ACTIVE, IDLE, TERMINATED or DEAD (only ACTIVE agents can execute actions)
- controls the executing time giving for each agent - once the time is expired, the agent dies.

The rescuer.py and explorer.py as provided in the packet are examples of use of the main functionnalities of the simulator.
The Explorer walks randomly in the environment while the Rescuer has a stored plan. The execution is sequential. 
When the explorer finishes the task of locating and reading the vital signals of victims, it calls the Rescuer agent to start
the rescue task.
