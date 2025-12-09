import typer
from typing_extensions import Annotated

app = typer.Typer(rich_markup_mode=None)


@app.command()
def main(
    name1: Annotated[str, typer.Argument(help="The name of the user to greet")],
    name: str = typer.Argument(..., metavar="name", help="Input your name"),
    optional_opt: str = typer.Option("option", help="可选的选项"),
    start_date: str = typer.Option(default="2022-01-01", help="开始日期，格式YYYY-MM-DD"),
    end_date: str = typer.Option(default="2022-12-31", help="结束日期，格式YYYY-MM-DD"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="详细输出模式"),
):
    print(f"Hello {name} {optional_opt} {start_date} {end_date} {'(verbose mode)' if verbose else ''}!")


if __name__ == "__main__":
    app()
