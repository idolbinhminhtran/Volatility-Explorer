from matplotlib import pyplot as plt
from shiny import ui, render, reactive
import pandas as pd
from modules.screener import vol_df, stock_cols
from faicons import icon_svg
import os
from dotenv import load_dotenv
import openai


# Load metrics_summary.csv for metrics display
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


# Define the UI for Individual Stock Analysis

def ui_individual_stock(stock_ids):
    custom_css = """
    .individual-layout {
        display: flex;
        flex-direction: row;
        gap: 0;
        width: 100%;
        justify-content: flex-start;
        align-items: stretch;
        min-height: 100vh;
    }
    .individual-sidebar-card {
        background: rgba(36, 38, 44, 0.85);
        border-radius: 2rem;
        box-shadow: 0 4px 18px 0 rgba(29,185,84,0.10);
        border: 2.5px solid;
        border-image: linear-gradient(120deg, #1db954 60%, #a78bfa 100%) 1;
        padding: 2.7rem 2rem 2.7rem 2rem;
        max-width: 350px;
        min-width: 280px;
        width: 320px;
        margin: 2.5rem 0 2.5rem 2.5rem;
        color: #fff;
        font-family: 'Inter', 'Roboto', sans-serif;
        position: relative;
        overflow: visible;
        display: flex;
        flex-direction: column;
        align-items: stretch;
        justify-content: flex-start;
        flex-shrink: 0;
        height: fit-content;
    }
    .individual-sidebar-card .individual-icon {
        display: flex; align-items: center; justify-content: center;
        background: linear-gradient(135deg, #1db954 60%, #a78bfa 100%);
        border-radius: 50%;
        padding: 1.2rem;
        font-size: 3.2rem;
        box-shadow: 0 2px 8px #1db95433;
        width: 4.2rem; height: 4.2rem;
        margin: 0 auto 1.5rem auto;
    }
    .individual-sidebar-card h2 {
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
    .individual-sidebar-card .individual-subtitle {
        color: #fff;
        font-size: 1.13rem;
        font-weight: 500;
        text-align: center;
        margin-bottom: 2.1rem;
        opacity: 0.88;
    }
    .individual-sidebar-card label, .individual-sidebar-card h4 {
        color: #1db954 !important;
        font-weight: 900;
        font-size: 1.08rem;
        letter-spacing: 0.01em;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 8px #1db95433;
    }
    .individual-sidebar-card h4 {
        margin-top: 1.7rem;
        margin-bottom: 1.1rem;
        font-size: 1.13rem;
        background: linear-gradient(90deg, #1db954 60%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-transform: uppercase;
    }
    .individual-main-content {
        flex: 1 1 0%;
        padding: 2.5rem 2.5rem 2.5rem 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 2.2rem;
        min-width: 0;
        margin-left: 0;
        width: 100%;
    }
    .individual-main-card {
        background: rgba(36, 38, 44, 0.95);
        border-radius: 1.5rem;
        box-shadow: 0 6px 32px 0 rgba(29,185,84,0.10), 0 1.5px 0 0 #1db954;
        border: 2.5px solid rgba(167,139,250,0.10);
        padding: 2.2rem 2.2rem 1.7rem 2.2rem;
        min-width: 320px;
        width: 100%;
        max-width: 700px;
        display: flex;
        flex-direction: column;
        align-items: center;
        transition: box-shadow 0.3s, border 0.3s, background 0.5s;
        margin-bottom: 1.5rem;
        margin-left: auto;
        margin-right: auto;
    }
    .individual-main-card:hover {
        box-shadow: 0 16px 48px 0 #1db954, 0 0 32px 4px #a78bfa;
        border: 2.5px solid #1db954;
        background: linear-gradient(120deg, #43e97b 60%, #1db954 100%);
    }
    .individual-main-title {
        font-size: 1.5rem;
        font-weight: 1000;
        color: #1db954;
        margin-bottom: 1.2rem;
        letter-spacing: 0.01em;
        font-family: 'Inter', sans-serif;
        text-align: center;
    }
    .individual-main-subtitle {
        font-size: 1.13rem;
        color: #a78bfa;
        font-weight: 600;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .metrics-comparison-card {
        background: rgba(44, 48, 56, 0.92);
        border-radius: 1.2rem;
        box-shadow: 0 1px 8px #1db95411;
        padding: 1.2rem 1.3rem 1.2rem 1.3rem;
        margin-bottom: 1.2rem;
        display: flex;
        flex-direction: column;
        gap: 0.7rem;
        align-items: center;
        width: 100%;
        max-width: 520px;
        margin-left: auto;
        margin-right: auto;
    }
    .metrics-comparison-table {
        width: 100%;
        background: transparent !important;
        color: #fff !important;
        font-size: 1.08rem;
        border-radius: 0.7rem;
        margin-bottom: 1.2rem;
        text-align: center;
    }
    .metrics-comparison-table table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        background: rgba(36, 38, 44, 0.92);
        border-radius: 0.8rem;
        box-shadow: 0 2px 12px #1db95422, 0 1.5px 0 0 #a78bfa22;
        overflow: hidden;
        font-family: 'Inter', 'Roboto', sans-serif;
        margin: 0 auto;
    }
    .metrics-comparison-table th {
        background: linear-gradient(90deg, #1db954 60%, #a78bfa 100%);
        color: #eaeaff;
        font-weight: 900;
        font-size: 1.08rem;
        letter-spacing: 0.01em;
        padding: 0.7rem 1.1rem;
        border: none;
        text-align: left;
    }
    .metrics-comparison-table td {
        color: #fff;
        font-size: 1.08rem;
        font-weight: 500;
        padding: 0.7rem 1.1rem;
        border-bottom: 1.5px solid #222a;
        border-right: none;
        background: transparent;
    }
    .metrics-comparison-table tr:last-child td {
        border-bottom: none;
    }
    .metrics-comparison-table tr {
        transition: background 0.2s;
    }
    .metrics-comparison-table tr:hover td {
        background: rgba(167,139,250,0.08);
    }
    .metrics-comparison-table th:first-child {
        border-top-left-radius: 0.8rem;
    }
    .metrics-comparison-table th:last-child {
        border-top-right-radius: 0.8rem;
    }
    .metrics-comparison-table td:first-child {
        border-left: none;
    }
    .metrics-comparison-table td:last-child {
        border-right: none;
    }
    .metrics-comparison-card h4 {
        color: #a78bfa !important;
        font-size: 1.18rem;
        font-weight: 900;
        margin-bottom: 0.7rem;
        margin-top: 0.5rem;
        letter-spacing: 0.01em;
        text-align: center;
    }
    .summary-text {
        color: #fff;
        font-size: 1.13rem;
        margin-top: 1.2rem;
        text-align: center;
    }
    .application-suggestion-section {
        width: 100%;
        max-width: 520px;
        margin: 2.2rem auto 0 auto;
        background: rgba(44, 48, 56, 0.92);
        border-radius: 1.2rem;
        box-shadow: 0 4px 24px 0 #a78bfa33, 0 1.5px 0 0 #1db95444;
        border: 2px solid rgba(167,139,250,0.18);
        position: relative;
        padding: 2.1rem 1.5rem 1.7rem 1.5rem;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        overflow: visible;
    }
    .application-suggestion-section .application-suggestion-accent {
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 7px;
        border-top-left-radius: 1.2rem;
        border-top-right-radius: 1.2rem;
        background: linear-gradient(90deg, #a78bfa 40%, #1db954 100%);
        box-shadow: 0 2px 8px #a78bfa33;
    }
    .application-suggestion-header {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        margin-bottom: 1.1rem;
        margin-top: 0.5rem;
    }
    .application-suggestion-header .faicon {
        font-size: 1.5rem;
        color: #a78bfa;
        filter: drop-shadow(0 0 6px #a78bfa88);
    }
    .application-suggestion-section h4 {
        font-size: 1.18rem;
        font-weight: 900;
        letter-spacing: 0.01em;
        color: #a78bfa;
        margin: 0;
        background: none;
        text-align: left;
    }
    .application-suggestion-section p {
        text-align: left;
        margin: 0.7rem 0 0 0;
        font-size: 1.13rem;
        color: #eaeaff;
        background: none;
        padding: 0;
        border-radius: 0;
        line-height: 1.7;
        font-family: 'Inter', 'Roboto', sans-serif;
        font-weight: 500;
        box-shadow: none;
        border: none;
    }
    @media (max-width: 1100px) {
        .individual-layout { flex-direction: column; align-items: stretch; }
        .individual-sidebar-card { margin: 1.2rem auto; width: 100%; max-width: 98vw; }
        .individual-main-content { padding: 1.2rem; }
    }
    @media (max-width: 700px) {
        .individual-main-content { padding: 0.5rem; }
        .individual-sidebar-card { padding: 1rem; }
    }
    """
    return ui.TagList(
        ui.tags.style(custom_css),
        ui.tags.div(
            # Layout: sidebar (left) and main content (right)
            ui.tags.div(
                # Sidebar (fixed width, left)
                ui.tags.div(
                    ui.tags.div(
                        icon_svg("chart-line"),
                        class_="individual-icon"
                    ),
                    ui.h2("Individual Stock"),
                    ui.p("Detailed volatility analysis.", class_="individual-subtitle"),
                    ui.h4("Select Stock"),
                    ui.input_select("stock_id", "Stock ID", stock_ids),
                    ui.tags.div(
                        ui.output_ui("stock_analysis_output"),
                        class_="summary-text",
                        style="margin-top:1.5rem;"
                    ),
                    class_="individual-sidebar-card"
                ),
                # Main content (right)
                ui.tags.div(
                    ui.tags.div(
                        ui.tags.div(
                            "Volatility Over Time",
                            class_="individual-main-title"
                        ),
                        ui.output_plot("stock_volatility_plot"),
                        class_="individual-main-card"
                    ),
                    ui.tags.div(
                        ui.tags.div(
                            "Financial Statistics Summary",
                            class_="individual-main-title"
                        ),
                        ui.tags.div(
                            ui.output_data_frame("stock_metrics_table"),
                            class_="metrics-comparison-table"
                        ),
                        class_="metrics-comparison-card"
                    ),
                    # Application Suggestion as a separate section below
                    ui.tags.div(
                        ui.tags.div(class_="application-suggestion-accent"),
                        ui.tags.div(
                            icon_svg("lightbulb"),
                            ui.tags.h4("Application Suggestion"),
                            class_="application-suggestion-header"
                        ),
                        ui.output_ui("stock_ai_suggestion"),
                        class_="application-suggestion-section"
                    ),
                    class_="individual-main-content"
                ),
                class_="individual-layout"
            )
        )
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

    @reactive.Calc
    def stock_metrics_df():
        stock_id = input.stock_id()
        if not stock_id:
            return pd.DataFrame()
        row = metrics_df[metrics_df['stock_id'] == str(stock_id)]
        if row.empty:
            return pd.DataFrame()
        df = row[metric_choices].T
        df.index = [metric_labels.get(idx, idx) for idx in df.index]
        df = df.reset_index().rename(columns={'index': 'Metric'})
        # Rename the value column to 'Value' (it will be the second column)
        if df.shape[1] > 1:
            df.columns.values[1] = 'Value'
            df['Value'] = df['Value'].round(6)
        return df

    @output
    @render.data_frame
    def stock_metrics_table():
        return stock_metrics_df()

    @output
    @render.ui
    def stock_ai_suggestion():
        stock_id = input.stock_id()
        df = stock_metrics_df()
        if not stock_id or df is None or df.empty:
            return "No financial statistics to analyze."
        # Format the table for the prompt
        prompt = f"""
You are a financial analyst AI. Given the following financial statistics for Stock {stock_id}, provide a brief evaluation and a suggestion on whether to purchase. Be concise and use the data provided only.\n\n{df.to_string(index=False)}\n\nRespond with your evaluation and purchase suggestion.\n"""
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=120,
                temperature=0.3
            )
            suggestion = response.choices[0].message.content.strip()
            return ui.tags.p(suggestion)
        except Exception as e:
            return f"Error getting suggestion: {e}"
