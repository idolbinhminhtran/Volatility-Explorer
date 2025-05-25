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
import numpy as np
import mplcursors
from matplotlib.patheffects import withStroke


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


# Load and prepare predicted volatility data
PRED_VOL_PATH = os.path.join(_project_dir, 'data', 'predicted_realized_vol.csv')
predicted_vol_df = None
if os.path.exists(PRED_VOL_PATH):
    predicted_vol_df = pd.read_csv(PRED_VOL_PATH)
    predicted_vol_df['stock_id'] = predicted_vol_df['stock_id'].astype(str)


# Define the UI for Individual Stock Analysis

def ui_individual_stock(stock_ids):
    # Use common and effects CSS for sidebar and layout consistency
    custom_css = get_common_css() + get_effects_css() + """
    /* Additional Individual Stock custom styles here if needed */
    """

    return ui.TagList(
        ui.tags.style(custom_css),
        ui.tags.div(
            # Sidebar
            ui.tags.div(
                ui.tags.div(
                    ui.tags.i(class_="fa fa-chart-line"),
                    class_="module-icon float-effect"
                ),
                ui.h2("Individual Stock Analysis", class_="animated-gradient-text"),
                ui.p("Detailed volatility analysis and forecasting for the selected stock.", class_="module-subtitle"),
                ui.h4("Select Stock"),
                ui.tags.div(
                    ui.input_select("stock_id", "", stock_ids, width="100%"),
                    class_="module-input"
                ),
                class_="sidebar-card"
            ),
            # Main content (vertical: Volatility Over Time on top, Financial Metrics below)
            ui.tags.div(
                # Volatility Over Time Card
                ui.tags.div(
                    ui.tags.div(
                        ui.tags.i(class_="fa fa-chart-area"),
                        ui.h3("Volatility Over Time", class_="card-title"),
                        class_="metrics-header"
                    ),
                    ui.output_plot("stock_volatility_plot"),
                    class_="content-card hover-card slide-in-up",
                    style="margin-bottom:1.5rem;"
                ),
                # Financial Metrics Card (modern table style)
                ui.tags.div(
                    ui.tags.div(
                        ui.tags.i(class_="fa fa-calculator"),
                        ui.h3("Financial Metrics", class_="card-title"),
                        class_="metrics-header"
                    ),
                    ui.tags.div(
                        # Table container
                        ui.tags.table(
                            # Table header
                            ui.tags.thead(
                                ui.tags.tr(
                                    ui.tags.th("Metric", class_="metric-header"),
                                    ui.tags.th("Value", class_="value-header"),
                                )
                            ),
                            # Table body
                            ui.tags.tbody(
                                ui.tags.tr(
                                    ui.tags.td(
                                        ui.tags.i(class_="fa fa-chart-bar metric-icon"),
                                        "Average Volatility",
                                        class_="metric-cell"
                                    ),
                                    ui.tags.td(
                                        ui.output_text("avg_volatility"),
                                        class_="value-cell highlight-green"
                                    ),
                                    class_="metric-row"
                                ),
                                ui.tags.tr(
                                    ui.tags.td(
                                        ui.tags.i(class_="fa fa-arrow-down metric-icon"),
                                        "Minimum Volatility",
                                        class_="metric-cell"
                                    ),
                                    ui.tags.td(
                                        ui.output_text("min_volatility"),
                                        class_="value-cell highlight-blue"
                                    ),
                                    class_="metric-row"
                                ),
                                ui.tags.tr(
                                    ui.tags.td(
                                        ui.tags.i(class_="fa fa-arrow-up metric-icon"),
                                        "Maximum Volatility",
                                        class_="metric-cell"
                                    ),
                                    ui.tags.td(
                                        ui.output_text("max_volatility"),
                                        class_="value-cell highlight-red"
                                    ),
                                    class_="metric-row"
                                ),
                                ui.tags.tr(
                                    ui.tags.td(
                                        ui.tags.i(class_="fa fa-ruler-horizontal metric-icon"),
                                        "Volatility Range",
                                        class_="metric-cell"
                                    ),
                                    ui.tags.td(
                                        ui.output_text("range_volatility"),
                                        class_="value-cell highlight-purple"
                                    ),
                                    class_="metric-row"
                                ),
                                ui.tags.tr(
                                    ui.tags.td(
                                        ui.tags.i(class_="fa fa-chart-line metric-icon"),
                                        "Standard Deviation",
                                        class_="metric-cell"
                                    ),
                                    ui.tags.td(
                                        ui.output_text("std_volatility"),
                                        class_="value-cell highlight-orange"
                                    ),
                                    class_="metric-row"
                                ),
                                ui.tags.tr(
                                    ui.tags.td(
                                        ui.tags.i(class_="fa fa-magic metric-icon"),
                                        "Predicted Volatility",
                                        class_="metric-cell"
                                    ),
                                    ui.tags.td(
                                        ui.output_text("pred_volatility"),
                                        class_="value-cell highlight-teal"
                                    ),
                                    class_="metric-row"
                                ),
                            ),
                            class_="metrics-table",
                            style="""
                                width: 100%;
                                border-collapse: separate;
                                border-spacing: 0 0.5rem;
                                margin: 1rem 0;
                            """
                        ),
                        style="""
                            background: linear-gradient(145deg, rgba(31,41,55,0.4) 0%, rgba(17,24,39,0.4) 100%);
                            border-radius: 1rem;
                            padding: 1.5rem;
                            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
                        """
                    ),
                    ui.tags.style("""
                        .metrics-table th {
                            text-align: left;
                            padding: 1rem;
                            color: #94a3b8;
                            font-size: 0.875rem;
                            text-transform: uppercase;
                            letter-spacing: 0.05em;
                            border-bottom: 2px solid rgba(148,163,184,0.1);
                        }
                        .metrics-table td {
                            padding: 1rem;
                            transition: all 0.2s;
                        }
                        .metric-cell {
                            display: flex;
                            align-items: center;
                            gap: 0.75rem;
                            color: #e2e8f0;
                            font-weight: 500;
                        }
                        .value-cell {
                            font-family: monospace;
                            font-size: 1.1rem;
                            font-weight: 600;
                            border-radius: 0.5rem;
                        }
                        .metric-row {
                            background: rgba(30,41,59,0.5);
                            border-radius: 0.5rem;
                            transition: transform 0.2s;
                        }
                        .metric-row:hover {
                            transform: translateX(0.25rem);
                            background: rgba(30,41,59,0.8);
                        }
                        .metric-icon {
                            width: 1.5rem;
                            height: 1.5rem;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            border-radius: 0.375rem;
                            background: rgba(255,255,255,0.1);
                        }
                        .highlight-green { color: #4ade80; }
                        .highlight-blue { color: #60a5fa; }
                        .highlight-red { color: #f87171; }
                        .highlight-purple { color: #a78bfa; }
                        .highlight-orange { color: #fb923c; }
                        .highlight-teal { color: #2dd4bf; }
                    """),
                    class_="content-card hover-card slide-in-up",
                    style="max-width:800px;"
                ),
                class_="main-content",
                style="display:flex;flex-direction:column;align-items:stretch;gap:0;"
            ),
            class_="module-layout"
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
            stock_id = input.stock_id()
            
            # Get predicted volatility if available
            pred_vol_html = ""
            if predicted_vol_df is not None:
                pred_vol_row = predicted_vol_df[predicted_vol_df['stock_id'] == stock_id]
                if not pred_vol_row.empty:
                    pred_vol = pred_vol_row['predicted_realized_vol'].values[0]
                    pred_vol_html = f"""
                    <div class="stat-item">
                        <span class="stat-label">Predicted Volatility:</span>
                        <span class="stat-value highlight-pred">{pred_vol:.6f}</span>
                    </div>
                    """
            
            return ui.HTML(
                f"""
                <div class="stat-item">
                    <span class="stat-label">ID:</span>
                    <span class="stat-value id-highlight">{stock_id}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Average Volatility:</span>
                    <span class="stat-value">{avg_vol:.6f}</span>
                </div>
                {pred_vol_html}
                <div class="stat-item">
                    <span class="stat-label">Min Volatility:</span>
                    <span class="stat-value">{min_vol:.6f}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Max Volatility:</span>
                    <span class="stat-value">{max_vol:.6f}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Range:</span>
                    <span class="stat-value">{max_vol - min_vol:.6f}</span>
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
            # Set style for modern dark theme
            plt.style.use('dark_background')
            fig, ax = plt.subplots(figsize=(12, 5))
            
            # Enhanced background with gradient
            bg_gradient = np.linspace(0, 1, 2)
            bg_gradient = np.vstack((bg_gradient, bg_gradient))
            ax.imshow(bg_gradient, extent=[0, len(data), 0, max(data['volatility'])*1.1],
                     aspect='auto', alpha=0.1, cmap='coolwarm')
            
            # Set modern dark background
            fig.patch.set_facecolor('#1a1b23')
            ax.set_facecolor('#1f2937')
            
            # Add stylish grid
            ax.grid(True, linestyle='--', alpha=0.1, color='#4b5563')
            
            # Plot volatility as a simple line chart (white line)
            ax.plot(
                data['time_id'],
                data['volatility'],
                label='Actual Values',
                color='white',
                linewidth=2.5,
                alpha=0.9,
                zorder=3,
            )
            
            # Add mean line with enhanced styling
            mean_vol = data['volatility'].mean()
            mean_line = ax.axhline(y=mean_vol, color='#f59e0b', linestyle='--',
                                 alpha=0.7, linewidth=1.5,
                                 label=f"Mean: {mean_vol:.6f}", zorder=1)
            
            # Add predicted volatility if available
            stock_id = input.stock_id()
            if predicted_vol_df is not None:
                pred_vol_row = predicted_vol_df[predicted_vol_df['stock_id'] == stock_id]
                if not pred_vol_row.empty:
                    pred_vol = pred_vol_row['predicted_realized_vol'].values[0]
                    pred_line = ax.axhline(y=pred_vol, color='#43e97b',
                                         linestyle='-', alpha=0.9, linewidth=2,
                                         label=f"Predicted: {pred_vol:.6f}", zorder=1)
            
            # Add upper quartile line with pulse animation
            high_threshold = data['volatility'].quantile(0.75)
            quartile_line = ax.axhline(y=high_threshold, color='#ef4444',
                                     linestyle=':', alpha=0.5, linewidth=1.5,
                                     label=f"Upper Quartile: {high_threshold:.6f}",
                                     zorder=1)
            
            # Enhanced styling with modern fonts
            ax.set_xlabel('Time ID', color='#e5e7eb', fontsize=12,
                         fontweight='bold', labelpad=10)
            ax.set_ylabel('Realized Volatility', color='#e5e7eb',
                         fontsize=12, fontweight='bold', labelpad=10)
            
            title = ax.set_title(f"Volatility Over Time for Stock ID {input.stock_id()}",
                               fontsize=16, fontweight='bold', color='#1db954',
                               pad=20, path_effects=[withStroke(linewidth=3, foreground='#1f2937')])
            
            # Style the axis with modern look
            ax.tick_params(axis='x', colors='#a78bfa', labelsize=10, length=6, rotation=45)
            ax.tick_params(axis='y', colors='#a78bfa', labelsize=10, length=6)
            
            # Enhanced spines
            for spine in ax.spines.values():
                spine.set_color('#4b5563')
                spine.set_linewidth(0.5)
            
            # Create modern legend with hover effect
            legend = ax.legend(loc='upper right', framealpha=0.95,
                             facecolor='#1f2937', edgecolor='#4b5563',
                             labelcolor='white', fontsize=10,
                             title='Metrics', title_fontsize=11)
            legend.get_frame().set_boxstyle('round,pad=0.5')
            legend.get_frame().set_linewidth(1)
            
            # Adjust layout
            fig.subplots_adjust(left=0.08, right=0.97, bottom=0.17, top=0.88)
            plt.tight_layout()
            
            return fig
        else:
            # Create empty plot with enhanced message
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.text(0.5, 0.5, 'No data available for this stock',
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=14, color='#a78bfa',
                   fontweight='bold', path_effects=[withStroke(linewidth=3,
                                                             foreground='#1f2937')])
            ax.set_facecolor('#1f2937')
            fig.patch.set_facecolor('#1a1b23')
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_color('#4b5563')
            plt.tight_layout()
            return fig

    @output
    @render.ui
    def volatility_analysis():
        data = stock_data()
        if data.empty:
            return None
            
        stock_id = input.stock_id()
        if predicted_vol_df is None:
            return None
            
        pred_vol_row = predicted_vol_df[predicted_vol_df['stock_id'] == stock_id]
        if pred_vol_row.empty:
            return None
            
        # Get the predicted and actual volatility
        pred_vol = pred_vol_row['predicted_realized_vol'].values[0]
        actual_vol = data['volatility'].mean()
        
        # Calculate the difference as a percentage
        diff = actual_vol - pred_vol
        diff_percent = (diff / pred_vol * 100) if pred_vol != 0 else 0
        
        # Create messaging based on the difference
        if abs(diff_percent) < 10:
            message = "The model prediction is very close to the actual observed volatility, indicating high accuracy."
            css_class = ""
        elif diff_percent > 0:
            message = "Actual volatility is higher than predicted. The stock may be experiencing more market uncertainty than expected."
            css_class = "positive"  # positive difference (actual > predicted)
        else:
            message = "Actual volatility is lower than predicted. The stock may be more stable than the model anticipated."
            css_class = "negative"  # negative difference (actual < predicted)
        
        return ui.HTML(
            f"""
            <div class="volatility-analysis">
                <div class="stats-title">Volatility Prediction Analysis</div>
                <div class="volatility-diff {css_class}">
                    {abs(diff_percent):.2f}% {'Above' if diff_percent > 0 else 'Below'} Prediction
                </div>
                <div class="volatility-message">
                    {message}
                </div>
            </div>
            """
        )

    @output
    @render.table
    def metrics_table():
        stock_id = input.stock_id()
        if not stock_id or stock_id not in metrics_df['stock_id'].values:
            return pd.DataFrame({"Metric": ["No data available"]})
        
        stock_metrics = metrics_df[metrics_df['stock_id'] == stock_id].iloc[0]
        
        # Create a DataFrame with metrics and values
        metrics_to_show = ['avg_bid_size1', 'avg_ask_size1', 'avg_spread']
        data = {"Metric": [], "Value": []}
        
        for metric in metrics_to_show:
            if metric in stock_metrics:
                label = metric_labels.get(metric, metric.replace('_', ' ').title())
                data["Metric"].append(label)
                data["Value"].append(f"{stock_metrics[metric]:.6f}")
                
        # Add predicted volatility if available
        if predicted_vol_df is not None:
            pred_vol_row = predicted_vol_df[predicted_vol_df['stock_id'] == stock_id]
            if not pred_vol_row.empty:
                data["Metric"].append("Predicted Volatility")
                data["Value"].append(f"{pred_vol_row['predicted_realized_vol'].values[0]:.6f}")
        
        return pd.DataFrame(data)

    @output
    @render.ui
    def stock_ai_suggestion():
        stock_id = input.stock_id()
        df = metrics_df[metrics_df['stock_id'] == stock_id].iloc[0][metric_choices]
        if not stock_id or df is None or df.empty:
            return "No financial statistics to analyze."
        
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
            
            # Split into analysis and recommendation
            parts = suggestion.split('. ')
            analysis = '. '.join(parts[:-1]) + '.'
            recommendation = parts[-1]
            
            # Add highlight class to important terms
            highlight_terms = ['buy', 'sell', 'hold', 'recommend', 'purchase', 'investment',
                             'positive', 'negative', 'upward', 'downward', 'trend']
            
            for term in highlight_terms:
                if term in analysis.lower():
                    analysis = analysis.replace(term, f'<span class="glow-effect">{term}</span>')
                if term in recommendation.lower():
                    recommendation = recommendation.replace(term, f'<span class="glow-effect">{term}</span>')
            
            return ui.tags.div(
                ui.tags.div(
                    ui.tags.i(class_="fa fa-chart-line"),
                    ui.tags.span("Analysis", class_="insight-tag"),
                    ui.HTML(f'<p class="ai-suggestion-content">{analysis}</p>'),
                    class_="insight-section"
                ),
                ui.tags.div(
                    ui.tags.i(class_="fa fa-lightbulb"),
                    ui.tags.span("Recommendation", class_="insight-tag"),
                    ui.HTML(f'<p class="ai-suggestion-content">{recommendation}</p>'),
                    class_="insight-section"
                )
            )
        except Exception as e:
            return f"Error getting suggestion: {e}"

    # Add server-side rendering for financial metrics
    @output
    @render.text
    def avg_bid_size():
        stock_id = input.stock_id()
        if stock_id and stock_id in metrics_df['stock_id'].values:
            return f"{metrics_df[metrics_df['stock_id'] == stock_id]['avg_bid_size1'].values[0]:.6f}"
        return "N/A"

    @output
    @render.text
    def avg_ask_size():
        stock_id = input.stock_id()
        if stock_id and stock_id in metrics_df['stock_id'].values:
            return f"{metrics_df[metrics_df['stock_id'] == stock_id]['avg_ask_size1'].values[0]:.6f}"
        return "N/A"

    @output
    @render.text
    def avg_spread():
        stock_id = input.stock_id()
        if stock_id and stock_id in metrics_df['stock_id'].values:
            return f"{metrics_df[metrics_df['stock_id'] == stock_id]['avg_spread'].values[0]:.6f}"
        return "N/A"

    @output
    @render.text
    def pred_volatility():
        stock_id = input.stock_id()
        if predicted_vol_df is not None and stock_id in predicted_vol_df['stock_id'].values:
            return f"{predicted_vol_df[predicted_vol_df['stock_id'] == stock_id]['predicted_realized_vol'].values[0]:.6f}"
        return "N/A"

    @output
    @render.text
    def avg_volatility():
        stock_id = input.stock_id()
        data = vol_df[["time_id", stock_id]].copy() if stock_id in vol_df.columns else None
        if data is not None and not data.empty:
            return f"{data[stock_id].mean():.6f}"
        return "N/A"

    @output
    @render.text
    def min_volatility():
        stock_id = input.stock_id()
        data = vol_df[["time_id", stock_id]].copy() if stock_id in vol_df.columns else None
        if data is not None and not data.empty:
            return f"{data[stock_id].min():.6f}"
        return "N/A"

    @output
    @render.text
    def max_volatility():
        stock_id = input.stock_id()
        data = vol_df[["time_id", stock_id]].copy() if stock_id in vol_df.columns else None
        if data is not None and not data.empty:
            return f"{data[stock_id].max():.6f}"
        return "N/A"

    @output
    @render.text
    def range_volatility():
        stock_id = input.stock_id()
        data = vol_df[["time_id", stock_id]].copy() if stock_id in vol_df.columns else None
        if data is not None and not data.empty:
            return f"{(data[stock_id].max() - data[stock_id].min()):.6f}"
        return "N/A"

    @output
    @render.text
    def std_volatility():
        stock_id = input.stock_id()
        data = vol_df[["time_id", stock_id]].copy() if stock_id in vol_df.columns else None
        if data is not None and not data.empty:
            return f"{data[stock_id].std():.6f}"
        return "N/A"

    @output
    @render.text
    def stock_title():
        stock_id = input.stock_id()
        return f"Stock {stock_id} Analysis"

    @output
    @render.text
    def model_accuracy():
        stock_id = input.stock_id()
        if predicted_vol_df is not None and stock_id in predicted_vol_df['stock_id'].values:
            pred_vol = predicted_vol_df[predicted_vol_df['stock_id'] == stock_id]['predicted_realized_vol'].values[0]
            actual_vol = vol_df[stock_id].mean()
            accuracy = ((pred_vol - actual_vol) / actual_vol) * 100
            return f"{accuracy:.2f}%"
        return "N/A"

    @output
    @render.table
    def comparison_table():
        stock_id = input.stock_id()
        if not stock_id or stock_id not in metrics_df['stock_id'].values:
            return pd.DataFrame()
        
        # Get comparison stocks (e.g., 3 stocks including the selected one)
        comparison_stocks = [stock_id]
        other_stocks = [s for s in metrics_df['stock_id'].values if s != stock_id]
        comparison_stocks.extend(other_stocks[:2])  # Add 2 more stocks for comparison
        
        # Select metrics to display
        metrics_to_show = ['avg_mid_price', 'total_return', 'avg_spread', 
                          'avg_bid_size1', 'avg_ask_size1', 'order_imbalance', 'vwap']
        
        # Create comparison DataFrame
        comparison_data = metrics_df[metrics_df['stock_id'].isin(comparison_stocks)][['stock_id'] + metrics_to_show]
        
        # Transpose for better display
        comparison_data_t = comparison_data.set_index('stock_id').T