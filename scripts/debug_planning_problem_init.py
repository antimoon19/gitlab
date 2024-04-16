from pathlib import Path
from typer.testing import CliRunner
import typer
from commonroad_dataset_converter.main import cli

# cli = typer.Typer(help="Generates CommonRoad scenarios from different datasets")

input = Path("/home/florian/datasets/mona.cps.cit.tum.de/processed/east")
output = Path(__file__).parents[1].joinpath("output_debug_mona")


runner = CliRunner()
result = runner.invoke(
    cli,
    [
        "--num-planning-problems",
        "4",
        "--max-scenarios",
        "10",
        "--obstacles-start-at-zero",
        "--keep-ego",
        str(input),
        str(output),
        "mona",
    ],
    catch_exceptions=False,
)
