import random
import sys
import os
import time


## importa classes
from environment import Env
from explorer import Explorer
from rescuer import Rescuer

def main(data_folder_name):
   
    # Set the path to config files and data files for the environment
    current_folder = os.path.abspath(os.getcwd())
    data_folder = os.path.abspath(os.path.join(current_folder, data_folder_name))
    
    # Instantiate the environment
    env = Env(data_folder)
    
    # config files for the agen5ts
    rescuer_file = os.path.join(data_folder, "rescuer_config.txt")
    explorer_file = os.path.join(data_folder, "explorer_config.txt")
    
    # Instantiate agents rescuer and explorer
    resc = Rescuer(env, rescuer_file)

    # Explorer needs to know rescuer to send the map
    # that's why rescuer is instatiated before
    # lista = ['E', 'N', 'NW', 'SW', 'NE', 'SE', 'W', 'S']
    # exp = Explorer(env, explorer_file, [resc], random.sample(lista, len(lista)))
    # exp = Explorer(env, explorer_file, [resc], random.sample(lista, len(lista)))
    # exp = Explorer(env, explorer_file, [resc], random.sample(lista, len(lista)))
    # exp = Explorer(env, explorer_file, [resc], random.sample(lista, len(lista)))
    exp = Explorer(env, explorer_file, [resc], ['E', 'N', 'S', 'W', 'NE', 'NW', 'SW', 'SE'])
    exp = Explorer(env, explorer_file, [resc], ['N', 'W', 'E', 'S', 'NW', 'NE', 'SE', 'SW'])
    exp = Explorer(env, explorer_file, [resc], ['W', 'S', 'N', 'E', 'SW', 'SE', 'NE', 'NW'])
    exp = Explorer(env, explorer_file, [resc], ['S', 'E', 'W', 'N', 'SE', 'NE', 'NW', 'SW'])

    # Run the environment simulator
    env.run()
    
        
if __name__ == '__main__':
    """ To get data from a different folder than the default called data
    pass it by the argument line"""
    
    if len(sys.argv) > 1:
        data_folder_name = sys.argv[1]
    else:
        data_folder_name = os.path.join("datasets", "data_teste_sala")
        
    main(data_folder_name)
