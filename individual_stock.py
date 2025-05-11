from matplotlib import pyplot as plt
from shiny import ui, render, reactive
import pandas as pd
from modules.screener import vol_df, stock_cols


# Define the UI for Individual Stock Analysis

def ui_individual_stock(stock_ids):
    return ui.tags.div(
        ui.h2("Individual Stock Analysis"),
        ui.p("Detailed analysis of individual stock volatility."),
        ui.input_select("stock_id", "Select Stock ID:", stock_ids),  # Stock ID picker
        ui.output_ui("stock_analysis_output"),
        ui.output_plot("stock_volatility_plot"),
        class_="main-content"
    )


def server_individual_stock(input, output, session):
    # Get the list of available stock IDs from the vol_df (make sure they are integers or strings)
    stock_ids = [str(col) for col in vol_df.columns if col != 'time_id']

    @reactive.Calc
    def stock_data():
        stock_id = input.stock_id()  # Get the selected stock ID
        print(f"Selected Stock ID: {stock_id}")  # Debugging line
        if stock_id:
            # Filter the data for the selected stock_id
            stock_data = vol_df[['time_id', stock_id]].copy()
            stock_data.columns = ['time_id', 'volatility']
            #print(stock_data.head())  # Debugging line
            return stock_data
        else:
            return pd.DataFrame(columns=['time_id', 'volatility'])

    # Display volatility for the selected stock in the output UI
    @output
    @render.ui
    def stock_analysis_output():
        data = stock_data()
        if not data.empty:
            return f"Analysis for Stock ID {input.stock_id()}: Average Volatility = {data['volatility'].mean():.4f}"
        return "No data available for the selected stock."

    # Plot volatility over time for the selected stock
    @output
    @render.plot
    def stock_volatility_plot():
        data = stock_data()
        if not data.empty:
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(data['time_id'], data['volatility'], label=f"Volatility for Stock ID {input.stock_id()}",
                    color='#1f77b4')
            ax.set_xlabel('Time ID')
            ax.set_ylabel('Realized Volatility')
            ax.set_title(f"Volatility Over Time for Stock ID {input.stock_id()}", fontsize=12, fontweight='bold')
            ax.legend()
            ax.grid(True)
            plt.tight_layout()
            return fig
        else:
            return None  # Return None if no data is available
