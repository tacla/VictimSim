import sys
import os
# Open the file for reading
env_size_file = os.path.join("..","data","env_size.txt")
with open(env_size_file, "r") as file:

    # Initialize variables
    env_dict = {}

    # Read each line of the file
    for line in file:

        # Split the line into words
        words = line.split()

        # Get the keyword and value
        keyword = words[0]
        raw_value = words[1]

        # Assign the value to the appropriate variable
        if keyword == "BASE":
            value = [int(i) for i in raw_value.split(',')]
        else:
            value = int(raw_value)

        env_dict[keyword] = value

    # Print the values
    print("dict:", env_dict)
  
