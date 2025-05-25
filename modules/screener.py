import os
import pandas as pd
from shiny import ui, render, reactive
from faicons import icon_svg
from modules.common_style import get_common_css
from modules.visual_effects import get_effects_css
import matplotlib.pyplot as plt

# --- Data loading and setup ---
_project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
VOL_PATH = os.path.join(_project_dir, 'data', 'vol_df.csv')
METRICS_PATH = os.path.join(_project_dir, 'data', 'metrics_summary.csv')
PRED_VOL_PATH = os.path.join(_project_dir, 'data', 'predicted_realized_vol.csv')

# Load volatility data
try:
    vol_df = pd.read_csv(VOL_PATH)
    stock_cols = [c for c in vol_df.columns if c != 'time_id']
    min_time = int(vol_df['time_id'].min())
    max_time = int(vol_df['time_id'].max())
except Exception:
    vol_df = pd.DataFrame()
    stock_cols = []
    min_time = 0
    max_time = 100

# Load metrics summary data
try:
    metrics_df = pd.read_csv(METRICS_PATH)
    metrics_df['stock_id'] = metrics_df['stock_id'].astype(int)
    # Get all metric columns except stock_id and realized_volatility
    metric_cols = [c for c in metrics_df.columns if c not in ('stock_id', 'realized_volatility')]
except Exception:
    metrics_df = pd.DataFrame()
    metric_cols = []

# Load predicted volatility
try:
    pred_vol_df = pd.read_csv(PRED_VOL_PATH)
    pred_vol_df['stock_id'] = pred_vol_df['stock_id'].astype(int)
    # Add predicted_realized_vol to metrics_df
    metrics_df = metrics_df.merge(
        pred_vol_df[['stock_id', 'predicted_realized_vol']],
        on='stock_id', how='left'
    )
    if 'predicted_realized_vol' not in metric_cols:
        metric_cols.append('predicted_realized_vol')
except Exception:
    print("Warning: Could not load predicted volatility data")

# Human-readable labels for metrics
metric_labels = {c: c.replace('_', ' ').title() for c in metric_cols}
if 'predicted_realized_vol' in metric_labels:
    metric_labels['predicted_realized_vol'] = 'Predicted Realized Volatility'
if 'avg_bid_size1' in metric_labels:
    metric_labels['avg_bid_size1'] = 'Avg Bid Size1'

# Add 'Volatility' to available metrics
metric_labels_with_vol = {'volatility': 'Volatility', **metric_labels}

# Explanations for metrics
metric_explanations = {
    'volatility': 'Realized volatility over the selected time range.',
    'avg_mid_price': 'Average of the mid price (mean of bid and ask) for the stock.',
    'total_return': 'Total return over the selected period.',
    'avg_spread': 'Average bid-ask spread.',
    'avg_bid_size1': 'Average size of the best bid.',
    'avg_ask_size1': 'Average size of the best ask.',
    'order_imbalance': 'Order imbalance between buy and sell orders.',
    'vwap': 'Volume-weighted average price.',
    'predicted_realized_vol': 'Model prediction of future realized volatility.'
}

__all__ = [
    'ui_screener',
    'server_screener',
    'vol_df',
    'stock_cols',
]

def ui_screener():
    """Stock Screener UI with sidebar controls."""
    custom_css = get_common_css() + get_effects_css() + """
    .screener-sidebar {
        padding: 1.5rem;
        background: rgba(36, 38, 44, 0.95);
        border-radius: 1.2rem;
        margin-bottom: 1rem;
    }
    .section-title {
        color: #a78bfa;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
        text-transform: uppercase;
    }
    .stat-checkbox {
        margin-bottom: 0.5rem;
    }
    .stat-checkbox label {
        color: #1db954;
        font-weight: 500;
    }
    .stat-checkbox input[type="checkbox"] {
        margin-right: 0.5rem;
    }
    .slider-label {
        color: #1db954;
        margin-bottom: 0.5rem;
        font-weight: 500;
    }
    /* --- Financial Statistics checkbox group enhancements --- */
    .financial-stats-box {
        background: rgba(36, 38, 44, 0.6);
        border: 1.5px solid rgba(167, 139, 250, 0.25);
        border-radius: 1rem;
        padding: 1rem 1.25rem;
        box-shadow: 0 6px 18px rgba(29, 185, 84, 0.12);
        backdrop-filter: blur(4px);
        margin-top: 0.5rem;
    }
    .financial-stats-box .shiny-input-checkboxgroup {
        display: flex;
        flex-direction: column;
        gap: 0.65rem;
    }
    .financial-stats-box .form-check {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    .financial-stats-box .form-check-input {
        appearance: none;
        -webkit-appearance: none;
        width: 1.15rem;
        height: 1.15rem;
        border: 2px solid #a78bfa;
        border-radius: 0.35rem;
        background: rgba(167, 139, 250, 0.08);
        position: relative;
        cursor: pointer;
        transition: all 0.25s ease;
    }
    .financial-stats-box .form-check-input:hover {
        box-shadow: 0 0 0 3px rgba(167, 139, 250, 0.3);
    }
    .financial-stats-box .form-check-input:checked {
        background: linear-gradient(135deg, #1db954 0%, #a78bfa 100%);
        border-color: #1db954;
    }
    .financial-stats-box .form-check-input:checked::after {
        content: '\\f00c';
        font-family: 'Font Awesome 6 Free';
        font-weight: 900;
        color: #ffffff;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -55%);
        font-size: 0.65rem;
    }
    .financial-stats-box .form-check-label {
        color: #bdbdfd;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.02em;
        cursor: pointer;
        transition: color 0.25s ease;
    }
    .financial-stats-box .form-check-input:checked + .form-check-label {
        color: #ffffff;
    }
    """
    
    return ui.TagList(
        ui.tags.style(custom_css),
        ui.tags.div(
            ui.tags.div(
                # Logo and title
                ui.tags.div(
                    ui.tags.div(ui.tags.i(class_="fa fa-search"), class_="module-icon"),
                    ui.h2("VOLTATRADE", class_="animated-gradient-text"),
                    ui.p("Filter and rank stocks by financial statistics.", class_="module-subtitle"),
                    class_="module-header"
                ),
                
                # Time Range Section
                ui.tags.div(
                    ui.h4("TIME RANGE", class_="section-title"),
                    ui.tags.div(
                        ui.tags.label("TIME ID RANGE (FOR VOLATILITY):", class_="slider-label"),
                        ui.input_slider(
                            "vol_time_range", "",
                            min=min_time, max=max_time,
                            value=[min_time, max_time]
                        ),
                        class_="module-input"
                    ),
                    class_="screener-sidebar"
                ),
                
                # Financial Statistics Section
                ui.tags.div(
                    ui.h4("FINANCIAL STATISTICS", class_="section-title"),
                    ui.tags.div(
                        ui.tags.label("SELECT FINANCIAL STATISTICS", class_="slider-label"),
                        ui.tags.div(
                            ui.input_checkbox_group(
                                "selected_stats",
                                "",
                                choices=metric_labels_with_vol,
                                selected=[]
                            ),
                            class_="financial-stats-box"
                        ),
                        class_="module-input"
                    ),
                    class_="screener-sidebar"
                ),
                
                # Top N Section
                ui.tags.div(
                    ui.h4("TOP N", class_="section-title"),
                    ui.tags.div(
                        ui.tags.label("TOP N STOCKS:", class_="slider-label"),
                        ui.input_slider(
                            "top_n", "",
                            min=1, max=len(stock_cols),
                            value=10
                        ),
                        class_="module-input"
                    ),
                    class_="screener-sidebar"
                ),
                
                # Get Started button with animation
                ui.tags.div(
                    ui.tags.a("GET STARTED - RUN THE MODEL", href="?tab=screener", class_="get-started-button"),
                    class_="get-started-container"
                ),
                
                class_="sidebar-card"
            ),
            # --- Main content area ---
            ui.tags.div(
                # Filtered Results card
                ui.tags.div(
                    ui.tags.div(
                        ui.tags.i(class_="fa fa-table header-icon"),
                        ui.tags.h3("Filtered Results", class_="card-title"),
                        style="display:flex;align-items:center;gap:10px;"
                    ),
                    ui.output_data_frame("screener_results"),
                    class_="content-card"
                ),
                # Visualization card
                ui.tags.div(
                    ui.tags.div(
                        ui.tags.i(class_="fa fa-chart-column header-icon"),
                        ui.tags.h3("Visualization", class_="card-title"),
                        style="display:flex;align-items:center;gap:10px;"
                    ),
                    ui.output_plot("screener_plot"),
                    # Add explanatory card for financial statistics
                    ui.tags.div(
                        ui.tags.div(
                            ui.tags.i(class_="fa fa-book-open", style="color: #1db954; margin-right: 10px;"),
                            "Financial Statistics Explained",
                            class_="stats-title",
                            style="""
                                font-size: 1.5rem;
                                font-weight: 800;
                                background: linear-gradient(90deg, #1db954, #a78bfa);
                                -webkit-background-clip: text;
                                -webkit-text-fill-color: transparent;
                                text-align: center;
                                margin-bottom: 1.5rem;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                padding: 10px;
                                border-bottom: 2px solid rgba(167, 139, 250, 0.2);
                            """
                        ),
                        ui.tags.div(
                            ui.tags.div(
                                ui.tags.div(
                                    ui.tags.div(
                                        ui.tags.i(class_="fa fa-chart-line", style="color: #1db954; font-size: 1.4rem;"),
                                        style="""
                                            background: rgba(29, 185, 84, 0.1);
                                            padding: 12px;
                                            border-radius: 12px;
                                            margin-right: 15px;
                                            transition: all 0.3s ease;
                                        """
                                    ),
                                    ui.tags.div(
                                        ui.tags.span("Volatility", style="font-weight: bold; color: #1db954; font-size: 1.1rem; display: block; margin-bottom: 6px;"),
                                        ui.tags.p(
                                            "Measures the degree of variation in a stock's price over time. Higher volatility indicates greater price fluctuations and potentially higher risk/reward.",
                                            style="margin: 0; color: #e0e0e0; line-height: 1.5;"
                                        ),
                                        style="flex: 1;"
                                    ),
                                    style="""
                                        display: flex;
                                        align-items: flex-start;
                                        padding: 15px;
                                        background: rgba(36, 38, 44, 0.6);
                                        border-radius: 16px;
                                        margin-bottom: 16px;
                                        border: 1px solid rgba(29, 185, 84, 0.1);
                                        transition: all 0.3s ease;
                                        cursor: pointer;
                                    """,
                                    class_="stat-item"
                                ),
                                # Repeat similar structure for other statistics with different icons and colors
                                ui.tags.div(
                                    ui.tags.div(
                                        ui.tags.i(class_="fa fa-dollar-sign", style="color: #1db954; font-size: 1.4rem;"),
                                        style="""
                                            background: rgba(29, 185, 84, 0.1);
                                            padding: 12px;
                                            border-radius: 12px;
                                            margin-right: 15px;
                                            transition: all 0.3s ease;
                                        """
                                    ),
                                    ui.tags.div(
                                        ui.tags.span("Average Mid Price", style="font-weight: bold; color: #1db954; font-size: 1.1rem; display: block; margin-bottom: 6px;"),
                                        ui.tags.p(
                                            "The average price between the best bid and ask prices. Represents a fair market value for the stock.",
                                            style="margin: 0; color: #e0e0e0; line-height: 1.5;"
                                        ),
                                        style="flex: 1;"
                                    ),
                                    style="""
                                        display: flex;
                                        align-items: flex-start;
                                        padding: 15px;
                                        background: rgba(36, 38, 44, 0.6);
                                        border-radius: 16px;
                                        margin-bottom: 16px;
                                        border: 1px solid rgba(29, 185, 84, 0.1);
                                        transition: all 0.3s ease;
                                        cursor: pointer;
                                    """,
                                    class_="stat-item"
                                ),
                                # Add similar blocks for other statistics...
                                ui.tags.div(
                                    ui.tags.div(
                                        ui.tags.i(class_="fa fa-chart-area", style="color: #1db954; font-size: 1.4rem;"),
                                        style="""
                                            background: rgba(29, 185, 84, 0.1);
                                            padding: 12px;
                                            border-radius: 12px;
                                            margin-right: 15px;
                                            transition: all 0.3s ease;
                                        """
                                    ),
                                    ui.tags.div(
                                        ui.tags.span("Total Return", style="font-weight: bold; color: #1db954; font-size: 1.1rem; display: block; margin-bottom: 6px;"),
                                        ui.tags.p(
                                            "The total percentage gain or loss in stock value over the selected time period, including both price changes and any distributions.",
                                            style="margin: 0; color: #e0e0e0; line-height: 1.5;"
                                        ),
                                        style="flex: 1;"
                                    ),
                                    style="""
                                        display: flex;
                                        align-items: flex-start;
                                        padding: 15px;
                                        background: rgba(36, 38, 44, 0.6);
                                        border-radius: 16px;
                                        margin-bottom: 16px;
                                        border: 1px solid rgba(29, 185, 84, 0.1);
                                        transition: all 0.3s ease;
                                        cursor: pointer;
                                    """,
                                    class_="stat-item"
                                ),
                                ui.tags.div(
                                    ui.tags.div(
                                        ui.tags.i(class_="fa fa-arrows-left-right", style="color: #1db954; font-size: 1.4rem;"),
                                        style="""
                                            background: rgba(29, 185, 84, 0.1);
                                            padding: 12px;
                                            border-radius: 12px;
                                            margin-right: 15px;
                                            transition: all 0.3s ease;
                                        """
                                    ),
                                    ui.tags.div(
                                        ui.tags.span("Average Spread", style="font-weight: bold; color: #1db954; font-size: 1.1rem; display: block; margin-bottom: 6px;"),
                                        ui.tags.p(
                                            "The average difference between the best bid and ask prices. A wider spread typically indicates lower liquidity and higher trading costs.",
                                            style="margin: 0; color: #e0e0e0; line-height: 1.5;"
                                        ),
                                        style="flex: 1;"
                                    ),
                                    style="""
                                        display: flex;
                                        align-items: flex-start;
                                        padding: 15px;
                                        background: rgba(36, 38, 44, 0.6);
                                        border-radius: 16px;
                                        margin-bottom: 16px;
                                        border: 1px solid rgba(29, 185, 84, 0.1);
                                        transition: all 0.3s ease;
                                        cursor: pointer;
                                    """,
                                    class_="stat-item"
                                ),
                                ui.tags.div(
                                    ui.tags.div(
                                        ui.tags.i(class_="fa fa-layer-group", style="color: #1db954; font-size: 1.4rem;"),
                                        style="""
                                            background: rgba(29, 185, 84, 0.1);
                                            padding: 12px;
                                            border-radius: 12px;
                                            margin-right: 15px;
                                            transition: all 0.3s ease;
                                        """
                                    ),
                                    ui.tags.div(
                                        ui.tags.span("Average Bid Size1", style="font-weight: bold; color: #1db954; font-size: 1.1rem; display: block; margin-bottom: 6px;"),
                                        ui.tags.p(
                                            "The average size of the best (highest) bid order. Indicates the buying interest at the best bid price level.",
                                            style="margin: 0; color: #e0e0e0; line-height: 1.5;"
                                        ),
                                        style="flex: 1;"
                                    ),
                                    style="""
                                        display: flex;
                                        align-items: flex-start;
                                        padding: 15px;
                                        background: rgba(36, 38, 44, 0.6);
                                        border-radius: 16px;
                                        margin-bottom: 16px;
                                        border: 1px solid rgba(29, 185, 84, 0.1);
                                        transition: all 0.3s ease;
                                        cursor: pointer;
                                    """,
                                    class_="stat-item"
                                ),
                                ui.tags.div(
                                    ui.tags.div(
                                        ui.tags.i(class_="fa fa-layer-group", style="color: #1db954; font-size: 1.4rem;"),
                                        style="""
                                            background: rgba(29, 185, 84, 0.1);
                                            padding: 12px;
                                            border-radius: 12px;
                                            margin-right: 15px;
                                            transition: all 0.3s ease;
                                        """
                                    ),
                                    ui.tags.div(
                                        ui.tags.span("Average Ask Size1", style="font-weight: bold; color: #1db954; font-size: 1.1rem; display: block; margin-bottom: 6px;"),
                                        ui.tags.p(
                                            "The average size of the best (lowest) ask order. Indicates the selling interest at the best ask price level.",
                                            style="margin: 0; color: #e0e0e0; line-height: 1.5;"
                                        ),
                                        style="flex: 1;"
                                    ),
                                    style="""
                                        display: flex;
                                        align-items: flex-start;
                                        padding: 15px;
                                        background: rgba(36, 38, 44, 0.6);
                                        border-radius: 16px;
                                        margin-bottom: 16px;
                                        border: 1px solid rgba(29, 185, 84, 0.1);
                                        transition: all 0.3s ease;
                                        cursor: pointer;
                                    """,
                                    class_="stat-item"
                                ),
                                ui.tags.div(
                                    ui.tags.div(
                                        ui.tags.i(class_="fa fa-scale-balanced", style="color: #1db954; font-size: 1.4rem;"),
                                        style="""
                                            background: rgba(29, 185, 84, 0.1);
                                            padding: 12px;
                                            border-radius: 12px;
                                            margin-right: 15px;
                                            transition: all 0.3s ease;
                                        """
                                    ),
                                    ui.tags.div(
                                        ui.tags.span("Order Imbalance", style="font-weight: bold; color: #1db954; font-size: 1.1rem; display: block; margin-bottom: 6px;"),
                                        ui.tags.p(
                                            "The difference between buying and selling pressure in the order book. A positive value indicates more buying pressure, while negative indicates more selling pressure.",
                                            style="margin: 0; color: #e0e0e0; line-height: 1.5;"
                                        ),
                                        style="flex: 1;"
                                    ),
                                    style="""
                                        display: flex;
                                        align-items: flex-start;
                                        padding: 15px;
                                        background: rgba(36, 38, 44, 0.6);
                                        border-radius: 16px;
                                        margin-bottom: 16px;
                                        border: 1px solid rgba(29, 185, 84, 0.1);
                                        transition: all 0.3s ease;
                                        cursor: pointer;
                                    """,
                                    class_="stat-item"
                                ),
                                ui.tags.div(
                                    ui.tags.div(
                                        ui.tags.i(class_="fa fa-chart-simple", style="color: #1db954; font-size: 1.4rem;"),
                                        style="""
                                            background: rgba(29, 185, 84, 0.1);
                                            padding: 12px;
                                            border-radius: 12px;
                                            margin-right: 15px;
                                            transition: all 0.3s ease;
                                        """
                                    ),
                                    ui.tags.div(
                                        ui.tags.span("VWAP", style="font-weight: bold; color: #1db954; font-size: 1.1rem; display: block; margin-bottom: 6px;"),
                                        ui.tags.p(
                                            "Volume-Weighted Average Price. A trading benchmark that shows the average price a stock has traded at throughout the day, weighted by volume. Used to assess if trades are executed at favorable prices.",
                                            style="margin: 0; color: #e0e0e0; line-height: 1.5;"
                                        ),
                                        style="flex: 1;"
                                    ),
                                    style="""
                                        display: flex;
                                        align-items: flex-start;
                                        padding: 15px;
                                        background: rgba(36, 38, 44, 0.6);
                                        border-radius: 16px;
                                        margin-bottom: 16px;
                                        border: 1px solid rgba(29, 185, 84, 0.1);
                                        transition: all 0.3s ease;
                                        cursor: pointer;
                                    """,
                                    class_="stat-item"
                                ),
                                ui.tags.div(
                                    ui.tags.div(
                                        ui.tags.i(class_="fa fa-robot", style="color: #1db954; font-size: 1.4rem;"),
                                        style="""
                                            background: rgba(29, 185, 84, 0.1);
                                            padding: 12px;
                                            border-radius: 12px;
                                            margin-right: 15px;
                                            transition: all 0.3s ease;
                                        """
                                    ),
                                    ui.tags.div(
                                        ui.tags.span("Predicted Realized Volatility", style="font-weight: bold; color: #1db954; font-size: 1.1rem; display: block; margin-bottom: 6px;"),
                                        ui.tags.p(
                                            "Model's prediction of future realized volatility. This forward-looking metric helps anticipate potential price movement magnitudes based on historical patterns and market conditions.",
                                            style="margin: 0; color: #e0e0e0; line-height: 1.5;"
                                        ),
                                        style="flex: 1;"
                                    ),
                                    style="""
                                        display: flex;
                                        align-items: flex-start;
                                        padding: 15px;
                                        background: rgba(36, 38, 44, 0.6);
                                        border-radius: 16px;
                                        margin-bottom: 16px;
                                        border: 1px solid rgba(29, 185, 84, 0.1);
                                        transition: all 0.3s ease;
                                        cursor: pointer;
                                    """,
                                    class_="stat-item"
                                ),
                                style="""
                                    display: grid;
                                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                                    gap: 20px;
                                    padding: 20px;
                                """
                            ),
                            class_="content-card hover-card",
                            style="""
                                background: rgba(36, 38, 44, 0.95);
                                border-radius: 16px;
                                margin-top: 20px;
                                border: 1px solid rgba(29, 185, 84, 0.1);
                                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
                            """
                        ),
                        # Add custom CSS for hover effects and animations
                        ui.tags.style("""
                            .stat-item:hover {
                                transform: translateY(-5px);
                                box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
                                border-color: rgba(29, 185, 84, 0.3);
                                background: rgba(36, 38, 44, 0.8);
                            }
                            .stat-item:hover i {
                                transform: scale(1.1);
                                background: rgba(29, 185, 84, 0.2);
                            }
                            @keyframes fadeInUp {
                                from {
                                    opacity: 0;
                                    transform: translateY(20px);
                                }
                                to {
                                    opacity: 1;
                                    transform: translateY(0);
                                }
                            }
                            .stat-item {
                                animation: fadeInUp 0.5s ease-out forwards;
                                animation-delay: calc(var(--animation-order) * 0.1s);
                            }
                        """),
                        class_="stats-explained-section"
                    ),
                    class_="content-card"
                ),
                class_="main-content"
            ),
            class_="module-layout"
        )
    )

def server_screener(input, output, session):
    """Server logic for the stock screener."""
    @reactive.Calc
    def filtered_metrics():
        selected = list(input.selected_stats())
        if not selected:
            return pd.DataFrame()

        n = input.top_n()
        result_df = None

        # If volatility is selected, compute it from vol_df over the selected time range
        if 'volatility' in selected:
            start_time, end_time = input.vol_time_range()
            subset = vol_df[(vol_df['time_id'] >= start_time) & (vol_df['time_id'] <= end_time)]
            df_long = subset.melt(id_vars=['time_id'], value_vars=stock_cols, var_name='stock_id', value_name='volatility')
            df_long['stock_id'] = df_long['stock_id'].astype(int)
            vol_mean = df_long.groupby('stock_id')['volatility'].mean().reset_index()
            vol_mean['volatility'] = vol_mean['volatility'].astype(float)
            result_df = vol_mean.rename(columns={'volatility': 'Volatility'})
            
            # Get other selected metrics from metrics_df
            sel_no_vol = [m for m in selected if m != 'volatility']
            if sel_no_vol:
                metrics_part = metrics_df[['stock_id'] + sel_no_vol]
                result_df = pd.merge(result_df, metrics_part, on='stock_id', how='left')
        else:
            # Only metrics from metrics_df
            result_df = metrics_df[['stock_id'] + selected]

        # Sort by the first selected metric
        sort_col = 'Volatility' if selected[0] == 'volatility' else selected[0]
        result_df = result_df.sort_values(sort_col, ascending=False).head(n)

        # Rename columns for display
        col_map = {'stock_id': 'Stock ID'}
        for m in selected:
            if m == 'volatility':
                col_map['Volatility'] = 'Volatility'
            else:
                col_map[m] = metric_labels[m]
        result_df = result_df.rename(columns=col_map)
        
        # Round numeric columns
        for col in result_df.columns:
            if col != 'Stock ID':
                result_df[col] = result_df[col].round(6)
                
        return result_df

    @output
    @render.data_frame
    def screener_results():
        return filtered_metrics()

    @output
    @render.plot
    def screener_plot():
        df = filtered_metrics()
        if df.empty:
            fig, ax = plt.subplots(figsize=(6, 4))
            fig.patch.set_facecolor('#23272f')
            ax.set_facecolor('#23272f')
            ax.text(0.5, 0.5, "No data available", ha='center', va='center', color='#a78bfa', fontsize=12)
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)
            return fig
        metric_cols = [c for c in df.columns if c != 'Stock ID']
        if not metric_cols:
            return None
        metric = metric_cols[0]
        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor('#23272f')
        ax.set_facecolor('#23272f')
        bars = ax.bar(df['Stock ID'].astype(str), df[metric], color='#1db954')
        ax.set_xlabel('Stock ID', color='white', fontsize=10)
        ax.set_ylabel(metric, color='white', fontsize=10)
        ax.set_title(f"Top {len(df)} Stocks by {metric}", fontsize=12, fontweight='bold', color='#1db954')
        ax.tick_params(axis='x', colors='#a78bfa', labelsize=8)
        ax.tick_params(axis='y', colors='#a78bfa', labelsize=8)
        ax.grid(True, alpha=0.2, color='#a78bfa', linestyle='--')
        for spine in ax.spines.values():
            spine.set_color('#444')
        plt.tight_layout()
        return fig
