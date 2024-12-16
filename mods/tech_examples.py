import copy

from genieutils.datfile import DatFile
from genieutils.tech import ResearchResourceCost, Tech

from constants import *
from mods import helpers

NAME = 'tech_examples'

# Example of changing a technology's cost to research
def change_tech_costs(df: DatFile):
    print("Set Corvinian Army costs to 69 food, 420 stone")
    new_food_cost: ResearchResourceCost = ResearchResourceCost(resources.FOOD, 69, 1)
    new_stone_cost: ResearchResourceCost = ResearchResourceCost(resources.STONE, 420, 1)
    empty_resource_cost: ResearchResourceCost = ResearchResourceCost(resources.NULL, 0, 0) # this inclusion is necessary because the tuple must have 3 items
    df.techs[techs.CORVINIAN_ARMY].resource_costs = (new_food_cost, new_stone_cost, empty_resource_cost)

    # Alternatively, use the helper function to convert (food_cost, wood_cost, stone_cost, gold_cost) into a valid cost
    print("Set Hul'che Javelineers costs to 300 food, 300 stone")
    df.techs[techs.HULCHE_JAVELINEERS].resource_costs = helpers.costs_array_to_tech_research_cost((300, 0, 300, 0))

# Change where the button to research shows up
def change_tech_button_location(df: DatFile):
    # Button locations are arranged like so:
    # 1   2   3   4   5
    # 6   7   8   9   10
    # 11  12  13  14  15
    # Note that buttons 5 and 15 can be occupied by things like the flag button or the town bell
    # If two technologies occupy the same button you will be able to research one after the other
    # If a unit overlaps with a technology button ID it could prevent it from ever being researched
    print("Moving loom to the bottom")
    df.techs[techs.LOOM].button_id = 12

# Move a technology to a different building
def change_tech_research_location(df: DatFile):
    print("Moving wheelbarrow to the lumber camp")
    df.techs[techs.WHEELBARROW].research_location = units.LUMBER_CAMP

    # There are a lot of fields that can only have one value, which means if you want it to hold multiple values, you will have to duplicate the entire object
    print("Copying wheelbarrow to mill")
    tech_copy: Tech = copy.deepcopy(df.techs[techs.WHEELBARROW]) # Create a deep copy of the technology (so that changing the copy won't change the original)
    tech_copy.research_location = units.MILL # Move it to the mill
    tech_copy.name = "Wheelbarrow mill" # Rename it for clarity
    df.techs.append(tech_copy) # Add the copy to the datfile

def run_tech_examples(df: DatFile):
    change_tech_costs(df)
    change_tech_button_location(df)
    change_tech_research_location(df)

