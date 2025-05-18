import os
import pandas as pd
import matplotlib.pyplot as plt
from shiny import ui, render, reactive
from faicons import icon_svg

# ——————————————————————————————————————————————————————————————————————————
# Load your metrics_summary.csv at module load
# ——————————————————————————————————————————————————————————————————————————
_project_dir   = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
METRICS_PATH   = os.path.join(_project_dir, 'data', 'metrics_summary.csv')
metrics_df     = pd.read_csv(METRICS_PATH)
metrics_df['stock_id'] = metrics_df['stock_id'].astype(int)

# all of the metric columns (except stock_id) available to select
metric_choices = [c for c in metrics_df.columns if c not in ('stock_id', 'realized_volatility')]
if 'predicted_volatility' not in metric_choices:
    metric_choices.append('predicted_volatility')

# Load predicted volatility and merge
PRED_VOL_PATH = os.path.join(_project_dir, 'data', 'predicted_realized_vol.csv')
if os.path.exists(PRED_VOL_PATH):
    pred_vol_df = pd.read_csv(PRED_VOL_PATH)
    pred_vol_df['stock_id'] = pred_vol_df['stock_id'].astype(int)
    metrics_df = metrics_df.merge(
        pred_vol_df[['stock_id', 'predicted_realized_vol']],
        on='stock_id', how='left'
    )
    metrics_df['predicted_volatility'] = metrics_df['predicted_realized_vol']
else:
    metrics_df['predicted_volatility'] = 0

# Human-readable labels for metrics
metric_labels = {c: c.replace('_', ' ').title() for c in metric_choices}
metric_labels['predicted_volatility'] = 'Predicted Volatility'
if 'avg_bid_size1' in metric_labels:
    metric_labels['avg_bid_size1'] = 'Avg Bid Size1'
# Add 'Volatility' to metric_labels for selection
metric_labels_with_vol = {'volatility': 'Volatility', **metric_labels}

VOL_PATH = os.path.join(_project_dir, 'data', 'vol_df.csv')
vol_df = pd.read_csv(VOL_PATH)
stock_cols = [c for c in vol_df.columns if c != 'time_id']
min_time = int(vol_df['time_id'].min())
max_time = int(vol_df['time_id'].max())

def ui_screener():
    custom_css = """
    .screener-layout { display: flex; flex-direction: row; gap: 2.5rem; width: 100%; }
    .screener-sidebar-card {
        background: rgba(36, 38, 44, 0.72);
        backdrop-filter: blur(14px) saturate(1.2);
        border-radius: 2rem;
        box-shadow: 0 4px 18px 0 rgba(29,185,84,0.10);
        border: 2.5px solid;
        border-image: linear-gradient(120deg, #1db954 60%, #a78bfa 100%) 1;
        padding: 2.7rem 2rem 2.7rem 2rem;
        max-width: 350px;
        margin: 2.5rem 0 2.5rem 2.5rem;
        color: #fff;
        font-family: 'Inter', 'Roboto', sans-serif;
        position: relative;
        overflow: visible;
        transition: box-shadow 0.3s, border 0.3s, background 0.5s;
        display: flex;
        flex-direction: column;
        align-items: stretch;
        justify-content: flex-start;
    }
    .screener-sidebar-card .screener-icon {
        display: flex; align-items: center; justify-content: center;
        background: linear-gradient(135deg, #1db954 60%, #a78bfa 100%);
        border-radius: 50%;
        padding: 1.2rem;
        font-size: 3.2rem;
        box-shadow: 0 2px 8px #1db95433;
        width: 4.2rem; height: 4.2rem;
        margin: 0 auto 1.5rem auto;
        /* No glow animation */
    }
    .screener-sidebar-card h2 {
        font-weight: 1000;
        font-size: 2.1rem;
        margin-bottom: 0.5rem;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        background: linear-gradient(90deg, #1db954 60%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        text-shadow: 0 0 16px #1db95444, 0 0 32px #a78bfa44;
    }
    .screener-sidebar-card .screener-subtitle {
        color: #fff;
        font-size: 1.13rem;
        font-weight: 500;
        text-align: center;
        margin-bottom: 2.1rem;
        opacity: 0.88;
    }
    .screener-sidebar-card label, .screener-sidebar-card h4 {
        color: #1db954 !important;
        font-weight: 900;
        font-size: 1.08rem;
        letter-spacing: 0.01em;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 8px #1db95433;
    }
    .screener-sidebar-card h4 {
        margin-top: 1.7rem;
        margin-bottom: 1.1rem;
        font-size: 1.13rem;
        background: linear-gradient(90deg, #1db954 60%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-transform: uppercase;
    }
    .screener-metric-box {
        background: rgba(44, 48, 56, 0.92);
        border-radius: 1.2rem;
        box-shadow: 0 1px 8px #1db95411;
        padding: 1.2rem 1.3rem 1.2rem 1.3rem;
        margin-bottom: 1.2rem;
        display: flex;
        flex-direction: column;
        gap: 0.7rem;
    }
    .screener-sidebar-card .metric-checkbox-group label {
        display: flex;
        align-items: center;
        font-weight: 700;
        font-size: 1.09rem;
        border-radius: 2rem;
        padding: 0.32rem 1.2rem 0.32rem 1.2rem;
        margin-bottom: 0.18rem;
        margin-top: 0.08rem;
        background: rgba(36, 38, 44, 0.65);
        color: #1db954;
        box-shadow: 0 1px 4px #1db95411;
        letter-spacing: 0.01em;
        border: 1.5px solid #23272f;
        transition: background 0.16s, color 0.16s, border 0.16s, font-weight 0.16s;
        cursor: pointer;
        min-height: 2.1rem;
        min-width: 0;
        user-select: none;
    }
    .screener-sidebar-card .metric-checkbox-group input[type="checkbox"]:checked + label {
        background: #1db95422;
        color: #1db954 !important;
        font-weight: 900;
        border: 1.5px solid #1db954;
        box-shadow: none;
    }
    .screener-sidebar-card .metric-checkbox-group label:hover {
        background: #23272f;
        color: #a78bfa !important;
        border: 1.5px solid #a78bfa;
    }
    .screener-sidebar-card .metric-checkbox-group input[type="checkbox"] {
        accent-color: #1db954;
        border-radius: 50%;
        width: 1.2rem; height: 1.2rem;
        margin-right: 0.8rem;
        transition: box-shadow 0.2s;
    }
    .screener-sidebar-card .metric-checkbox-group input[type="checkbox"]:checked {
        accent-color: #1db954;
        box-shadow: none;
    }
    .screener-sidebar-card .sidebar-section {
        margin-bottom: 2.2rem;
    }
    .screener-sidebar-card .sidebar-divider {
        border: none;
        border-top: 1.5px solid rgba(167,139,250,0.12);
        margin: 1.2rem 0;
    }
    .screener-sidebar-card .sidebar-card {
        margin-bottom: 2.2rem;
    }
    .screener-sidebar-card .input-slider {
        margin-bottom: 1.2rem;
    }
    .screener-main-content {
        flex: 1 1 0%;
        padding: 2.5rem 2.5rem 2.5rem 0;
        display: flex;
        flex-direction: column;
        align-items: stretch;
    }
    .screener-title-row {
        display: flex; align-items: center; gap: 1.1rem; margin-bottom: 0.2rem;
    }
    .screener-title {
        font-size: 2.1rem;
        font-weight: 1000;
        background: linear-gradient(90deg, #1db954 60%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        margin-top: 0;
        letter-spacing: -1px;
        display: inline-block;
    }
    .screener-subtitle {
        font-size: 1.13rem;
        color: #a78bfa;
        font-weight: 600;
        margin-bottom: 1.5rem;
    }
    .screener-card {
        background: rgba(36, 38, 44, 0.95);
        border-radius: 1.2rem;
        box-shadow: 0 6px 32px 0 rgba(29,185,84,0.10), 0 1.5px 0 0 #1db954;
        border: 2.5px solid rgba(167,139,250,0.10);
        padding: 2.2rem 2.2rem 1.7rem 2.2rem;
        margin-bottom: 2.2rem;
        color: #fff;
    }
    .screener-card table {
        background: transparent !important;
        color: #fff !important;
        font-size: 1.08rem;
        border-radius: 0.7rem;
    }
    .screener-card th {
        background: linear-gradient(90deg, #1db954 60%, #a78bfa 100%) !important;
        color: #fff !important;
        font-weight: 900;
        font-size: 1.08rem;
        border: none;
    }
    .screener-card td {
        background: transparent !important;
        color: #fff !important;
        border: none;
    }
    .screener-card tr {
        border-radius: 0.7rem;
        transition: background 0.2s, transform 0.2s;
    }
    .screener-card tr:hover {
        background: rgba(167,139,250,0.10);
        transform: scale(1.01);
    }
    .screener-card .dataframe {
        background: transparent !important;
        color: #fff !important;
    }
    .screener-card .matplotlib-figure {
        background: transparent !important;
    }
    @media (max-width: 1100px) {
        .screener-layout { flex-direction: column; }
        .screener-main-content { padding: 1.2rem; }
        .screener-sidebar-card { margin: 1.2rem auto; }
    }
    @media (max-width: 700px) {
        .screener-main-content { padding: 0.5rem; }
        .screener-sidebar-card { padding: 1rem; }
    }
    .metric-box-title {
        font-size: 1.08rem;
        font-weight: 900;
        color: #1db954;
        margin-bottom: 0.7rem;
        margin-top: 0.1rem;
        letter-spacing: 0.01em;
        text-transform: uppercase;
        font-family: 'Inter', sans-serif;
        background: none;
    }
    .screener-sidebar-card .metric-checkbox-group input[type="checkbox"] {
        appearance: none;
        width: 1.25rem;
        height: 1.25rem;
        border: 2px solid #1db954;
        border-radius: 0.35rem;
        background: #23272f;
        margin-right: 0.8rem;
        position: relative;
        cursor: pointer;
        transition: border 0.18s, box-shadow 0.18s;
        outline: none;
        vertical-align: middle;
    }
    .screener-sidebar-card .metric-checkbox-group input[type="checkbox"]:checked {
        background: #1db954;
        border-color: #1db954;
    }
    .screener-sidebar-card .metric-checkbox-group input[type="checkbox"]:checked:after {
        content: '';
        display: block;
        position: absolute;
        left: 0.32rem;
        top: 0.12rem;
        width: 0.35rem;
        height: 0.7rem;
        border: solid #fff;
        border-width: 0 0.18rem 0.18rem 0;
        transform: rotate(45deg);
    }
    """
    return ui.TagList(
        ui.tags.style(custom_css),
        ui.tags.div(
            ui.tags.div(
                # Sidebar card
                ui.tags.div(
                    ui.tags.div(
                        icon_svg("circle-dot"),
                        class_="screener-icon"
                    ),
                    ui.h2("Stock Screener"),
                    ui.p("Filter and rank stocks by metrics.", class_="screener-subtitle"),
                    ui.h4("Time Range"),
                    ui.input_slider(
                        "vol_time_range", "Time ID Range (for Volatility):",
                        min=min_time, max=max_time,
                        value=(min_time, max_time), step=1
                    ),
                    ui.h4("Financial Statistics"),
                    ui.tags.div(
                        ui.tags.div("Select financial statistics", class_="metric-box-title"),
                        ui.input_checkbox_group(
                            "scr_metrics", None,
                            choices=metric_labels_with_vol,
                            selected=metric_choices[:2]
                        ),
                        class_="screener-metric-box metric-checkbox-group"
                    ),
                    ui.h4("Top N"),
                    ui.input_slider(
                        "top_n", "Top N Stocks:",
                        min=1, max=len(metrics_df), value=10, step=1
                    ),
                    class_="screener-sidebar-card"
                ),
                style="flex:0 0 360px;display:flex;flex-direction:column;align-items:stretch;"
            ),
            ui.tags.div(
                # Main content
                ui.tags.div(
                    ui.tags.span(icon_svg("magnifying-glass"), class_="screener-title-icon"),
                    ui.tags.h2("Stock Screener", class_="screener-title"),
                    class_="screener-title-row"
                ),
                ui.tags.div(
                    "Showing the top N stocks by your chosen metrics (ranked by the first).",
                    class_="screener-subtitle"
                ),
                ui.tags.div(
                    ui.output_data_frame("scr_table"),
                    class_="screener-card"
                ),
                class_="screener-main-content"
            ),
            class_="screener-layout"
        )
    )


def server_screener(input, output, session):

    @reactive.Calc
    def top_metrics():
        sel = list(input.scr_metrics())
        if not sel:
            return pd.DataFrame()

        n = input.top_n()
        result_df = None

        # If volatility is selected, compute it from vol_df over the selected time range
        if 'volatility' in sel:
            start_time, end_time = input.vol_time_range()
            subset = vol_df[(vol_df['time_id'] >= start_time) & (vol_df['time_id'] <= end_time)]
            df_long = subset.melt(id_vars=['time_id'], value_vars=stock_cols, var_name='stock_id', value_name='volatility')
            df_long['stock_id'] = df_long['stock_id'].astype(int)
            vol_mean = df_long.groupby('stock_id')['volatility'].mean().reset_index()
            vol_mean['volatility'] = vol_mean['volatility'].astype(float)
            result_df = vol_mean.rename(columns={'volatility': 'Volatility'})
            sel_no_vol = [m for m in sel if m not in ('volatility', 'realized_volatility')]
            if sel_no_vol:
                metrics_part = metrics_df[['stock_id'] + sel_no_vol]
                result_df = pd.merge(result_df, metrics_part, on='stock_id', how='left')
        else:
            # Only metrics from metrics_df
            result_df = metrics_df[['stock_id'] + sel]

        # Sort by the first selected metric (use actual column name for metrics, 'Volatility' for volatility)
        sort_col = 'Volatility' if sel[0] == 'volatility' else sel[0]
        result_df = result_df.sort_values(sort_col, ascending=False).head(n)

        # Rename columns for display
        col_map = {'stock_id': 'Stock ID'}
        for m in sel:
            if m == 'volatility':
                col_map['Volatility'] = 'Volatility'
            else:
                col_map[m] = m.replace('_', ' ').title()
        result_df = result_df.rename(columns=col_map)
        # Round all numeric columns except 'Stock ID' to 6 decimals
        for col in result_df.columns:
            if col != 'Stock ID':
                result_df[col] = result_df[col].round(6)
        return result_df

    @output
    @render.data_frame
    def scr_table():
        df = top_metrics()
        return df

    @output
    @render.plot
    def scr_plot():
        df = top_metrics()
        fig, ax = plt.subplots(figsize=(8, 4))
        if df.empty:
            ax.text(0.5, 0.5, "No metrics selected", ha='center', va='center')
            return fig

        x = df['Stock ID'].astype(str)
        y = df.iloc[:, 1]
        ax.bar(x, y, alpha=0.75)
        ax.set_xlabel('Stock ID')
        ax.set_ylabel(df.columns[1])
        ax.set_title(f"Top {len(df)} Stocks by {df.columns[1]}", color='#1976D2')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(axis='y', linestyle='--', alpha=0.4)
        plt.tight_layout()
        return fig
