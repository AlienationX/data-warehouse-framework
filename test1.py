import typer
from rich.console import Console
from rich.theme import Theme

# 1. 定义一个无边框、无颜色的主题
custom_theme = Theme({
    # 可以在这里定义其他样式，但保持简洁
    "info": "",
    "warning": "",
    "danger": ""
})

# 2. 创建一个使用该主题的控制台实例，并禁用高级功能
plain_console = Console(theme=custom_theme, highlight=False, soft_wrap=True)

# 3. 创建Typer应用，并传入自定义的控制台实例
app = typer.Typer(
    rich_markup_mode="markdown",  # 可根据需要调整
    # rich_console=plain_console    # 关键：使用自定义Console
)

@app.command()
def hello(name: str):
    """Say hello to someone."""
    typer.echo(f"Hello {name}")

if __name__ == "__main__":
    app()