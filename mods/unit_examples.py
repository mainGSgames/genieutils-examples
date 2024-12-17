import copy

from genieutils.datfile import DatFile
from genieutils.unit import AttackOrArmor, Unit, ResourceCost, ResourceStorage
from genieutils.effect import EffectCommand, Effect

from constants import *
from mods import helpers

NAME = "unit_examples"


def run_unit_examples(df: DatFile):
    change_movement_speed(df)
    change_graphics(df)
    change_unit_costs(df)
    change_unit_storages(df)
    change_attacks(df)
    change_armors(df)
    change_hero_mode(df)
    change_charge_events(df)
    change_hp(df)
    change_train_location(df)


# Change how fast units move
def change_movement_speed(df: DatFile):
    print("Making missionaries super speed")
    for civ in df.civs:
        civ.units[units.MISSIONARY].speed = 2

    print("Making all villagers %d%% slower" % 50)
    for civ in df.civs:
        for unit in civ.units:
            if unit.class_ == unit_classes.CIVILIAN:
                unit.speed *= 0.5


# Change unit and building appearance
def change_graphics(df: DatFile):
    print("Give the Armenian wonder to the Britons")
    # Whenever you change unit stats, you should always make the same modifications to every Civ's list of units
    # However for graphics and sounds, this is where each Civ's units are differentiated
    # There are no actual "architecture sets", it's just that certain civs happen to share a lot of building graphics
    df.civs[civilizations.BRITONS].units[units.WONDER].standing_graphic = df.civs[civilizations.ARMENIANS].units[units.WONDER].standing_graphic
    df.civs[civilizations.BRITONS].units[units.WONDER].dying_graphic = df.civs[civilizations.ARMENIANS].units[units.WONDER].dying_graphic
    df.civs[civilizations.BRITONS].units[units.WONDER].undead_graphic = df.civs[civilizations.ARMENIANS].units[units.WONDER].undead_graphic
    df.civs[civilizations.BRITONS].units[units.WONDER].damage_graphics = df.civs[civilizations.ARMENIANS].units[units.WONDER].damage_graphics
    df.civs[civilizations.BRITONS].units[units.WONDER].building = df.civs[civilizations.ARMENIANS].units[units.WONDER].building
    df.civs[civilizations.BRITONS].units[units.WONDER].creatable.garrison_graphic = df.civs[civilizations.ARMENIANS].units[units.WONDER].creatable.garrison_graphic

    print("Giving Persians the Central Asian building architectures")
    helpers.copy_architecture(df, civilizations.CUMANS, civilizations.PERSIANS)


# Change units' attack values and bonus damages
def change_attacks(df: DatFile):
    # Note that it is typically better to give units basic attack by creating a free technology available to everyone that will buff its stats
    print("Giving slingers 1 extra attack")
    for civ in df.civs:
        # In the slinger's attack list, its pierce damage is listed at index 2. This method depends on the ordering of elements and not generally advised
        civ.units[units.SLINGER].type_50.attacks[2].amount += 1
        # If you don't update its displayed attack it will display as having a bonus +1 attack like it would from researching technologies
        civ.units[units.SLINGER].type_50.displayed_attack += 1

    print("Giving knights 1 extra attack")
    # If you want the upgrades to give the same bonus stats as normal, you'll have to add the stats to all units in the line
    target_units = [units.KNIGHT, units.CAVALIER, units.PALADIN, units.SAVAR]
    for civ in df.civs:
        for unit_id in target_units:
            civ.units[unit_id].type_50.displayed_attack += 1
            # The more dynamic method of increasing attack is to loop through the unit's attacks and find the one that is associated with its melee damage
            for attack in civ.units[unit_id].type_50.attacks:
                if attack.class_ == armor_classes.MELEE:
                    attack.amount += 1

    print("Give all cavalry archers 1 bonus damage vs. infantry")
    for civ in df.civs:
        for unit in civ.units:
            if unit.class_ == unit_classes.CAVALRY_ARCHER:
                has_infantry_bonus_damage = False
                # Check if the unit already has bonus damage against infantry
                for attack in unit.type_50.attacks:
                    if attack.class_ == armor_classes.INFANTRY:
                        # If it does, increase the value by one
                        attack.amount += 1
                        has_infantry_bonus_damage = True
                # If it does not, create a new bonus attack against infantry with a value of one
                if not has_infantry_bonus_damage:
                    new_bonus_damage: AttackOrArmor = AttackOrArmor(armor_classes.INFANTRY, 1)
                    unit.type_50.attacks.append(new_bonus_damage)

    print("Making arson give infantry units bonus vs. siege")
    # Since we are adding this effect to arson, the increase will need to be done through an EffectCommand
    arson_effect_id = df.techs[techs.ARSON].effect_id
    bonus_vs_siege_effect_command: EffectCommand = EffectCommand(
        command_types.ATTRIBUTE_MODIFIER_ADDITIVE, -1, unit_classes.INFANTRY, attributes.ATTACK, helpers.amount_type_to_d(1, armor_classes.SIEGE_WEAPON)
    )
    df.effects[arson_effect_id].effect_commands.append(bonus_vs_siege_effect_command)
    # However, if a unit doesn't already have a bonus of that type, an EffectCommand will do nothing
    # So for the infantry units that have no bonus vs. siege, we need to give them a default bonus vs. siege of 0
    for civ in df.civs:
        for unit in civ.units:
            if unit.class_ == unit_classes.INFANTRY:
                has_siege_bonus_damage = False
                # Check if it has bonus vs. siege
                for attack in unit.type_50.attacks:
                    if attack.class_ == armor_classes.SIEGE_WEAPON:
                        has_siege_bonus_damage = True
                # If it does not, give it a bonus vs. siege of 0
                if not has_siege_bonus_damage:
                    new_bonus_damage: AttackOrArmor = AttackOrArmor(armor_classes.SIEGE_WEAPON, 0)
                    unit.type_50.attacks.append(new_bonus_damage)


# Change units' armor values and ways it receives bonus damages
def change_armors(df: DatFile):
    print("Giving condottiero +1/+1P armor")
    for civ in df.civs:
        # Loop through the unit's armors, checking for melee and pierce types
        for armor in civ.units[units.CONDOTTIERO].type_50.armours:
            if armor.class_ == armor_classes.MELEE or armor.class_ == armor_classes.PIERCE:
                armor.amount += 1
        # Like with attacks, don't forget to update the displayed armor
        civ.units[units.CONDOTTIERO].type_50.displayed_melee_armour += 1
        # For whatever reason, pierce armor is inside a unit's creatable instead
        civ.units[units.CONDOTTIERO].creatable.displayed_pierce_armor += 1

    print("Making monks immune to pierce attacks")
    # Because of the way attacks and armors interact, removing a unit's armor class will make it immune to that type of damage
    for civ in df.civs:
        for unit in civ.units:
            # Don't forget to check for monks and monks with relics as those are two separate units with separate unit classes
            # Also warrior priests without relics are categorized as infantry as far as its unit.class_ is concerned
            if unit.class_ == unit_classes.MONK or unit.class_ == unit_classes.MONK_WITH_RELIC or unit.base_id == units.WARRIOR_PRIEST:
                # Remove all armors whose class is pierce
                unit.type_50.armours = list(filter(lambda armor: armor.class_ != armor_classes.PIERCE, unit.type_50.armours))
                unit.creatable.displayed_pierce_armor = 999

    print("Giving war wagons +2 bonus damage vs. villagers")
    # There is no existing "villager" armor class, so we have to create one
    # Armor class of 10 is unused, so let's give all villagers an armor type 10 of value 0
    # This means that any unit with attack type of 10 will do that full damage amount as bonus damage to villagers
    for civ in df.civs:
        for unit in civ.units:
            if unit.class_ == unit_classes.CIVILIAN:
                new_bonus_weakness: AttackOrArmor = AttackOrArmor(10, 0)
                unit.type_50.armours.append(new_bonus_weakness)
    # Now give war wagons a corresponding attack
    new_bonus_attack: AttackOrArmor = AttackOrArmor(10, 2)
    for civ in df.civs:
        civ.units[units.WAR_WAGON].type_50.attacks.append(new_bonus_attack)
        civ.units[units.ELITE_WAR_WAGON].type_50.attacks.append(new_bonus_attack)


# Modify charging attacks and dodges
def change_charge_events(df: DatFile):
    print("Buffing coustillier charge attack")
    for civ in df.civs:
        civ.units[units.COUSTILLIER].creatable.recharge_rate *= 2
        civ.units[units.COUSTILLIER].creatable.max_charge *= 2
        civ.units[units.ELITE_COUSTILLIER].creatable.recharge_rate *= 3
        civ.units[units.ELITE_COUSTILLIER].creatable.max_charge *= 3

    print("Giving houses the ability to dodge projectiles")
    for civ in df.civs:
        for house_id in units.HOUSE_ALL:
            civ.units[house_id].creatable.max_charge = 1
            civ.units[house_id].creatable.recharge_rate = 1
            # Charge event and type can be copied from Shrivamsha Riders
            civ.units[house_id].creatable.charge_event = 0
            civ.units[house_id].creatable.charge_type = 4


# Give or take away certain characteristics associated with hero units
def change_hero_mode(df: DatFile):
    print("Make monks inconvertible and have regen when they pick up relics")
    # A hero mode flag of 2 means they cannot be converted, a flag of 4 means they have regen
    # In order to create something with both, simply add up these flags
    # The full list of flags is available on the AoE2DE UGC Guide
    for civ in df.civs:
        for unit in civ.units:
            if unit.class_ == unit_classes.MONK_WITH_RELIC:
                unit.creatable.hero_mode = 6


# Modify the costs required to train units
def change_unit_costs(df: DatFile):
    print("Making war elephants cost no gold")
    for civ in df.civs:
        gold_cost: ResourceCost = ResourceCost(resources.GOLD, 85, 1)
        empty_cost: ResourceCost = ResourceCost(-1, 0, 0)
        headroom_cost: ResourceCost = ResourceCost(resources.POPULATION_HEADROOM, 1, 0)
        civ.units[units.WAR_ELEPHANT].creatable.resource_costs = (gold_cost, empty_cost, headroom_cost)
        civ.units[units.ELITE_WAR_ELEPHANT].creatable.resource_costs = (gold_cost, empty_cost, headroom_cost)
        # Alternatively, use the helper method
        civ.units[units.WAR_ELEPHANT].creatable.resource_costs = helpers.costs_array_to_unit_cost([0, 0, 0, 85])
        civ.units[units.ELITE_WAR_ELEPHANT].creatable.resource_costs = helpers.costs_array_to_unit_cost([0, 0, 0, 85])


# Modify what resources are obtained by training a unit / building a building
def change_unit_storages(df: DatFile):
    print("Making villagers cost 2 population space")
    population_headroom: ResourceStorage = ResourceStorage(resources.POPULATION_HEADROOM, -2, 2)  # Subtract 2 from the available population, but give it back after unit death
    current_population: ResourceStorage = ResourceStorage(resources.CURRENT_POPULATION, 2, 2)  # Add 2 to the current population, but give it back after unit death
    total_units: ResourceStorage = ResourceStorage(resources.TOTAL_UNITS_OWNED, 2, 1)  # Add 2 to the total units owned, but keep it after unit death
    empty_storage: ResourceStorage = ResourceStorage(-1, 0, 0)
    for civ in df.civs:
        for unit in civ.units:
            if unit.class_ == unit_classes.CIVILIAN:
                unit.resource_storages = (population_headroom, current_population, total_units)

    print("Building a krepost gives you 1 gold")
    for civ in df.civs:
        # Maintain its ability to give you 20 pop space which resets upon dying
        # Give you 1 gold when you complete the krepost which stays upon destruction
        # ResourceStorage(resources.GOLD, 1, 1) would give you 1 gold the moment you started the foundation and you would keep it after destruction
        civ.units[units.KREPOST].resource_storages = (ResourceStorage(resources.POPULATION_HEADROOM, 20, 4), ResourceStorage(resources.GOLD, 1, 8), empty_storage)

    print("You can only have one standing castle at a time")
    # In order to accomplish this, we need to create a new resource. Let's use resource ID 120 since that isn't used for anything else
    # Give every civilization 1 of this resource at the start of the game
    CASTLE_RESOURCE = 120
    for civ in df.civs:
        civ.resources[CASTLE_RESOURCE] = 1
    # Now make every castle cost 1 castle_resource but do NOT deduct it as a cost, the resource storages will take care of the deductions
    # This is so that if you don't have enough castle_resource you won't be able to build another (otherwise you would just go negative castle_resource without issue)
    for civ in df.civs:
        castle_stone_cost = ResourceCost(resources.STONE, 650, 1)
        # Notably castles have a wood cost of 0 because without it the Detinets EffectCommand would be unable to modify the value
        castle_wood_cost = ResourceCost(resources.WOOD, 0, 1)
        castle_resource_cost = ResourceCost(CASTLE_RESOURCE, 1, 0)  # Costs 1 but does not deduct when you start construction
        civ.units[units.CASTLE].creatable.resource_costs = (castle_stone_cost, castle_wood_cost, castle_resource_cost)
        # Now, deduct the castle_resource upon completion of the castle, but give it back when the castle is destroyed
        castle_headroom_storage = ResourceStorage(resources.POPULATION_HEADROOM, 20, 4)
        castle_mercenary_kipchak_storage = ResourceStorage(resources.MERCENARY_KIPCHAK_COUNT, 0, 64)
        castle_resource_storage = ResourceStorage(CASTLE_RESOURCE, -1, 2)
        civ.units[units.CASTLE].resource_storages = (castle_headroom_storage, castle_mercenary_kipchak_storage, castle_resource_storage)


# Modify units' hit points
def change_hp(df: DatFile):
    print("Giving bombard cannons 4000 HP")
    # Note here that we are changing the base stats, meaning that the Turk bonus of +25% gunpowder HP will give them extra 1000 HP
    for civ in df.civs:
        civ.units[units.BOMBARD_CANNON].hit_points = 4000
        civ.units[units.HOUFNICE].hit_points = 4000

    print("Making all cavalry archers permanently have 1 HP")
    # First make all cavalry archers start with 1 HP
    for civ in df.civs:
        for unit in civ.units:
            if unit.class_ == unit_classes.CAVALRY_ARCHER:
                unit.hit_points = 1
    # Now we need to make all effects in the game unable to change this
    for effect in df.effects:
        # Loop through every effect in the game, and then loop through every effect_command of that effect
        effect_command_index = 0
        while effect_command_index < len(effect.effect_commands):
            effect_command: EffectCommand = effect.effect_commands[effect_command_index]
            # The only effect commands that could change HP would be attribute modifiers
            # Because of the way command_types are arranged, we can check for attribute_modifier_additive/multiplicative/set by taking modulus 10
            if effect_command.type < 100 and (effect_command.type % 10 == 0 or effect_command.type % 10 == 4 or effect_command.type % 10 == 5):
                # For these effect_commands, the C value will always be the attribute field, so make sure it has to do with points
                if effect_command.c == attributes.HIT_POINTS:
                    # The B value will always the the unit class, so if it is cavalry archer, simply remove it
                    if effect_command.b == unit_classes.CAVALRY_ARCHER:
                        effect.effect_commands.pop(effect_command_index)
                        effect_command_index -= 1
                    elif effect_command.a >= 0:
                        # The A value will be the unit ID, so check if that unit is actually a cavalry archer, and remove it if it is
                        # Checking the unit class of GAIA's units will suffice
                        if df.civs[civilizations.GAIA].units[effect_command.a].class_ == unit_classes.CAVALRY_ARCHER:
                            effect.effect_commands.pop(effect_command_index)
                            effect_command_index -= 1
            effect_command_index += 1


# Change where units are trained
def change_train_location(df: DatFile):
    print("Moving hand cannoneeers to lumber camps")
    for civ in df.civs:
        civ.units[units.HAND_CANNONEER].creatable.train_location_id = units.LUMBER_CAMP
        # See tech examples for button layout. Note that this change isn't necessary because lumber camps don't have anything located at button id of 4
        civ.units[units.HAND_CANNONEER].creatable.button_id = 14

    print("Making missionaries trainable at mining camps")
    # Since each unit can only have one train location, in order for a unit to be trainable at multiple locations there must be multiple copies of that unit
    for civ in df.civs:
        missionary_copy: Unit = copy.deepcopy(civ.units[units.MISSIONARY])  # Create a copy of missionary unit
        civ.units.append(missionary_copy)  # Append it to the civ's units
        new_missionary_id = len(civ.units) - 1
        civ.units[new_missionary_id].base_id = new_missionary_id  # Update its id
        civ.units[new_missionary_id].copy_id = new_missionary_id
        civ.units[new_missionary_id].creatable.train_location_id = units.MINING_CAMP
        civ.units[new_missionary_id].creatable.button_id = 4  # This button change is necessary because otherwise stone mining would get in the way
    # Make every effect in the game that specifically affects the missionary unit also affect the new missionary copy
    # Note that this process becomes significantly more complex when you are trying to duplicate a unit with upgrades
    # For example if you want to make militia recruitable from mills you would have to duplicate militia, man-at-arms, long-swordsmen, two-handed swordsmen,
    # champions, and legionaries, copy every EffectCommand that affects those units specifically EXCEPT the upgrading EffectCommands -- for those you need each unit
    # to upgrade along its corresponding copied unit's upgrade
    for effect in df.effects:
        # Loop through every effect in the game, and then loop through every effect_command of that effect
        original_effect_command_length = len(effect.effect_commands)
        for effect_command_index in range(original_effect_command_length):
            effect_command: EffectCommand = effect.effect_commands[effect_command_index]
            # Check attribute modifiers or enabling effect_commands
            if effect_command.type < 100 and (effect_command.type % 10 == 0 or effect_command.type % 10 == 4 or effect_command.type % 10 == 5 or effect_command.type % 10 == 2):
                if effect_command.a == units.MISSIONARY:
                    duplicated_effect_command: EffectCommand = copy.deepcopy(effect_command)
                    duplicated_effect_command.a = new_missionary_id
                    effect.effect_commands.append(duplicated_effect_command)
