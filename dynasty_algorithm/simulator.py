"""Core dynasty simulation logic.

The model is intentionally compact and transparent: it is designed for gameplay,
prototyping, and experimentation rather than demographic prediction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from random import Random
from typing import Iterable, Literal

Sex = Literal["female", "male"]


@dataclass(frozen=True)
class StartingChild:
    """Basic information about a child who already exists at simulation start."""

    age: int
    sex: Sex


@dataclass(frozen=True)
class SimulationConfig:
    """Configuration knobs and starting-ruler checklist for a dynasty simulation."""

    current_monarch_age: int = 18
    current_monarch_sex: Sex = "female"
    starting_children: tuple[StartingChild, ...] = ()
    max_years: int = 80
    fertility_chance: float = 0.28
    disease_risk: float = 0.06
    recovery_chance: float = 0.55
    succession_min_age: int = 0


@dataclass
class Person:
    """A dynasty member tracked by age, sex, health, and family relationship."""

    identifier: int
    age: int
    sex: Sex
    parent_id: int | None = None
    alive: bool = True
    sick: bool = False
    children: list["Person"] = field(default_factory=list)

    @property
    def label(self) -> str:
        """Return a nameless display label for event output."""

        return f"Person {self.identifier} ({self.sex}, age {self.age})"

    def living_children(self) -> list["Person"]:
        """Return living children ordered from oldest to youngest."""

        return sorted((child for child in self.children if child.alive), key=lambda child: child.age, reverse=True)


@dataclass(frozen=True)
class SimulationResult:
    """Final state and event log from a simulation run."""

    years_simulated: int
    reigning_monarch: Person | None
    dynasty_members: tuple[Person, ...]
    events: tuple[str, ...]


class DynastySimulator:
    """Simulate a nameless monarch, children, disease, death, and succession."""

    def __init__(self, config: SimulationConfig, seed: int | None = None) -> None:
        self.config = config
        self.random = Random(seed)
        self.year = 0
        self.events: list[str] = []
        self._next_identifier = 1
        self.monarch = self._create_person(config.current_monarch_age, config.current_monarch_sex)
        self.members: list[Person] = [self.monarch]
        self._add_starting_children(config.starting_children)

    def run(self) -> SimulationResult:
        """Run until max years elapse, the dynasty ends, or no monarch survives."""

        self.events.append(f"Year 0: {self.monarch.label} begins ruling.")
        if self.monarch.children:
            child_summary = ", ".join(child.label for child in self.monarch.children)
            self.events.append(f"Year 0: Starting children: {child_summary}.")

        for year in range(1, self.config.max_years + 1):
            self.year = year
            self._advance_year()
            if self.monarch is None:
                self.events.append(f"Year {year}: The dynasty has ended.")
                break

        return SimulationResult(
            years_simulated=self.year,
            reigning_monarch=self.monarch,
            dynasty_members=tuple(self.members),
            events=tuple(self.events),
        )

    def _create_person(self, age: int, sex: Sex, parent_id: int | None = None) -> Person:
        person = Person(identifier=self._next_identifier, age=age, sex=sex, parent_id=parent_id)
        self._next_identifier += 1
        return person

    def _add_starting_children(self, starting_children: Iterable[StartingChild]) -> None:
        for child_info in starting_children:
            child = self._create_person(child_info.age, child_info.sex, parent_id=self.monarch.identifier)
            self.monarch.children.append(child)
            self.members.append(child)

    def _advance_year(self) -> None:
        for person in tuple(self.living_members()):
            person.age += 1
            self._resolve_health(person)

        if self.monarch is not None and self.monarch.alive:
            self._maybe_have_child(self.monarch)
        elif self.monarch is not None:
            self._choose_successor(self.monarch)

    def _resolve_health(self, person: Person) -> None:
        if person.sick:
            death_risk = self._mortality_risk(person) + 0.18
            if self.random.random() < death_risk:
                self._die(person, "from disease")
                return
            if self.random.random() < self.config.recovery_chance:
                person.sick = False
                self.events.append(f"Year {self.year}: {person.label} recovers.")
            return

        if self.random.random() < self._mortality_risk(person):
            self._die(person, "of natural causes")
            return

        if self.random.random() < self._disease_risk_for(person):
            person.sick = True
            self.events.append(f"Year {self.year}: {person.label} falls ill.")

    def _mortality_risk(self, person: Person) -> float:
        if person.age < 5:
            return 0.035
        if person.age < 45:
            return 0.01
        if person.age < 65:
            return 0.025
        return min(0.35, 0.04 + ((person.age - 65) * 0.012))

    def _disease_risk_for(self, person: Person) -> float:
        age_modifier = 1.5 if person.age < 8 or person.age > 60 else 1.0
        return min(0.8, self.config.disease_risk * age_modifier)

    def _maybe_have_child(self, parent: Person) -> None:
        maximum_reproductive_age = 45 if parent.sex == "female" else 60
        if not 16 <= parent.age <= maximum_reproductive_age:
            return
        existing_children_penalty = max(0.05, 1 - (len(parent.children) * 0.08))
        if self.random.random() >= self.config.fertility_chance * existing_children_penalty:
            return

        child = self._create_person(age=0, sex=self.random.choice(("female", "male")), parent_id=parent.identifier)
        parent.children.append(child)
        self.members.append(child)
        self.events.append(f"Year {self.year}: The monarch has a child: {child.label}.")

    def _die(self, person: Person, cause: str) -> None:
        person.alive = False
        person.sick = False
        self.events.append(f"Year {self.year}: {person.label} dies {cause}.")
        if person is self.monarch:
            self._choose_successor(person)

    def _choose_successor(self, deceased_monarch: Person) -> None:
        eligible_heirs = [
            child
            for child in deceased_monarch.living_children()
            if child.age >= self.config.succession_min_age
        ]
        self.monarch = eligible_heirs[0] if eligible_heirs else None
        if self.monarch is not None:
            self.events.append(f"Year {self.year}: {self.monarch.label} inherits.")

    def living_members(self) -> Iterable[Person]:
        """Return living dynasty members."""

        return (member for member in self.members if member.alive)
