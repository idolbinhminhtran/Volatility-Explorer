import os
import pandas as pd
import matplotlib.pyplot as plt
from shiny import ui, render, reactive
from faicons import icon_svg

# Determine project root and data path
_project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_PATH = os.path.join(_project_dir, 'data/vol_df.csv')

# Load realized volatility panel (wide format)
vol_df = pd.read_csv(DATA_PATH)

# Identify time_id range and stock columns
min_time = int(vol_df['time_id'].min())
max_time = int(vol_df['time_id'].max())
stock_cols = [c for c in vol_df.columns if c != 'time_id']

# UI for the screener panel
def ui_screener():
    return ui.nav_panel(
        "Volatility Screener",
        ui.layout_sidebar(
            ui.sidebar(
                ui.tags.div(
                    icon_svg("magnifying-glass"),
                    ui.h2("Filters"),
                    style="display:flex;align-items:center;gap:10px;margin-bottom:1.5rem;"
                ),
                ui.input_slider(
                    "scr_time_range", "Time ID Range:",
                    min=min_time, max=max_time,
                    value=(min_time, max_time), step=1
                ),
                ui.input_slider(
                    "top_n", "Top N Stocks:",
                    min=1, max=len(stock_cols), value=10, step=1
                ),
                width=270,
                position="left",
                class_="screener-sidebar"
            ),
            ui.tags.div(
                ui.tags.div(
                    ui.tags.span(icon_svg("magnifying-glass"), class_="screener-title-icon"),
                    ui.tags.h2("Volatility Screener", class_="screener-title"),
                    class_="screener-title-row"
                ),
                ui.tags.div(
                    "Showing the top N stocks by average realized volatility. Use the filter to adjust N and time range.",
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

# Server logic for screener
def server_screener(input, output, session):
    @reactive.Calc
    def filtered_data():
        start_time, end_time = input.scr_time_range()
        subset = vol_df[
            (vol_df['time_id'] >= start_time) &
            (vol_df['time_id'] <= end_time)
        ]
        df_long = subset.melt(
            id_vars=['time_id'], value_vars=stock_cols,
            var_name='stock_id', value_name='rv'
        )
        df_long['stock_id'] = df_long['stock_id'].astype(int)
        df_mean = (
            df_long.groupby('stock_id')['rv']
                   .mean()
                   .reset_index(name='Avg Realized Volatility')
        )
        top_n = input.top_n()
        return df_mean.sort_values('Avg Realized Volatility', ascending=False).head(top_n)

    @output
    @render.data_frame
    def scr_table():
        """
        Show top N stocks in a paginated data table.
        """
        df_top = filtered_data()
        return df_top.rename(
            columns={
                'stock_id': 'Stock ID',
                'Avg Realized Volatility': 'Avg Realized Volatility'
            }
        )

    @output
    @render.plot
    def scr_plot():
        df = filtered_data()
        fig, ax = plt.subplots(figsize=(10, 4))
        # Plot line and fill under curve for average realized volatility
        ax.plot(df['stock_id'].astype(str), df['Avg Realized Volatility'], color='#1f77b4', linewidth=2)
        ax.fill_between(df['stock_id'].astype(str), df['Avg Realized Volatility'], color='#1f77b4', alpha=0.3)
        ax.set_xlabel('Stock ID')
        ax.set_ylabel('Avg Realized Volatility')
        ax.set_title('Top N Stocks by Avg Realized Volatility', fontsize=12, fontweight='bold')
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        for spine in ax.spines.values():
            spine.set_visible(False)
        # Show only a subset of x-ticks for readability
        xticks = df['stock_id'].astype(str)
        if len(xticks) > 10:
            step = max(1, len(xticks)//10)
            ax.set_xticks(xticks[::step])
            ax.set_xticklabels(xticks[::step], rotation=45, ha='right')
        else:
            ax.set_xticklabels(xticks, rotation=0)
        plt.tight_layout()
        return fig
