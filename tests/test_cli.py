import pytest
import sys
from garden_ai.app.main import app
from garden_ai.client import GardenClient
from typer.testing import CliRunner
import string
import random
from garden_ai.app.pipeline import validate_identifier

runner = CliRunner()


@pytest.mark.cli
@pytest.mark.skipif(
    sys.version_info < (3, 8), reason="mocked call_args.kwargs breaks under 3.7"
)
def test_garden_create(garden_all_fields, tmp_path, mocker):
    mock_client = mocker.MagicMock(GardenClient)
    mocker.patch("garden_ai.app.garden.GardenClient").return_value = mock_client

    command = [
        "garden",
        "create",
        str(tmp_path / "pea_directory"),
        "--title",
        garden_all_fields.title,
        "--description",
        garden_all_fields.description,
        "--year",
        garden_all_fields.year,
    ]
    for name in garden_all_fields.authors:
        command += ["--author", name]
    for name in garden_all_fields.contributors:
        command += ["--contributor", name]
    result = runner.invoke(app, command)
    assert result.exit_code == 0

    mock_client.create_garden.assert_called_once()
    kwargs = mock_client.create_garden.call_args.kwargs
    for key in kwargs:
        assert kwargs[key] == getattr(garden_all_fields, key)
    mock_client.put_local.assert_called_once()


def test_pipeline_create(tmp_path, mocker):
    mock_client = mocker.MagicMock(GardenClient)
    mocker.patch("garden_ai.app.pipeline.GardenClient").return_value = mock_client
    # TODO


def test_validate_identifier():
    possible_name = "".join(random.choices(string.printable, k=50))
    valid_name = validate_identifier(possible_name)
    assert valid_name.isidentifier()
