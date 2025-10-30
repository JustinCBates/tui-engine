
import tui_engine.factories as widgets
from tui_engine.page import Page


def run_demo() -> None:
    page = Page(title="Demo Example")
    hdr = page.container("header")
    hdr.add(widgets.text("title", "Demo Example Title"))
    body = page.container("body")
    body.add(widgets.text("intro", "This is a minimal container demo."))
    # Render to width 80 for console
    print("\n".join(page.render(80)))


if __name__ == "__main__":
    run_demo()
