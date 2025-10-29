from src.tui_engine.page import Page

def run_demo():
    page = Page("Demo Example")
    page.container("header", "header").text("title", "Demo Example Title")
    body = page.container("body", "section")
    body.text("intro", "This is a minimal container demo.")
    print("\n".join(page.render(80)))

if __name__ == "__main__":
    run_demo()
