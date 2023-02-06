#!/usr/bin/env python3
# module for the bare "garden" command
import typer
import pathlib
from typing import List, Optional
from rich import print
import json
from datetime import datetime

from garden_ai import Garden, GardenClient

from pathlib import Path

app = typer.Typer()


@app.callback()
def help_info():
    """
    [friendly description of the garden CLI and/or project]

    maybe also some example usage? This docstring is automatically turned into --help text.

    if we want to add opts for "bare garden" that'd come before any subcommand,
    here is where we'd declare them e.g. `garden [opts for "garden"] create
    [opts for "garden create"]`
    """
    pass


def is_valid_directory(directory: Path):
    """
    validate the string optionally provided by the user as a directory for the
    garden.  should return the value if successful
    """
    pass


@app.command()
def create(
    directory: Path = typer.Argument(
        pathlib.Path.cwd(),  # default to current directory
        callback=is_valid_directory,
        dir_okay=True,
        file_okay=False,
        writable=True,
        readable=True,
    ),
    authors: List[str] = typer.Option(
        ...,
        "-a",
        "--author",
        help=(
            "Name an author of this Garden. Repeat this to indicate multiple authors: "
            "`garden create ... --author='Mendel, Gregor' -a 'Other-Author, Anne' ...` (order is preserved)."
        ),
        rich_help_panel="Required",
        prompt=False,  # NOTE: prompting won't play nice with list values
    ),
    title: str = typer.Option(
        ...,
        "-t",
        "--title",
        prompt="Please enter a title for your Garden:",
        help="Provide an official title (as it should appear in citations)",
        rich_help_panel="Required",
    ),
    year: str = typer.Option(
        str(datetime.now().year),  # default to current year
        "-y",
        "--year",
        rich_help_panel="Required",
    ),
    contributors: List[str] = typer.Option(
        [],
        "-c",
        "--contributor",
        help=(
            "Acknowledge a contributor in this Garden. Repeat to indicate multiple (like --author). "
        ),
        rich_help_panel="Recommended",
    ),
    description: Optional[str] = typer.Option(
        None,
        "-d",
        "--description",
        help=(
            "A brief summary of the Garden and/or its purpose, to aid discovery by other Gardeners."
        ),
        rich_help_panel="Recommended",
    ),
    # not pictured: language, tags, version
):
    """Create a new Garden"""
    client = GardenClient()
    garden = client.create_garden(
        authors=authors,
        title=title,
        year=year,
        description=description or "",
        contributors=contributors or [],
    )
    garden.doi = (
        "10.26311/fake-doi"  # TODO just until doi minting via backend is demo-ready
    )
    client.register_metadata(garden, directory)  # writes garden.json
    return
