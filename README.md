# VictimSim
A simulator for testing search algorithms in rescue scenarios.
The simulator is used in the course on Artificial Intelligence at UTFPR, Curitiba.
VictimSim simulates catastrophic scenarios with a 2D grid environment where artificial agents search for victims and try to save them.

Some features of the simulator:
- allows one or more agents, each agent has its own color configurable by the config files (in data folder)
- detects colision of an agent with the walls and with the end of the grid (BUMPED perception)
- an agent can detect obstacles and the end of the grid in the neighborhood (one step ahead from the current position)
- more than one agent can occupy the same cell without colision
- controls the scheduling of each agent by its state: ACTIVE, IDLE, TERMINATED or DEAD (only ACTIVE agents can execute actions)
- controls the executing time allowed for each agent - once the time is expired, the agent dies.

The rescuer.py and explorer.py, as provided in the package, are examples of use of the main functionnalities of the simulator.
The Explorer navigates randomly in the environment while the Rescuer has a stored plan. The execution is sequential. 
Upon completion of the Explorer's task of locating and reading vital victim signals, it calls the Rescuer agent to initiate
the rescue mission.

The tools folder contains programs to generate new 2D environments either from scratch or based on existing ones.
