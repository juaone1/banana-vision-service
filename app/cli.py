import typer
from app.migrations.base import run_migrations

cli = typer.Typer()

@cli.command()
def migrate():
    """Run database migrations."""
    import asyncio
    asyncio.run(run_migrations())
    print("Migrations completed successfully!")

if __name__ == "__main__":
    cli() 