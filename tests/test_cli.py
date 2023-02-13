import pytest
from garden_ai.app.garden import app
from garden_ai.client import GardenClient
from typer.testing import CliRunner

runner = CliRunner()


@pytest.mark.cli
def test_garden_create(garden_all_fields, tmp_path, mocker):
    mock_client = mocker.MagicMock(GardenClient)
    mocker.patch("garden_ai.app.create.GardenClient").return_value = mock_client

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
    result = runner.invoke(app, command)
    assert result.exit_code == 0
    mock_client.create_garden.assert_called_once()
    mock_client.register_metadata.assert_called_once()
