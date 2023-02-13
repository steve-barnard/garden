import pytest
from typer.testing import CliRunner
from garden_ai.app.garden import app
from garden_ai.gardens import Garden

runner = CliRunner()


@pytest.mark.cli
def test_garden_create(garden_all_fields, tmp_path, mocker):
    # patch just the create_garden method
    mocker.patch(
        "garden_ai.app.garden.GardenClient",
        create_garden=lambda _, **kwargs: Garden(**kwargs),
    )

    g = garden_all_fields
    command = [
        "create",
        str(tmp_path / "pea_directory"),
        "--title",
        g.title,
        "--description",
        g.description,
        "--year",
        g.year,
    ]
    for name in g.authors:
        command += ["--author", name]
    for name in g.contributors:
        command += ["--contributor", name]
    # mocker.patch("garden_ai.app.garden.typer.launch").return_value = 0
    # mocker.patch("garden_ai.app.garden.rich.prompt.input").return_value = "MyToken"
    result = runner.invoke(app, command)
    assert result.exit_code == 0
