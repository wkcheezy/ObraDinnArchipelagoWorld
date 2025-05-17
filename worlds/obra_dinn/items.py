from BaseClasses import Item
from .subclasses import Character


class ObraDinnItem(Item):
    name = "Return of the Obra Dinn"


CHARACTERS = [character.value for character in Character]
