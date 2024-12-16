# Genieutils Examples

Examples using genieutils-py demonstrating how to create AoE2 mods in Python

## Setup Instructions

1. If you do not have git, install it and clone this repository with the command `git clone https://github.com/Krakenmeister/genieutils-examples.git` [Tutorial video](https://www.youtube.com/watch?v=ne5ACsz-k2o&ab_channel=TonyTeachesTech)
2. You will need Python 3.11 or higher, can be checked with the command `python --version` in Command Prompt. Downloads can be found [here](https://www.python.org/downloads/), video tutorial [here](https://www.youtube.com/watch?v=m9I-YpOjXVQ&ab_channel=GeekyScript)
3. Open a terminal/command prompt at the location of the cloned repository. If you run `dir` in Command Prompt or `ls` on Linux it should print out all of the files in this repository, e.g. create_mod.py, requirements.txt, datfiles, etc.
4. Create a virtual environment for Python to install only the packages it needs where it needs them. This is done with the command `python -m venv venv`
5. Activate the virtual environment with the command `call venv/Scripts/activate` for Windows, or `source venv/bin/activate` in Linux environments. When activated, the prompter should have a little `(venv)` indicator before the printing the directory you are currently in. To exit the virtual environment you can run `deactivate`
6. Install the genieutils-py library and any other dependencies. This can be accomplished with `python -m pip install -r requirements.txt`
7. Try running the example suite with `python ./create_mod.py`. It should load the game data, parse it, run the example modifications, and save the new file to datfiles/empires2_x2_p1.dat. This has successfully run once you get the output "Process completed!" Note that the parsing might take a while and if your machine has too little memory your operating system might terminate it for taking too long and hogging RAM. However, once it completes once it will cache that information to make it faster on subsequent runs.

## Coding Environment

If you have a Python coding workspace that works for you, feel free to skip this. If you are newer though, getting this up and running correctly will be quite helpful. First you're going to want to download an IDE, in this case I recommend VSCode ([download here](https://code.visualstudio.com/download)). Then open the project directory, which should look something like this:

![image of VSCode](https://github.com/Krakenmeister/genieutils-examples/blob/main/tutorial/vscode_open.png?raw=true)

The most valuable aspect of using VSCode is its ability to recognize the genieutils-py library. When you have it working it will auto-complete for you, highlight syntax for easy readability, and allow you to navigate and reference the genieutils library in a couple clicks. First, you need to install the Python extension.
