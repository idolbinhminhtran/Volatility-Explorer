from shiny import App, ui, render
from shinyswatch import theme
from faicons  import icon_svg

css = """
/* Gradient background */
.navbar {
  background: linear-gradient(90deg, #2a9d8f, #264653);
}
/* Nav link color + hover */
.nav-link {
  color: #f1faee !important;
  font-weight: 500;
  padding: 0.5rem 1rem;
}
.nav-link:hover,
.nav-link.active {
  color: #e9c46a !important;
  background-color: rgba(0,0,0,0.1);
  border-radius: 0.25rem;
}
/* Brand text/logo */
.navbar-brand,
.navbar-brand:hover {
  color: #f1faee !important;
}
"""

app_ui = ui.TagList(
    ui.tags.head(
        ui.tags.style(css)
    ),

    ui.page_navbar(

        ui.nav_spacer(),

        ui.nav_panel(
            "Home",
            ui.h1("Welcome to Volatility Explorer!"),
            ui.p("This is the home page content."),
            icon=icon_svg("house-chimney"),  
        ),
        ui.nav_panel(
            "Volatility Screener",
            ui.h2("About this App"),
            ui.p("This app is a scaffold for a Python Shiny application with a navbar."),
            icon=icon_svg("magnifying-glass"), 
        ),
        ui.nav_panel(
            "Individual Stock Analysis",
            ui.h3("Contact Information"),
            ui.p("Email: example@example.com"),
            icon=icon_svg("chart-line"), 
        ),
        ui.nav_panel(
            "Stock Comparison",
            icon=icon_svg("scale-balanced") 

        ),
        ui.nav_panel(
            "Portfolio Tracker",
            icon=icon_svg("wallet")     
        ),
        
        title=ui.tags.a(
            ui.tags.img(
                src="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/icons/graph-up.svg",
                height="30px",
                style="margin-right:8px;"
            ),
            "Volatility Explorer",
            style="display:flex;align-items:center;color:white;text-decoration:none;"
        ),
        theme=theme.cosmo,
    )

)




def server(input, output, session):
    
    pass

app = App(app_ui, server)

if __name__ == "__main__":
    app.run()
