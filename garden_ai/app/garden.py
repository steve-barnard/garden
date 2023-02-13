# module for the bare "garden" command
import logging
import garden_ai.app.create as create
import typer

logger = logging.getLogger()

app = typer.Typer()

# subcommands are typer apps in their own right
app.add_typer(create.app, name="create")


@app.callback()
def help_info():
    """
    🌱 Hello, Garden 🌱

    I'm some help text!
    """
    # TODO I think this is where --version, --verbose etc logic should go
    pass
