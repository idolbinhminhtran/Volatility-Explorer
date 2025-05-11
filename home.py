import os
from shiny import App, ui, render, reactive
from shinyswatch import theme
from faicons import icon_svg
from modules.screener import ui_screener, server_screener
from modules.portfolio_tracker import ui_portfolio_tracker, server_portfolio_tracker
from modules.individual_stock import ui_individual_stock, server_individual_stock
from modules.screener import stock_cols, vol_df
from modules.stock_comparison import ui_stock_comparison, server_stock_comparison

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
  padding: 1rem 2rem;
  max-width: 1600px;
  margin: 0 auto;
  min-height: calc(100vh - 150px);  # Added for vertical fit
}

/* Card styling */
.feature-card {
  background: linear-gradient(135deg, #fff 80%, #f3f7fa 100%);
  border-radius: 1.2rem;
  box-shadow: 0 4px 24px rgba(25, 118, 210, 0.08);
  padding: 2rem 1.5rem !important;  
  position: relative;
  margin-top: 3.5rem;  # Space for icon
  min-height: 320px;  # Changed from fixed height
  width: 100%;
  text-align: center;
  transition: box-shadow 0.2s, transform 0.2s;
  border: none;
}

.feature-card:hover {
  box-shadow: 0 8px 32px rgba(25, 118, 210, 0.16);
  transform: translateY(-4px) scale(1.02);
}

.feature-card .feature-icon {
  position: absolute;
  top: -28px;
  left: 50%;
  transform: translateX(-50%);
  background: #1976D2;
  color: #fff;
  border-radius: 50%;
  padding: 0.9rem;
  font-size: 2rem;
  box-shadow: 0 2px 8px rgba(25,118,210,0.12);
  z-index: 2;
}

.feature-card strong {
  display: block;
  font-size: 1.3rem;
  font-weight: 800;
  color: #1976D2;
  margin-bottom: 0.5rem;
  margin-top: 1.2rem;
}

.feature-card p {
  color: #444;
  font-size: 1.08rem;
  margin-bottom: 1.7rem;
  margin-top: 0.2rem;
}

.feature-card .btn-cta:hover {
  background: linear-gradient(135deg, #1976D2, #534bae);
  color: #fff !important;
  box-shadow: 0 4px 16px rgba(25,118,210,0.18);
}

/* Feature list styling */
.feature-list {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;  # Reduced from 2rem
  list-style: none;
  padding: 0;
  margin: 1rem 0; # Reduced from 2rem
  width: 100%;
}

.feature-list li {
  padding: 0 !important; 
  margin: 0 !important; 
  background: rgba(255,255,255,0.05); 
  border-radius: 0.375rem;
  display: block;  # Changed from flex
  align-items: center;
  gap: 1rem;
  position: relative;  # Added for icon containment
}

.feature-list strong {
  color: var(--accent);
}

.welcome-section {
  text-align: center;
  padding: 4rem 2rem 3rem 2rem;
  background: linear-gradient(135deg, #e3f0ff 60%, #f7faff 100%);
  border-radius: 2.2rem;
  margin-bottom: 2.5rem;
  box-shadow: 0 8px 32px rgba(25, 118, 210, 0.13);
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
  position: relative;
  border: 2.5px solid #e3f0fa;
}

.welcome-section .welcome-icon {
  background: linear-gradient(135deg, #1976D2 60%, #42a5f5 100%);
  color: #fff;
  border-radius: 50%;
  padding: 1.3rem;
  font-size: 3.2rem;
  box-shadow: 0 2px 12px rgba(25,118,210,0.13);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.2rem;
}

.welcome-section .display-4 {
  font-size: 3.3rem;
  font-weight: 900;
  color: #1a237e;
  margin-bottom: 1.1rem;
  margin-top: 0.5rem;
  letter-spacing: -1px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.welcome-section .lead {
  color: #444;
  font-size: 1.35rem;
  margin-bottom: 0;
  font-weight: 500;
}

/* Action buttons container */
.action-buttons {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1rem;
  margin: 2rem 0;
}

.screener-sidebar {
  background: linear-gradient(135deg, #f7faff 80%, #e3f2fd 100%);
  border-radius: 1.5rem;
  padding: 2.5rem 1.7rem 2.2rem 1.7rem;
  box-shadow: 0 6px 24px rgba(25,118,210,0.10);
  position: relative;
  min-height: 100%;
  border-left: 10px solid #1976D2;
  margin-top: 1.2rem;
}

.screener-sidebar h2 {
  font-size: 2.5rem;
  font-weight: 900;
  color: #1976D2;
  margin-bottom: 2.2rem;
  display: flex;
  align-items: center;
  gap: 0.7rem;
  letter-spacing: -1px;
}

.screener-sidebar label,
.screener-sidebar .form-label {
  font-size: 1.18rem;
  font-weight: 700;
  color: #1976D2;
  margin-top: 1.5rem;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.screener-sidebar .form-range,
.screener-sidebar input[type=range] {
  accent-color: #1976D2;
  height: 8px;
  border-radius: 4px;
}

.screener-sidebar .form-control,
.screener-sidebar input[type=number] {
  border-radius: 10px;
  border: 1.5px solid #e0e0e0;
  padding: 0.4rem 0.8rem;
  font-size: 1.08rem;
  background: #f7faff;
}

.screener-sidebar .input-group {
  margin-bottom: 1.7rem;
}

.screener-card {
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 6px 32px rgba(25,118,210,0.10);
  padding: 2.2rem 2.2rem 2rem 2.2rem;
  margin-bottom: 2.5rem;
  margin-top: 1.2rem;
}

.screener-card table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 2px 8px rgba(25,118,210,0.06);
  overflow: hidden;
  margin-bottom: 0;
  font-size: 1.13rem;
}

.screener-card th {
  background: linear-gradient(90deg, #1976D2 80%, #42a5f5 100%);
  color: #fff;
  font-weight: 800;
  font-size: 1.18rem;
  padding: 0.85rem 1.3rem;
  border: none;
  letter-spacing: 0.5px;
  white-space: normal;
  overflow: visible;
  text-overflow: initial;
  word-break: break-word;
}

.screener-card td {
  padding: 0.85rem 1.1rem;
  border: none;
  font-size: 1.08rem;
  color: #212121;
}

.screener-card tr:nth-child(even) {
  background: #f7faff;
}

.screener-card tr:hover {
  background: #e3f2fd;
  transition: background 0.2s;
}

.screener-card th:last-child {
  color: #fff;
  font-weight: 800;
}

.screener-card th:first-child,
.screener-card td:first-child {
  color: #212121;
  font-weight: 700;
}

.screener-title-row {
  display: flex;
  align-items: center;
  gap: 22px;
  margin-bottom: 0.7rem;
  margin-top: 1.2rem;
  justify-content: flex-start;
}

.screener-title-icon {
  background: linear-gradient(135deg, #1976D2 60%, #42a5f5 100%);
  color: #fff;
  border-radius: 50%;
  padding: 18px;
  font-size: 2.7rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px rgba(25,118,210,0.13);
}

.screener-title {
  color: #1976D2;
  font-size: 2.8rem;
  font-weight: 900;
  margin: 0;
  letter-spacing: -1.5px;
  text-shadow: 0 2px 8px rgba(25,118,210,0.08);
}

.screener-subtitle {
  color: #555;
  font-size: 1.22rem;
  margin-bottom: 1.7rem;
  margin-left: 80px;
  font-weight: 500;
}

.portfolio-sidebar {
  background: linear-gradient(135deg, #f7f9fa 80%, #ede7f6 100%);
  border-radius: 18px;
  padding: 2.2rem 1.5rem 2rem 1.5rem;
  box-shadow: 0 4px 16px rgba(149,117,205,0.07);
  position: relative;
  min-height: 100%;
  border-left: 8px solid #8E24AA;
}

.portfolio-sidebar h2 {
  font-size: 2.3rem;
  font-weight: 900;
  color: #8E24AA;
  margin-bottom: 2rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.portfolio-sidebar label,
.portfolio-sidebar .form-label {
  font-size: 1.15rem;
  font-weight: 600;
  color: #333;
  margin-top: 1.5rem;
  margin-bottom: 0.5rem;
}

.portfolio-sidebar .form-control,
.portfolio-sidebar input[type=number] {
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  padding: 0.3rem 0.7rem;
  font-size: 1rem;
}

.portfolio-sidebar .input-group {
  margin-bottom: 1.5rem;
}

.portfolio-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(149,117,205,0.10);
  padding: 2rem 2rem 1.5rem 2rem;
  margin-bottom: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.portfolio-card h2 {
  color: #8E24AA;
  font-size: 2rem;
  font-weight: 800;
  margin-bottom: 1.2rem;
}

.portfolio-card .shiny-output-plot {
  margin-bottom: 1.5rem;
  background: #f3e5f5;
  border-radius: 12px;
  padding: 1rem;
}

.feature-list-container {
  background: #f9fafe;
  border-radius: 1.7rem;
  box-shadow: 0 8px 32px rgba(25, 118, 210, 0.13);
  padding: 3.2rem 2.5rem;
  max-width: 1200px;
  width: 100%;
  margin: 3rem auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  border: 2px solid #e3f0fa;
}

.key-features-title {
  text-align: center;
  width: 100%;
  margin-bottom: 2.2rem;
  font-size: 2.1rem;
  font-weight: 800;
  color: #1976D2;
  letter-spacing: -0.5px;
}

.feature-list {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 2.2rem;
  width: 100%;
  padding: 0;
  margin: 2rem 0 0 0;
}

.feature-list li {
  flex: 1 1 220px;
  max-width: 270px;
  min-width: 220px;
  min-height: 480px;
  display: flex;
  align-items: stretch;
  justify-content: center;
  padding: 0;
  margin: 0;
  background: none;
  border: none;
  box-shadow: none;
  border-radius: 0;
  transition: none;
}

.feature-card {
  background: linear-gradient(135deg, #fff 80%, #f3f7fa 100%);
  border-radius: 1.2rem;
  box-shadow: 0 4px 24px rgba(25, 118, 210, 0.08);
  margin: 0;
  padding: 2.2rem 2rem 2.5rem 2rem;
  position: relative;
  width: 100%;
  max-width: 270px;
  min-height: 480px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  transition: box-shadow 0.2s, transform 0.2s;
  border: none;
}

.feature-card .feature-icon {
  position: absolute;
  top: -32px;
  left: 50%;
  transform: translateX(-50%);
  background: #1976D2;
  color: #fff;
  border-radius: 50%;
  padding: 0.9rem;
  font-size: 2.2rem;
  box-shadow: 0 2px 8px rgba(25,118,210,0.12);
  z-index: 2;
}

.feature-card strong {
  display: block;
  font-size: 1.3rem;
  font-weight: 800;
  color: #1976D2;
  margin-bottom: 0.5rem;
  margin-top: 1.2rem;
}

.feature-card p {
  color: #444;
  font-size: 1.08rem;
  margin-bottom: 1.7rem;
  margin-top: 0.2rem;
}

.feature-card .btn-cta {
  width: 80%;
  max-width: 320px;
  margin: 0 auto;
  display: block;
  font-size: 1.1rem;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(25,118,210,0.10);
  letter-spacing: 0.01em;
  transition: background 0.2s, box-shadow 0.2s, transform 0.2s;
}

.feature-card .btn-cta:hover {
  background: linear-gradient(135deg, #1976D2, #534bae);
  color: #fff !important;
  box-shadow: 0 4px 16px rgba(25,118,210,0.18);
  transform: translateY(-2px) scale(1.03);
}

.feature-card-btn {
  margin-top: auto;
  width: 100%;
  display: flex;
  justify-content: center;
}

@media (max-width: 1100px) {
  .feature-list {
    gap: 1.2rem;
  }
  .feature-list li, .feature-card {
    min-width: 180px;
    max-width: 220px;
    min-height: 420px;
  }
}

@media (max-width: 800px) {
  .feature-list {
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
  }
  .feature-list li, .feature-card {
    max-width: 95vw;
    min-width: 0;
    min-height: 320px;
  }
}

/* Table cell coloring for positive/negative values */
.screener-card td, .portfolio-card td {
  transition: color 0.2s;
}
.screener-card td.positive, .portfolio-card td.positive {
  color: #2e7d32 !important;
  font-weight: 700;
}
.screener-card td.negative, .portfolio-card td.negative {
  color: #c62828 !important;
  font-weight: 700;
}

/* Visually appealing metric accordion */
.metric-accordion {
  border: 2.5px solid #90caf9;
  border-radius: 1.2rem;
  box-shadow: 0 4px 24px rgba(25, 118, 210, 0.10);
  background: #f7faff;
  margin-bottom: 1.2rem;
  overflow: hidden;
  padding: 1.1rem 1.2rem 0.7rem 1.2rem;
  transition: box-shadow 0.2s, border-color 0.2s;
}
.metric-accordion .accordion-header {
  border: none;
  border-top-left-radius: 1.2rem;
  border-top-right-radius: 1.2rem;
  background: #f7faff;
  margin: 0;
  padding: 0.6rem 1.2rem 0.6rem 1.2rem;
  width: 100%;
  box-sizing: border-box;
  font-size: 1.18rem;
  font-weight: 800;
  color: #1976D2;
  box-shadow: 0 2px 8px rgba(25,118,210,0.07);
  transition: background 0.2s, color 0.2s;
}
.metric-accordion .accordion-header:hover, .metric-accordion .accordion-header:focus {
  background: #e3f0fa;
  color: #1565c0;
}
.metric-accordion .accordion-panel {
  border: none !important;
  box-shadow: none !important;
  background: none !important;
}

.metric-select-box {
  background: none;
  border-radius: 0;
  box-shadow: none;
  padding: 0;
  margin-bottom: 0;
  border: none;
}

.metric-checkbox-group {
  border: none;
  box-shadow: none;
  background: none;
  padding: 0;
}

/* --- Individual Stock Analysis Tab Styling --- */
.analysis-layout {
  display: flex;
  gap: 2.5rem;
  margin-top: 2.5rem;
  flex-wrap: wrap;
}

.sidebar-card {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 18px;
  box-shadow: 0 4px 24px rgba(44, 62, 80, 0.08);
  padding: 2rem 1.5rem;
  min-width: 260px;
  max-width: 320px;
  flex: 0 0 320px;
  margin-bottom: 1.5rem;
}

.summary-text {
  color: #5a5a5a;
  margin-top: 1.5rem;
  font-size: 1.1rem;
}

.main-card {
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 4px 24px rgba(44, 62, 80, 0.08);
  padding: 2rem 2rem 1.5rem 2rem;
  flex: 1 1 350px;
  min-width: 350px;
  margin-bottom: 1.5rem;
}

@media (max-width: 900px) {
  .analysis-layout {
    flex-direction: column;
    gap: 1.5rem;
  }
  .sidebar-card, .main-card {
    max-width: 100%;
    min-width: unset;
    flex: 1 1 100%;
  }
}

.metric-checkbox-group input[type="checkbox"] {
  accent-color: #1976D2;
  width: 1.25rem;
  height: 1.25rem;
  border-radius: 6px;
  margin-right: 0.7rem;
  vertical-align: middle;
  transition: box-shadow 0.2s;
}
.metric-checkbox-group label {
  font-size: 1.13rem;
  font-weight: 500;
  color: #222;
  padding: 0.45rem 0.7rem;
  border-radius: 8px;
  margin-bottom: 0.2rem;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: background 0.18s, color 0.18s;
}
.metric-checkbox-group input[type="checkbox"]:checked + label {
  color: #1976D2;
  font-weight: 700;
  background: #e3f0fa;
}
.metric-checkbox-group label:hover {
  background: #f7faff;
  color: #1976D2;
}

.metric-accordion::before,
.metric-accordion::after,
.metric-accordion .accordion-panel::before,
.metric-accordion .accordion-panel::after {
  display: none !important;
  content: none !important;
}
"""
stock_ids = [str(col) for col in vol_df.columns if col != 'time_id']

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
                    ui.tags.span(icon_svg("chart-line"), class_="welcome-icon"),
                    ui.h1("Welcome to Stock Screener", class_="display-4"),
                    ui.p(
                        "Your comprehensive platform for market risk analysis and portfolio optimization. Powered by Optiver dataset and advanced analytics.",
                        class_="lead"
                    ),
                    class_="welcome-section"
                ),
                
                ui.tags.div(
                    ui.h2("Key Features", class_="key-features-title"),
                    ui.tags.div(
                        ui.tags.ul(
                            ui.tags.li(
                                ui.tags.div(
                                    ui.tags.span(icon_svg("magnifying-glass"), class_="feature-icon"),
                                    ui.tags.strong("Stock Screener", style="color:#ff6d00;"),
                                    ui.tags.p("Filter and rank stocks by metrics with customizable parameters."),
                                    ui.tags.div(
                                        ui.input_action_button(
                                            "go_screener",
                                            ui.tags.span(icon_svg("magnifying-glass"), " Stock Screener"),
                                            class_="btn btn-cta",
                                            style="margin-top:1.2rem;"
                                        ),
                                        class_="feature-card-btn"
                                    ),
                                    class_="feature-card"
                                )
                            ),
                            ui.tags.li(
                                ui.tags.div(
                                    ui.tags.span(icon_svg("chart-line"), class_="feature-icon"),
                                    ui.tags.strong("Individual Stock Analysis", style="color:#ff6d00;"),
                                    ui.tags.p("Deep dive into single ticker analysis with comprehensive volatility metrics and charts."),
                                    ui.tags.div(
                                        ui.input_action_button(
                                            "go_individual",
                                            ui.tags.span(icon_svg("chart-line"), " Stock Analysis"),
                                            class_="btn btn-cta",
                                            style="margin-top:1.2rem;"
                                        ),
                                        class_="feature-card-btn"
                                    ),
                                    class_="feature-card"
                                )
                            ),
                            ui.tags.li(
                                ui.tags.div(
                                    ui.tags.span(icon_svg("scale-balanced"), class_="feature-icon"),
                                    ui.tags.strong("Stock Comparison", style="color:#ff6d00;"),
                                    ui.tags.p("Compare multiple equities side-by-side with advanced benchmarking tools."),
                                    ui.tags.div(
                                        ui.input_action_button(
                                            "go_compare",
                                            ui.tags.span(icon_svg("scale-balanced"), " Compare Stocks"),
                                            class_="btn btn-cta",
                                            style="margin-top:1.2rem;"
                                        ),
                                        class_="feature-card-btn"
                                    ),
                                    class_="feature-card"
                                )
                            ),
                            ui.tags.li(
                                ui.tags.div(
                                    ui.tags.span(icon_svg("wallet"), class_="feature-icon"),
                                    ui.tags.strong("Portfolio Tracker", style="color:#ff6d00;"),
                                    ui.tags.p("Monitor and optimize your portfolio's risk profile in real-time."),
                                    ui.tags.div(
                                        ui.input_action_button(
                                            "go_portfolio",
                                            ui.tags.span(icon_svg("wallet"), " Portfolio Tracker"),
                                            class_="btn btn-cta",
                                            style="margin-top:1.2rem;"
                                        ),
                                        class_="feature-card-btn"
                                    ),
                                    class_="feature-card"
                                )
                            ),
                            class_="feature-list"
                        ),
                        class_="feature-list-container"
                    ),
                ),
                class_="main-content"
            ),
            icon=icon_svg("house-chimney"),
        ),

        ui_screener(),

        ui.nav_panel(
            "Individual Stock Analysis",
            ui_individual_stock(stock_ids=stock_ids),
            icon=icon_svg("chart-line"),
            value="individual",
        ),

        ui.nav_panel(
            "Stock Comparison",
            ui.tags.div(
                ui_stock_comparison(stock_ids=stock_ids),
                class_="main-content"
            ),
            icon=icon_svg("scale-balanced"),
            value="compare",
        ),

        ui_portfolio_tracker(),
        
        title=ui.tags.a(
            ui.tags.img(
                src="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/icons/graph-up.svg",
                height="30px",
                style="margin-right:8px;"
            ),
            "Stock Screener",
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

    server_screener(input, output, session)
    server_individual_stock(input, output, session)
    server_stock_comparison(input, output, session)
    server_portfolio_tracker(input, output, session)

here = os.path.dirname(__file__)
www_path = os.path.join(here, "www")
app = App(
        app_ui,
        server, 
        static_assets=www_path
    )

if __name__ == "__main__":
    app.run()
