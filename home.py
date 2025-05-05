import os
from shiny import App, ui, render, reactive
from shinyswatch import theme
from faicons import icon_svg


css = """
/* Modern financial app styling */
:root {
  --primary-dark: #1a237e;
  --primary-light: #534bae;
  --accent: #ff6d00;
  --text-light: #f5f5f5;
  --text-dark: #212121;
  --success: #2e7d32;
  --warning: #f57c00;
  --danger: #c62828;
}

/* Navbar styling */
.navbar {
  background: linear-gradient(135deg, var(--primary-dark), var(--primary-light));
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 0.75rem 1rem;
}

/* Nav links */
.nav-link {
  color: var(--text-light) !important;
  font-weight: 500;
  padding: 0.75rem 1.25rem;
  transition: all 0.3s ease;
  border-radius: 0.25rem;
  margin: 0 0.25rem;
}

.nav-link:hover,
.nav-link.active {
  color: var(--text-light) !important;
  background-color: rgba(255,255,255,0.1);
  transform: translateY(-1px);
}

/* Brand styling */
.navbar-brand {
  color: var(--text-light) !important;
  font-size: 1.5rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

/* Main content area */
.main-content {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

/* Card styling */
.feature-card {
  background: white;
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin: 1rem 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  transition: transform 0.3s ease;
  display: flex;
  align-items: center;
  max-width: 700px;
  margin-left: auto;
  margin-right: auto;
  position: relative;
}

.feature-card::before {
  content: "";
  display: block;
  position: absolute;
  left: 0;
  top: 1.5rem;
  bottom: 1.5rem;
  width: 6px;
  border-radius: 6px;
  background: #ff6d00;
}

.feature-card > div {
  width: 100%;
  text-align: center;
}

.feature-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

/* Button styling */
.btn-cta {
  background: linear-gradient(135deg, var(--primary-dark), var(--primary-light));
  color: var(--text-light) !important;
  border: none;
  font-size: 1.1rem;
  padding: 0.75rem 1.5rem;
  border-radius: 0.375rem;
  transition: all 0.3s ease;
  margin: 0.5rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-cta:hover {
  background: linear-gradient(135deg, var(--primary-light), var(--primary-dark));
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

/* Feature list styling */
.feature-list {
  list-style: none;
  padding: 0;
  margin: 2rem 0;
}

.feature-list li {
  padding: 1rem;
  margin: 0.5rem 0;
  background: rgba(255,255,255,0.05);
  border-radius: 0.375rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.feature-list strong {
  color: var(--accent);
}

/* Welcome section */
.welcome-section {
  text-align: center;
  padding: 3rem 1rem;
  background: linear-gradient(135deg, rgba(26,35,126,0.05), rgba(83,75,174,0.05));
  border-radius: 1rem;
  margin-bottom: 2rem;
}

/* Action buttons container */
.action-buttons {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1rem;
  margin: 2rem 0;
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
            ui.tags.div(
                ui.tags.div(
                    ui.h1("Welcome to Volatility Explorer", class_="display-4"),
                    ui.p(
                        "Your comprehensive platform for market risk analysis and portfolio optimization. "
                        "Powered by real-time data and advanced analytics.",
                        class_="lead"
                    ),
                    class_="welcome-section"
                ),
                
                ui.tags.div(
                    ui.h2("Key Features", class_="text-center mb-4"),
                    ui.tags.ul(
                        ui.tags.li(
                            ui.tags.div(
                                ui.tags.div(
                                    ui.tags.strong("Volatility Screener", style="color:#ff6d00;"),
                                    ui.tags.p("Filter and rank stocks by volatility metrics with customizable parameters."),
                                ),
                                class_="feature-card"
                            ),
                            class_="feature-card"
                        ),
                        ui.tags.li(
                            ui.tags.div(
                                ui.tags.div(
                                    ui.tags.strong("Individual Stock Analysis", style="color:#ff6d00;"),
                                    ui.tags.p("Deep dive into single ticker analysis with comprehensive volatility metrics and charts."),
                                ),
                                class_="feature-card"
                            ),
                            class_="feature-card"
                        ),
                        ui.tags.li(
                            ui.tags.div(
                                ui.tags.div(
                                    ui.tags.strong("Stock Comparison", style="color:#ff6d00;"),
                                    ui.tags.p("Compare multiple equities side-by-side with advanced benchmarking tools."),
                                ),
                                class_="feature-card"
                            ),
                            class_="feature-card"
                        ),
                        ui.tags.li(
                            ui.tags.div(
                                ui.tags.div(
                                    ui.tags.strong("Portfolio Tracker", style="color:#ff6d00;"),
                                    ui.tags.p("Monitor and optimize your portfolio's risk profile in real-time."),
                                ),
                                class_="feature-card"
                            ),
                            class_="feature-card"
                        ),
                        class_="feature-list"
                    ),
                ),

                ui.tags.div(
                    ui.input_action_button(
                        "go_screener", 
                        ui.tags.span(icon_svg("magnifying-glass"), " Volatility Screener"), 
                        class_="btn-cta"
                    ),
                    ui.input_action_button(
                        "go_individual", 
                        ui.tags.span(icon_svg("chart-line"), " Stock Analysis"), 
                        class_="btn-cta"
                    ),
                    ui.input_action_button(
                        "go_compare", 
                        ui.tags.span(icon_svg("scale-balanced"), " Compare Stocks"), 
                        class_="btn-cta"
                    ),
                    ui.input_action_button(
                        "go_portfolio", 
                        ui.tags.span(icon_svg("wallet"), " Portfolio Tracker"), 
                        class_="btn-cta"
                    ),
                    class_="action-buttons"
                ),
                class_="main-content"
            ),
            icon=icon_svg("house-chimney"),
        ),

        ui.nav_panel(
            "Volatility Screener",
            ui.tags.div(
                ui.h2("Volatility Screener"),
                ui.p("Analyze and filter stocks based on volatility metrics."),
                class_="main-content"
            ),
            icon=icon_svg("magnifying-glass"),
            value="screener",
        ),

        ui.nav_panel(
            "Individual Stock Analysis",
            ui.tags.div(
                ui.h2("Individual Stock Analysis"),
                ui.p("Detailed analysis of individual stock volatility."),
                class_="main-content"
            ),
            icon=icon_svg("chart-line"),
            value="individual",
        ),

        ui.nav_panel(
            "Stock Comparison",
            ui.tags.div(
                ui.h2("Stock Comparison"),
                ui.p("Compare volatility metrics across multiple stocks."),
                class_="main-content"
            ),
            icon=icon_svg("scale-balanced"),
            value="compare",
        ),

        ui.nav_panel(
            "Portfolio Tracker",
            ui.tags.div(
                ui.h2("Portfolio Tracker"),
                ui.p("Monitor your portfolio's overall volatility."),
                class_="main-content"
            ),
            icon=icon_svg("wallet"),
            value="portfolio",
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
        id="main_nav",
    )
)

def server(input, output, session):
    @reactive.Effect
    @reactive.event(input.go_screener)
    def _():
        ui.update_navs("main_nav", selected="screener")

    @reactive.Effect
    @reactive.event(input.go_individual)
    def _():
        ui.update_navs("main_nav", selected="individual")

    @reactive.Effect
    @reactive.event(input.go_compare)
    def _():
        ui.update_navs("main_nav", selected="compare")

    @reactive.Effect
    @reactive.event(input.go_portfolio)
    def _():
        ui.update_navs("main_nav", selected="portfolio")

here = os.path.dirname(__file__)
www_path = os.path.join(here, "www")
app = App(
        app_ui,
        server, 
        static_assets=www_path
    )

if __name__ == "__main__":
    app.run()
