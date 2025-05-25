import os
from shiny import App, ui, render, reactive
from shinyswatch import theme
from modules.screener import ui_screener, server_screener
from modules.portfolio_tracker import ui_portfolio_tracker, server_portfolio_tracker, get_sparkline
from modules.individual_stock import ui_individual_stock, server_individual_stock
from modules.screener import stock_cols, vol_df
from modules.stock_comparison import ui_stock_comparison, server_stock_comparison
from modules.model_details import ui_model_details, server_model_details
from modules.common_style import get_common_css
from modules.visual_effects import get_effects_css, get_interactive_js
import pandas as pd
import numpy as np
from faicons import icon_svg

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
    // Since the tooltip uses position: fixed, viewport coordinates are sufficient
    tooltip.style.left = (rect.left + rect.width / 2) + 'px';
    tooltip.style.top = (rect.top - tooltip.offsetHeight - 16) + 'px';
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
        return ui.tags.div(
            ui.tags.div(
                ui.tags.button(
                    ui.tags.i(class_="fa fa-bars"),
                    id="sidebar-toggle",
                    class_="sidebar-toggle-btn"
                ),
                ui.tags.i(class_="fa fa-chart-pie", style="font-size:1.5rem;color:var(--primary);"),
                ui.tags.span("VOLTATRADE", class_="topbar-title"),
                class_="topbar-left"
            ),
            ui.tags.div(
                ui.tags.span(
                    ui.tags.i(class_="fa fa-clock"),
                    "Last updated: May 12, 2025 09:30 EST",
                    class_="topbar-updated" 
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
                ui.tags.div("Volta", class_="logo-text-primary"),
                ui.tags.div("Trade", class_="logo-text-secondary"),
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
                error_display = f"{stock['error']:+.2f}%"
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
            return ui_dashboard()

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
        
        # Custom CSS for enhanced visual effects
        enhanced_css = """
        .hero-container {
            position: relative;
            overflow: hidden;
            padding: 3rem 2rem;
            background: linear-gradient(135deg, rgba(36, 38, 44, 0.95) 0%, rgba(17, 18, 22, 0.98) 100%);
            border-radius: 1.2rem;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            margin-bottom: 2.5rem;
            border: 1px solid rgba(29, 185, 84, 0.1);
        }
        
        .hero-container::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(29, 185, 84, 0.05) 0%, transparent 60%);
            animation: pulse 15s infinite ease-in-out;
            z-index: 0;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); opacity: 0.3; }
            50% { transform: scale(1.05); opacity: 0.5; }
            100% { transform: scale(1); opacity: 0.3; }
        }
        
        .hero-title {
            font-size: 3.5rem;
            font-weight: 900;
            background: linear-gradient(90deg, #1db954 0%, #a78bfa 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
            position: relative;
            z-index: 1;
            text-align: center;
            letter-spacing: 2px;
            text-shadow: 0 0 20px rgba(29, 185, 84, 0.3);
            animation: text-focus 1s ease-out;
        }
        
        @keyframes text-focus {
            0% { letter-spacing: 5px; opacity: 0; filter: blur(12px); }
            100% { letter-spacing: 2px; opacity: 1; filter: blur(0); }
        }
        
        .hero-subtitle {
            font-size: 1.3rem;
            color: #e0e0e0;
            text-align: center;
            max-width: 800px;
            margin: 0 auto 1.5rem;
            line-height: 1.6;
            position: relative;
            z-index: 1;
            animation: fade-in 1.2s ease-out;
        }
        
        @keyframes fade-in {
            0% { opacity: 0; transform: translateY(20px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        
        .feature-card-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2.5rem;
        }
        
        .feature-card {
            background: rgba(36, 38, 44, 0.95);
            border-radius: 1rem;
            padding: 1.8rem;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
            border: 1px solid rgba(29, 185, 84, 0.1);
            position: relative;
            overflow: hidden;
            height: 100%;
            display: flex;
            flex-direction: column;
            animation: card-in 0.6s ease-out;
            animation-fill-mode: both;
        }
        
        .feature-card:nth-child(1) { animation-delay: 0.1s; }
        .feature-card:nth-child(2) { animation-delay: 0.2s; }
        .feature-card:nth-child(3) { animation-delay: 0.3s; }
        .feature-card:nth-child(4) { animation-delay: 0.4s; }
        
        @keyframes card-in {
            0% { opacity: 0; transform: translateY(30px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        
        .feature-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 15px 35px rgba(29, 185, 84, 0.2);
            border-color: rgba(29, 185, 84, 0.3);
        }
        
        .feature-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #1db954, #a78bfa);
            transform: scaleX(0);
            transform-origin: left;
            transition: transform 0.6s ease;
        }
        
        .feature-card:hover::before {
            transform: scaleX(1);
        }
        
        .feature-icon {
            font-size: 2.5rem;
            color: #1db954;
            margin-bottom: 1.2rem;
            background: rgba(29, 185, 84, 0.1);
            width: 70px;
            height: 70px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            margin-bottom: 1.5rem;
            transition: all 0.3s ease;
        }
        
        .feature-card:hover .feature-icon {
            background: rgba(29, 185, 84, 0.2);
            transform: scale(1.1);
        }
        
        .feature-title {
            font-size: 1.4rem;
            font-weight: 700;
            color: #1db954;
            margin-bottom: 1rem;
        }
        
        .feature-description {
            font-size: 1rem;
            color: #bdbdbd;
            line-height: 1.6;
            flex-grow: 1;
        }
        
        .get-started-button {
            display: inline-block;
            background: linear-gradient(90deg, #1db954, #a78bfa);
            color: white;
            padding: 1rem 2.5rem;
            border-radius: 2rem;
            font-weight: 700;
            font-size: 1.1rem;
            text-decoration: none;
            box-shadow: 0 10px 20px rgba(29, 185, 84, 0.3);
            transition: all 0.3s ease;
            border: none;
            letter-spacing: 1px;
            position: relative;
            overflow: hidden;
            z-index: 1;
        }
        
        .get-started-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 30px rgba(29, 185, 84, 0.4);
        }
        
        .get-started-button::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, #a78bfa, #1db954);
            opacity: 0;
            z-index: -1;
            transition: opacity 0.3s ease;
        }
        
        .get-started-button:hover::before {
            opacity: 1;
        }
        
        .get-started-container {
            display: flex;
            justify-content: center;
            margin-bottom: 3rem;
        }
        
        .insights-container {
            background: rgba(36, 38, 44, 0.92);
            border-radius: 1.2rem;
            padding: 2rem;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(29, 185, 84, 0.1);
            margin-bottom: 2rem;
        }
        
        .insights-title {
            font-size: 1.8rem;
            font-weight: 800;
            color: #1db954;
            margin-bottom: 1.5rem;
            text-align: center;
            position: relative;
        }
        
        .insights-title::after {
            content: '';
            position: absolute;
            bottom: -10px;
            left: 50%;
            transform: translateX(-50%);
            width: 100px;
            height: 3px;
            background: linear-gradient(90deg, #1db954, #a78bfa);
            border-radius: 3px;
        }
        
        .info-icon {
            color: #aeb0b3;
            margin-left: 0.4rem;
            cursor: help;
            font-size: 0.9rem;
        }
        .summary-card-title {
            display: flex;
            align-items: center;
            gap: 0.35rem;
            font-weight: 600;
            color: #d0d0d0;
        }
        .summary-card-overview {
            position: relative; /* allow absolute positioning inside */
        }
        .summary-card-overview .info-icon {
            position: absolute !important;
            bottom: 1rem !important;
            right: 1rem !important;
            left: auto !important;
            top: auto !important;
            margin-left: 0 !important; /* reset previous gap */
            font-size: 0.95rem !important;
            color: #aeb0b3 !important;
            opacity: 0.85;
        }
        /* Optional hover effect */
        .summary-card-overview .info-icon:hover {
            color: #ffffff;
        }
        /* Custom tooltip CSS block removed – rely on global JS tooltip handler */
        """
        
        return ui.TagList(
            ui.tags.style(enhanced_css),
            ui.tags.div(
                # Hero section with animated effects
                ui.tags.div(
                    ui.tags.h1("VOLTATRADE", class_="hero-title"),
                    ui.tags.p("A powerful tool for analyzing stock market volatility patterns, predicting future price movements, and making smarter trading decisions.", class_="hero-subtitle"),
                    class_="hero-container"
                ),
                
                # Feature cards in a responsive grid
                ui.tags.div(
                    ui.tags.div(
                        ui.tags.div(ui.tags.i(class_="fa fa-search"), class_="feature-icon"),
                        ui.tags.h3("Stock Screener", class_="feature-title"),
                        ui.tags.p("Filter and rank stocks by financial statistics. Identify trading opportunities based on volatility patterns and other key metrics.", class_="feature-description"),
                        class_="feature-card"
                    ),
                    ui.tags.div(
                        ui.tags.div(ui.tags.i(class_="fa fa-chart-line"), class_="feature-icon"),
                        ui.tags.h3("Individual Stock Analysis", class_="feature-title"),
                        ui.tags.p("Dive deep into a specific stock's volatility patterns. Analyze historical trends and get AI-powered predictions on future price moves.", class_="feature-description"),
                        class_="feature-card"
                    ),
                    ui.tags.div(
                        ui.tags.div(ui.tags.i(class_="fa fa-balance-scale"), class_="feature-icon"),
                        ui.tags.h3("Stock Comparison", class_="feature-title"),
                        ui.tags.p("Compare volatility metrics between multiple stocks. Understand relative risk profiles and identify the best opportunities for your trading strategy.", class_="feature-description"),
                        class_="feature-card"
                    ),
                    ui.tags.div(
                        ui.tags.div(ui.tags.i(class_="fa fa-wallet"), class_="feature-icon"),
                        ui.tags.h3("Portfolio Tracker", class_="feature-title"),
                        ui.tags.p("Monitor your portfolio's volatility metrics in real-time. Get AI-powered insights on portfolio diversification and optimization strategies.", class_="feature-description"),
                        class_="feature-card"
                    ),
                    class_="feature-card-container"
                ),
                
                # Get Started button with animation
                ui.tags.div(
                    ui.tags.a("GET STARTED - RUN THE MODEL", href="?tab=screener", class_="get-started-button"),
                    class_="get-started-container"
                ),
                
                # Model Insights Panel with enhanced styling
                ui.tags.div(
                    ui.tags.div("Model Insights", class_="insights-title"),
                    ui.tags.div(
                        ui.tags.div("Model Performance", class_="model-section-title"),
                        ui.tags.div(
                            *[
                                ui.tags.div(
                                    ui.tags.div(
                                        ui.tags.div(
                                            [
                                                "Average Forecast Error",
                                                ui.tags.i(class_="fa fa-info-circle info-icon", tabindex="0", **{"data-tooltip": "The average percentage difference between predicted and actual volatility values. A positive value of +9% indicates our model tends to predict slightly higher than actual values, showing a conservative approach to risk assessment. This bias helps ensure we don't underestimate potential market volatility."})
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
                                            [
                                                "Model Confidence",
                                                ui.tags.i(class_="fa fa-info-circle info-icon", tabindex="0", **{"data-tooltip": "Represents the model's certainty in its predictions based on historical data patterns and current market conditions. A 63% confidence level indicates reliable performance, derived from consistent market patterns and stable correlations between stocks. This metric helps users gauge the trustworthiness of predictions in different market scenarios."})
                                            ],
                                            class_="summary-card-title"
                                        ),
                                        ui.tags.div("63%", class_="summary-card-value"),
                                        class_="summary-card-content"
                                    ),
                                    ui.tags.div(ui.tags.i(class_="fa fa-chart-line"), class_="summary-card-icon purple"),
                                    class_="summary-card-overview"
                                ),
                                ui.tags.div(
                                    ui.tags.div(
                                        ui.tags.div(
                                            [
                                                "Root Mean Square Percentage Error",
                                                ui.tags.i(class_="fa fa-info-circle info-icon", tabindex="0", **{"data-tooltip": "A sophisticated accuracy metric that measures the model's prediction precision. The 37% value indicates that our typical prediction error is just over one-third of the actual value. This metric is particularly sensitive to large errors, ensuring our model maintains reliability even during high volatility periods. For financial volatility prediction, values under 40% are considered acceptable performance."})
                                            ],
                                            class_="summary-card-title"
                                        ),
                                        ui.tags.div("37%", class_="summary-card-value"),
                                        class_="summary-card-content"
                                    ),
                                    ui.tags.div(ui.tags.i(class_="fa fa-wave-square"), class_="summary-card-icon blue"),
                                    class_="summary-card-overview"
                                ),
                            ],
                            class_="summary-cards-row-overview"
                        ),
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
                    class_="insights-container"
                ),
                class_="main-content-inner"
            )
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

# Add dashboard/overview UI function
def ui_dashboard():
    """Create a dashboard overview that integrates key information from all modules."""
    
    custom_css = """
    .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        gap: 1.5rem;
        width: 100%;
    }
    
    .dashboard-card {
        background: rgba(36, 38, 44, 0.92);
        border-radius: 1.2rem;
        box-shadow: 0 8px 32px 0 rgba(0,0,0,0.15);
        border: 1px solid rgba(29,185,84,0.15);
        padding: 1.5rem;
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        min-height: 300px;
    }
    
    .dashboard-card:hover {
        transform: translateY(-5px);
        border-color: rgba(29,185,84,0.3);
        box-shadow: 0 15px 40px 0 rgba(29,185,84,0.15);
    }
    
    .dashboard-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.2rem;
        padding-bottom: 0.8rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    
    .dashboard-icon {
        font-size: 1.8rem;
        color: #1db954;
        width: 3rem;
        height: 3rem;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(29,185,84,0.1);
        border-radius: 50%;
    }
    
    .dashboard-title {
        font-size: 1.3rem;
        font-weight: 800;
        color: #1db954;
        margin: 0;
    }
    
    .dashboard-content {
        flex: 1;
        display: flex;
        flex-direction: column;
    }
    
    .dashboard-summary {
        margin-bottom: 1rem;
        color: #e0e0e0;
        line-height: 1.5;
    }
    
    .dashboard-metrics {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.8rem;
        margin-bottom: 1rem;
    }
    
    .dashboard-metric {
        background: rgba(36, 38, 44, 0.5);
        border-radius: 0.8rem;
        padding: 0.8rem;
        border: 1px solid rgba(167, 139, 250, 0.1);
    }
    
    .metric-label {
        font-size: 0.8rem;
        color: #a78bfa;
        margin-bottom: 0.3rem;
    }
    
    .metric-value {
        font-size: 1.2rem;
        font-weight: 700;
        color: #fff;
    }
    
    .dashboard-actions {
        margin-top: auto;
        display: flex;
        justify-content: flex-end;
    }
    
    .dashboard-btn {
        background: linear-gradient(90deg, #1db954 0%, #a78bfa 100%);
        border: none;
        color: white;
        padding: 0.6rem 1rem;
        border-radius: 0.8rem;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.3s ease;
        text-decoration: none;
    }
    
    .dashboard-btn:hover {
        opacity: 0.9;
        transform: translateY(-2px);
    }
    """
    
    return ui.TagList(
        ui.tags.style(custom_css),
        ui.tags.div(
            ui.tags.h1("VoltaTrade Dashboard", 
                     style="color:#1db954;font-size:2rem;margin-bottom:1.5rem;"),
            
            ui.tags.div(
                # Stock Screener Card
                ui.tags.div(
                    ui.tags.div(
                        ui.tags.div(icon_svg("magnifying-glass"), class_="dashboard-icon"),
                        ui.h3("Stock Screener", class_="dashboard-title"),
                        class_="dashboard-header"
                    ),
                    ui.tags.div(
                        ui.tags.p("Find top-performing stocks based on financial metrics and volatility patterns.", 
                                class_="dashboard-summary"),
                        ui.tags.div(
                            ui.tags.div(
                                ui.tags.div("Top Stock", class_="metric-label"),
                                ui.tags.div("70", class_="metric-value"),
                                class_="dashboard-metric"
                            ),
                            ui.tags.div(
                                ui.tags.div("Avg Mid Price", class_="metric-label"),
                                ui.tags.div("1.000127", class_="metric-value"),
                                class_="dashboard-metric"
                            ),
                            class_="dashboard-metrics"
                        ),
                        ui.tags.div(
                            ui.tags.a("Go to Stock Screener", href="?tab=screener", class_="dashboard-btn"),
                            class_="dashboard-actions"
                        ),
                        class_="dashboard-content"
                    ),
                    class_="dashboard-card"
                ),
                
                # Individual Stock Analysis Card
                ui.tags.div(
                    ui.tags.div(
                        ui.tags.div(icon_svg("chart-line"), class_="dashboard-icon"),
                        ui.h3("Individual Stock Analysis", class_="dashboard-title"),
                        class_="dashboard-header"
                    ),
                    ui.tags.div(
                        ui.tags.p("Detailed volatility analysis and prediction for individual stocks.", 
                                class_="dashboard-summary"),
                        ui.tags.div(
                            ui.tags.div(
                                ui.tags.div("Featured Stock", class_="metric-label"),
                                ui.tags.div("1", class_="metric-value"),
                                class_="dashboard-metric"
                            ),
                            ui.tags.div(
                                ui.tags.div("Predicted Volatility", class_="metric-label"),
                                ui.tags.div("0.001950", class_="metric-value"),
                                class_="dashboard-metric"
                            ),
                            class_="dashboard-metrics"
                        ),
                        ui.tags.div(
                            ui.tags.a("Analyze Stock", href="?tab=individual", class_="dashboard-btn"),
                            class_="dashboard-actions"
                        ),
                        class_="dashboard-content"
                    ),
                    class_="dashboard-card"
                ),
                
                # Stock Comparison Card
                ui.tags.div(
                    ui.tags.div(
                        ui.tags.div(icon_svg("scale-balanced"), class_="dashboard-icon"),
                        ui.h3("Stock Comparison", class_="dashboard-title"),
                        class_="dashboard-header"
                    ),
                    ui.tags.div(
                        ui.tags.p("Compare volatility patterns and financial metrics across multiple stocks.", 
                                class_="dashboard-summary"),
                        ui.tags.div(
                            ui.tags.div(
                                ui.tags.div("Stable Stock", class_="metric-label"),
                                ui.tags.div("Stock 1", class_="metric-value"),
                                class_="dashboard-metric"
                            ),
                            ui.tags.div(
                                ui.tags.div("Model Accuracy", class_="metric-label"),
                                ui.tags.div("-42.68%", class_="metric-value"),
                                class_="dashboard-metric"
                            ),
                            class_="dashboard-metrics"
                        ),
                        ui.tags.div(
                            ui.tags.a("Compare Stocks", href="?tab=comparison", class_="dashboard-btn"),
                            class_="dashboard-actions"
                        ),
                        class_="dashboard-content"
                    ),
                    class_="dashboard-card"
                ),
                
                # Portfolio Tracker Card
                ui.tags.div(
                    ui.tags.div(
                        ui.tags.div(icon_svg("wallet"), class_="dashboard-icon"),
                        ui.h3("Portfolio Tracker", class_="dashboard-title"),
                        class_="dashboard-header"
                    ),
                    ui.tags.div(
                        ui.tags.p("Track your stock portfolio with volatility predictions and diversification metrics.", 
                                class_="dashboard-summary"),
                        ui.tags.div(
                            ui.tags.div(
                                ui.tags.div("Portfolio Value", class_="metric-label"),
                                ui.tags.div("$82.00", class_="metric-value"),
                                class_="dashboard-metric"
                            ),
                            ui.tags.div(
                                ui.tags.div("Daily Swing", class_="metric-label"),
                                ui.tags.div("±$0.10", class_="metric-value"),
                                class_="dashboard-metric"
                            ),
                            class_="dashboard-metrics"
                        ),
                        ui.tags.div(
                            ui.tags.a("Manage Portfolio", href="?tab=portfolio", class_="dashboard-btn"),
                            class_="dashboard-actions"
                        ),
                        class_="dashboard-content"
                    ),
                    class_="dashboard-card"
                ),
                
                class_="dashboard-grid"
            ),
            style="padding: 2rem; max-width: 1400px; margin: 0 auto;"
        )
    )

here = os.path.dirname(__file__)
www_path = os.path.join(here, "www")
app = App(
        app_ui,
        server, 
        static_assets=www_path
    )

if __name__ == "__main__":
    app.run(port=8002)