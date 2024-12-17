import copy

from genieutils.datfile import DatFile
from genieutils.tech import ResearchResourceCost, Tech
from genieutils.effect import Effect, EffectCommand

from constants import *
from mods import helpers

NAME = "tech_examples"



# Change a technology's name
def change_tech_name(df: DatFile):
    # Changing the internal name of a technology will have no effect in-game
    # It is very useful for organization as it will show up as the searchable name when the .dat file is viewed in Advanced Genie Editor
    print("Changing internal name of town watch")
    df.techs[techs.TOWN_WATCH].name = "peepin toms"

    # Without a UI mod, it is impossible to fully customize a technology's name or description
    # The data mod can only change the ID that the UI will lookup in a table to find the string that goes with it
    print("Changing the displayed name of double-bit axe")
    # If you look in the base-game files at resources/en/strings/key-value/key-value-strings-utf8.txt you will see the entry corresponding to 5849 should equal "Smoke Imix God"
    df.techs[techs.DOUBLE_BIT_AXE].language_dll_name = 5849
    # Note that you could write a UI mod that gives whatever number you put here a different value, but as stated previously that will act independently of the data mod
    df.techs[techs.DOUBLE_BIT_AXE].language_dll_description = 208605  # What will this say?


# Example of changing a technology's cost to research
def change_tech_costs(df: DatFile):
    print("Set Corvinian Army costs to 69 food, 420 stone")
    new_food_cost: ResearchResourceCost = ResearchResourceCost(resources.FOOD, 69, 1)
    new_stone_cost: ResearchResourceCost = ResearchResourceCost(resources.STONE, 420, 1)
    empty_resource_cost: ResearchResourceCost = ResearchResourceCost(resources.NULL, 0, 0)  # this inclusion is necessary because the tuple must have 3 items
    df.techs[techs.CORVINIAN_ARMY].resource_costs = (
        new_food_cost,
        new_stone_cost,
        empty_resource_cost,
    )

    # Alternatively, use the helper function to convert (food_cost, wood_cost, stone_cost, gold_cost) into a valid cost
    print("Set Hul'che Javelineers costs to 300 food, 300 stone")
    df.techs[techs.HULCHE_JAVELINEERS].resource_costs = helpers.costs_array_to_tech_research_cost((300, 0, 300, 0))

    # Also note that technology discounts are calculated additively instead of multiplicatively and if you want to be precise with your technology cost changes
    # you should also recalculate any discounts that might be affected




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


# Modify research times
def change_tech_research_time(df: DatFile):
    # Simple example
    print("Making Feudal Age research in 5 seconds")
    df.techs[techs.FEUDAL_AGE].research_time = 5

    # More involved example
    print("Double the research time of all barracks technologies")
    for tech in df.techs:
        if tech.research_location == units.BARRACKS:
            tech.research_time *= 2


# Move a technology to a different building
def change_tech_research_location(df: DatFile):
    # Simple example
    print("Moving wheelbarrow to the lumber camp")
    df.techs[techs.WHEELBARROW].research_location = units.LUMBER_CAMP

    # More involved example...
    # There are a lot of fields that can only have one value, which means if you want it to hold multiple values, you will have to duplicate the entire object
    print("Copying wheelbarrow to mill")
    tech_copy: Tech = copy.deepcopy(df.techs[techs.WHEELBARROW])  # Create a deep copy of the technology (so that changing the copy won't change the original)
    tech_copy.research_location = units.MILL  # Move it to the mill
    tech_copy.name = "Wheelbarrow mill"  # Rename it for clarity

    # Unfortunately now that we have two wheelbarrow technologies, we will be able to research BOTH of them. So we will have to make them mutually exclusive
    # We can accomplish this by making each wheelbarrow technology disable the other (* see foot note)
    # However, right now both technologies are linked to the same Effect. If we change one's Effect it will change both's Effects
    # Let's create a new wheelbarrow effect for the new technology
    original_wheelbarrow_effect_id = df.techs[techs.WHEELBARROW].effect_id
    effect_copy: Effect = copy.deepcopy(df.effects[original_wheelbarrow_effect_id])  # Copy the effect whose ID is that of the wheelbarrow's effect ID
    effect_copy.name = "Wheelbarrow mill effect"  # Rename it for clarity

    disable_original_wheelbarrow_tech: EffectCommand = EffectCommand(102, -1, -1, -1, techs.WHEELBARROW)
    effect_copy.effect_commands.append(disable_original_wheelbarrow_tech)
    df.effects.append(effect_copy)  # Add the new effect to the datfile
    tech_copy.effect_id = len(df.effects) - 1  # Make it so our new technology will apply the new effect

    df.techs.append(tech_copy)  # Add the copy to the datfile
    wheelbarrow_copy_id = len(df.techs) = 1 # Save its tech ID

    # Don't forget that the original wheelbarrow has to disable our new one as well
    disable_new_wheelbarrow_tech: EffectCommand = EffectCommand(102, -1, -1, -1, wheelbarrow_copy_id)
    df.effects[original_wheelbarrow_effect_id].effect_commands.append(disable_new_wheelbarrow_tech)

    # * We can also more simply accomplish this by having both technologies disable themselves and the other, because once the research is complete, disabling it won't
    # reverse its effects. This is a more niche solution though, and learning how technologies and effects interact is important. I encourage you to implement
    # this solution though as a test of your understanding! (hint: you do not need to create any Effects, just EffectCommands)


# Alter which technologies are required before another technology is researchable
def change_tech_prerequisites(df: DatFile):
    print("Making halberdier available in Castle Age for all civs")
    # The following two commands accomplish the same task, replacing the imperial age requirement with a castle age requirement
    df.techs[techs.HALBERDIER].required_techs = (
        techs.CASTLE_AGE,
        techs.PIKEMAN,
        956,
        -1,
        -1,
        -1,
    )  # This is more readable but somewhat hard-coded
    df.techs[techs.HALBERDIER].required_techs = tuple(
        map(
            lambda prerequisite: (techs.CASTLE_AGE if prerequisite == techs.IMPERIAL_AGE else prerequisite),
            df.techs[techs.HALBERDIER].required_techs,
        )
    )  # This is less readable but will adapt in case of other modifications

    print("Making coinage available in Feudal Age for Franks")
    # Because coinage has civilization = -1, anyone can research it, and any modification we make to it will apply to all civilizations equally
    # In order to accomplish our task, we first must create a dummy prerequisite tech that Franks insantly research for free upon researching Feudal Age
    coinage_prerequisite: Tech = Tech() # This will default to no prerequisites, no cost, no research time, no research location
    coinage_prerequisite.name = "Coinage prerequisite" # change name for clarity
    coinage_prerequisite.civ = civilizations.FRANKS
    coinage_prerequisite.required_techs = (techs.FEUDAL_AGE, -1, -1, -1, -1, -1)
    coinage_prerequisite.required_tech_count = 1

    df.techs.append(coinage_prerequisite) # Add the technology
    coinage_prerequisite_tech_id = len(df.techs) - 1 # Save the new tech ID

    # Now add the new prerequisite as a requirement to research coinage
    df.techs[techs.COINAGE].required_techs = (techs.CASTLE_AGE, coinage_prerequisite_tech_id, -1, -1, -1, -1)
    # You would think that ADDING a required technology would make it impossible for any other civ to research coinage
    # But we are notably NOT increasing the required tech count, meaning that you still only need ONE of the required techs to satisfy your prerequisites
    # That means that you need either Castle Age OR the dummy prerequisite in order to research coinage
    # In other words every other civ remains unaffected (they will fulfill the requirements by reaching Castle Age) and Franks will be able to fulfill the requirements
    # upon hitting Feudal Age

def run_tech_examples(df: DatFile):
    change_tech_name(df)
    change_tech_costs(df)
    change_tech_button_location(df)
    change_tech_research_time(df)
    change_tech_research_location(df)
    change_tech_prerequisites(df)