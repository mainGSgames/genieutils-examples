from genieutils.datfile import DatFile
from genieutils.task import Task
from genieutils.effect import Effect, EffectCommand
from genieutils.tech import ResearchResourceCost, Tech
from genieutils.unit import ResourceCost

from constants import *

NAME = "helpers"


def amount_type_to_d(value: int, type: int) -> float:
    # Ensure the input is within the range of an 8-bit signed integer
    value = value & 0xFF  # Mask to 8 bits
    if value & 0x80:  # Handle sign extension for negative numbers
        value -= 0x100

    # Ensure the type is within the range of an 8-bit unsigned integer
    type = type & 0xFF

    # Combine value and type into a 32-bit integer
    NewD = (type << 8) | (value & 0xFF)

    # Convert to float and return
    return float(NewD)


# Convert a 4-item list of resource costs into the appropriate tuple format for researching technologies
# The costs should be organized as [food_cost, wood_cost, stone_cost, gold_cost]
# Note that you can only have a maximum of 3 positive costs
def costs_array_to_tech_research_cost(costs: tuple[int, int, int, int]) -> tuple[ResearchResourceCost, ResearchResourceCost, ResearchResourceCost]:
    num_positive_costs = 0
    for cost in costs:
        if cost > 0:
            num_positive_costs += 1

    # If this has no costs or 4 different costs, return an empty cost
    if num_positive_costs <= 0 or num_positive_costs > 3:
        print("Incorrect technology cost detected")
        return (ResearchResourceCost(resources.NULL, 0, 0), ResearchResourceCost(resources.NULL, 0, 0), ResearchResourceCost(resources.NULL, 0, 0))

    # Add the positive costs
    resource_costs = []
    for resource_type in range(4):
        if costs[resource_type] > 0:
            resource_costs.append(ResearchResourceCost(resource_type, costs[resource_type], 1))

    # Pad the costs with empty amounts so that we get a total of 3 costs
    while len(resource_costs) < 3:
        resource_costs.append(ResearchResourceCost(resources.NULL, 0, 0))

    return tuple(resource_costs)


# Convert a 4-item list to resource costs in the appropriate tuple format for unit costs
# The costs should be organized as [food_cost, wood_cost, stone_cost, gold_cost]
# For units you can have a maximum of 2 positive costs and buildings can have a maximum of 3 positive costs (units need a headroom cost)
def costs_array_to_unit_cost(costs: tuple[int, int, int, int], isBuilding: bool) -> tuple[ResourceCost, ResourceCost, ResourceCost]:
    empty_cost: ResourceCost = ResourceCost(-1, 0, 0)

    num_positive_costs = 0
    for cost in costs:
        if cost > 0:
            num_positive_costs += 1

    # If it's a unit make sure it has 2 or less positive costs, if it's a building make sure it has 3 or less positive costs
    if num_positive_costs <= 0 or num_positive_costs > 3 or (num_positive_costs > 2 and isBuilding):
        print("Incorrect unit cost detected")
        return (empty_cost, empty_cost, empty_cost)

    resource_costs = []
    for resource_type in range(4):
        if costs[resource_type] > 0:
            resource_costs.append(ResourceCost(resource_type, costs[resource_type], 1))

    desired_len = 3
    if not isBuilding:
        desired_len = 2

    # Pad the costs up to the correct amount
    while len(resource_costs) < desired_len:
        resource_costs.append(empty_cost)

    # For units add a population headroom cost
    if not isBuilding:
        resource_costs.append(ResourceCost(resources.POPULATION_HEADROOM, 1, 0))

    return tuple(resource_costs)


def create_empty_tech() -> Tech:
    empty_cost: ResearchResourceCost = ResearchResourceCost(-1, 0, 0)
    return Tech(
        required_techs=(-1, -1, -1, -1, -1, -1),
        resource_costs=(empty_cost, empty_cost, empty_cost),
        required_tech_count=0,
        civ=-1,
        full_tech_mode=0,
        research_location=-1,
        language_dll_name=0,
        language_dll_description=0,
        research_time=0,
        effect_id=-1,
        type=0,
        icon_id=-1,
        button_id=0,
        language_dll_help=0,
        language_dll_tech_tree=0,
        hot_key=-1,
        name="",
        repeatable=1,
    )


# Copy the unit graphics from civilization onto another
def copy_architecture(df: DatFile, copyFrom: int, copyTo: int):
    df.civs[copyTo].icon_set = df.civs[copyFrom].icon_set  # Holds no gameplay purpose but good for organization in AGE
    for unit_id in range(len(df.civs[copyFrom].units)):
        if df.civs[copyFrom].units[unit_id] is None:
            continue
        if (
            df.civs[copyFrom].units[unit_id].class_ == unit_classes.BUILDING
            or df.civs[copyFrom].units[unit_id].class_ == unit_classes.TOWER
            or df.civs[copyFrom].units[unit_id].class_ == unit_classes.WALL
            or df.civs[copyFrom].units[unit_id].class_ == unit_classes.GATE
        ):
            df.civs[copyTo].units[unit_id].standing_graphic = df.civs[copyFrom].units[unit_id].standing_graphic
            df.civs[copyTo].units[unit_id].dying_graphic = df.civs[copyFrom].units[unit_id].dying_graphic
            df.civs[copyTo].units[unit_id].undead_graphic = df.civs[copyFrom].units[unit_id].undead_graphic
            df.civs[copyTo].units[unit_id].damage_graphics = df.civs[copyFrom].units[unit_id].damage_graphics
            df.civs[copyTo].units[unit_id].building = df.civs[copyFrom].units[unit_id].building
            df.civs[copyTo].units[unit_id].creatable.garrison_graphic = df.civs[copyFrom].units[unit_id].creatable.garrison_graphic
        elif (
            df.civs[copyFrom].units[unit_id].class_ == unit_classes.KING
            or df.civs[copyFrom].units[unit_id].class_ == unit_classes.TRADE_CART
            or df.civs[copyFrom].units[unit_id].class_ == unit_classes.MONK
            or df.civs[copyFrom].units[unit_id].class_ == unit_classes.MONK_WITH_RELIC
        ):
            df.civs[copyTo].units[unit_id].standing_graphic = df.civs[copyFrom].units[unit_id].standing_graphic
            df.civs[copyTo].units[unit_id].dying_graphic = df.civs[copyFrom].units[unit_id].dying_graphic
            df.civs[copyTo].units[unit_id].undead_graphic = df.civs[copyFrom].units[unit_id].undead_graphic
            df.civs[copyTo].units[unit_id].dead_fish.walking_graphic = df.civs[copyFrom].units[unit_id].dead_fish.walking_graphic
            df.civs[copyTo].units[unit_id].type_50.attack_graphic = df.civs[copyFrom].units[unit_id].type_50.attack_graphic
            if df.civs[copyFrom].units[unit_id].class_ == unit_classes.TRADE_CART:
                for task_id in range(len(df.civs[copyFrom].units[unit_id].bird.tasks)):
                    df.civs[copyTo].units[unit_id].bird.tasks[task_id].carrying_graphic_id = df.civs[copyFrom].units[unit_id].bird.tasks[task_id].carrying_graphic_id
            elif df.civs[copyFrom].units[unit_id].class_ == unit_classes.MONK:
                for task_id in range(len(df.civs[copyFrom].units[unit_id].bird.tasks)):
                    df.civs[copyTo].units[unit_id].bird.tasks[task_id].proceeding_graphic_id = df.civs[copyFrom].units[unit_id].bird.tasks[task_id].proceeding_graphic_id
