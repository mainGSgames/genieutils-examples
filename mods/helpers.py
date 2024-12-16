from genieutils.datfile import DatFile
from genieutils.task import Task
from genieutils.effect import Effect, EffectCommand
from genieutils.tech import ResearchResourceCost

from constants import *

NAME = 'helpers'

def amount_type_to_d(value: int, type: int) -> float:
    # Ensure the input is within the range of an 8-bit signed integer
    value = value & 0xFF  # Mask to 8 bits
    if value & 0x80:     # Handle sign extension for negative numbers
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
