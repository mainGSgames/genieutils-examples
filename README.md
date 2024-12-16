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

![image of VSCode](https://github.com/Krakenmeister/genieutils-examples/blob/main/readme_images/vscode_open.png?raw=true)

The most valuable aspect of using VSCode is its ability to recognize the genieutils-py library. When you have it working it will auto-complete for you, highlight syntax for easy readability, and allow you to navigate and reference the genieutils library in a couple clicks. First, you need to install the Python extension. Navigate to the Extension tab and install Python, Python Debugger, Pylance, and Black Formatter.

![image of extensions](https://github.com/Krakenmeister/genieutils-examples/blob/main/readme_images/vscode_extensions.png?raw=true)

Then click on the top bar, "Show and Run Commands >", "Python: Select Interpreter", and then click on the recommended interpreter that should be located locally, i.e. `.\venv\Scripts\python.exe`. Once the intepreter is correctly linked, your code should color in all of the genieutils class objects. This means you can right click on these objects and go directly to their definition and source code to learn how they are put together. It will auto-complete objects with their properties and give errors when you have arranged them incorrectly.

![image of python interpreter](https://github.com/Krakenmeister/genieutils-examples/blob/main/readme_images/vscode_interpreter_0.png?raw=true)
![image of python interpreter](https://github.com/Krakenmeister/genieutils-examples/blob/main/readme_images/vscode_interpreter_1.png?raw=true)
![image of python interpreter](https://github.com/Krakenmeister/genieutils-examples/blob/main/readme_images/vscode_interpreter_2.png?raw=true)
![image of python interpreter](https://github.com/Krakenmeister/genieutils-examples/blob/main/readme_images/vscode_interpreter_3.png?raw=true)
![image of python interpreter](https://github.com/Krakenmeister/genieutils-examples/blob/main/readme_images/vscode_interpreter_4.png?raw=true)
![image of python interpreter](https://github.com/Krakenmeister/genieutils-examples/blob/main/readme_images/vscode_interpreter_5.png?raw=true)

On top of this, you can select the black formatter to auto-format your code on save. Top bar, "Show and Run Commands >", "Preferences: Open Settings (UI)". Then in the settings search for "format on save" and enable it. When you search "black-formatter" you can add extra arguments, like changing the formatted line length to 200 with `--line-length=200`.

## Advanced Genie Editor

Advanced Genie Editor (AGE) is the Graphical User Interface equivalent of genieutils. Both are tools for manipulating binary game .dat files. Since AGE presents all of the information in a visually organized manner, a working familiarity with it will significantly speed up your ability to create mods with genieutils. Also, it can be used as a reference for values and IDs that aren't included as constants in this suite of examples.

To open it, first locate your base game directory. It should be something along the lines of `C:\Program Files (x86)\Steam\steamapps\common\AoE2DE` (insert your Steam download directory). Then go to Tools_Builds folder and open AdvancedGenieEditor3.exe. Your base game .dat file will be located in `[your base directory]\resources\_common\dat\empires2_x2_p1.dat` and can be opened in AGE for inspection.

## DatFile Structure and How They Work

DatFiles can be broken down into the following tree:

-   DatFile
    -   Techs
        -   Effect ID (link)
    -   Effects
        -   EffectCommands
    -   Civs
        -   Units
    -   Graphics
    -   Sounds

First thing to note is that each civilization has its own unique set of units. This means that the British Longswordsman can have different base stats from a Mongol Longswordsman. That said, this is almost NEVER the correct way to civ-specific modifications. All civs' units are nearly identical, so whenever you make a modification to one civ's unit, you should make the exact same modification to every civ's unit of the same ID.

Instead, civ-specific modifications are done with technologies that only that particular civilization has access to. All civilization bonuses are simply technologies researched by a civilization instantly and for free at the start of the game. Now a technology in and of itself doesn't do anything. It has an Effect ID which is the index of the Effect in the DatFile that will be applied upon research. Once again, Effects in and of themselves don't do anything. Each Effect has a list of EffectCommands, and THESE are the actual objects that change how the game state through unit stats, researchability, upgrades, etc.

Let's see this in action (follow along by opening the base game in AGE):

Take the Turk bonus of gunpowder units +25% HP. All of the Turk gunpowder units have identical base stats as every other civilization's gunpowder units. However there is a technology of ID 301, meaning it is the 301st (0-indexed) entry of the DatFile.Techs list, called "C-Bonus, Gunpowder +25% HP". The technology's civilization value is 10, meaning the 10th civilization (0-indexed) has exclusive access to it, which is the Turks. It has 0 required technologies, 0 research time, 0 cost, and -1 i.e. no research location. This causes it to be instantly researched for you at the start of the game if and only if you are the Turkish (or 10th) civilization.

The gunpowder bonus tech has an Effect ID of 296, which means that at the start of the game, it will take the 296th entry (0-indexed) of the DatFile.Effects list and apply that all of that Effect's EffectCommands to the Turkish civilization. Examining Effect 296 and we find that it is called "C-Bonus, Gunpowder +25% HP". It has 14 EffectCommands, one for each gunpowder unit. Each EffectCommand has type 5 (attribute multiply), corresponding unit value, corresponding attribute value (HP), and amount multiplier of 1.25 which equals +25%.

## Modding

You are now ready to make dynamic mods with genieutils! The power of Python is at your fingertips and the only limit for mods now is your creativity. Dissect the examples located in the mods folder, start simple when you try your own changes, and have fun!
