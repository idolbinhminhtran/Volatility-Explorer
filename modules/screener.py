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
# Human-readable labels for metrics
metric_labels = {c: c.replace('_', ' ').title() for c in metric_choices}

# Add 'Volatility' to metric_labels for selection
metric_labels_with_vol = {'volatility': 'Volatility', **metric_labels}

VOL_PATH = os.path.join(_project_dir, 'data', 'vol_df.csv')
vol_df = pd.read_csv(VOL_PATH)
stock_cols = [c for c in vol_df.columns if c != 'time_id']
min_time = int(vol_df['time_id'].min())
max_time = int(vol_df['time_id'].max())

def ui_screener():
    return ui.nav_panel(
        "Stock Screener",
        ui.layout_sidebar(
            ui.sidebar(
                ui.tags.div(
                    icon_svg("magnifying-glass"),
                    ui.h2("Filters"),
                    style="display:flex;align-items:center;gap:10px;margin-bottom:1.5rem;"
                ),
                ui.input_slider(
                    "vol_time_range", "Time ID Range (for Volatility):",
                    min=min_time, max=max_time,
                    value=(min_time, max_time), step=1
                ),
                # multi‐select for metrics
                ui.accordion(
                    ui.accordion_panel(
                        "Select metrics:",
                        ui.input_checkbox_group(
                            "scr_metrics", "",
                            choices=metric_labels_with_vol,
                            selected=metric_choices[:2]
                        ),
                        class_="metric-checkbox-group metric-select-box"
                    ),
                    class_="metric-accordion"
                ),
                ui.input_slider(
                    "top_n", "Top N Stocks:",
                    min=1, max=len(metrics_df), value=10, step=1
                ),
                width=270,
                position="left",
                class_="screener-sidebar"
            ),
            ui.tags.div(
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
                class_="main-content"
            )
        ),
        icon=icon_svg("magnifying-glass"),
        value="screener"
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
        return top_metrics()

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
        ax.set_title(f"Top {len(df)} Stocks by {df.columns[1]}")
        ax.tick_params(axis='x', rotation=45)
        ax.grid(axis='y', linestyle='--', alpha=0.4)
        plt.tight_layout()
        return fig
