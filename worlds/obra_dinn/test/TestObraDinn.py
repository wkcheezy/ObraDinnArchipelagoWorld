from test.bases import WorldTestBase
from worlds.obra_dinn import CHARACTERS


class ObraDinnTest(WorldTestBase):
    game = "Return of the Obra Dinn"

    def test_EachCharacterHasLocation(self):
        self.assertEqual(len(CHARACTERS), len(list(self.multiworld.get_locations(self.player))))
