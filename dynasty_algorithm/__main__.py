"""Command line interface for the dynasty simulator."""

from __future__ import annotations

import argparse

from .simulator import DynastySimulator, SimulationConfig, StartingChild


def parse_child(value: str) -> StartingChild:
    """Parse a child checklist entry in AGE:SEX form."""

    try:
        age_text, sex = value.split(":", 1)
        age = int(age_text)
    except ValueError as error:
        raise argparse.ArgumentTypeError("children must use AGE:SEX, for example 12:female") from error

    if age < 0:
        raise argparse.ArgumentTypeError("child age cannot be negative")
    if sex not in {"female", "male"}:
        raise argparse.ArgumentTypeError("child sex must be 'female' or 'male'")
    return StartingChild(age=age, sex=sex)  # type: ignore[arg-type]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Simulate a nameless monarch's life, children, disease, and succession."
    )
    parser.add_argument("--age", type=int, default=18, help="current monarch age")
    parser.add_argument(
        "--sex",
        choices=("female", "male"),
        default="female",
        help="current monarch sex",
    )
    parser.add_argument(
        "--child",
        action="append",
        type=parse_child,
        default=[],
        metavar="AGE:SEX",
        help="existing child; repeat for multiple children, for example --child 12:female --child 8:male",
    )
    parser.add_argument("--years", type=int, default=80, help="maximum number of years to simulate")
    parser.add_argument("--seed", type=int, default=None, help="random seed for reproducible runs")
    parser.add_argument("--fertility", type=float, default=0.28, help="base yearly chance of childbirth")
    parser.add_argument("--disease-risk", type=float, default=0.06, help="base yearly chance of disease")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = SimulationConfig(
        current_monarch_age=args.age,
        current_monarch_sex=args.sex,
        starting_children=tuple(args.child),
        max_years=args.years,
        fertility_chance=args.fertility,
        disease_risk=args.disease_risk,
    )
    result = DynastySimulator(config, seed=args.seed).run()

    print("Starting ruler checklist")
    print(f"- Current monarch age: {config.current_monarch_age}")
    print(f"- Current monarch sex: {config.current_monarch_sex}")
    if config.starting_children:
        for index, child in enumerate(config.starting_children, start=1):
            print(f"- Child {index}: age {child.age}, sex {child.sex}")
    else:
        print("- Existing children: none")
    print()

    for event in result.events:
        print(event)

    print("\nSummary")
    print(f"Years simulated: {result.years_simulated}")
    if result.reigning_monarch is None:
        print("Reigning monarch: none")
    else:
        print(f"Reigning monarch: {result.reigning_monarch.label}")
    living = sum(1 for person in result.dynasty_members if person.alive)
    print(f"Living dynasty members: {living}/{len(result.dynasty_members)}")


if __name__ == "__main__":
    main()
