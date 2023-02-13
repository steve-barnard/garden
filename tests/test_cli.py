import pytest
import json
from typer.testing import CliRunner
from garden_ai.app.garden import app
from garden_ai.gardens import Garden

runner = CliRunner()


@pytest.mark.cli
def test_garden_create(garden_all_fields, tmp_path, mocker):
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
    mocker.patch("garden_ai.app.garden.typer.launch").return_value = 0
    mocker.patch("garden_ai.app.garden.rich.prompt.input").return_value = "MyToken"
    result = runner.invoke(app, command)
    if result.exception:
        raise result.exception
    assert result.exit_code == 0
    with open(str(tmp_path / "pea_directory" / "garden.json"), "r") as f:
        # asserts the record produced by "garden create" can instantiate a valid garden:
        metadata = json.load(f)
        new_garden = Garden(**metadata)
        assert new_garden.title == g.title
        assert new_garden.description == g.description
        assert set(new_garden.authors) == set(g.authors)
        assert set(new_garden.contributors) == set(g.contributors)
