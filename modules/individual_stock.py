from matplotlib import pyplot as plt
from shiny import ui, render, reactive
import pandas as pd
from modules.screener import vol_df, stock_cols
from faicons import icon_svg


# Define the UI for Individual Stock Analysis

def ui_individual_stock(stock_ids):
    return ui.layout_sidebar(
        ui.sidebar(
            ui.tags.div(
                ui.tags.div(
                    icon_svg("chart-line"),
                    style="display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#1976D2 60%,#42a5f5 100%);color:#fff;border-radius:50%;padding:1.1rem;font-size:2.2rem;box-shadow:0 2px 8px rgba(25,118,210,0.12);width:3.5rem;height:3.5rem;margin:0 auto 1.2rem auto;"
                ),
                ui.h2("Individual Stock", style="color:#1976D2;font-weight:900;text-align:center;margin-bottom:0.5rem;margin-top:0;letter-spacing:-1px;"),
                ui.p("Detailed volatility analysis.", style="text-align:center;color:#444;font-size:1.08rem;margin-bottom:1.5rem;margin-top:0;"),
                ui.h4("Select Stock", style="margin-bottom:1.2rem;color:#1976D2;font-weight:700;text-align:left;"),
                ui.input_select("stock_id", "Stock ID", stock_ids),
                ui.tags.div(
                    ui.output_ui("stock_analysis_output"),
                    class_="summary-text",
                    style="margin-top:1.5rem;"
                ),
                class_="sidebar-card"
            ),
            width=320
        ),
        ui.tags.div(
            ui.tags.div(
            ),
            ui.output_plot("stock_volatility_plot"),
            class_="main-card"
        ),
        class_="analysis-layout"
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
            ax.set_title(f"Volatility Over Time for Stock ID {input.stock_id()}", fontsize=12, fontweight='bold', color='#1976D2')
            ax.legend()
            ax.grid(True)
            plt.tight_layout()
            return fig
        else:
            return None  # Return None if no data is available
