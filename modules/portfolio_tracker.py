import os
import pandas as pd
import matplotlib.pyplot as plt
from shiny import ui, render, reactive
from faicons import icon_svg
from dotenv import load_dotenv
import openai
from modules.common_style import get_common_css
from modules.visual_effects import get_effects_css, get_interactive_js
import numpy as np
import json
import plotly.express as px  # NEW IMPORT

__all__ = [
    'ui_portfolio_tracker',
    'server_portfolio_tracker',
    'get_sparkline',
]

# ——————————————————————————————————————————————————————————————————————————
# Load your vol_df and define stock_cols here
# ——————————————————————————————————————————————————————————————————————————
_project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
VOL_PATH = os.path.join(_project_dir, 'data', 'vol_df.csv')
vol_df = pd.read_csv(VOL_PATH)
stock_cols = [c for c in vol_df.columns if c != 'time_id']

# Load metrics summary for price lookup
METRICS_PATH = os.path.join(_project_dir, 'data', 'metrics_summary.csv')
metrics_df = pd.read_csv(METRICS_PATH)
metrics_df['stock_id'] = metrics_df['stock_id'].astype(str)

# Load and prepare predicted volatility data
PRED_VOL_PATH = os.path.join(_project_dir, 'data', 'predicted_realized_vol.csv')
predicted_vol_df = None
if os.path.exists(PRED_VOL_PATH):
    predicted_vol_df = pd.read_csv(PRED_VOL_PATH)
    predicted_vol_df['stock_id'] = predicted_vol_df['stock_id'].astype(str)

# Load environment variables from .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client only if API key is available
client = None
if api_key and api_key != "your_api_key_here":
    client = openai.OpenAI(api_key=api_key)
else:
    print("Warning: OpenAI API key not found or not set. AI features will be disabled.")
    # You can set a flag here to disable AI features

# Helper to create compact inline sparkline using existing function
def get_sparkline(values):
    """Return HTML sparkline for a 1-D iterable of numeric values."""
    try:
        return volatility_sparkline_html(list(values), n_ticks=0, y_label="", x_label="")
    except Exception:
        return ui.tags.div("No data", class_="empty-plot")

def ui_portfolio_tracker():
    # Use common CSS plus effects and specific styles for this module
    custom_css = get_common_css() + get_effects_css() + """
    /* Enhanced Portfolio Tracker Styles */
    .module-layout {
        display: grid;
        grid-template-columns: 300px 1fr;
        gap: 1.5rem;
        padding: 2rem;
        height: 100vh;
        overflow: hidden;
    }
    .main-content {
        padding-top: 2.5rem;
        display: flex;
        flex-direction: column;
        gap: 2.5rem;
        overflow-y: auto;
        padding-right: 1rem;
    }
    .insights-container {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    .insight-card {
        background: rgba(36, 38, 44, 0.98);
        border-radius: 1.2rem;
        padding: 1.5rem;
        border: 1px solid rgba(167, 139, 250, 0.2);
    }
    .insight-card.summary {
        border-color: rgba(29, 185, 84, 0.2);
    }
    .insight-card.diversification {
        border-color: rgba(255, 152, 0, 0.2);
    }
    .insight-card.model-predictions {
        border-color: rgba(167, 139, 250, 0.3);
    }
    .insight-title {
        font-size: 1.2rem;
        font-weight: 800;
        margin-bottom: 1rem;
        color: #1db954;
    }
    .insight-card.diversification .insight-title {
        color: #ff9800;
    }
    .insight-card.model-predictions .insight-title {
        color: #a78bfa;
    }
    .value-highlight {
        color: #1db954;
        font-weight: 700;
    }
    .stock-highlight {
        color: #a78bfa;
        font-weight: 700;
    }
    .progress-bar {
        height: 0.8rem;
        background: rgba(31, 33, 40, 0.6);
        border-radius: 0.4rem;
        margin: 1rem 0;
        overflow: hidden;
    }
    .progress {
        height: 100%;
        background: linear-gradient(90deg, #ff9800, #ffb74d);
        border-radius: 0.4rem;
    }
    .insight-explanation {
        margin-top: 1rem;
        font-size: 0.9rem;
        color: #e0e0e0;
        line-height: 1.5;
    }
    .content-header {
        display: flex;
        align-items: center;
        gap: 1.2rem;
        margin-bottom: 2.2rem;
    }
    .content-header-icon {
        font-size: 2.5rem;
        color: #1db954;
        background: #232526;
        border-radius: 1.2rem;
        padding: 0.7rem 1.1rem;
        box-shadow: 0 2px 12px #1db95455, 0 0 0 4px rgba(29,185,84,0.08);
        display: flex;
        align-items: center;
        justify-content: center;
        filter: drop-shadow(0 0 8px #1db95455);
    }
    .content-title {
        font-size: 2.4rem;
        font-weight: 900;
        background: linear-gradient(90deg, #1db954 0%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: 0.01em;
    }
    .content-subtitle {
        font-size: 1.1rem;
        color: #b3b3b3;
        margin-top: 0.2rem;
        margin-bottom: 0;
    }
    .content-card {
        background: rgba(36, 38, 44, 0.98);
        border-radius: 1.5rem;
        box-shadow: 0 6px 24px 0 rgba(31, 38, 135, 0.10);
        padding: 2.2rem 2.2rem 2.2rem 2.2rem;
        margin-bottom: 0.5rem;
        width: 100%;
        max-width: 1200px;
        margin-left: auto;
        margin-right: auto;
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
        flex-shrink: 0;
        overflow: visible;
    }
    .chart-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.2rem;
    }
    .chart-header-icon {
        font-size: 2rem;
        color: #a78bfa;
        background: #232526;
        border-radius: 1rem;
        padding: 0.5rem 0.9rem;
        box-shadow: 0 2px 12px #a78bfa55, 0 0 0 4px rgba(167,139,250,0.08);
        display: flex;
        align-items: center;
        justify-content: center;
        filter: drop-shadow(0 0 8px #a78bfa55);
    }
    .chart-title {
        font-size: 1.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #a78bfa 0%, #1db954 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: 0.01em;
    }
    /* Portfolio Stock Cards */
    .portfolio-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
        grid-gap: 2rem;
        width: 100%;
    }
    .stock-card {
        background: rgba(36, 38, 44, 0.92);
        backdrop-filter: blur(10px);
        border-radius: 1.2rem;
        border: 1px solid rgba(29, 185, 84, 0.15);
        padding: 1.5rem;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        box-shadow: 0 2px 8px 0 rgba(29,185,84,0.07);
    }
    .stock-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.2rem;
    }
    .stock-id {
        font-size: 1.4rem;
        font-weight: 900;
        color: #1db954;
    }
    .prediction-badge {
        background: rgba(29, 185, 84, 0.15);
        border-radius: 0.6rem;
        padding: 0.4rem 0.8rem;
        font-size: 0.9rem;
        color: #1db954;
        font-weight: 700;
    }
    .stock-metrics {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin-bottom: 1.2rem;
    }
    .metric {
        background: rgba(31, 33, 40, 0.6);
        border-radius: 0.8rem;
        padding: 0.8rem;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #a78bfa;
        margin-bottom: 0.3rem;
    }
    .metric-value {
        font-size: 1.2rem;
        font-weight: 700;
        color: #fff;
    }
    .sparkline-wrap {
        margin-top: 1rem;
    }
    .remove-btn {
        position: absolute;
        top: 0.5rem;
        right: 0.5rem;
        background: rgba(255, 77, 79, 0.2);
        border: none;
        border-radius: 50%;
        width: 1.8rem;
        height: 1.8rem;
        display: flex;
        align-items: center;
        justify-content: center;
        color: rgba(255, 77, 79, 0.7);
        font-size: 1rem;
        cursor: pointer;
        opacity: 0;
        transition: all 0.2s ease;
    }
    
    .stock-card:hover .remove-btn {
        opacity: 1;
    }
    
    .remove-btn:hover {
        background: rgba(255, 77, 79, 0.4);
        color: rgba(255, 255, 255, 0.9);
    }
    
    /* Portfolio Selector */
    .portfolio-selection {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-bottom: 1.5rem;
    }
    
    .portfolio-tag {
        background: rgba(31, 33, 40, 0.6);
        border: 1px solid rgba(29, 185, 84, 0.2);
        border-radius: 1rem;
        padding: 0.5rem 1rem;
        color: #1db954;
        font-weight: 700;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .portfolio-tag.selected {
        background: #1db954;
        color: #fff;
        box-shadow: 0 4px 10px rgba(29, 185, 84, 0.3);
    }
    
    /* Empty State */
    .empty-portfolio {
        padding: 2rem;
        text-align: center;
        background: rgba(36, 38, 44, 0.92);
        border-radius: 1.2rem;
        border: 2px dashed rgba(255, 255, 255, 0.1);
    }
    
    .empty-icon {
        font-size: 3rem;
        color: rgba(255, 255, 255, 0.2);
        margin-bottom: 1rem;
    }
    """
    
    # Add interactive elements
    interactive_js = get_interactive_js() + """
    $(document).ready(function() {
        $('.portfolio-tag').click(function() {
            $(this).toggleClass('selected');
            
            // Gather selected values and update hidden input
            var selected = [];
            $('.portfolio-tag.selected').each(function() {
                selected.push($(this).data('value'));
            });
            
            // Update hidden input with selected values
            Shiny.setInputValue('portfolio', selected);
        });
    });
    """
    
    return ui.TagList(
        ui.tags.style(custom_css),
        # Ensure Plotly library is available globally for any Plotly-generated charts
        ui.tags.script(src="https://cdn.plot.ly/plotly-2.30.1.min.js"),
        ui.tags.script(interactive_js),
        ui.tags.div(
            # Sidebar (left)
            ui.tags.div(
                ui.tags.div(
                    ui.tags.i(class_="fa fa-wallet"),
                    class_="module-icon"
                ),
                ui.h2("Portfolio Tracker", class_="animated-gradient-text"),
                ui.p("Monitor your stock volatility.", class_="module-subtitle"),
                
                # Portfolio Selection
                ui.h4("Select Stocks"),
                ui.tags.div(
                    ui.input_select("stock_to_add", "Search for Stock", choices=list(stock_cols)),
                    class_="module-input"
                ),
                ui.tags.div(
                    ui.input_numeric("quantity", "Quantity", value=1, min=1, step=1),
                    class_="module-input"
                ),
                ui.input_action_button("add_to_portfolio", "Add to Portfolio", class_="module-btn"),
                
                # Current Portfolio
                # ui.h4("Your Portfolio"),
                ui.tags.div(id="portfolio_container", class_="portfolio-selection"),
                ui.tags.div(
                    ui.input_text("portfolio", "", "[]"),
                    style="display:none;"
                ),
                
                class_="sidebar-card"
            ),
            
            # Main Content (center)
            ui.tags.div(
                # Header
                ui.tags.div(
                    ui.tags.div(icon_svg("wallet"), class_="content-header-icon"),
                    ui.h1("Portfolio Tracker", class_="content-title"),
                    ui.p("Monitor your portfolio of stocks and track volatility metrics.", class_="content-subtitle"),
                    class_="content-header"
                ),
                
                # Portfolio Summary
                ui.tags.div(
                    ui.output_ui("portfolio_stocks"),
                    class_="content-card"
                ),
                
                # Portfolio Composition Pie Chart
                ui.tags.div(
                    ui.tags.div(
                        ui.tags.div(icon_svg("chart-pie"), class_="chart-header-icon"),
                        ui.h3("Holding Proportions", class_="chart-title"),
                        class_="chart-header"
                    ),
                    ui.output_ui("pt_pie"),
                    class_="content-card"
                ),
                
                # Portfolio Insights (moved here)
                ui.tags.div(
                    ui.tags.div(
                        ui.tags.div(icon_svg("lightbulb"), class_="chart-header-icon"),
                        ui.h3("Portfolio Insights", class_="chart-title"),
                        class_="chart-header"
                    ),
                    ui.output_ui("portfolio_insights"),
                    class_="content-card"
                ),
                
                class_="main-content"
            ),
            
            class_="module-layout"
        )
    )

def server_portfolio_tracker(input, output, session):
    portfolio = reactive.Value([])

    @reactive.Effect
    @reactive.event(input.add_to_portfolio)
    def _add_holding():
        holdings = portfolio()
        try:
            stock = int(input.stock_to_add())
            qty = int(input.quantity()) if input.quantity() is not None else 1
        except Exception:
            return
        # price from metrics_df avg_mid_price
        try:
            price = float(metrics_df.loc[metrics_df['stock_id']==str(stock),'avg_mid_price'].values[0])
        except Exception:
            price = 1.0
        vol = qty
        new_holdings = [h.copy() for h in holdings]
        for h in new_holdings:
            if h['stock_id'] == stock:
                h['volume'] += vol
                h['price'] = price
                break
        else:
            new_holdings.append({'stock_id': stock, 'volume': vol, 'price': price})
        portfolio.set(new_holdings)

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
        return portfolio_pie_plotly_html(df)  # UPDATED to use Plotly version instead of SVG

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
            return ui.tags.div("No portfolio to analyze.", class_="ai-suggestion-content")
        
        # Check if OpenAI client is initialized
        if client is None:
            return ui.tags.div([
                ui.tags.div(
                    ui.tags.span(ui.tags.i(class_="fa fa-exclamation-triangle"), class_="icon"),
                    ui.tags.span("OpenAI API Not Configured"),
                    class_="ai-suggestion-header"
                ),
                ui.tags.div(
                    "To enable AI portfolio analysis, please add your OpenAI API key to the .env file.", 
                    class_="ai-suggestion-content"
                )
            ])
            
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
                ui.tags.span("Evaluation:", class_="ai-suggestion-section"),
                ui.tags.div(eval_text, class_="ai-suggestion-content"),
                ui.tags.span("Analysis:", class_="ai-suggestion-section"),
                ui.tags.div(analysis_text, class_="ai-suggestion-content"),
                ui.tags.span("Suggestion:", class_="ai-suggestion-section"),
                ui.tags.div(suggestion_text, class_="ai-suggestion-content"),
            ])
        except Exception as e:
            return ui.tags.div(f"Error getting suggestion: {e}", class_="ai-suggestion-content")

    @output
    @render.ui
    def portfolio_stocks():
        holdings = portfolio()
        portfolio_list = [str(h['stock_id']) for h in holdings]
        if not portfolio_list:
            return ui.HTML(
                """
                <div class="empty-portfolio">
                    <div class="empty-icon"><i class="fa fa-folder-open"></i></div>
                    <h3>Your portfolio is empty</h3>
                    <p>Add stocks to your portfolio to see analysis</p>
                </div>
                """
            )
        
        stock_cards = []
        for stock_id in portfolio_list:
            data = vol_df[['time_id', stock_id]]
            if not data.empty:
                avg_vol = data[stock_id].mean()
                min_vol = data[stock_id].min()
                max_vol = data[stock_id].max()
                
                # Get predicted volatility
                pred_badge = ""
                if predicted_vol_df is not None:
                    pred_row = predicted_vol_df[predicted_vol_df['stock_id'] == stock_id]
                    if not pred_row.empty:
                        pred_vol = pred_row['predicted_realized_vol'].values[0]
                        pred_badge = f'<span class="prediction-badge">Pred: {pred_vol:.6f}</span>'
                
                # Generate sparkline for this stock
                spark = get_sparkline(data[stock_id].values)
                
                stock_cards.append(
                    f"""
                    <div class="stock-card">
                        <button class="remove-btn" onclick="Shiny.setInputValue('remove_from_portfolio', '{stock_id}')">
                            <i class="fa fa-times"></i>
                        </button>
                        <div class="stock-header">
                            <div class="stock-id">Stock {stock_id}</div>
                            {pred_badge}
                        </div>
                        <div class="stock-metrics">
                            <div class="metric">
                                <div class="metric-label">Avg Volatility</div>
                                <div class="metric-value">{avg_vol:.6f}</div>
                            </div>
                            <div class="metric">
                                <div class="metric-label">Max Volatility</div>
                                <div class="metric-value">{max_vol:.6f}</div>
                            </div>
                        </div>
                        {spark}
                    </div>
                    """
                )
        
        cards_html = "".join(stock_cards)
        return ui.HTML(f'<div class="portfolio-grid">{cards_html}</div>')

    @output
    @render.ui
    def portfolio_insights():
        holdings = portfolio()
        portfolio_list = [str(h['stock_id']) for h in holdings]
        if not portfolio_list:
            return ui.HTML(
                """
                <div class="insights-placeholder">
                    <p>Add stocks to your portfolio to see insights</p>
                </div>
                """
            )
        
        # Get actual volatility for portfolio stocks
        portfolio_data = []
        holdings_dict = {str(h['stock_id']): h for h in holdings}
        for stock_id in portfolio_list:
            data = vol_df[['time_id', stock_id]]
            if not data.empty:
                avg_vol = data[stock_id].mean()
                std_dev = data[stock_id].std()
                hold = holdings_dict.get(stock_id, {})
                volume = hold.get('volume', 1)
                price = hold.get('price', 1.0)
                # Get predicted volatility
                pred_vol = None
                if predicted_vol_df is not None:
                    pred_row = predicted_vol_df[predicted_vol_df['stock_id'] == stock_id]
                    if not pred_row.empty:
                        pred_vol = pred_row['predicted_realized_vol'].values[0]
                
                portfolio_data.append({
                    'stock_id': stock_id,
                    'avg_vol': avg_vol,
                    'std_dev': std_dev,
                    'vol_ratio': std_dev / avg_vol if avg_vol > 0 else float('inf'),
                    'pred_vol': pred_vol,
                    'volume': volume,
                    'price': price
                })
        
        if not portfolio_data:
            return ui.HTML(
                """
                <div class="insights-placeholder">
                    <p>No data available for selected stocks</p>
                </div>
                """
            )
        
        # Average portfolio volatility
        avg_portfolio_vol = sum(item['avg_vol'] for item in portfolio_data) / len(portfolio_data) if portfolio_data else 0
        
        # Find highest and lowest volatility stocks
        portfolio_data.sort(key=lambda x: x['avg_vol'])
        lowest_vol_stock = portfolio_data[0]['stock_id']
        highest_vol_stock = portfolio_data[-1]['stock_id']
        
        # Calculate predicted vs actual insights if available
        prediction_insights = ""
        stocks_with_predictions = [s for s in portfolio_data if s['pred_vol'] is not None]
        
        if stocks_with_predictions:
            # Portfolio average predicted volatility
            avg_pred_vol = sum(item['pred_vol'] for item in stocks_with_predictions) / len(stocks_with_predictions)
            
            # Calculate mean prediction error
            prediction_errors = [abs(s['avg_vol'] - s['pred_vol']) / s['pred_vol'] 
                                if s['pred_vol'] > 0 else float('inf') 
                                for s in stocks_with_predictions]
            avg_pred_error = sum(prediction_errors) / len(prediction_errors)
            
            # Find most over and under predicted stocks
            for s in stocks_with_predictions:
                s['pred_diff'] = s['avg_vol'] - s['pred_vol']
            
            stocks_with_predictions.sort(key=lambda x: x['pred_diff'])
            most_underpredicted = stocks_with_predictions[-1]['stock_id'] if stocks_with_predictions else None
            most_overpredicted = stocks_with_predictions[0]['stock_id'] if stocks_with_predictions else None
            
            total_pred_change = sum(abs(s['pred_vol']) * s['price'] * s['volume'] for s in stocks_with_predictions)
            prediction_insights = f"""
            <div class="insight-card model-predictions">
                <div class="insight-title">Volatility Predictions</div>
                <p>Portfolio Average Predicted Volatility: <span class="value-highlight">{avg_pred_vol:.6f}</span></p>
                <p>Potential Daily Swing: <span class="value-highlight">±{total_pred_change:,.2f}</span></p>
                <div class="insight-explanation">
                    <p>Stock <span class="stock-highlight">{most_underpredicted}</span> shows higher volatility than predicted, 
                    possibly indicating unexpected market factors affecting its performance.</p>
                    <p>Stock <span class="stock-highlight">{most_overpredicted}</span> shows lower volatility than predicted, 
                    suggesting better stability than the model anticipated.</p>
                </div>
            </div>
            """
        
        # Create portfolio diversification insights based on volatility distribution
        vol_std = np.std([item['avg_vol'] for item in portfolio_data])
        diversification_score = 0
        if avg_portfolio_vol > 0:
            diversification_score = min(100, max(0, 100 - (vol_std / avg_portfolio_vol * 100)))
        
        diversification_message = "Well diversified with a good mix of volatility profiles."
        if diversification_score < 60:
            diversification_message = "Limited diversification. Consider adding stocks with different volatility patterns."
        elif diversification_score < 80:
            diversification_message = "Moderately diversified. Room for improvement by adding complementary volatility profiles."
        
        # ---- Build cards ----
        summary_card = f"""
            <div class=\"insight-card summary\">
                <div class=\"insight-title\">Portfolio Summary</div>
                <p>Total Net Worth: <span class=\"value-highlight\">${portfolio_value():,.2f}</span></p>
                <p>Portfolio Size: <span class=\"value-highlight\">{len(portfolio_list)}</span> stocks</p>
                <p>Average Volatility: <span class=\"value-highlight\">{avg_portfolio_vol:.6f}</span></p>
                <p>Lowest Volatility: Stock <span class=\"stock-highlight\">{lowest_vol_stock}</span></p>
                <p>Highest Volatility: Stock <span class=\"stock-highlight\">{highest_vol_stock}</span></p>
            </div>
        """

        diversification_card = f"""
            <div class=\"insight-card diversification\">
                <div class=\"insight-title\">Volatility Distribution</div>
                <div class=\"progress-bar\">
                    <div class=\"progress\" style=\"width: {diversification_score}%\"></div>
                </div>
                <p>Diversification Score: <span class=\"value-highlight\">{diversification_score:.1f}</span> / 100</p>
                <div class=\"insight-explanation\">
                    <p>{diversification_message}</p>
                </div>
            </div>
        """

        # Combine all cards (prediction_insights may already contain a full <div> block or be empty)
        combined_html = summary_card + diversification_card + prediction_insights

        return ui.HTML(combined_html)

# --- Custom HTML/CSS visualizations ---
def portfolio_pie_plotly_html(df):
    """Return an interactive Plotly pie chart showing holding proportions."""
    if df.empty:
        return ui.tags.div("No holdings", class_="empty-plot")

    # Use custom brand-aligned palette (green, purple, teal, orange, yellow)
    brand_palette = ["#1db954", "#a78bfa", "#64d8cb", "#ffb74d", "#e1ff70", "#f06292"]
    fig = px.pie(
        df,
        values="value",
        names="stock_id",
        color_discrete_sequence=brand_palette,
    )

    fig.update_traces(
        textinfo="percent+label",
        pull=0.02,
        hovertemplate="<b>%{label}</b><br>Value: %{value}<br>Share: %{percent}<extra></extra>"
    )
    fig.update_layout(
        width=360,  # ensure chart fits horizontally
        height=360,
        margin=dict(t=0, b=0, l=0, r=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )

    # Wrap chart HTML in flex container to center within content card
    fig_html = fig.to_html(include_plotlyjs="cdn", full_html=False, config={"displayModeBar": False})
    centered_html = f'<div style="display:flex;justify-content:center;">{fig_html}</div>'
    return ui.HTML(centered_html)

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
