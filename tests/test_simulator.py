import unittest

from dynasty_algorithm import DynastySimulator, SimulationConfig, StartingChild
from dynasty_algorithm.__main__ import parse_child


class DynastySimulatorTests(unittest.TestCase):
    def test_seeded_simulation_is_reproducible(self):
        config = SimulationConfig(current_monarch_age=25, current_monarch_sex="female", max_years=25)

        first = DynastySimulator(config, seed=7).run()
        second = DynastySimulator(config, seed=7).run()

        self.assertEqual(first.events, second.events)

    def test_starting_children_are_tracked_with_ages_and_sex(self):
        config = SimulationConfig(
            current_monarch_age=40,
            current_monarch_sex="male",
            starting_children=(StartingChild(age=12, sex="female"), StartingChild(age=8, sex="male")),
            max_years=1,
            fertility_chance=0.0,
            disease_risk=0.0,
        )

        result = DynastySimulator(config, seed=3).run()

        children = result.dynasty_members[0].children
        self.assertEqual([(child.age, child.sex) for child in children], [(13, "female"), (9, "male")])

    def test_children_can_be_born_without_names(self):
        config = SimulationConfig(current_monarch_age=20, current_monarch_sex="female", max_years=1, fertility_chance=1.0)

        result = DynastySimulator(config, seed=3).run()

        children = result.dynasty_members[0].children
        self.assertEqual(len(children), 1)
        self.assertIn("Person", children[0].label)

    def test_dynasty_can_end_without_heirs(self):
        config = SimulationConfig(current_monarch_age=100, current_monarch_sex="male", max_years=20, disease_risk=0.0)

        result = DynastySimulator(config, seed=1).run()

        self.assertIsNone(result.reigning_monarch)
        self.assertIn("dynasty has ended", result.events[-1])

    def test_parse_child_accepts_checklist_values(self):
        child = parse_child("12:female")

        self.assertEqual(child, StartingChild(age=12, sex="female"))


if __name__ == "__main__":
    unittest.main()
