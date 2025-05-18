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
    custom_css = """
    .portfolio-layout { display: flex; flex-direction: row; gap: 2.5rem; width: 100%; }
    .portfolio-sidebar-card {
        background: rgba(36, 38, 44, 0.72);
        backdrop-filter: blur(14px) saturate(1.2);
        border-radius: 2rem;
        box-shadow: 0 8px 32px 0 rgba(29,185,84,0.18), 0 0px 0 0 #1db954;
        border: 2.5px solid;
        border-image: linear-gradient(120deg, #1db954 60%, #a78bfa 100%) 1;
        padding: 2.7rem 2rem 2.7rem 2rem;
        max-width: 350px;
        margin: 2.5rem 0 2.5rem 2.5rem;
        color: #fff;
        font-family: 'Inter', 'Roboto', sans-serif;
        position: relative;
        overflow: visible;
        transition: box-shadow 0.3s, border 0.3s, background 0.5s;
        display: flex;
        flex-direction: column;
        align-items: stretch;
        justify-content: flex-start;
        /* Glowing border effect */
        box-shadow: 0 0 0 2px #1db95444, 0 8px 32px 0 #1db95422;
    }
    .portfolio-sidebar-card .portfolio-icon {
        display: flex; align-items: center; justify-content: center;
        background: linear-gradient(135deg, #1db954 60%, #a78bfa 100%);
        border-radius: 50%;
        padding: 1.2rem;
        font-size: 3.2rem;
        box-shadow: 0 2px 8px #1db95433;
        width: 4.2rem; height: 4.2rem;
        margin: 0 auto 1.5rem auto;
    }
    .portfolio-sidebar-card h2 {
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
    .portfolio-sidebar-card .portfolio-subtitle {
        color: #fff;
        font-size: 1.13rem;
        font-weight: 500;
        text-align: center;
        margin-bottom: 2.1rem;
        opacity: 0.88;
    }
    .portfolio-sidebar-card label, .portfolio-sidebar-card h4 {
        color: #1db954 !important;
        font-weight: 900;
        font-size: 1.08rem;
        letter-spacing: 0.01em;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 8px #1db95433;
    }
    .portfolio-sidebar-card h4 {
        margin-top: 1.7rem;
        margin-bottom: 1.1rem;
        font-size: 1.13rem;
        background: linear-gradient(90deg, #1db954 60%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-transform: uppercase;
    }
    .portfolio-sidebar-card .input-slider, .portfolio-sidebar-card .input-select, .portfolio-sidebar-card .input-numeric {
        margin-bottom: 1.2rem;
    }
    .portfolio-main-content {
        flex: 1 1 0%;
        padding: 2.5rem 2.5rem 2.5rem 0;
        display: flex;
        flex-direction: column;
        align-items: stretch;
        gap: 2.2rem;
    }
    .portfolio-card, .ts-card {
        background: rgba(36, 38, 44, 0.95);
        border-radius: 1.2rem;
        box-shadow: 0 6px 32px 0 rgba(29,185,84,0.10), 0 1.5px 0 0 #1db954;
        border: 2.5px solid rgba(167,139,250,0.10);
        padding: 2.2rem 2.2rem 1.7rem 2.2rem;
        color: #fff;
        margin-bottom: 1.5rem;
    }
    .portfolio-card .card-title {
        font-size: 1.25rem;
        font-weight: 900;
        color: #1db954;
        margin-bottom: 1.1rem;
        letter-spacing: 0.01em;
        background: linear-gradient(90deg, #1db954 60%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .portfolio-card table, .portfolio-card .dataframe {
        background: transparent !important;
        color: #fff !important;
        font-size: 1.08rem;
        border-radius: 0.7rem;
    }
    .portfolio-card th {
        background: linear-gradient(90deg, #1db954 60%, #a78bfa 100%) !important;
        color: #fff !important;
        font-weight: 900;
        font-size: 1.08rem;
        border: none;
    }
    .portfolio-card td {
        background: transparent !important;
        color: #fff !important;
        border: none;
    }
    .portfolio-card tr {
        border-radius: 0.7rem;
        transition: background 0.2s, transform 0.2s;
    }
    .portfolio-card tr:hover {
        background: rgba(167,139,250,0.10);
        transform: scale(1.01);
    }
    .portfolio-card .matplotlib-figure {
        background: transparent !important;
    }
    .portfolio-card .application-suggestion {
        font-size: 1.12rem;
        color: #222;
        background: #f3e5f5;
        padding: 1rem 1.2rem;
        border-radius: 1rem;
        margin-top: 1.2rem;
    }
    @media (max-width: 1100px) {
        .portfolio-layout { flex-direction: column; }
        .portfolio-main-content { padding: 1.2rem; }
        .portfolio-sidebar-card { margin: 1.2rem auto; }
    }
    @media (max-width: 700px) {
        .portfolio-main-content { padding: 0.5rem; }
        .portfolio-sidebar-card { padding: 1rem; }
    }
    .portfolio-input {
        margin-bottom: 1.3rem;
        display: flex;
        flex-direction: column;
        gap: 0.4rem;
        position: relative;
    }
    .portfolio-input label {
        color: #1db954 !important;
        font-weight: 800;
        font-size: 1.08rem;
        letter-spacing: 0.01em;
        margin-bottom: 0.2rem;
        text-shadow: 0 0 8px #1db95433;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        transition: color 0.25s;
    }
    .portfolio-input:focus-within label {
        color: #a78bfa !important;
        text-shadow: 0 0 12px #a78bfa55;
    }
    .portfolio-input select, .portfolio-input input[type="number"], .portfolio-input input[type="text"] {
        background: rgba(36, 38, 44, 0.82);
        border: 2px solid #1db954;
        border-radius: 0.8rem;
        color: #fff;
        font-size: 1.13rem;
        font-family: 'Inter', 'Roboto', sans-serif;
        padding: 0.7rem 1.1rem;
        outline: none;
        box-shadow: 0 2px 12px 0 rgba(29,185,84,0.10), 0 1px 0 0 #fff1;
        transition: border 0.2s, box-shadow 0.2s, background 0.3s;
        position: relative;
        /* Glassy highlight */
        background-image: linear-gradient(120deg, rgba(255,255,255,0.08) 0%, rgba(29,185,84,0.05) 100%);
    }
    .portfolio-input select:focus, .portfolio-input input:focus {
        border: 2px solid #a78bfa;
        box-shadow: 0 0 0 3px #a78bfa55, 0 2px 12px 0 #a78bfa33;
        background: rgba(36, 38, 44, 0.95);
        animation: inputGlow 1.2s linear infinite alternate;
    }
    @keyframes inputGlow {
        0% { box-shadow: 0 0 0 3px #a78bfa55, 0 2px 12px 0 #a78bfa33; }
        100% { box-shadow: 0 0 0 6px #1db95455, 0 2px 18px 0 #1db95433; }
    }
    .portfolio-btn {
        width: 100%;
        background: linear-gradient(90deg, #1db954 60%, #a78bfa 100%);
        color: #fff;
        font-weight: 900;
        font-size: 1.13rem;
        border: none;
        border-radius: 0.9rem;
        padding: 0.85rem 0;
        margin-bottom: 0.5rem;
        box-shadow: 0 2px 12px 0 rgba(29,185,84,0.10);
        letter-spacing: 0.04em;
        cursor: pointer;
        transition: background 0.2s, box-shadow 0.2s, transform 0.15s;
        position: relative;
        overflow: hidden;
    }
    .portfolio-btn:hover, .portfolio-btn:focus {
        background: linear-gradient(90deg, #a78bfa 60%, #1db954 100%);
        box-shadow: 0 4px 24px 0 #a78bfa44, 0 0 0 4px #a78bfa33;
        transform: scale(1.03);
        animation: btnGlow 1.2s linear infinite alternate;
    }
    @keyframes btnGlow {
        0% { box-shadow: 0 4px 24px 0 #a78bfa44, 0 0 0 4px #a78bfa33; }
        100% { box-shadow: 0 4px 32px 0 #1db95444, 0 0 0 8px #1db95433; }
    }
    .portfolio-btn:active {
        transform: scale(0.98);
        box-shadow: 0 1px 4px 0 #1db95444;
    }
    .portfolio-btn.btn-danger {
        background: linear-gradient(90deg, #ff1744 60%, #a78bfa 100%);
        color: #fff;
        font-weight: 900;
    }
    .portfolio-btn.btn-danger:hover, .portfolio-btn.btn-danger:focus {
        background: linear-gradient(90deg, #a78bfa 60%, #ff1744 100%);
        box-shadow: 0 4px 24px 0 #ff174444, 0 0 0 4px #ff174433;
        animation: btnGlowDanger 1.2s linear infinite alternate;
    }
    @keyframes btnGlowDanger {
        0% { box-shadow: 0 4px 24px 0 #ff174444, 0 0 0 4px #ff174433; }
        100% { box-shadow: 0 4px 32px 0 #a78bfa44, 0 0 0 8px #a78bfa33; }
    }
    .portfolio-summary-row {
      display: flex;
      gap: 2.2rem;
      margin-bottom: 2.2rem;
      justify-content: flex-start;
      flex-wrap: wrap;
    }
    .portfolio-summary-card {
      background: rgba(36,38,44,0.92);
      border-radius: 1.2rem;
      box-shadow: 0 4px 24px 0 #1db95422, 0 1.5px 0 0 #1db954;
      border: 2.5px solid rgba(167,139,250,0.13);
      padding: 1.5rem 2.1rem 1.3rem 1.7rem;
      min-width: 210px;
      display: flex;
      align-items: center;
      gap: 1.1rem;
      position: relative;
      transition: box-shadow 0.3s, border 0.3s, background 0.5s;
    }
    .portfolio-summary-icon {
      width: 2.7rem;
      height: 2.7rem;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.45rem;
      box-shadow: 0 2px 12px 0 #1db95433;
      margin-right: 0.2rem;
    }
    .portfolio-summary-icon.value { background: linear-gradient(135deg, #e3f0ff 60%, #90caf9 100%); color: #1976d2; }
    .portfolio-summary-icon.change { background: linear-gradient(135deg, #e8f5e9 60%, #b9f6ca 100%); color: #1db954; }
    .portfolio-summary-icon.beta { background: linear-gradient(135deg, #fffde7 60%, #ffe082 100%); color: #ffb300; }
    .portfolio-summary-icon.sharpe { background: linear-gradient(135deg, #f3e5f5 60%, #ce93d8 100%); color: #a78bfa; }
    .portfolio-summary-content {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      justify-content: center;
    }
    .portfolio-summary-label {
      font-size: 1.01rem;
      font-weight: 700;
      color: #bdbdbd;
      margin-bottom: 0.18rem;
      letter-spacing: 0.01em;
    }
    .portfolio-summary-value {
      font-size: 1.55rem;
      font-weight: 900;
      color: #fff;
      letter-spacing: 0.01em;
    }
    .portfolio-summary-value.positive { color: #1db954; }
    .portfolio-summary-value.negative { color: #ff1744; }
    .pie-hover-legend-container {
      position: relative;
      display: flex;
      justify-content: center;
      align-items: center;
      min-width: 280px;
      min-height: 260px;
    }
    .pie-hover-legend-container .pie-legend {
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.25s;
    }
    .pie-hover-legend-container:hover .pie-legend {
      opacity: 1;
      pointer-events: auto;
    }
    .application-suggestion-card {
      background: rgba(243,229,245,0.10);
      border-radius: 1.2rem;
      box-shadow: 0 4px 24px 0 #a78bfa22, 0 1.5px 0 0 #a78bfa;
      border: 2.5px solid rgba(167,139,250,0.18);
      padding: 2.1rem 2.2rem 1.7rem 2.2rem;
      color: #fff;
      font-family: 'Inter', 'Roboto', sans-serif;
      margin-bottom: 1.5rem;
      position: relative;
      overflow: visible;
      transition: box-shadow 0.3s, border 0.3s, background 0.5s;
    }
    .application-suggestion-header {
      font-size: 1.18rem;
      font-weight: 900;
      color: #a78bfa;
      margin-bottom: 1.1rem;
      letter-spacing: 0.01em;
      display: flex;
      align-items: center;
      gap: 0.6rem;
    }
    .application-suggestion-header .icon {
      font-size: 1.5rem;
      color: #a78bfa;
      background: rgba(167,139,250,0.13);
      border-radius: 50%;
      padding: 0.4rem;
      box-shadow: 0 2px 8px #a78bfa33;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .application-suggestion-section {
      font-size: 1.08rem;
      font-weight: 800;
      color: #a78bfa;
      margin-top: 1.1rem;
      margin-bottom: 0.3rem;
      letter-spacing: 0.01em;
      display: block;
    }
    .application-suggestion-content {
      font-size: 1.09rem;
      color: #e1e1e6;
      font-weight: 400;
      margin-bottom: 0.7rem;
      line-height: 1.6;
      letter-spacing: 0.01em;
    }
    """
    return ui.TagList(
        ui.tags.style(custom_css),
        ui.tags.div(
            # Two-column layout: sidebar left, main content right
            ui.tags.div(
                # Sidebar card
                ui.tags.div(
                    ui.tags.div(
                        icon_svg("wallet"),
                        class_="portfolio-icon"
                    ),
                    ui.h2("Portfolio Builder"),
                    ui.p("Add stocks and track your portfolio.", class_="portfolio-subtitle"),
                    ui.h4("Add Stock"),
                    ui.tags.div(
                        ui.input_select("pt_stock", "Stock ID:", choices=[str(s) for s in stock_cols]),
                        class_="portfolio-input"
                    ),
                    ui.tags.div(
                        ui.input_numeric("pt_volume", "Volume:", value=1, min=0),
                        class_="portfolio-input"
                    ),
                    ui.tags.div(
                        ui.input_numeric("pt_price", "Price per share:", value=1.0, min=0.0, step=0.01),
                        class_="portfolio-input"
                    ),
                    ui.input_action_button("pt_add", "Add to Portfolio", class_="portfolio-btn"),
                    ui.input_action_button("pt_clear", "Clear Portfolio", class_="portfolio-btn btn-danger", style="margin-top:1rem;"),
                    class_="portfolio-sidebar-card"
                ),
                style="flex:0 0 360px;display:flex;flex-direction:column;align-items:stretch;min-width:340px;max-width:380px;"
            ),
            ui.tags.div(
                # Main content column: summary cards row, then plots
                ui.tags.div(
                    # Summary cards row at the top
                    ui.tags.div(
                        ui.tags.div(
                            ui.tags.div(icon_svg("arrow-trend-up"), class_="portfolio-summary-icon value"),
                            ui.tags.div(
                                ui.tags.div("Portfolio Value", class_="portfolio-summary-label"),
                                ui.tags.span(ui.output_text("portfolio_value_card"), class_="portfolio-summary-value"),
                                class_="portfolio-summary-content"
                            ),
                            class_="portfolio-summary-card"
                        ),
                        ui.tags.div(
                            ui.tags.div(icon_svg("arrow-up-right-from-square"), class_="portfolio-summary-icon change"),
                            ui.tags.div(
                                ui.tags.div("Daily Change", class_="portfolio-summary-label"),
                                ui.tags.span(ui.output_text("daily_change_card"), class_="portfolio-summary-value positive"),
                                class_="portfolio-summary-content"
                            ),
                            class_="portfolio-summary-card"
                        ),
                        ui.tags.div(
                            ui.tags.div(icon_svg("wave-square"), class_="portfolio-summary-icon beta"),
                            ui.tags.div(
                                ui.tags.div("Portfolio Beta", class_="portfolio-summary-label"),
                                ui.tags.span(ui.output_text("portfolio_beta_card"), class_="portfolio-summary-value"),
                                class_="portfolio-summary-content"
                            ),
                            class_="portfolio-summary-card"
                        ),
                        ui.tags.div(
                            ui.tags.div(icon_svg("award"), class_="portfolio-summary-icon sharpe"),
                            ui.tags.div(
                                ui.tags.div("Sharpe Ratio", class_="portfolio-summary-label"),
                                ui.tags.span(ui.output_text("sharpe_ratio_card"), class_="portfolio-summary-value"),
                                class_="portfolio-summary-content"
                            ),
                            class_="portfolio-summary-card"
                        ),
                        class_="portfolio-summary-row"
                    ),
                    style="margin-bottom:2.2rem;"
                ),
                ui.tags.div(
                    ui.tags.div(
                        icon_svg("wallet"),
                        ui.h2("Portfolio Composition", class_="card-title"),
                        style="display:flex;align-items:center;gap:10px;"
                    ),
                    ui.output_ui("pt_pie"),
                    class_="portfolio-card"
                ),
                ui.tags.div(
                    ui.tags.div(
                        icon_svg("chart-line"),
                        ui.h2("Volatility Over Time", class_="card-title"),
                        style="display:flex;align-items:center;gap:10px;"
                    ),
                    ui.output_ui("pt_ts_plot"),
                    class_="portfolio-card ts-card"
                ),
                ui.tags.div(
                    ui.output_data_frame("pt_table"),
                    class_="portfolio-card"
                ),
                ui.tags.div(
                    ui.output_ui("pt_ai_suggestion"),
                    class_="portfolio-card application-suggestion"
                ),
                class_="portfolio-main-content",
                style="flex:1 1 0%;padding:2.5rem 2.5rem 2.5rem 0;display:flex;flex-direction:column;align-items:stretch;gap:2.2rem;min-width:0;"
            ),
            class_="portfolio-layout",
            style="display:flex;flex-direction:row;gap:2.5rem;width:100%;align-items:flex-start;"
        )
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

    # --- Summary card calculations ---
    @reactive.Calc
    def portfolio_value():
        df = df_portfolio()
        return df['value'].sum() if not df.empty else 0

    @reactive.Calc
    def daily_change():
        # Placeholder: replace with real calculation if available
        return 0.0074  # +0.74%

    @reactive.Calc
    def portfolio_beta():
        # Placeholder
        return 1.05

    @reactive.Calc
    def sharpe_ratio():
        # Placeholder
        return 1.72

    @output
    @render.text
    def portfolio_value_card():
        val = portfolio_value()
        return f"${val:,.2f}K" if val >= 1000 else f"${val:,.2f}"

    @output
    @render.text
    def daily_change_card():
        change = daily_change()
        sign = "+" if change >= 0 else ""
        return f"{sign}{change*100:.2f}%"

    @output
    @render.text
    def portfolio_beta_card():
        return f"{portfolio_beta():.2f}"

    @output
    @render.text
    def sharpe_ratio_card():
        return f"{sharpe_ratio():.2f}"

    @output
    @render.ui
    def pt_pie():
        df = df_portfolio()
        return portfolio_pie_html(df)

    @output
    @render.ui
    def pt_ts_plot():
        df = df_portfolio()
        if df.empty:
            return ui.tags.div("No portfolio holdings", class_="empty-plot")
        stocks_in_portfolio = [str(s) for s in df['stock_id']]
        weights = df.set_index('stock_id')['proportion'].to_dict()
        ts_df = vol_df[['time_id'] + stocks_in_portfolio].copy()
        for s in stocks_in_portfolio:
            ts_df[s] = ts_df[s] * weights[int(s)]
        ts_df['portfolio_vol'] = ts_df[stocks_in_portfolio].sum(axis=1)
        ts = ts_df['portfolio_vol'].tolist()
        time_ids = ts_df['time_id'].tolist()
        return volatility_sparkline_html(ts, time_ids=time_ids)

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
            return ui.tags.div("No portfolio to analyze.", class_="application-suggestion-card")
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
            # Split into sections for formatting
            import re
            eval_match = re.search(r"Evaluation:(.*?)(Analysis:|Suggestion:|$)", suggestion, re.DOTALL)
            analysis_match = re.search(r"Analysis:(.*?)(Suggestion:|$)", suggestion, re.DOTALL)
            suggestion_match = re.search(r"Suggestion:(.*)", suggestion, re.DOTALL)
            eval_text = eval_match.group(1).strip() if eval_match else ""
            analysis_text = analysis_match.group(1).strip() if analysis_match else ""
            suggestion_text = suggestion_match.group(1).strip() if suggestion_match else ""
            return ui.tags.div([
                ui.tags.div([
                    ui.tags.span(icon_svg("lightbulb"), class_="icon"),
                    ui.tags.span("Application Suggestion")
                ], class_="application-suggestion-header"),
                ui.tags.span("Evaluation:", class_="application-suggestion-section"),
                ui.tags.div(eval_text, class_="application-suggestion-content"),
                ui.tags.span("Analysis:", class_="application-suggestion-section"),
                ui.tags.div(analysis_text, class_="application-suggestion-content"),
                ui.tags.span("Suggestion:", class_="application-suggestion-section"),
                ui.tags.div(suggestion_text, class_="application-suggestion-content"),
            ], class_="application-suggestion-card")
        except Exception as e:
            return ui.tags.div(f"Error getting suggestion: {e}", class_="application-suggestion-card")

# --- Custom HTML/CSS visualizations ---
def portfolio_pie_html(df):
    if df.empty:
        return ui.tags.div("No holdings", class_="empty-plot")
    import math
    size = 260  # Larger pie chart
    radius = size // 2 - 18
    cx, cy = size // 2, size // 2
    total = df['proportion'].sum()
    colors = ["#1db954", "#a78bfa", "#ff1744", "#ffb300", "#00bcd4", "#8e24aa"]
    angles = [p * 360 for p in df['proportion']]
    paths = []
    start_angle = 0
    for i, (idx, row) in enumerate(df.iterrows()):
        angle = angles[i]
        end_angle = start_angle + angle
        start_rad = math.radians(start_angle)
        end_rad = math.radians(end_angle)
        x1 = cx + radius * math.cos(start_rad)
        y1 = cy + radius * math.sin(start_rad)
        x2 = cx + radius * math.cos(end_rad)
        y2 = cy + radius * math.sin(end_rad)
        large_arc = 1 if angle > 180 else 0
        path = f"M{cx},{cy} L{x1},{y1} A{radius},{radius} 0 {large_arc},1 {x2},{y2} Z"
        paths.append(ui.HTML(f'<path d="{path}" fill="{colors[i%len(colors)]}" stroke="#222" stroke-width="1"/>'))
        start_angle = end_angle
    legend_items = []
    for i, (idx, row) in enumerate(df.iterrows()):
        legend_items.append(
            ui.tags.div([
                ui.tags.span(style=f"display:inline-block;width:0.9em;height:0.9em;background:{colors[i%len(colors)]};border-radius:0.3em;margin-right:0.4em;vertical-align:middle;"),
                ui.tags.span(f"{row['stock_id']}: {row['proportion']*100:.1f}%")
            ], style="margin-bottom:0.2em;display:flex;align-items:center;font-size:0.98em;")
        )
    legend = ui.tags.div(
        *legend_items,
        class_="pie-legend",
        style="position:absolute;top:12px;right:12px;background:rgba(36,38,44,0.92);padding:0.5em 0.8em;border-radius:0.8em;box-shadow:0 2px 12px #1db95422;z-index:2;font-size:0.98em;min-width:90px;display:inline-block;"
    )
    return ui.tags.div(
        ui.tags.div("Value Proportion (%)", style="font-size:1.08em;font-weight:700;color:#a78bfa;margin-bottom:0.5em;"),
        ui.tags.div(
            ui.tags.div(
                ui.tags.svg(*paths, width=size, height=size, style="display:block;margin:auto;"),
                legend,
                class_="pie-hover-legend-container"
            ),
            style="display:flex;justify-content:center;align-items:center;"
        ),
        style="padding:1.2em 0;"
    )

def volatility_sparkline_html(ts, time_ids=None, y_label="Volatility", x_label="", n_ticks=4):
    if ts is None or len(ts) == 0:
        return ui.tags.div("No portfolio holdings", class_="empty-plot")
    left_pad = 60  # More space for y-axis
    w, h = 520, 160  # Larger plot
    min_v, max_v = min(ts), max(ts)
    if max_v - min_v < 1e-8:
        points = [(left_pad + i/(len(ts)-1)*w, h/2) for i in range(len(ts))]
    else:
        scale = lambda v: h - ((v - min_v) / (max_v - min_v)) * (h-28) + 14
        points = [(left_pad + i/(len(ts)-1)*w, scale(v)) for i, v in enumerate(ts)]
    points_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    area_points = points + [(left_pad + w, h), (left_pad, h)]
    area_points_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in area_points)
    y_ticks = [min_v + (max_v-min_v)*i/(n_ticks-1) for i in range(n_ticks)]
    y_tick_els = []
    for v in y_ticks:
        y = h - ((v - min_v) / (max_v - min_v)) * (h-28) + 14
        y_tick_els.append(ui.HTML(f'<line x1="{left_pad-10}" x2="{left_pad}" y1="{y:.1f}" y2="{y:.1f}" stroke="#a78bfa" stroke-width="1" opacity="0.5"/>'))
        y_tick_els.append(ui.HTML(f'<text x="{left_pad-12}" y="{y+4:.1f}" fill="#a78bfa" font-size="13" text-anchor="end">{v:.2f}</text>'))
    y_label_el = ui.HTML(f'<text x="6" y="22" fill="#a78bfa" font-size="15" text-anchor="start">{y_label}</text>')
    svg = ui.tags.svg(
        ui.HTML(
            '<defs>'
            '<linearGradient id="volAreaGrad" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0%" stop-color="#a78bfa" stop-opacity="0.32"/>'
            '<stop offset="100%" stop-color="#a78bfa" stop-opacity="0.04"/>'
            '</linearGradient>'
            '</defs>'
            f'<polygon points="{area_points_str}" fill="url(#volAreaGrad)" />'
            f'<polyline points="{points_str}" fill="none" stroke="#a78bfa" stroke-width="2.5"/>'
        ),
        *y_tick_els,
        y_label_el,
        width=w+left_pad, height=h+32, style="background:rgba(36,38,44,0.85);border-radius:1.2rem;overflow:visible;"
    )
    return ui.tags.div(svg, class_="sparkline-wrap")
