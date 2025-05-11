import os
import pandas as pd
import matplotlib.pyplot as plt
from shiny import ui, render, reactive
from faicons import icon_svg
from dotenv import load_dotenv
import openai

# ——————————————————————————————————————————————————————————————————————————
# Load your vol_df and define stock_cols here
# ——————————————————————————————————————————————————————————————————————————
_project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
VOL_PATH = os.path.join(_project_dir, 'data', 'vol_df.csv')
vol_df = pd.read_csv(VOL_PATH)
stock_cols = [c for c in vol_df.columns if c != 'time_id']

# Load environment variables from .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)

def ui_portfolio_tracker():
    return ui.nav_panel(
        "Portfolio Tracker",
        ui.layout_sidebar(
            ui.sidebar(
                ui.tags.div(
                    ui.tags.div(
                        icon_svg("wallet"),
                        style="display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#8E24AA 60%,#ce93d8 100%);color:#fff;border-radius:50%;padding:1.1rem;font-size:2.2rem;box-shadow:0 2px 8px rgba(149,117,205,0.12);width:3.5rem;height:3.5rem;margin:0 auto 1.2rem auto;"
                    ),
                    ui.h2("Portfolio Builder", style="color:#8E24AA;font-weight:900;text-align:center;margin-bottom:0.5rem;margin-top:0;letter-spacing:-1px;"),
                    ui.p("Add stocks and track your portfolio.", style="text-align:center;color:#444;font-size:1.08rem;margin-bottom:1.5rem;margin-top:0;"),
                    ui.h4("Add Stock", style="margin-bottom:1.2rem;color:#8E24AA;font-weight:700;text-align:left;"),
                    ui.input_select("pt_stock", "Stock ID:", choices=[str(s) for s in stock_cols]),
                    ui.input_numeric("pt_volume", "Volume:", value=1, min=0),
                    ui.input_numeric("pt_price", "Price per share:", value=1.0, min=0.0, step=0.01),
                    ui.input_action_button("pt_add", "Add to Portfolio"),
                    ui.input_action_button("pt_clear", "Clear Portfolio", class_="btn-danger", style="margin-top:1rem;"),
                    class_="sidebar-card"
                ),
                width=320,
                position="left"
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
                ui.tags.div(
                    ui.output_ui("pt_ai_suggestion"),
                    style="margin-top:1.5rem;"
                ),
                class_="main-content"
            )
        ),
        icon=icon_svg("wallet"),
        value="portfolio"
    )


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
            ax.set_title('Value Proportion', color='#8E24AA')
        return fig

    @output
    @render.plot
    def pt_ts_plot():
        df = df_portfolio()
        if df.empty:
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.text(0.5, 0.5, "No portfolio holdings", ha='center', va='center')
            ax.axis('off')
            return fig
        # Portfolio weights by stock_id (as string)
        weights = df.set_index('stock_id')['proportion'].to_dict()
        # Subset vol_df to only stocks in portfolio
        stocks_in_portfolio = [str(s) for s in df['stock_id']]
        ts_df = vol_df[['time_id'] + stocks_in_portfolio].copy()
        # Compute weighted sum for each time_id
        for s in stocks_in_portfolio:
            ts_df[s] = ts_df[s] * weights[int(s)]
        ts_df['portfolio_vol'] = ts_df[stocks_in_portfolio].sum(axis=1)
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(ts_df['time_id'], ts_df['portfolio_vol'], color='#8E24AA', linewidth=2)
        ax.fill_between(ts_df['time_id'], ts_df['portfolio_vol'], color='#8E24AA', alpha=0.2)
        ax.set_xlabel('Time ID')
        ax.set_ylabel('Portfolio Volatility')
        ax.set_title('Portfolio Volatility Over Time', fontsize=12, fontweight='bold', color='#8E24AA')
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_xticks(ts_df['time_id'][::len(ts_df)//10 or 1])
        ax.set_xticklabels(ts_df['time_id'][::len(ts_df)//10 or 1], rotation=45, ha='right')
        plt.tight_layout()
        return fig

    @output
    @render.data_frame
    def pt_table():
        df = df_portfolio()
        return df.rename(columns={'stock_id': 'Stock ID', 'volume': 'Volume', 'price': 'Price', 'value': 'Value', 'proportion': 'Proportion'})

    @output
    @render.ui
    def pt_ai_suggestion():
        df = df_portfolio()
        if df is None or df.empty:
            return "No portfolio to analyze."
        # Format the table for the prompt
        prompt = f"""
You are a financial analyst AI. Given the following portfolio table, provide a brief evaluation, analysis, and suggestion for the user. Be concise and use the data provided only.\n\n{df.to_string(index=False)}\n\nRespond with your evaluation, analysis, and suggestion.\n"""
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=180,
                temperature=0.3
            )
            suggestion = response.choices[0].message.content.strip()
            # Add bold and newlines for the three key words
            suggestion = suggestion.replace('Evaluation:', '<b>Evaluation:</b><br>')
            suggestion = suggestion.replace('Analysis:', '<br><b>Analysis:</b><br>')
            suggestion = suggestion.replace('Suggestion:', '<br><b>Suggestion:</b><br>')
            return ui.tags.div([
                ui.tags.h4("Application Suggestion", style="color:#8E24AA;font-weight:700;margin-bottom:0.7rem;margin-top:0.5rem;"),
                ui.tags.p(ui.HTML(suggestion), style="font-size:1.12rem;color:#222;background:#f3e5f5;padding:1rem 1.2rem;border-radius:1rem;")
            ])
        except Exception as e:
            return f"Error getting suggestion: {e}"
