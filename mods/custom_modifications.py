import copy

from genieutils.datfile import DatFile
from genieutils.effect import EffectCommand, Effect
from genieutils.civ import Civ
from genieutils.tech import Tech, ResearchResourceCost
from genieutils.unit import Unit, AttackOrArmor, Task, ResourceCost, ResourceStorage, Type50, Bird, Creatable, Building

from constants import *
from mods import helpers

NAME = "custom_modifications"

def run_custom_modifications(df: DatFile):
    print("Your code goes here:")
