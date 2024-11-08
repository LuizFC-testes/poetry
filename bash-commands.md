This file describes the process of creating a bash command for poetry applications

# src/poetry/console/application.py

The file that handles the command calls

## Function *load_command*

Imports the module with the command specified by the *name* argument, which must follow a specific path structure, and gets the Command subclass that deals with the execution of the respective command