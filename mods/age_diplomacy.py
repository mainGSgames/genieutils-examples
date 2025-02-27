import copy

from genieutils.datfile import DatFile
from genieutils.unit import Unit, ResourceCost, ResourceStorage, Task
from constants import *
from mods import helpers

NAME = "age_diplomacy"

def run_age_diplomacy(df: DatFile):
    # Modification Overview
    # 1. Triple health of all buildings
    # 2. Double build time of all buildings
    # 3. Make SPEARMAN and HALBERDIER train twice as fast

    # Adjust age-research times
    RESEARCH_MULTIPLIER = 1.2
    print("TEST: Making Age research take longer")
    df.techs[techs.FEUDAL_AGE].research_time = int(df.techs[techs.FEUDAL_AGE].research_time * RESEARCH_MULTIPLIER)
    df.techs[techs.CASTLE_AGE].research_time = int(df.techs[techs.CASTLE_AGE].research_time * RESEARCH_MULTIPLIER)
    df.techs[techs.IMPERIAL_AGE].research_time = int(df.techs[techs.IMPERIAL_AGE].research_time * RESEARCH_MULTIPLIER)

    # Apply modifications
    disable_additional_town_centers(df)
    slower_villager_training_time(df)
    slower_tradecart_training_time(df)
    triple_building_health(df)       
    double_building_build_time(df)   
    accelerate_spearman_halberdier_train_time(df)  
    disable_additional_markets(df) 
    better_siege_towers(df)

def slower_villager_training_time(df: DatFile):
    print("Making villagers take longer to train")
    for civ in df.civs:
        for unit in civ.units:
            if unit is not None and unit.class_ == unit_classes.CIVILIAN:
                if hasattr(unit, 'creatable') and unit.creatable is not None:
                    original_train_time = unit.creatable.train_time
                    if original_train_time >= 0:
                        unit.creatable.train_time = int(original_train_time * 1.2)  # Longer training time
                        print(f"Unit ID {unit.id}: Train time increased from {original_train_time} to {unit.creatable.train_time}")
                    else:
                        print(f"Unit ID {unit.id}: Train time not modified (original Train Time: {original_train_time})")

def slower_tradecart_training_time(df: DatFile):
    print("Making tradecarts take longer")
    for civ in df.civs:
        for unit in civ.units:
            if unit is not None and unit.class_ in [unit_classes.TRADE_CART, unit_classes.TRADE_BOAT]:
                if hasattr(unit, 'creatable') and unit.creatable is not None:
                    original_train_time = unit.creatable.train_time
                    if original_train_time >= 0:
                        unit.creatable.train_time = int(original_train_time * 2)  # Double the training time
                        print(f"Unit ID {unit.id}: Train time increased from {original_train_time} to {unit.creatable.train_time}")
                    else:
                        print(f"Unit ID {unit.id}: Train time not modified (original Train Time: {original_train_time})")


def disable_additional_town_centers(df: DatFile):
    print("You can only have one standing town_center at a time")

    TOWN_CENTER_RESOURCE = 120

    # Skip civ 0 (GAIA). Start at civ 1 for actual playable civs.
    for civ_index in range(1, len(df.civs)):
        civ = df.civs[civ_index]

        # Give them 1 'Town Center Resource' so they can build exactly 1
        civ.resources[TOWN_CENTER_RESOURCE] = 1

        # Overwrite the cost/storage on every variant of the Town Center
        for tc_id in units.TOWN_CENTER_ALL:
            tc_stone_cost = ResourceCost(resources.STONE, 100, 1)
            tc_wood_cost = ResourceCost(resources.WOOD, 200, 1)
            tc_resource_cost = ResourceCost(TOWN_CENTER_RESOURCE, 1, 0)
            civ.units[tc_id].creatable.resource_costs = (
                tc_stone_cost,
                tc_wood_cost,
                tc_resource_cost
            )

            # Provide pop space to this player only
            # Deduct TOWN_CENTER_RESOURCE upon completion
            # Return TOWN_CENTER_RESOURCE on death
            tc_headroom_storage = ResourceStorage(resources.POPULATION_HEADROOM, 5, 4)
            tc_resource_storage = ResourceStorage(TOWN_CENTER_RESOURCE, -1, 2)
            empty_storage = ResourceStorage(-1, 0, 0)

            civ.units[tc_id].resource_storages = (
                tc_headroom_storage,
                tc_resource_storage,
                empty_storage,
            )


def disable_additional_markets(df: DatFile):
    print("You can only have one standing market at a time")
    MARKET_RESOURCE = 61

    # (Optionally skip civ 0 so that GAIA doesn't also get a "market resource")
    for civ_index in range(1, len(df.civs)):
        civ = df.civs[civ_index]

        # Give each civ exactly 1 'MARKET_RESOURCE'
        civ.resources[MARKET_RESOURCE] = 1

        # For each Market variant, overwrite cost and storages
        for market_id in units.MARKET_ALL:
            market_unit = civ.units[market_id]
            if market_unit is not None and market_unit.creatable is not None:
                market_stone_cost = ResourceCost(resources.STONE, 0, 1)
                market_wood_cost  = ResourceCost(resources.WOOD, 175, 1)
                market_resource_cost = ResourceCost(MARKET_RESOURCE, 1, 0)

                market_unit.creatable.resource_costs = (
                    market_stone_cost,
                    market_wood_cost,
                    market_resource_cost,
                )

                # Deduct the MARKET_RESOURCE on completion, return it on destruction
                market_headroom_storage = ResourceStorage(resources.POPULATION_HEADROOM, 0, 4)
                market_resource_storage = ResourceStorage(MARKET_RESOURCE, -1, 2)
                empty_storage           = ResourceStorage(-1, 0, 0)

                market_unit.resource_storages = (
                    market_headroom_storage,
                    market_resource_storage,
                    empty_storage,
                )



def triple_building_health(df: DatFile):
    print("Tripling health of all buildings")
    MAX_HP = 32767  # Maximum value for int16
    for civ in df.civs:
        for unit in civ.units:
            if unit is not None and unit.class_ in [unit_classes.BUILDING, unit_classes.WALL]:
                original_hp = unit.hit_points
                if original_hp >= 0:
                    
                    new_hp = original_hp
                    if (
                        unit.id in [units.CASTLE, units.TOWN_CENTER, units.DONJON] 
                        or unit.id in units.TOWN_CENTER_ALL
                        or unit.class_ == unit_classes.WALL
                        or unit.class_ == unit_classes.TOWER
                    ):
                        new_hp = original_hp * 3
                    else:
                        new_hp = original_hp * 2

                    if new_hp > MAX_HP:
                        new_hp = MAX_HP
                        print(f"Unit ID {unit.id} ({unit.name}): HP tripled from {original_hp} to {new_hp} (capped to {MAX_HP})")
                    else:
                        print(f"Unit ID {unit.id} ({unit.name}): HP tripled from {original_hp} to {new_hp}")
                    unit.hit_points = new_hp
                else:
                    print(f"Unit ID {unit.id} ({unit.name}): HP not modified (original HP: {original_hp})")


def double_building_build_time(df: DatFile):
    print("Doubling build times of all buildings")
    MAX_BUILD_TIME = 32767  # Maximum value for int16
    for civ in df.civs:
        for unit in civ.units:
            if unit is not None and unit.class_ == unit_classes.BUILDING:
                if hasattr(unit, 'creatable') and unit.creatable is not None:
                    original_train_time = unit.creatable.train_time
                    if original_train_time >= 0:
                        new_train_time = original_train_time 

                        # slower build time for castles, donjons, walls, and towers to avoid forward castle cheese when castles are stronger
                        if (
                            unit.id in [units.CASTLE, units.DONJON] 
                            or unit.class_ == unit_classes.WALL
                            or unit.class_ == unit_classes.TOWER
                        ):
                            new_train_time = int(original_train_time * 2)
                        else:
                            new_train_time = int(original_train_time * 1.6)

                        if new_train_time > MAX_BUILD_TIME:
                            new_train_time = MAX_BUILD_TIME
                            print(f"Unit ID {unit.id} ({unit.name}): Build time doubled from {original_train_time} to {new_train_time} (capped to {MAX_BUILD_TIME})")
                        else:
                            print(f"Unit ID {unit.id} ({unit.name}): Build time doubled from {original_train_time} to {new_train_time}")
                        unit.creatable.train_time = new_train_time
                    else:
                        print(f"Unit ID {unit.id} ({unit.name}): Build time not modified (original Build Time: {original_train_time})")


def accelerate_spearman_halberdier_train_time(df: DatFile):
    print("Doubling training speed for SPEARMAN and HALBERDIER")
    target_units = [units.SPEARMAN, units.PIKEMAN, units.HEAVY_PIKEMAN, units.PIKEMAN_DONJON, units.SPEARMAN_DONJON, units.HALBERDIER, units.HALBERDIER_DONJON, units.SKIRMISHER, units.ELITE_SKIRMISHER, units.IMPERIAL_SKIRMISHER]
    
    for civ in df.civs:
        for unit in civ.units:
            if unit is not None and unit.id in target_units:
                if hasattr(unit, 'creatable') and unit.creatable is not None:
                    original_train_time = unit.creatable.train_time
                    if original_train_time > 0:
                        new_train_time = max(int(original_train_time / 2), 1)  # Halve the train time, minimum 1
                        unit.creatable.train_time = new_train_time
                        print(f"Unit ID {unit.id} ({unit.name}): Train time halved from {original_train_time} to {unit.creatable.train_time}")
                    else:
                        print(f"Unit ID {unit.id} ({unit.name}): Train time not modified (original Train Time: {original_train_time})")


def better_siege_towers(df: DatFile):
    print("Modifying Siege Towers to only cost 100 wood and have double hit points")
    for civ in df.civs:
        for unit in civ.units:
            if unit is not None and unit.id == units.SIEGE_TOWER:
                # Make siege towers slower
                unit.speed = int(unit.speed * 0.5)
                print(f"Siege Tower ID {units.SIEGE_TOWER}: speed halved from to {unit.speed}")
                
                # Ensure the unit has a 'creatable' attribute
                if unit.creatable is not None:
                    # Set resource costs to only 100 wood, others to 0
                    unit.creatable.resource_costs = (
                        ResourceCost(resources.GOLD, 50, 1),    # Stone cost set to 0
                        ResourceCost(resources.WOOD, 200, 1),    # Wood cost set to 100
                        ResourceCost(-1, 0, 0),                  # No third resource cost
                    )
                    print(f"Siege Tower ID {units.SIEGE_TOWER}: Resource costs set to 100 wood, 50 gold, 0 other resources")
                else:
                    print(f"Siege Tower ID {units.SIEGE_TOWER} has no creatable data; skipping resource cost modification")
