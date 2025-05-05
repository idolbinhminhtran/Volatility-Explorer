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
            # Sidebar: filters
            ui.sidebar(
                ui.h2("Filters"),
                ui.input_slider(
                    "scr_time_range", "Time ID Range:",
                    min=min_time, max=max_time,
                    value=(min_time, max_time), step=1
                ),
                ui.input_slider(
                    "top_n", "Top N Stocks:",
                    min=1, max=len(stock_cols), value=10, step=1
                ),
                width=250,
                position="left"
            ),
            # Main content area: summary table + plot
            ui.tags.div(
                ui.tags.div(
                    ui.tags.span(icon_svg("magnifying-glass"), class_="screener-title-icon"),
                    ui.tags.h2("Volatility Screener", class_="screener-title"),
                    class_="screener-title-row"
                ),
                ui.tags.div(
                    "Showing the top N stocks by choosen metrics. Use the filter to adjust N and time range.",
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
        """
        Render horizontal bar chart of top N stocks.
        """
        df_top = filtered_data()
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.barh(df_top['stock_id'].astype(str), df_top['Avg Realized Volatility'])
        ax.invert_yaxis()
        ax.set_xlabel('Avg Realized Volatility')
        ax.set_ylabel('Stock ID')
        plt.tight_layout()
        return fig
