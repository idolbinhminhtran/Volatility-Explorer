import pandas as pd
import matplotlib.pyplot as plt
from shiny import ui, render, reactive
from faicons import icon_svg
from modules.screener import vol_df, stock_cols  # Make sure you import the necessary data
import os
from dotenv import load_dotenv
import openai


# Load metrics_summary.csv for metrics comparison
_project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
METRICS_PATH = os.path.join(_project_dir, 'data', 'metrics_summary.csv')
metrics_df = pd.read_csv(METRICS_PATH)
metrics_df['stock_id'] = metrics_df['stock_id'].astype(str)
metric_choices = [c for c in metrics_df.columns if c not in ('stock_id', 'realized_volatility')]
metric_labels = {c: c.replace('_', ' ').title() for c in metric_choices}
if 'avg_bid_size1' in metric_labels:
    metric_labels['avg_bid_size1'] = 'Avg Bid Size1'


# Load environment variables from .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)


# Define the UI for Stock Comparison
def ui_stock_comparison(stock_ids):
    return ui.layout_sidebar(
        ui.sidebar(
            ui.tags.div(
                ui.tags.div(
                    icon_svg("scale-balanced"),
                    style="display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#00838F 60%,#42a5f5 100%);color:#fff;border-radius:50%;padding:1.1rem;font-size:2.2rem;box-shadow:0 2px 8px rgba(25,118,210,0.12);width:3.5rem;height:3.5rem;margin:0 auto 1.2rem auto;"
                ),
                ui.h2("Stock Comparison", style="color:#00838F;font-weight:900;text-align:center;margin-bottom:0.5rem;margin-top:0;letter-spacing:-1px;"),
                ui.p("Compare financial statistics across multiple stocks.", style="text-align:center;color:#444;font-size:1.08rem;margin-bottom:1.5rem;margin-top:0;"),
                ui.h4("Select Stocks", style="margin-bottom:1.2rem;color:#00838F;font-weight:700;text-align:left;"),
                ui.input_select("stock_1", "Stock 1", stock_ids),
                ui.input_select("stock_2", "Stock 2", stock_ids),
                ui.input_select("stock_3", "Stock 3", stock_ids),
                class_="sidebar-card"
            ),
            width=320
        ),
        ui.tags.div(
            ui.tags.div(
                ui.tags.div(
                    ui.h4("Stock 1 Analysis", style="color:#00838F;font-weight:700;margin-bottom:0.7rem;"),
                    ui.output_ui("stock_1_analysis"),
                    ui.output_plot("stock_1_volatility_plot"),
                    class_="main-card",
                    style="margin-bottom:2rem;"
                ),
                ui.tags.div(
                    ui.h4("Stock 2 Analysis", style="color:#00838F;font-weight:700;margin-bottom:0.7rem;"),
                    ui.output_ui("stock_2_analysis"),
                    ui.output_plot("stock_2_volatility_plot"),
                    class_="main-card",
                    style="margin-bottom:2rem;"
                ),
                ui.tags.div(
                    ui.h4("Stock 3 Analysis", style="color:#00838F;font-weight:700;margin-bottom:0.7rem;"),
                    ui.output_ui("stock_3_analysis"),
                    ui.output_plot("stock_3_volatility_plot"),
                    class_="main-card",
                    style="margin-bottom:2rem;"
                ),
                style="display:flex;flex-wrap:wrap;gap:2rem;justify-content:space-between;"
            ),
            ui.tags.div(
                ui.h4("Comparison Plot", style="color:#2e7d32;font-weight:700;margin-bottom:0.7rem;margin-top:2rem;"),
                ui.output_plot("comparison_plot"),
                class_="main-card"
            ),
            ui.tags.div(
                ui.h4("Financial Statistics Comparison", style="color:#00838F;font-weight:700;margin-bottom:0.7rem;margin-top:2rem;"),
                ui.tags.div(
                    ui.output_data_frame("metrics_comparison_table"),
                    class_="metrics-comparison-table"
                ),
                ui.tags.div(
                    ui.output_ui("best_stock_suggestion"),
                    style="margin-top:1.5rem;"
                ),
                class_="metrics-comparison-card"
            ),
            class_="main-content"
        ),
        class_="analysis-layout"
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
            ax.set_title(f"Volatility Over Time for Stock {input.stock_1()}", fontsize=12, fontweight='bold', color='#00838F')
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
            ax.set_title(f"Volatility Over Time for Stock {input.stock_2()}", fontsize=12, fontweight='bold', color='#00838F')
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
            ax.set_title(f"Volatility Over Time for Stock {input.stock_3()}", fontsize=12, fontweight='bold', color='#00838F')
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
        ax.set_title("Comparison of Volatility Over Time", fontsize=14, fontweight='bold', color='#00838F')
        ax.legend()
        ax.grid(True)
        plt.tight_layout()
        return fig

    @output
    @render.data_frame
    def metrics_comparison_table():
        s1, s2, s3 = input.stock_1(), input.stock_2(), input.stock_3()
        selected = [s for s in [s1, s2, s3] if s]
        if not selected:
            return pd.DataFrame()
        df = metrics_df[metrics_df['stock_id'].isin(selected)].set_index('stock_id').T
        df = df.loc[metric_choices]
        df.index = [metric_labels.get(idx, idx) for idx in df.index]
        df.columns = [f"Stock {col}" for col in df.columns]
        df = df.reset_index().rename(columns={'index': 'Metric'})
        # Round all numeric columns except 'Metric'
        for col in df.columns:
            if col != 'Metric':
                df[col] = df[col].round(6)
        return df

    @reactive.Calc
    def metrics_df_for_suggestion():
        s1, s2, s3 = input.stock_1(), input.stock_2(), input.stock_3()
        selected = [s for s in [s1, s2, s3] if s]
        if not selected:
            return pd.DataFrame()
        df = metrics_df[metrics_df['stock_id'].isin(selected)].set_index('stock_id').T
        df = df.loc[metric_choices]
        df.index = [metric_labels.get(idx, idx) for idx in df.index]
        df.columns = [f"Stock {col}" for col in df.columns]
        df = df.reset_index().rename(columns={'index': 'Metric'})
        for col in df.columns:
            if col != 'Metric':
                df[col] = df[col].round(6)
        return df

    @output
    @render.ui
    def best_stock_suggestion():
        # Get the current metrics table (using the reactive calc) as a string
        df = metrics_df_for_suggestion()
        if df is None or df.empty:
            return "No financial statistics to analyze."
        # Format the table for the prompt
        prompt = f"""
You are a financial analyst AI. Given the following stock financial statistics table, suggest which stock is the best investment and explain why in 2-3 sentences. Be concise and use the data provided only.\n\n{df.to_string(index=False)}\n\nRespond with the stock ID and your reasoning.\n"""
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=120,
                temperature=0.3
            )
            suggestion = response.choices[0].message.content.strip()
            return ui.tags.div([
                ui.tags.h4("Application Suggestion", style="color:#00838F;font-weight:700;margin-bottom:0.7rem;margin-top:0.5rem;"),
                ui.tags.p(suggestion, style="font-size:1.12rem;color:#222;background:#e0f7fa;padding:1rem 1.2rem;border-radius:1rem;")
            ])
        except Exception as e:
            return f"Error getting suggestion: {e}"
