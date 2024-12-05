import random

# Define the list of commands
commands = [
    #"ENGINE_BTN",
    "ACCELERATE", "BRAKE", "LOCK", "UNLOCK",
    "LEFT_DOOR_LOCK", "LEFT_DOOR_UNLOCK", "LEFT_DOOR_OPEN", 
    "LEFT_DOOR_CLOSE", "TRUNK_OPEN", "SOS"
]

# Generate 100 random commands
random_commands = [random.choice(commands) for _ in range(100)]

# Write commands to a file
with open("random_commands.txt", "w") as file:
    file.write("ENGINE_BTN\n")
    for command in random_commands:
        file.write(command + "\n")

print("100 random commands have been written to random_commands.txt.")