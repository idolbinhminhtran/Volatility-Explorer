import os
import pandas as pd
import matplotlib.pyplot as plt
from shiny import ui, render, reactive
from faicons import icon_svg
from dotenv import load_dotenv
import openai
from modules.common_style import get_common_css
from modules.visual_effects import get_effects_css, get_interactive_js

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

# Initialize OpenAI client only if API key is available
client = None
if api_key and api_key != "your_api_key_here":
    client = openai.OpenAI(api_key=api_key)
else:
    print("Warning: OpenAI API key not found or not set. AI features will be disabled.")
    # You can set a flag here to disable AI features

def ui_portfolio_tracker():
    # Use common CSS plus portfolio-specific CSS
    custom_css = get_common_css() + get_effects_css() + """
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
        box-shadow: 0 4px 24px 0 rgba(29,185,84,0.13), 0 1.5px 0 0 rgba(29,185,84,0.1);
        border: 2.5px solid rgba(167,139,250,0.13);
        padding: 1.5rem 2.1rem 1.3rem 1.7rem;
        min-width: 210px;
        display: flex;
        align-items: center;
        gap: 1.1rem;
        position: relative;
        transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
        transform: translateY(0);
        opacity: 0;
        animation: slideInUp 0.5s cubic-bezier(0.165, 0.84, 0.44, 1) forwards;
    }
    
    .portfolio-summary-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px 0 rgba(29,185,84,0.2);
        border-color: rgba(29,185,84,0.25);
    }
    
    .portfolio-summary-card:nth-child(1) { animation-delay: 0.1s; }
    .portfolio-summary-card:nth-child(2) { animation-delay: 0.2s; }
    .portfolio-summary-card:nth-child(3) { animation-delay: 0.3s; }
    .portfolio-summary-card:nth-child(4) { animation-delay: 0.4s; }
    
    .portfolio-summary-icon {
        width: 2.7rem;
        height: 2.7rem;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.45rem;
        box-shadow: 0 2px 12px 0 rgba(29,185,84,0.2);
        margin-right: 0.2rem;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    
    .portfolio-summary-card:hover .portfolio-summary-icon {
        transform: scale(1.1) rotate(10deg);
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
    
    /* Layout alignment overrides */
    .module-layout { gap: 0.5rem; }
    .sidebar-card { margin-top: 80px; }
    .main-content { padding-top: 80px; }
    """
    
    interactive_js = get_interactive_js()
    
    return ui.TagList(
        ui.tags.style(custom_css),
        ui.tags.script(interactive_js),
        ui.tags.div(
            # Two-column layout: sidebar left, main content right
            ui.tags.div(
                # Sidebar card
                ui.tags.div(
                    ui.tags.div(
                        ui.tags.div(ui.tags.i(class_="fa fa-wallet"), class_="module-icon float-effect"),
                        class_="module-icon float-effect"
                    ),
                    ui.h2("Portfolio Builder", class_="animated-gradient-text"),
                    ui.p("Add stocks and track your portfolio.", class_="module-subtitle"),
                    ui.h4("Add Stock"),
                    ui.tags.div(
                        ui.input_select("pt_stock", "Stock ID:", choices=[str(s) for s in stock_cols]),
                        class_="module-input"
                    ),
                    ui.tags.div(
                        ui.input_numeric("pt_volume", "Volume:", value=1, min=0),
                        class_="module-input"
                    ),
                    ui.tags.div(
                        ui.input_numeric("pt_price", "Price per share:", value=1.0, min=0.0, step=0.01),
                        class_="module-input"
                    ),
                    ui.input_action_button("pt_add", "Add to Portfolio", class_="module-btn"),
                    ui.input_action_button("pt_clear", "Clear Portfolio", class_="module-btn", 
                                           style="background:linear-gradient(90deg, #ff1744 60%, #a78bfa 100%);margin-top:1rem;"),
                    class_="sidebar-card"
                ),
                style="flex:0 0 360px;display:flex;flex-direction:column;align-items:stretch;min-width:340px;max-width:380px;"
            ),
            ui.tags.div(
                # Main content column: summary cards row, then plots
                ui.tags.div(
                    # Summary cards row at the top
                    ui.tags.div(
                        ui.tags.div(
                            ui.tags.div(ui.tags.i(class_="fa fa-arrow-trend-up"), class_="portfolio-summary-icon value hover-icon"),
                            ui.tags.div(
                                ui.tags.div("Portfolio Value", class_="portfolio-summary-label"),
                                ui.tags.span(ui.output_text("portfolio_value_card"), class_="portfolio-summary-value animate-counter", **{"data-decimals": "2"}),
                                class_="portfolio-summary-content"
                            ),
                            class_="portfolio-summary-card hover-card"
                        ),
                        ui.tags.div(
                            ui.tags.div(ui.tags.i(class_="fa fa-arrow-up-right-from-square"), class_="portfolio-summary-icon change hover-icon"),
                            ui.tags.div(
                                ui.tags.div("Daily Change", class_="portfolio-summary-label"),
                                ui.tags.span(ui.output_text("daily_change_card"), class_="portfolio-summary-value positive animate-counter", **{"data-decimals": "2"}),
                                class_="portfolio-summary-content"
                            ),
                            class_="portfolio-summary-card hover-card"
                        ),
                        ui.tags.div(
                            ui.tags.div(ui.tags.i(class_="fa fa-wave-square"), class_="portfolio-summary-icon beta hover-icon"),
                            ui.tags.div(
                                ui.tags.div("Portfolio Beta", class_="portfolio-summary-label"),
                                ui.tags.span(ui.output_text("portfolio_beta_card"), class_="portfolio-summary-value animate-counter", **{"data-decimals": "2"}),
                                class_="portfolio-summary-content"
                            ),
                            class_="portfolio-summary-card hover-card"
                        ),
                        ui.tags.div(
                            ui.tags.div(ui.tags.i(class_="fa fa-award"), class_="portfolio-summary-icon sharpe hover-icon"),
                            ui.tags.div(
                                ui.tags.div("Sharpe Ratio", class_="portfolio-summary-label"),
                                ui.tags.span(ui.output_text("sharpe_ratio_card"), class_="portfolio-summary-value animate-counter", **{"data-decimals": "2"}),
                                class_="portfolio-summary-content"
                            ),
                            class_="portfolio-summary-card hover-card"
                        ),
                        class_="portfolio-summary-row"
                    ),
                    style="margin-bottom:2.2rem;"
                ),
                ui.tags.div(
                    ui.tags.div(
                        ui.tags.div(ui.tags.i(class_="fa fa-chart-pie"), class_="hover-icon"),
                        ui.h3("Portfolio Composition", class_="card-title"),
                        style="display:flex;align-items:center;gap:10px;"
                    ),
                    ui.output_ui("pt_pie"),
                    class_="content-card hover-card slide-in-up"
                ),
                ui.tags.div(
                    ui.tags.div(
                        ui.tags.div(ui.tags.i(class_="fa fa-chart-line"), class_="hover-icon"),
                        ui.h3("Volatility Over Time", class_="card-title"),
                        style="display:flex;align-items:center;gap:10px;"
                    ),
                    ui.output_ui("pt_ts_plot"),
                    class_="content-card hover-card slide-in-up",
                    style="animation-delay:0.2s;"
                ),
                ui.tags.div(
                    ui.tags.div(
                        ui.tags.div(ui.tags.i(class_="fa fa-table"), class_="hover-icon"),
                        ui.h3("Portfolio Holdings", class_="card-title"),
                        style="display:flex;align-items:center;gap:10px;"
                    ),
                    ui.output_data_frame("pt_table"),
                    class_="content-card hover-card slide-in-up interactive-table",
                    style="animation-delay:0.4s;"
                ),
                ui.tags.div(
                    ui.tags.div(
                        ui.tags.div(
                            ui.tags.div(ui.tags.i(class_="fa fa-lightbulb"), class_="icon"),
                            ui.tags.span("AI Analysis"),
                            class_="ai-suggestion-header"
                        ),
                        ui.output_ui("pt_ai_suggestion"),
                        class_="ai-suggestion hover-card slide-in-up",
                        style="animation-delay:0.6s;"
                    ),
                    class_="ai-suggestion hover-card slide-in-up",
                    style="animation-delay:0.6s;"
                ),
                class_="main-content stagger-cards"
            ),
            class_="module-layout"
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
                ui.tags.div(
                    ui.tags.svg(*paths, width=size, height=size, style="display:block;margin:auto;"),
                    legend,
                    class_="pie-hover-legend-container"
                ),
                style="display:flex;justify-content:center;align-items:center;"
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
