import pandas as pd
import matplotlib.pyplot as plt
from shiny import ui, render, reactive
from faicons import icon_svg
from modules.screener import vol_df, stock_cols  # Make sure you import the necessary data


# Define the UI for Stock Comparison
def ui_stock_comparison(stock_ids):
    return ui.tags.div(
        ui.h2("Stock Comparison"),
        ui.p("Compare volatility metrics across multiple stocks."),

        # Layout rows for displaying 3 stock analysis side by side
        ui.row(
            ui.column(4,  # Adjust column width for each stock analysis
                      ui.input_select("stock_1", "Select Stock 1:", stock_ids),  # Stock ID picker for Stock 1
                      ui.output_ui("stock_1_analysis"),  # Output for Stock 1 Analysis
                      ui.output_plot("stock_1_volatility_plot")  # Plot for Stock 1
                      ),
            ui.column(4,  # Adjust column width for each stock analysis
                      ui.input_select("stock_2", "Select Stock 2:", stock_ids),  # Stock ID picker for Stock 2
                      ui.output_ui("stock_2_analysis"),  # Output for Stock 2 Analysis
                      ui.output_plot("stock_2_volatility_plot")  # Plot for Stock 2
                      ),
            ui.column(4,  # Adjust column width for each stock analysis
                      ui.input_select("stock_3", "Select Stock 3:", stock_ids),  # Stock ID picker for Stock 3
                      ui.output_ui("stock_3_analysis"),  # Output for Stock 3 Analysis
                      ui.output_plot("stock_3_volatility_plot")  # Plot for Stock 3
                      )
        ),
        ui.output_plot("comparison_plot"),  # Display comparison plot at the bottom
        class_="main-content"
    )


# Server logic for Stock Comparison
def server_stock_comparison(input, output, session):
    # Define individual stock analysis logic for Stock 1
    @reactive.Calc
    def stock_1_data():
        stock_id = input.stock_1()
        if stock_id:
            stock_data = vol_df[['time_id', stock_id]].copy()
            stock_data.columns = ['time_id', 'volatility']
            return stock_data
        else:
            return pd.DataFrame(columns=['time_id', 'volatility'])

    @output
    @render.ui
    def stock_1_analysis():
        data = stock_1_data()
        if not data.empty:
            return f"Analysis for Stock {input.stock_1()}: Average Volatility = {data['volatility'].mean():.4f}"
        return "No data available for the selected stock."

    @output
    @render.plot
    def stock_1_volatility_plot():
        data = stock_1_data()
        if not data.empty:
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(data['time_id'], data['volatility'], label=f"Volatility for Stock {input.stock_1()}",
                    color='#1f77b4')
            ax.set_xlabel('Time ID')
            ax.set_ylabel('Realized Volatility')
            ax.set_title(f"Volatility Over Time for Stock {input.stock_1()}", fontsize=12, fontweight='bold')
            ax.legend()
            ax.grid(True)
            plt.tight_layout()
            return fig
        else:
            return None

    # Repeat for Stock 2 and Stock 3
    @reactive.Calc
    def stock_2_data():
        stock_id = input.stock_2()
        if stock_id:
            stock_data = vol_df[['time_id', stock_id]].copy()
            stock_data.columns = ['time_id', 'volatility']
            return stock_data
        else:
            return pd.DataFrame(columns=['time_id', 'volatility'])

    @output
    @render.ui
    def stock_2_analysis():
        data = stock_2_data()
        if not data.empty:
            return f"Analysis for Stock {input.stock_2()}: Average Volatility = {data['volatility'].mean():.4f}"
        return "No data available for the selected stock."

    @output
    @render.plot
    def stock_2_volatility_plot():
        data = stock_2_data()
        if not data.empty:
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(data['time_id'], data['volatility'], label=f"Volatility for Stock {input.stock_2()}",
                    color='#ff7f0e')
            ax.set_xlabel('Time ID')
            ax.set_ylabel('Realized Volatility')
            ax.set_title(f"Volatility Over Time for Stock {input.stock_2()}", fontsize=12, fontweight='bold')
            ax.legend()
            ax.grid(True)
            plt.tight_layout()
            return fig
        else:
            return None

    @reactive.Calc
    def stock_3_data():
        stock_id = input.stock_3()
        if stock_id:
            stock_data = vol_df[['time_id', stock_id]].copy()
            stock_data.columns = ['time_id', 'volatility']
            return stock_data
        else:
            return pd.DataFrame(columns=['time_id', 'volatility'])

    @output
    @render.ui
    def stock_3_analysis():
        data = stock_3_data()
        if not data.empty:
            return f"Analysis for Stock {input.stock_3()}: Average Volatility = {data['volatility'].mean():.4f}"
        return "No data available for the selected stock."

    @output
    @render.plot
    def stock_3_volatility_plot():
        data = stock_3_data()
        if not data.empty:
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(data['time_id'], data['volatility'], label=f"Volatility for Stock {input.stock_3()}",
                    color='#2ca02c')
            ax.set_xlabel('Time ID')
            ax.set_ylabel('Realized Volatility')
            ax.set_title(f"Volatility Over Time for Stock {input.stock_3()}", fontsize=12, fontweight='bold')
            ax.legend()
            ax.grid(True)
            plt.tight_layout()
            return fig
        else:
            return None

    @output
    @render.plot
    def comparison_plot():
        # Combine all three stock volatility data for comparison
        fig, ax = plt.subplots(figsize=(12, 6))

        # Stock 1 plot
        data_1 = stock_1_data()
        if not data_1.empty:
            ax.plot(data_1['time_id'], data_1['volatility'], label=f"Stock {input.stock_1()} Volatility",
                    color='#1f77b4')

        # Stock 2 plot
        data_2 = stock_2_data()
        if not data_2.empty:
            ax.plot(data_2['time_id'], data_2['volatility'], label=f"Stock {input.stock_2()} Volatility",
                    color='#ff7f0e')

        # Stock 3 plot
        data_3 = stock_3_data()
        if not data_3.empty:
            ax.plot(data_3['time_id'], data_3['volatility'], label=f"Stock {input.stock_3()} Volatility",
                    color='#2ca02c')

        ax.set_xlabel('Time ID')
        ax.set_ylabel('Realized Volatility')
        ax.set_title("Comparison of Volatility Over Time", fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True)
        plt.tight_layout()
        return fig
