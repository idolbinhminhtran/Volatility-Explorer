from matplotlib import pyplot as plt
from shiny import ui, render, reactive
import pandas as pd
from modules.screener import vol_df, stock_cols
from faicons import icon_svg
import os
from dotenv import load_dotenv
import openai
from modules.common_style import get_common_css
from modules.visual_effects import get_effects_css, get_interactive_js


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
    # Use common CSS plus effects and specific styles for this module
    custom_css = get_common_css() + get_effects_css() + """
    /* Enhanced Layout for Individual Stock Page */
    .module-layout {
        display: grid;
        grid-template-columns: 320px 1fr;
        gap: 0.5rem;
        width: 100%;
        min-height: calc(100vh - 80px);
        background: linear-gradient(135deg, rgba(22, 24, 29, 0.9) 0%, rgba(31, 33, 40, 0.95) 100%);
        padding: 1rem;
        position: relative;
    }
    
    /* Sidebar Card Enhancement */
    .sidebar-card {
        background: rgba(33, 35, 42, 0.92);
        backdrop-filter: blur(14px) saturate(1.2);
        border-radius: 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(29,185,84,0.18);
        border: 2px solid #1db954;
        padding: 1.8rem 1.5rem;
        width: 100%;
        min-width: 300px;
        height: fit-content;
        color: #fff;
        font-family: 'Inter', 'Roboto', sans-serif;
        position: relative;
        overflow: visible;
        transition: all 0.3s ease;
        align-self: start;
        margin: 80px 0 0 0;
    }
    
    /* Module icon sizing */
    .sidebar-card .module-icon {
        background: #1db954;
        border-radius: 50%;
        margin: 0 auto 1.5rem auto;
        width: 5rem;
        height: 5rem;
        font-size: 2.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        box-shadow: 0 0 20px rgba(29, 185, 84, 0.4);
    }
    
    /* Title styling */
    .sidebar-card h2 {
        font-size: 1.8rem;
        margin-bottom: 0.5rem;
        color: #1db954;
        text-align: center;
        text-transform: uppercase;
        font-weight: 800;
        letter-spacing: 0.05em;
    }
    
    .sidebar-card .module-subtitle {
        text-align: center;
        margin-bottom: 2rem;
        opacity: 0.8;
    }
    
    /* Section headers */
    .sidebar-card h4 {
        color: #1db954;
        font-size: 1.2rem;
        font-weight: 700;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    
    /* Stock stats styling */
    .stock-summary {
        margin-top: 1.2rem;
        padding: 1.2rem;
        background: rgba(31, 33, 42, 0.92);
        border-radius: 0.8rem;
        border: 1px solid rgba(29, 185, 84, 0.2);
    }
    
    .stats-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1db954;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .stat-item {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.7rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px dashed rgba(255, 255, 255, 0.1);
    }
    
    .stat-item:last-child {
        border-bottom: none;
        margin-bottom: 0;
    }
    
    .stat-label {
        color: #e0e0e0;
        font-size: 0.9rem;
    }
    
    .stat-value {
        color: #1db954;
        font-weight: 700;
        font-size: 0.9rem;
    }
    
    /* ID highlight */
    .id-highlight {
        color: #a78bfa;
        font-weight: 800;
    }
    
    /* More compact content */
    .main-content {
        display: grid;
        grid-template-columns: 1fr;
        gap: 1.2rem;
        padding: 80px 0 0 0;
        animation: fadeIn 0.5s forwards 0.2s;
    }
    
    /* Main content header */
    .content-header {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        margin-bottom: 1rem;
    }
    
    .content-header-icon {
        font-size: 1.8rem;
        color: #1db954;
    }
    
    .content-title {
        font-size: 1.8rem;
        font-weight: 900;
        color: #1db954;
        margin: 0;
    }
    
    .content-subtitle {
        font-size: 1rem;
        color: #a78bfa;
        margin-bottom: 1.5rem;
    }
    
    /* Chart Card Enhancement */
    .chart-card {
        border-radius: 1.2rem;
        background: rgba(33, 35, 42, 0.92);
        border: 1px solid rgba(167, 139, 250, 0.15);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        padding: 1.2rem;
        margin-bottom: 0;
        transition: all 0.3s ease;
    }
    
    .chart-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 32px rgba(29, 185, 84, 0.15);
        border-color: rgba(29, 185, 84, 0.3);
    }
    
    .chart-header {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        margin-bottom: 0.8rem;
        padding-bottom: 0.6rem;
        border-bottom: 1px solid rgba(167, 139, 250, 0.1);
    }
    
    .chart-header-icon {
        font-size: 1.1rem;
        color: #1db954;
        background: rgba(29, 185, 84, 0.1);
        border-radius: 50%;
        width: 2.2rem;
        height: 2.2rem;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
    }
    
    .chart-card:hover .chart-header-icon {
        background: rgba(29, 185, 84, 0.2);
        transform: rotate(15deg);
    }
    
    .chart-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #e0e0e0;
        margin: 0;
    }
    
    /* Plot sizing fix */
    .plot-container {
        height: 280px;
        overflow: visible;
    }
    
    /* Make sure plot container fits properly */
    .js-plotly-plot {
        max-height: 280px;
    }
    
    /* Stats card styling */
    .stats-card {
        border-radius: 1.2rem;
        background: rgba(33, 35, 42, 0.92);
        border: 1px solid rgba(167, 139, 250, 0.15);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        padding: 1.2rem;
        margin-bottom: 0;
        transition: all 0.3s ease;
    }
    
    .stats-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 32px rgba(167, 139, 250, 0.15);
        border-color: rgba(167, 139, 250, 0.3);
    }
    
    /* Table styling */
    .metrics-comparison-table {
        margin-bottom: 0 !important;
    }
    
    .metrics-comparison-table table {
        border-collapse: separate;
        border-spacing: 0;
        width: 100%;
        background: transparent !important;
        overflow: hidden;
        border-radius: 0.8rem;
        margin-bottom: 0;
    }
    
    .metrics-comparison-table th {
        background: linear-gradient(90deg, #1db954 0%, #43e97b 100%) !important;
        color: white !important;
        font-weight: 700;
        font-size: 1rem;
        padding: 0.7rem 1rem;
        text-align: left;
    }
    
    .metrics-comparison-table td {
        background: transparent !important;
        color: white !important;
        font-size: 1rem;
        padding: 0.6rem 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        font-family: 'Inter', 'Roboto', sans-serif;
    }
    
    .metrics-comparison-table tr:nth-child(even) td {
        background: rgba(255, 255, 255, 0.02) !important;
    }
    
    .metrics-comparison-table tr:hover td {
        background: rgba(167, 139, 250, 0.08) !important;
    }
    
    /* AI Analysis card */
    .ai-analysis-card {
        border-radius: 1.2rem;
        background: rgba(33, 35, 42, 0.92);
        border: 1px solid rgba(167, 139, 250, 0.15);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        padding: 1.2rem;
        margin-bottom: 0;
        transition: all 0.3s ease;
    }
    
    .ai-analysis-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 32px rgba(122, 94, 233, 0.15);
        border-color: rgba(122, 94, 233, 0.3);
    }
    
    .ai-header {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        margin-bottom: 0.8rem;
        padding-bottom: 0.6rem;
        border-bottom: 1px solid rgba(167, 139, 250, 0.1);
    }
    
    .ai-header-icon {
        font-size: 1.1rem;
        color: #a78bfa;
        background: rgba(167, 139, 250, 0.1);
        border-radius: 50%;
        width: 2.2rem;
        height: 2.2rem;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
    }
    
    .ai-analysis-card:hover .ai-header-icon {
        background: rgba(167, 139, 250, 0.2);
        transform: rotate(15deg);
    }
    
    .ai-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #e0e0e0;
        margin: 0;
    }
    
    .ai-suggestion-content {
        line-height: 1.6;
        color: #e0e0e0;
        font-size: 1rem;
        margin-bottom: 0;
    }
    
    .glow-effect {
        color: #a78bfa;
        font-weight: 700;
        position: relative;
    }
    
    .glow-effect::after {
        content: '';
        position: absolute;
        left: 0;
        right: 0;
        bottom: -2px;
        height: 1px;
        background: #a78bfa;
        opacity: 0.5;
    }
    """
    
    # Include interactive JavaScript
    interactive_js = get_interactive_js() + """
    // Add interactive elements specifically for the individual stock page
    document.addEventListener('DOMContentLoaded', function() {
        // Add hover effects to chart
        const chartCard = document.querySelector('.chart-card');
        if (chartCard) {
            const plot = chartCard.querySelector('.js-plotly-plot');
            if (plot) {
                plot.style.transition = 'all 0.3s ease';
                chartCard.addEventListener('mouseover', function() {
                    plot.style.transform = 'scale(1.02)';
                });
                chartCard.addEventListener('mouseout', function() {
                    plot.style.transform = 'scale(1)';
                });
            }
        }
        
        // Add row highlight that syncs with data points
        const tableRows = document.querySelectorAll('.metrics-comparison-table tbody tr');
        tableRows.forEach(row => {
            row.addEventListener('mouseenter', function() {
                this.style.background = 'rgba(167, 139, 250, 0.08)';
            });
            row.addEventListener('mouseleave', function() {
                this.style.background = '';
            });
        });
    });
    """
    
    return ui.TagList(
        ui.tags.style(custom_css),
        ui.tags.script(interactive_js),
        ui.tags.div(
            # Layout: sidebar (left) and main content (right)
            ui.tags.div(
                # Sidebar (fixed width, left)
                ui.tags.div(
                    # Logo/Icon
                    ui.tags.div(
                        ui.tags.i(class_="fa fa-chart-line"),
                        class_="module-icon"
                    ),
                    # Title
                    ui.h2("Individual Stock", class_="animated-gradient-text"),
                    ui.p("Detailed volatility analysis.", class_="module-subtitle"),
                    
                    # Stock Selection
                    ui.h4("Select Stock"),
                    ui.tags.div(
                        ui.input_select("stock_id", "Stock ID", stock_ids, width="100%"),
                        class_="module-input"
                    ),
                    
                    # Stock Stats Summary
                    ui.tags.div(
                        ui.tags.div("Analysis for Stock ID", class_="stats-title"),
                        ui.output_ui("stock_analysis_output"),
                        class_="stock-summary"
                    ),
                    
                    class_="sidebar-card"
                ),
                
                # Main content (right)
                ui.tags.div(
                    # Header area
                    ui.tags.div(
                        ui.tags.div(
                            ui.tags.i(class_="fa fa-chart-line"),
                            class_="content-header-icon"
                        ),
                        ui.tags.h2("Individual Stock Analysis", class_="content-title"),
                        class_="content-header"
                    ),
                    ui.tags.div(
                        f"Detailed volatility analysis for stocks in your portfolio.",
                        class_="content-subtitle"
                    ),
                
                    # Volatility Chart
                    ui.tags.div(
                        ui.tags.div(
                            ui.tags.div(
                                ui.tags.i(class_="fa fa-chart-line"),
                                class_="chart-header-icon"
                            ),
                            ui.tags.h3("Volatility Over Time", class_="chart-title"),
                            class_="chart-header"
                        ),
                        ui.tags.div(
                            ui.output_plot("stock_volatility_plot", height="280px", width="100%"),
                            class_="plot-container"
                        ),
                        class_="chart-card",
                        style="animation-delay: 0.1s"
                    ),
                    
                    # Financial Statistics
                    ui.tags.div(
                        ui.tags.div(
                            ui.tags.div(
                                ui.tags.i(class_="fa fa-table"),
                                class_="chart-header-icon"
                            ),
                            ui.tags.h3("Financial Statistics Summary", class_="chart-title"),
                            class_="chart-header"
                        ),
                        ui.tags.div(
                            ui.output_data_frame("stock_metrics_table"),
                            class_="metrics-comparison-table"
                        ),
                        class_="stats-card",
                        style="animation-delay: 0.2s"
                    ),
                    
                    # AI Analysis
                    ui.tags.div(
                        ui.tags.div(
                            ui.tags.div(
                                ui.tags.i(class_="fa fa-lightbulb"),
                                class_="ai-header-icon"
                            ),
                            ui.tags.h3("AI Analysis", class_="ai-title"),
                            class_="ai-header"
                        ),
                        ui.output_ui("stock_ai_suggestion"),
                        class_="ai-analysis-card",
                        style="animation-delay: 0.3s"
                    ),
                    
                    class_="main-content stagger-cards"
                ),
                class_="module-layout"
            )
        )
    )


def server_individual_stock(input, output, session):
    # Get the list of available stock IDs from the vol_df (make sure they are integers or strings)
    stock_ids = [str(col) for col in vol_df.columns if col != 'time_id']

    @reactive.Calc
    def stock_data():
        stock_id = input.stock_id()  # Get the selected stock ID
        if stock_id:
            # Filter the data for the selected stock_id
            stock_data = vol_df[['time_id', stock_id]].copy()
            stock_data.columns = ['time_id', 'volatility']
            return stock_data
        else:
            return pd.DataFrame(columns=['time_id', 'volatility'])

    # Display volatility for the selected stock in the output UI
    @output
    @render.ui
    def stock_analysis_output():
        data = stock_data()
        if not data.empty:
            avg_vol = data['volatility'].mean()
            min_vol = data['volatility'].min()
            max_vol = data['volatility'].max()
            return ui.HTML(
                f"""
                <div class="stat-item">
                    <span class="stat-label">ID:</span>
                    <span class="stat-value id-highlight">{input.stock_id()}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Average Volatility:</span>
                    <span class="stat-value">{avg_vol:.4f}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Min Volatility:</span>
                    <span class="stat-value">{min_vol:.4f}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Max Volatility:</span>
                    <span class="stat-value">{max_vol:.4f}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Range:</span>
                    <span class="stat-value">{max_vol - min_vol:.4f}</span>
                </div>
                """
            )
        return "No data available for the selected stock."

    # Plot volatility over time for the selected stock
    @output
    @render.plot
    def stock_volatility_plot():
        data = stock_data()
        if not data.empty:
            fig, ax = plt.subplots(figsize=(10, 3.2))
            
            # Set dark background
            fig.patch.set_facecolor('#23272f')
            ax.set_facecolor('#23272f')
            
            # Plot data with enhanced styling
            ax.plot(data['time_id'], data['volatility'], label=f"Volatility for Stock ID {input.stock_id()}",
                   color='#1db954', linewidth=2.5, alpha=0.9)
            
            # Add area under the curve with gradient
            ax.fill_between(data['time_id'], data['volatility'], alpha=0.2, color='#1db954')
            
            # Add points to highlight the data
            ax.scatter(data['time_id'], data['volatility'], 
                      color='#a78bfa', s=30, zorder=5, alpha=0.8)
            
            # Add horizontal lines to show mean and key levels
            mean_vol = data['volatility'].mean()
            ax.axhline(y=mean_vol, color='#ff9800', linestyle='--', alpha=0.7, 
                      linewidth=1.5, label=f"Mean: {mean_vol:.4f}")
            
            # Highlight periods of high volatility
            high_threshold = data['volatility'].quantile(0.75)
            ax.axhline(y=high_threshold, color='#ff5252', linestyle=':', alpha=0.5,
                      linewidth=1, label=f"Upper Quartile: {high_threshold:.4f}")
            
            # Styling
            ax.set_xlabel('Time ID', color='white', fontsize=12)
            ax.set_ylabel('Realized Volatility', color='white', fontsize=12)
            ax.set_title(f"Volatility Over Time for Stock ID {input.stock_id()}", 
                        fontsize=14, fontweight='bold', color='#1db954')
            
            ax.tick_params(axis='x', colors='#a78bfa')
            ax.tick_params(axis='y', colors='#a78bfa')
            ax.grid(True, alpha=0.2, color='#a78bfa', linestyle='--')
            
            # Style the spines
            for spine in ax.spines.values():
                spine.set_color('#444')
                
            ax.legend(facecolor='#2d3748', edgecolor='#444', 
                    fontsize=10, loc='upper right', framealpha=0.9)
            
            plt.tight_layout()
            return fig
        else:
            # Return empty plot with message
            fig, ax = plt.subplots(figsize=(10, 4))
            fig.patch.set_facecolor('#23272f')
            ax.set_facecolor('#23272f')
            ax.text(0.5, 0.5, "No data available", 
                   ha='center', va='center', color='#a78bfa', fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)
            return fig

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
            # Split into parts for styling
            parts = suggestion.split('. ')
            styled_parts = []
            for i, part in enumerate(parts):
                if i < len(parts) - 1:  # Add period back except for last part
                    part = part + '.'
                # Add highlight class to important terms
                for term in ['buy', 'sell', 'hold', 'recommend', 'purchase', 'investment']:
                    if term in part.lower():
                        part = part.replace(term, f'<span class="glow-effect">{term}</span>')
                styled_parts.append(part)
            
            styled_suggestion = ' '.join(styled_parts)
            return ui.tags.div(
                ui.HTML(f'<p class="ai-suggestion-content">{styled_suggestion}</p>')
            )
        except Exception as e:
            return f"Error getting suggestion: {e}"
