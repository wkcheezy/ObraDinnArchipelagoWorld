import random
from math import floor

from BaseClasses import Item, Region, ItemClassification
from worlds.AutoWorld import World
from .items import ObraDinnItem, CHARACTERS
from .locations import ObraDinnLocation, LOCATIONS
from .options import ObraDinnOptions
from .subclasses import Character
from ..LauncherComponents import launch_subprocess, components, Component, Type


def launch_client():
    from .client import launch
    launch_subprocess(launch, name="ObraDinnClient")


components.append(
    Component("Return of the Obra Dinn Client", "ObraDinnClient", func=launch_client, component_type=Type.CLIENT))


class ObraDinnWorld(World):
    """
    Return of the Obra Dinn is an Insurance Adventure with Minimal Color. It is 1807 and the Obra Dinn, declared lost at
     sea in 1803, has reappeared without a trace of crew or cargo. As an insurance investigator, it is your job to
     investigate what happened and prepare a full assessment of damages. Determine the fates of each soul on board using
     a mysterious pocket watch, and solve the mystery behind the disappearance and return of the Obra Dinn.
    """
    game = "Return of the Obra Dinn"
    options_dataclass = ObraDinnOptions
    options = ObraDinnOptions
    base_id = 39090
    topology_present = True
    item_name_to_id = {name: id for id, name in enumerate([*CHARACTERS, "Shell Part"], base_id)}
    location_name_to_id = {name: id for id, name in enumerate(LOCATIONS, base_id)}
    item_name_groups = {"names": CHARACTERS}

    # TODO: Edit the required amount for a completed check?
    # TODO: Make this a player option, and possibly allow them to specifiy what name(s) to start with (ensuring the minimum value is 3 in single player games to prevent softlock (check to see if there's only one player?))
    starting_name_count = 3
    starting_names: list[Character] = []

    def generate_early(self) -> None:
        # TODO: Add events to locations to mark them as completed, and use these events as completion condition? (since, if we're adding verbs, not all names might be in item pool (though would they get added to starting inventory if there's an overflow of items?))
        # TODO: Instead of ^this, just add X victory events to X fates (where X is the number of starting names) and makes those fates require every name to access
        # TODO: If we're adding verbs, create item groups
        # TODO: Check to see if the starting name needs another name to be completed, and if so, add it to the starting inventory!!!
        # TODO: Weigh certain verbs differently in terms of priority? (i.e. if "spiked" and "speared" both work, make one progressive and the other useful/filler?
        # TODO: If we're adding verbs to starting pool, need to ensure the three names we add have a verb they need to be completed
        self.starting_names = random.sample(CHARACTERS, self.starting_name_count)
        for starting_name in self.starting_names:
            self.multiworld.push_precollected(self.create_item(starting_name))

    def create_item(self, name: str) -> Item:
        return ObraDinnItem(name, ItemClassification.progression, self.item_name_to_id[name], self.player)

    def create_items(self) -> None:
        for character in CHARACTERS:
            if character not in self.starting_names:
                self.multiworld.itempool.append(self.create_item(character))

        # Replace starting names with end goal items
        # for _ in range(self.starting_name_count):
        #     self.multiworld.itempool.append(self.create_item("Shell Part"))

    def create_regions(self) -> None:
        menu_region = Region(self.origin_region_name, self.player, self.multiworld)

        for location in LOCATIONS:
            menu_region.locations.append(
                ObraDinnLocation(self.player, location, self.location_name_to_id[location], menu_region))

        self.multiworld.regions.append(menu_region)

    def set_rules(self) -> None:
        # TODO: Now that we know how to provide outside variables to lambda, does that allow us to switch the locations back to character names since we can potentially set the required amount of names/available locations to 3
        for i, loc in enumerate(LOCATIONS):
            required_amount = (floor(i / 3) + 1) * 3
            location = self.multiworld.get_location(loc, self.player)
            location.access_rule = lambda state, r=required_amount: state.has_group("names", self.player, r)

    def pre_fill(self) -> None:
        for loc in LOCATIONS[-len(self.starting_names):]:
            self.multiworld.get_location(loc, self.player).place_locked_item(self.create_item("Shell Part"))
            # add_item_rule(self.multiworld.get_location(loc, self.player), lambda item: item.name == "Shell Part")

            # TODO: Rely on the "send goal completed" method in the mod as opposed to this, or make the shell parts events

        self.multiworld.completion_condition[self.player] = lambda state: state.count("Shell Part", self.player) == 3
        # visualize_regions(self.multiworld.get_region(self.origin_region_name, self.player), "obra_dinn.puml")
