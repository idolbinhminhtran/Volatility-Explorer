import os
import pandas as pd
import matplotlib.pyplot as plt
from shiny import ui, render, reactive
from faicons import icon_svg

# Load stock list and data from screener
from .screener import stock_cols, vol_df

# UI for the portfolio tracker panel
def ui_portfolio_tracker():
    return ui.nav_panel(
        "Portfolio Tracker",
        ui.layout_sidebar(
            ui.sidebar(
                ui.tags.div(
                    icon_svg("wallet"),
                    ui.h2("Portfolio Builder"),
                    style="display:flex;align-items:center;gap:10px;margin-bottom:1.5rem;"
                ),
                ui.input_select("pt_stock", "Stock ID:", choices=[str(s) for s in stock_cols]),
                ui.input_numeric("pt_volume", "Volume:", value=1, min=0),
                ui.input_numeric("pt_price", "Price per share:", value=1.0, min=0.0, step=0.01),
                ui.input_action_button("pt_add", "Add to Portfolio"),
                ui.input_action_button("pt_clear", "Clear Portfolio", class_="btn-danger"),
                ui.tags.hr(),
                ui.tags.div(
                    icon_svg("chart-line"),
                    ui.h2("Time Series Viewer"),
                    style="display:flex;align-items:center;gap:10px;margin:1.5rem 0 1rem 0;"
                ),
                ui.input_select("pt_ts_stock", "Select Stock to Plot:", choices=[str(s) for s in stock_cols]),
                width=270,
                position="left",
                class_="portfolio-sidebar"
            ),
            ui.tags.div(
                ui.tags.div(
                    ui.tags.div(
                        icon_svg("wallet"),
                        ui.h2("Portfolio Composition", class_="card-title"),
                        style="display:flex;align-items:center;gap:10px;"
                    ),
                    ui.output_plot("pt_pie"),
                    class_="portfolio-card"
                ),
                ui.tags.div(
                    ui.tags.div(
                        icon_svg("chart-line"),
                        ui.h2("Volatility Over Time", class_="card-title"),
                        style="display:flex;align-items:center;gap:10px;"
                    ),
                    ui.output_plot("pt_ts_plot"),
                    class_="portfolio-card ts-card"
                ),
                ui.tags.div(
                    ui.output_data_frame("pt_table"),
                    class_="portfolio-card"
                ),
                class_="main-content"
            )
        ),
        icon=icon_svg("wallet"),
        value="portfolio"
    )

# Server logic for portfolio tracker
def server_portfolio_tracker(input, output, session):
    portfolio = reactive.Value([])

    @reactive.Effect
    @reactive.event(input.pt_add)
    def _add_holding():
        holdings = portfolio()
        stock = int(input.pt_stock())
        vol = input.pt_volume()
        price = input.pt_price()
        new_holdings = [h.copy() for h in holdings]
        for h in new_holdings:
            if h['stock_id'] == stock:
                h['volume'] += vol
                h['price'] = price
                break
        else:
            new_holdings.append({'stock_id': stock, 'volume': vol, 'price': price})
        portfolio.set(new_holdings)

    @reactive.Effect
    @reactive.event(input.pt_clear)
    def _clear():
        portfolio.set([])

    @reactive.Calc
    def df_portfolio():
        df = pd.DataFrame(portfolio())
        if df.empty:
            return df
        df['value'] = df['volume'] * df['price']
        df['proportion'] = df['value'] / df['value'].sum()
        return df

    @output
    @render.plot
    def pt_pie():
        df = df_portfolio()
        fig, ax = plt.subplots(figsize=(5, 5))
        if df.empty:
            ax.text(0.5, 0.5, "No holdings", ha='center', va='center')
        else:
            ax.pie(df['value'], labels=df['stock_id'].astype(str), autopct='%1.1f%%', startangle=90)
            ax.set_title('Value Proportion')
        return fig

    @output
    @render.plot
    def pt_ts_plot():
        # Styled area chart of volatility over time for selected stock
        stock = int(input.pt_ts_stock())
        ts_df = vol_df[['time_id', str(stock)]].rename(columns={str(stock): 'rv'})
        ts_df = ts_df.sort_values('time_id')
        fig, ax = plt.subplots(figsize=(10, 4))
        # Plot line and fill under curve
        ax.plot(ts_df['time_id'], ts_df['rv'], color='#1f77b4', linewidth=2)
        ax.fill_between(ts_df['time_id'], ts_df['rv'], color='#1f77b4', alpha=0.3)
        # Style axes
        ax.set_xlabel('Time ID')
        ax.set_ylabel('Realized Volatility')
        ax.set_title(f'Stock {stock} Volatility Over Time', fontsize=12, fontweight='bold')
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        for spine in ax.spines.values():
            spine.set_visible(False)
        # Rotate x labels for readability, show sparse ticks
        ax.set_xticks(ts_df['time_id'][::len(ts_df)//10 or 1])
        ax.set_xticklabels(ts_df['time_id'][::len(ts_df)//10 or 1], rotation=45, ha='right')
        plt.tight_layout()
        return fig

    @output
    @render.data_frame
    def pt_table():
        df = df_portfolio()
        return df.rename(columns={'stock_id': 'Stock ID', 'volume': 'Volume', 'price': 'Price', 'value': 'Value', 'proportion': 'Proportion'})
