import click

from .app_main import app


@click.command()
@click.option("--port", default=8050, help="Port for the Dash app.")
@click.option("--local", is_flag=True, help="Run app locally.")
def serve(port=8050, local=False):
    """Run the dashboard"""
    if not local:
        host = "0.0.0.0"  # Host IP address
        debug = False
    else:
        host = "127.0.0.1"
        debug = True  # Enable debug mode for local mode
    app.run_server(port=port, host=host, debug=debug)


if __name__ == "__main__":
    serve()
