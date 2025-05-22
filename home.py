import os
from shiny import App, ui, render, reactive
from shinyswatch import theme
from modules.screener import ui_screener, server_screener
from modules.portfolio_tracker import ui_portfolio_tracker, server_portfolio_tracker
from modules.individual_stock import ui_individual_stock, server_individual_stock
from modules.screener import stock_cols, vol_df
from modules.stock_comparison import ui_stock_comparison, server_stock_comparison
from modules.model_details import ui_model_details, server_model_details
from modules.common_style import get_common_css
from modules.visual_effects import get_effects_css, get_interactive_js
import pandas as pd
import numpy as np

stock_ids = [str(col) for col in vol_df.columns if col != 'time_id']

# Navigation items for sidebar
nav_items = [
    {"id": "home", "label": "Overview", "icon": "home"},
    {"id": "screener", "label": "Stock Screener", "icon": "search"},
    {"id": "individual", "label": "Individual Stock Analysis", "icon": "chart-line"},
    {"id": "compare", "label": "Stock Comparison", "icon": "balance-scale"},
    {"id": "portfolio", "label": "Portfolio Tracker", "icon": "wallet"},
    {"id": "model", "label": "Model Details", "icon": "brain"}
]

app_ui = ui.page_fluid(
    # Load required CSS and JavaScript
    ui.tags.head(
        # External CSS
        ui.tags.link(rel="stylesheet", href="styles.css"),
        # Font Awesome
        ui.tags.link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"),
        # Inter font for better typography
        ui.tags.link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap"),
        # Common CSS and effects
        ui.tags.style(get_common_css() + get_effects_css()),
        ui.tags.script(get_interactive_js()),
        # --- Add JS for sidebar interaction ---
        ui.tags.script(r'''
document.addEventListener('DOMContentLoaded', function() {
  // Toggle sidebar on mobile
  const toggleBtn = document.getElementById('sidebar-toggle');
  const sidebar = document.querySelector('.sidebar');
  
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', function() {
      sidebar.classList.toggle('sidebar-open');
    });
  }
  
  // Global tooltip functionality
  let tooltip;
  function showTooltip(e, text) {
    if (!tooltip) {
      tooltip = document.createElement('div');
      tooltip.className = 'custom-tooltip-global';
      document.body.appendChild(tooltip);
    }
    tooltip.textContent = text;
    tooltip.classList.add('show');
    // Position above the icon
    const rect = e.target.getBoundingClientRect();
    const scrollY = window.scrollY || window.pageYOffset;
    const scrollX = window.scrollX || window.pageXOffset;
    tooltip.style.left = (rect.left + rect.width/2 + scrollX) + 'px';
    tooltip.style.top = (rect.top + scrollY - tooltip.offsetHeight - 16) + 'px';
    tooltip.style.transform = 'translateX(-50%)';
    tooltip.style.visibility = 'visible';
    tooltip.style.opacity = '1';
  }
  
  function hideTooltip() {
    if (tooltip) {
      tooltip.classList.remove('show');
      tooltip.style.visibility = 'hidden';
      tooltip.style.opacity = '0';
    }
  }
  
  // Improved event delegation for tooltip handling
  document.body.addEventListener('mouseover', function(e) {
    let target = e.target;
    // Check if the target or any of its parent elements have the info-icon class
    while (target && target !== document.body) {
      if (target.classList.contains('info-icon')) {
        const text = target.getAttribute('data-tooltip');
        if (text) showTooltip(e, text);
        break;
      }
      target = target.parentElement;
    }
  }, true);
  
  document.body.addEventListener('mouseout', function(e) {
    let target = e.target;
    while (target && target !== document.body) {
      if (target.classList.contains('info-icon')) {
        hideTooltip();
        break;
      }
      target = target.parentElement;
    }
  }, true);
  
  // Also handle touch events for mobile
  document.body.addEventListener('touchstart', function(e) {
    let target = e.target;
    while (target && target !== document.body) {
      if (target.classList.contains('info-icon')) {
        const text = target.getAttribute('data-tooltip');
        if (text) showTooltip(e, text);
        break;
      }
      target = target.parentElement;
    }
  }, true);
  
  document.body.addEventListener('touchend', function(e) {
    let target = e.target;
    while (target && target !== document.body) {
      if (target.classList.contains('info-icon')) {
        setTimeout(hideTooltip, 2000); // Hide after 2 seconds on touch devices
        break;
      }
      target = target.parentElement;
    }
  }, true);
  
  // Fix for the model-insights-container z-index issues
  const insightsContainer = document.querySelector('.model-insights-container');
  if (insightsContainer) {
    const infoIcons = insightsContainer.querySelectorAll('.info-icon');
    infoIcons.forEach(icon => {
      icon.style.zIndex = '100';
    });
  }
});

document.navigateToStock = function(id) {
  Shiny.setInputValue('main_nav', 'individual');
  // slight delay to let module load then set stock id
  setTimeout(function() { Shiny.setInputValue('stock_id', id); }, 300);
}
'''),
    ),
    ui.output_ui("app_root")
)

def server(input, output, session):
    # Track which module is selected
    current_page = reactive.Value("home")
    dark_mode = reactive.Value(True)  # Dark mode enabled by default
    darkmode_anim = reactive.Value(False)
    sidebar_collapsed = reactive.Value(False)  # Track sidebar state
    # --- Notification state ---
    # Function to generate notifications based on forecast vs realized volatility
    def generate_vol_notifications():
        notes = []
        try:
            pred_df = pd.read_csv("data/predicted_realized_vol.csv")
            vol_df = pd.read_csv("data/vol_df.csv")
            latest_row = vol_df.iloc[-1]
            stock_cols = [str(c) for c in vol_df.columns if c != "time_id"]
            realized_vols = {str(col): latest_row[col] for col in stock_cols}

            for _, row in pred_df.iterrows():
                symbol = str(int(row["stock_id"]))
                forecast_rv = row["predicted_realized_vol"] * 100
                current_rv = realized_vols.get(symbol)
                if current_rv is None:
                    continue
                diff = forecast_rv - current_rv
                notes.append({
                    "symbol": symbol,
                    "forecast": forecast_rv,
                    "realized": current_rv,
                    "diff": diff,
                })

            # sort by absolute difference and keep top 5
            notes = sorted(notes, key=lambda x: abs(x["diff"]), reverse=True)[:5]

            from datetime import datetime
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            for n in notes:
                n["time"] = now_str
            return notes
        except Exception as _:
            # fallback static note
            return [{"title": "Data", "message": "Unable to load volatility data.", "time": "-"}]

    notifications = reactive.Value(generate_vol_notifications())
    show_notifications = reactive.Value(True)  # open by default
    
    # Navigation event handlers
    @reactive.Effect
    @reactive.event(input.main_nav)
    def update_page_from_button():
        current_page.set(input.main_nav())
    
    # Handle sidebar toggle
    @reactive.Effect
    @reactive.event(input.toggle_sidebar)
    def _():
        sidebar_collapsed.set(not sidebar_collapsed())

    @reactive.Effect
    @reactive.event(input.toggle_darkmode)
    def _():
        dark_mode.set(not dark_mode())
        darkmode_anim.set(True)

    @reactive.Effect
    def _():
        if darkmode_anim():
            import time
            time.sleep(0.5)
            darkmode_anim.set(False)

    @output
    @render.ui
    def topbar_ui():
        icon_class = "fa fa-sun" if dark_mode() else "fa fa-moon"
        anim_class = "topbar-darkmode animated" if darkmode_anim() else "topbar-darkmode"
        # Build notification bell with badge
        notif_count = len(notifications())
        bell_icon = ui.tags.span(
            ui.tags.i(class_="fa fa-bell"),
            ui.tags.span(str(notif_count), class_="notification-badge") if notif_count else None,
            style="position:relative;display:inline-flex;align-items:center;"
        )
        return ui.tags.div(
            ui.tags.div(
                ui.tags.button(
                    ui.tags.i(class_="fa fa-bars"),
                    id="sidebar-toggle",
                    class_="sidebar-toggle-btn"
                ),
                ui.tags.i(class_="fa fa-chart-pie", style="font-size:1.5rem;color:var(--primary);"),
                ui.tags.span("STOCK SCREENING", class_="topbar-title"),
                class_="topbar-left"
            ),
                ui.tags.div(
                ui.tags.span(
                    ui.tags.i(class_="fa fa-clock"),
                    "Last updated: May 12, 2025 09:30 EST",
                    class_="topbar-updated"
                ),
                ui.input_action_button("toggle_darkmode", ui.tags.i(class_=icon_class), class_=anim_class, aria_label="Toggle dark mode"),
                ui.input_action_button("toggle_notifications", bell_icon, class_="topbar-icon-btn", aria_label="Notifications"),
                ui.tags.button(
                    ui.tags.i(class_="fa fa-cog"),
                    class_="topbar-icon-btn"
                ),
                class_="topbar-right"
            ),
            ui.tags.div(class_="topbar-gradient-bar"),
            class_="topbar"
        )
        
    @output
    @render.ui
    def sidebar_ui():
        collapsed_class = "sidebar collapsed" if sidebar_collapsed() else "sidebar"
        
        # Sidebar navigation items
        nav_elements = []
        for item in nav_items:
            is_active = current_page() == item["id"]
            active_class = "sidebar-nav-item active" if is_active else "sidebar-nav-item"
            
            nav_elements.append(
                ui.tags.button(
                    ui.tags.div(
                        ui.tags.i(class_=f"fa fa-{item['icon']}"),
                        ui.tags.span(item["label"], class_="sidebar-nav-label"),
                        class_="sidebar-nav-content"
                    ),
                    id=f"nav_{item['id']}",
                    class_=active_class,
                    onclick=f"Shiny.setInputValue('main_nav', '{item['id']}');"
                )
            )
        
        # Create watchlist section
        watchlist = create_watchlist_ui()
        
        # Create attention pairs section
        attention_pairs = create_attention_pairs_ui()
        
        return ui.tags.div(
            # Logo section
            ui.tags.div(
                ui.tags.i(class_="fa fa-chart-pie logo-icon"),
                ui.tags.div("Volatility", class_="logo-text-primary"),
                ui.tags.div("Explorer", class_="logo-text-secondary"),
                class_="sidebar-logo"
            ),
            
            # Navigation section
            ui.tags.div(
                ui.tags.div("Navigation", class_="sidebar-section-title"),
                ui.tags.div(
                    *nav_elements,
                    class_="sidebar-nav-items"
                ),
                class_="sidebar-section"
            ),
            
            # Watchlist section (collapsible on small screens)
            ui.tags.div(
                watchlist,
                class_="sidebar-section watchlist-section"
            ),
            
            # Attention pairs section (collapsible on small screens)
            ui.tags.div(
                attention_pairs,
                class_="sidebar-section attention-pairs-section"
            ),
            
            # Footer with profile (optional)
            ui.tags.div(
                ui.tags.div(
                    ui.tags.div("B", class_="sidebar-avatar"),
                    ui.tags.div("User", class_="sidebar-username"),
                    class_="sidebar-user"
                ),
                ui.tags.button(
                    ui.tags.i(class_="fa fa-sign-out-alt"),
                    class_="sidebar-logout"
                ),
                class_="sidebar-footer"
            ),
            
            class_=collapsed_class
        )

    @output
    @render.ui
    def app_root():
        class_name = "app-root dark-mode" if dark_mode() else "app-root"
        return ui.tags.div(
            ui.output_ui("topbar_ui"),
            ui.output_ui("dashboard_container"),
            ui.output_ui("notifications_ui"),
            class_=class_name
        )

    @output
    @render.ui
    def dashboard_container():
        class_name = "dashboard-layout dark-mode" if dark_mode() else "dashboard-layout"
        return ui.tags.div(
            # Sidebar navigation
            ui.output_ui("sidebar_ui"),
            
            # Main content area
            ui.tags.div(
                ui.output_ui("page_content"),
                class_="main-content"
            ),
            class_=class_name
        )

    def create_watchlist_ui():
        # Create a watchlist UI for the sidebar using real stock data
        # Get stock data for watchlist
        try:
            pred_df = pd.read_csv("data/predicted_realized_vol.csv")
            vol_df = pd.read_csv("data/vol_df.csv")
            stock_cols = [str(c) for c in vol_df.columns if c != "time_id"]
            latest_row = vol_df.iloc[-1]
            realized_vols = {str(col): latest_row[col] for col in stock_cols}

            # Build list similar to heatmap logic: positive errors sorted desc
            stocks = []
            for _, row in pred_df.iterrows():
                symbol = str(int(row["stock_id"]))
                forecasted_rv = row["predicted_realized_vol"] * 100
                current_rv = realized_vols.get(symbol, None)
                if current_rv is None:
                    continue
                current_rv *= 100
                error = forecasted_rv - current_rv
                stocks.append({"symbol": symbol, "error": error})

            top_stocks = sorted(stocks, key=lambda x: abs(x["error"]), reverse=True)[:5]
            
            watchlist_items = []
            for stock in top_stocks:
                error_display = f"{stock['error']:+.1f}%"
                pill_class = "sidebar-pill green" if stock['error'] >= 0 else "sidebar-pill red"
                
                watchlist_items.append(ui.tags.li(
                    ui.tags.span(f"Stock {stock['symbol']}", class_="sidebar-label"),
                    ui.tags.span(error_display, class_=pill_class),
                    class_="sidebar-list-item"
                ))
            
            return ui.tags.div(
                ui.tags.h3("Watchlist", class_="sidebar-section-title"),
                ui.tags.ul(
                    *watchlist_items,
                    class_="sidebar-list"
                )
            )
            
        except Exception as e:
            # Fallback to default watchlist if there's an error
            return ui.tags.div(
                ui.tags.h3("Watchlist", class_="sidebar-section-title"),
                ui.tags.ul(
                    ui.tags.li(
                        ui.tags.span("AAPL", class_="sidebar-label"),
                        ui.tags.span("+1.2%", class_="sidebar-pill green"),
                        class_="sidebar-list-item"
                    ),
                    ui.tags.li(
                        ui.tags.span("MSFT", class_="sidebar-label"),
                        ui.tags.span("+0.8%", class_="sidebar-pill green"),
                        class_="sidebar-list-item"
                    ),
                    ui.tags.li(
                        ui.tags.span("GOOGL", class_="sidebar-label"),
                        ui.tags.span("-0.5%", class_="sidebar-pill red"),
                        class_="sidebar-list-item"
                    ),
                    ui.tags.li(
                        ui.tags.span("AMZN", class_="sidebar-label"),
                        ui.tags.span("+1.7%", class_="sidebar-pill green"),
                        class_="sidebar-list-item"
                    ),
                    class_="sidebar-list"
                )
            )

    def create_attention_pairs_ui():
        # Create attention pairs UI for the sidebar with real data
        try:
            pred_df = pd.read_csv("data/predicted_realized_vol.csv")
            vol_df = pd.read_csv("data/vol_df.csv")
            
            # Get the top 5 stocks for potential pairs
            stock_cols = [str(c) for c in vol_df.columns if c != "time_id"]
            latest_row = vol_df.iloc[-1]
            top_stocks = sorted(stock_cols, key=lambda x: latest_row[x], reverse=True)[:5]
            
            # Create pairs (simplified example)
            # In a real app, you would calculate correlation or other meaningful metrics
            pairs = [
                {"pair": f"{top_stocks[0]} - {top_stocks[1]}", "score": 0.85},
                {"pair": f"{top_stocks[1]} - {top_stocks[2]}", "score": 0.72},
                {"pair": f"{top_stocks[0]} - {top_stocks[3]}", "score": 0.68}
            ]
            
            pair_items = []
            for pair_data in pairs:
                pair_items.append(ui.tags.li(
                    ui.tags.span(pair_data["pair"], class_="sidebar-label"),
                    ui.tags.span(f"{pair_data['score']:.2f}", class_="sidebar-pill purple"),
                    class_="sidebar-list-item"
                ))
            
            return ui.tags.div(
                ui.tags.h3("High Attention Pairs", class_="sidebar-section-title"),
                ui.tags.ul(
                    *pair_items,
                    class_="sidebar-list"
                )
            )
        
        except Exception as e:
            # Fallback to default attention pairs if there's an error
            return ui.tags.div(
                ui.tags.h3("High Attention Pairs", class_="sidebar-section-title"),
                ui.tags.ul(
                    ui.tags.li(
                        ui.tags.span("AAPL - MSFT", class_="sidebar-label"),
                        ui.tags.span("0.85", class_="sidebar-pill purple"),
                        class_="sidebar-list-item"
                    ),
                    ui.tags.li(
                        ui.tags.span("GOOGL - FB", class_="sidebar-label"),
                        ui.tags.span("0.72", class_="sidebar-pill purple"),
                        class_="sidebar-list-item"
                    ),
                    ui.tags.li(
                        ui.tags.span("AMZN - NFLX", class_="sidebar-label"),
                        ui.tags.span("0.68", class_="sidebar-pill purple"),
                        class_="sidebar-list-item"
                    ),
                    class_="sidebar-list"
                )
            )

    @output
    @render.ui
    def page_content():
        page = current_page()
        
        if page == "home":
            return home_content_ui()
        elif page == "screener":
            return ui_screener()
        elif page == "individual":
            return ui_individual_stock(stock_ids=stock_ids)
        elif page == "compare":
            return ui_stock_comparison(stock_ids=stock_ids) 
        elif page == "portfolio":
            return ui_portfolio_tracker()
        elif page == "model":
            return ui_model_details()
        else:
            return ui.tags.div("Page not found", style="text-align: center; margin-top: 2rem;")

    def home_content_ui():
        try:
            pred_df = pd.read_csv("data/predicted_realized_vol.csv")
            vol_df = pd.read_csv("data/vol_df.csv")
            stock_cols = [str(c) for c in vol_df.columns if c != "time_id"]
            latest_row = vol_df.iloc[-1]
            realized_vols = {str(col): latest_row[col] for col in stock_cols}
            real_stocks = []
            for _, row in pred_df.iterrows():
                symbol = str(int(row["stock_id"]))
                name = f"Stock {symbol}"
                forecasted_rv = row["predicted_realized_vol"] * 100
                current_rv = realized_vols.get(symbol, None)
                if current_rv is not None:
                    current_rv = current_rv * 100
                    error = forecasted_rv - current_rv
                    real_stocks.append({
                        "symbol": symbol,
                        "name": name,
                        "forecasted_rv": forecasted_rv,
                        "current_rv": current_rv,
                        "error": error
                    })
            # Sort and select 5 positive and 4 negative error cards
            positive_cards = sorted([s for s in real_stocks if s["error"] >= 0], key=lambda x: -x["error"])[:5]
            negative_cards = sorted([s for s in real_stocks if s["error"] < 0], key=lambda x: x["error"])[:5]
            real_stocks = positive_cards + negative_cards
        except Exception as e:
            return ui.tags.div(f"Error: {e}", style="color:red;font-size:1.5rem;text-align:center;")
        
        return ui.tags.div(
            # Header with dashboard title
            ui.tags.div(
                ui.tags.h1("Dashboard Overview", class_="dashboard-title"),
                class_="dashboard-header"
            ),
            
            # --- Model Insights Panel ---
            ui.tags.div(
                # Title for Model Insights
                ui.tags.div("Model Insights", class_="model-insights-title"),
                
                # Model Performance cards
                ui.tags.div(
                    ui.tags.div("Model Performance", class_="model-section-title"),
                    ui.tags.div(
                        *[
                            ui.tags.div(
                                ui.tags.div(
                                    ui.tags.div(
                                        [
                                            "Average Forecast Error",
                                            ui.tags.i(class_="fa fa-info-circle info-icon", tabindex="0", **{"data-tooltip": "How much, on average, the model's predictions differ from the actual volatility. Lower is better."})
                                        ],
                                        class_="summary-card-title"
                                    ),
                                    ui.tags.div("+9%", class_="summary-card-value"),
                                    class_="summary-card-content"
                                ),
                                ui.tags.div(ui.tags.i(class_="fa fa-chart-line"), class_="summary-card-icon"),
                                class_="summary-card-overview"
                            ),
                            ui.tags.div(
                                ui.tags.div(
                                    ui.tags.div(
                                        ui.tags.span("Root Mean Square Percentage Error", class_="card-title-text"),
                                        ui.tags.i(class_="fa fa-info-circle info-icon", tabindex="0", **{"data-tooltip": "Shows the average size of prediction errors as a percentage. Lower means more accurate predictions."}),
                                        class_="summary-card-title"
                                    ),
                                    ui.tags.div("33%", class_="summary-card-value"),
                                    class_="summary-card-content"
                                ),
                                ui.tags.div(ui.tags.i(class_="fa fa-wave-square"), class_="summary-card-icon blue"),
                                class_="summary-card-overview rmspe-card"
                            ),
                            ui.tags.div(
                                ui.tags.div(
                                    ui.tags.div(
                                        [
                                            "Model Confidence",
                                            ui.tags.i(class_="fa fa-info-circle info-icon", tabindex="0", **{"data-tooltip": "How sure the model is about its predictions. Higher confidence means the model is more certain."})
                                        ],
                                        class_="summary-card-title"
                                    ),
                                    ui.tags.div("67%", class_="summary-card-value"),
                                    class_="summary-card-content"
                                ),
                                ui.tags.div(ui.tags.i(class_="fa fa-chart-line"), class_="summary-card-icon purple"),
                                class_="summary-card-overview"
                            ),
                            ui.tags.div(
                                ui.tags.div(
                                    ui.tags.div(
                                        [
                                            "Last Training",
                                            ui.tags.i(class_="fa fa-info-circle info-icon", tabindex="0", **{"data-tooltip": "How recently the model was updated with new data. More recent training means fresher insights."})
                                        ],
                                        class_="summary-card-title"
                                    ),
                                    ui.tags.div("2h ago", class_="summary-card-value"),
                                    class_="summary-card-content"
                                ),
                                ui.tags.div(ui.tags.i(class_="fa fa-calendar"), class_="summary-card-icon yellow"),
                                class_="summary-card-overview"
                            ),
                        ],
                        class_="summary-cards-row-overview"
                    ),
                    # Add "View Model Details" button
                    ui.tags.div(
                        ui.tags.button(
                            ui.tags.i(class_="fa fa-brain"),
                            "View Model Details",
                            class_="view-model-btn",
                            onclick="Shiny.setInputValue('main_nav', 'model');"
                        ),
                        class_="model-btn-container"
                    ),
                    class_="model-performance-section"
                ),
                
                ui.tags.hr(class_="model-section-divider"),
                
                # Heatmap
                ui.tags.div(
                    ui.tags.div("Next-Day Volatility Forecast Heatmap", class_="model-section-title"),
                    ui.tags.div(
                        *([
                            ui.tags.div(
                                ui.tags.div(stock["symbol"], class_="stock-symbol"),
                                ui.tags.div(stock["name"], class_="company-name"),
                                ui.tags.div(f"Forecasted RV: {stock['forecasted_rv']:.2f}%", class_="stat-row"),
                                ui.tags.div(f"Current RV: {stock['current_rv']:.2f}%", class_="stat-row"),
                                ui.tags.div("Different", class_="error-label"),
                                ui.tags.div(f"{stock['error']:+.2f}%", class_="error-value"),
                                class_=("overview-card positive" if stock['error'] >= 0 else "overview-card negative"),
                                title=f"{stock['symbol']} | Different: {stock['error']:.2f}% | Forecasted: {stock['forecasted_rv']:.2f}% | Current: {stock['current_rv']:.2f}%",
                                onclick=f"navigateToStock('{stock['symbol']}')"
                            ) for stock in real_stocks
                        ] if real_stocks else [
                            ui.tags.div("No data available for heatmap cards.", style="color:red;font-size:1.5rem;text-align:center;")
                        ]),
                        class_="overview-card-grid"
                    ),
                    class_="heatmap-section"
                ),
                class_="model-insights-container"
            ),
            class_="main-content-inner"
        )

    # Toggle the notification panel
    @reactive.Effect
    @reactive.event(input.toggle_notifications)
    def _():
        show_notifications.set(not show_notifications())

    # --- Notifications panel UI ---
    @output
    @render.ui
    def notifications_ui():
        if not show_notifications():
            return None

        items = []
        for n in notifications():
            direction = "up" if n["diff"] >= 0 else "down"
            items.append(
                ui.tags.li(
                    # header row with symbol and time
                    ui.tags.div(
                        ui.tags.span(n["symbol"], class_="notif-symbol"),
                        ui.tags.span(n["time"], class_="notif-time"),
                        class_="notif-header"
                    ),
                    # body rows
                    ui.tags.div(
                        f"Forecast: {n['forecast']:.2f}%, Realized: {n['realized']:.2f}%",
                        class_="notif-body"
                    ),
                    ui.tags.div(
                        f"Δ{n['diff']:+.2f}%",
                        class_=f"notif-diff {direction}"
                    ),
                    class_=f"notification-item {direction}"
                )
            )

        return ui.tags.div(
            ui.tags.div(
                ui.tags.h4("Notifications"),
                ui.tags.ul(*items, class_="notification-list"),
                class_="notification-panel"
            )
        )

    # Call server logic for each module
    server_screener(input, output, session)
    server_individual_stock(input, output, session)
    server_stock_comparison(input, output, session)
    server_portfolio_tracker(input, output, session)
    server_model_details(input, output, session)

here = os.path.dirname(__file__)
www_path = os.path.join(here, "www")
app = App(
        app_ui,
        server, 
        static_assets=www_path
    )

if __name__ == "__main__":
    app.run(port=8002)