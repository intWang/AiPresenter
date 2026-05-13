import typer

app = typer.Typer(help="AI presenter CLI for configured app profiles.")


@app.command()
def run(profile: str = typer.Option(..., "--profile", help="Profile id or YAML path.")) -> None:
    """Run an AI presenter profile."""
    typer.echo(f"Profile requested: {profile}")
