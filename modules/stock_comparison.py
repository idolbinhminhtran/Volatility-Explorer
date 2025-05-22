import pandas as pd
import matplotlib.pyplot as plt
from shiny import ui, render, reactive
from faicons import icon_svg
from modules.screener import vol_df, stock_cols  # Make sure you import the necessary data
import os
from dotenv import load_dotenv
import openai
from modules.common_style import get_common_css
from modules.visual_effects import get_effects_css, get_interactive_js


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
    # Use the common CSS and add any specific CSS for this module
    custom_css = get_common_css() + get_effects_css() + """
    .compare-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        width: 100%;
        margin-bottom: 2rem;
    }
    
    .metrics-comparison-table {
        width: 100%;
        margin-bottom: 1.2rem;
        transform: translateY(10px);
        opacity: 0;
        animation: slideInUp 0.8s cubic-bezier(0.165, 0.84, 0.44, 1) forwards;
    }
    
    .comparison-subtitle {
        font-size: 1.25rem;
        font-weight: 900;
        margin-bottom: 0.5rem;
        color: #1db954;
        background: linear-gradient(90deg, #1db954 60%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        transition: all 0.3s ease;
    }
    
    .content-card:hover .comparison-subtitle {
        background: linear-gradient(90deg, #a78bfa 60%, #1db954 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Stock select indicators with animation */
    .sidebar-card .select-group {
        position: relative;
        margin-bottom: 1.5rem;
        transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
    }
    
    .sidebar-card .stock-indicator {
        position: absolute;
        left: -20px;
        top: 50%;
        transform: translateY(-50%);
        width: 8px;
        height: 8px;
        border-radius: 50%;
        opacity: 0;
        transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
        box-shadow: 0 0 0 0 rgba(29,185,84,0.7);
    }
    
    .sidebar-card .select-group:hover {
        transform: translateX(5px);
    }
    
    .sidebar-card .select-group:hover .stock-indicator {
        opacity: 1;
        transform: translateY(-50%) scale(1.5);
        animation: pulseScale 2s infinite;
    }
    
    .sidebar-card .stock-indicator.stock1 { background: #1db954; }
    .sidebar-card .stock-indicator.stock2 { background: #a78bfa; }
    .sidebar-card .stock-indicator.stock3 { background: #ff9800; }
    
    /* Enhanced comparison plot */
    .comparison-plot {
        position: relative;
        overflow: hidden;
        padding: 15px;
        border-radius: 8px;
    }
    
    .comparison-plot::before {
        content: '';
        position: absolute;
        top: -10px; right: -10px; bottom: -10px; left: -10px;
        background: linear-gradient(135deg, rgba(29,185,84,0.05), rgba(167,139,250,0.05));
        border-radius: 12px;
        z-index: -1;
        transition: opacity 0.3s;
        opacity: 0.5;
    }
    
    .content-card:hover .comparison-plot::before {
        opacity: 1;
    }
    
    /* Legend items with hover effect */
    .legend-item {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 15px;
        margin-right: 10px;
        margin-bottom: 8px;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        cursor: pointer;
    }
    
    .legend-item:hover {
        transform: translateY(-2px) scale(1.05);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .legend-item.stock1 {
        background-color: rgba(29,185,84,0.15);
        color: #1db954;
    }
    
    .legend-item.stock2 {
        background-color: rgba(167,139,250,0.15);
        color: #a78bfa;
    }
    
    .legend-item.stock3 {
        background-color: rgba(255,152,0,0.15);
        color: #ff9800;
    }
    
    /* Analysis text fade-in */
    .analysis-text {
        opacity: 0;
        animation: fadeIn 0.5s forwards;
    }
    
    .stock1-analysis { animation-delay: 0.2s; }
    .stock2-analysis { animation-delay: 0.4s; }
    .stock3-analysis { animation-delay: 0.6s; }
    
    /* Animated value indicator */
    @keyframes pulse-bg {
        0% { background-color: rgba(29,185,84,0.1); }
        50% { background-color: rgba(29,185,84,0.2); }
        100% { background-color: rgba(29,185,84,0.1); }
    }
    
    .value-highlight {
        background-color: rgba(29,185,84,0.1);
        padding: 2px 8px;
        border-radius: 10px;
        font-weight: bold;
        animation: pulse-bg 2s infinite;
    }
    
    /* Enhanced table styling */
    .dataframe th {
        position: relative;
        overflow: hidden;
    }
    
    .dataframe th::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, #1db954, #a78bfa);
        transform: scaleX(0);
        transform-origin: bottom right;
        transition: transform 0.3s;
    }
    
    .dataframe th:hover::after {
        transform: scaleX(1);
        transform-origin: bottom left;
    }
    
    /* Animated sidebar icon */
    @keyframes float {
        0% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
        100% { transform: translateY(0); }
    }
    
    .sidebar-card .module-icon {
        animation: float 3s infinite ease-in-out;
    }
    
    /* Gradient button */
    .action-btn {
        background: linear-gradient(90deg, #1db954 0%, #a78bfa 100%);
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        cursor: pointer;
        transition: transform 0.2s, box-shadow 0.2s;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        margin-top: 15px;
        box-shadow: 0 4px 10px rgba(29,185,84,0.2);
    }
    
    .action-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(29,185,84,0.3);
    }
    
    .action-btn:active {
        transform: translateY(0);
    }
    
    .action-btn i {
        font-size: 0.9em;
    }
    
    /* Layout alignment overrides */
    .module-layout { gap: 0.5rem; }
    .sidebar-card { margin-top: 80px; }
    .main-content { padding-top: 80px; }
    """
    
    # Include interactive JavaScript
    interactive_js = get_interactive_js() + """
    // Add interactive elements for stock comparison page
    document.addEventListener('DOMContentLoaded', function() {
        // Create interactive legend for the comparison chart
        setTimeout(() => {
            const legendItems = document.querySelectorAll('.legend-item');
            const plotLines = document.querySelectorAll('.js-line-path');
            
            if (legendItems.length > 0 && plotLines.length > 0) {
                legendItems.forEach((item, index) => {
                    item.addEventListener('mouseenter', () => {
                        // Highlight related line
                        if (plotLines[index]) {
                            plotLines[index].style.strokeWidth = '4px';
                            plotLines[index].style.filter = 'drop-shadow(0 0 6px rgba(255,255,255,0.5))';
                        }
                        
                        // Make other lines semi-transparent
                        plotLines.forEach((line, i) => {
                            if (i !== index) {
                                line.style.opacity = '0.3';
                            }
                        });
                    });
                    
                    item.addEventListener('mouseleave', () => {
                        // Reset all lines
                        plotLines.forEach(line => {
                            line.style.strokeWidth = '2px';
                            line.style.opacity = '1';
                            line.style.filter = 'none';
                        });
                    });
                });
            }
        }, 1000); // Delay to ensure chart is rendered
        
        // Add 3D tilt effect to all cards with hover-card class
        const hoverCards = document.querySelectorAll('.hover-card');
        hoverCards.forEach(card => {
            card.addEventListener('mousemove', function(e) {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                
                const rotateX = (y - centerY) / 25;
                const rotateY = (centerX - x) / 25;
                
                this.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'perspective(1000px) rotateX(0) rotateY(0)';
            });
        });
    });
    """
    
    return ui.TagList(
        ui.tags.style(custom_css),
        ui.tags.script(interactive_js),
        ui.tags.div(
            # Sidebar
            ui.tags.div(
                ui.tags.div(
                    ui.tags.div(ui.tags.i(class_="fa fa-scale-balanced"), class_="module-icon float-effect"),
                    class_="module-icon float-effect"
                ),
                ui.h2("Stock Comparison", class_="animated-gradient-text"),
                ui.p("Compare statistics across stocks.", class_="module-subtitle"),
                ui.h4("Select Stocks"),
                ui.tags.div(
                    ui.tags.div(class_="stock-indicator stock1"),
                    ui.tags.div(
                        ui.input_select("stock_1", "Stock 1", stock_ids),
                        class_="module-input"
                    ),
                    class_="select-group"
                ),
                ui.tags.div(
                    ui.tags.div(class_="stock-indicator stock2"),
                    ui.tags.div(
                        ui.input_select("stock_2", "Stock 2", stock_ids),
                        class_="module-input"
                    ),
                    class_="select-group"
                ),
                ui.tags.div(
                    ui.tags.div(class_="stock-indicator stock3"),
                    ui.tags.div(
                        ui.input_select("stock_3", "Stock 3", stock_ids),
                        class_="module-input"
                    ),
                    class_="select-group"
                ),
                ui.tags.button(
                    ui.tags.div(ui.tags.i(class_="fa fa-arrows-rotate"), class_="hover-icon"),
                    "Reset Selection",
                    id="reset_stocks",
                    class_="module-btn"
                ),
                class_="sidebar-card"
            ),
            # Main content
            ui.tags.div(
                # Individual stock analysis cards
                ui.tags.div(
                    ui.tags.div(
                        ui.tags.div(
                            ui.tags.div(ui.tags.i(class_="fa fa-chart-line"), class_="hover-icon"),
                            ui.tags.h3("Stock 1 Analysis", class_="comparison-subtitle"),
                            style="display:flex;align-items:center;gap:10px;"
                        ),
                        ui.output_ui("stock_1_analysis", class_="analysis-text stock1-analysis"),
                        ui.output_plot("stock_1_volatility_plot"),
                        class_="content-card hover-card slide-in-up",
                        style="border-left: 4px solid #1db954"
                    ),
                    ui.tags.div(
                        ui.tags.div(
                            ui.tags.div(ui.tags.i(class_="fa fa-chart-line"), class_="hover-icon"),
                            ui.tags.h3("Stock 2 Analysis", class_="comparison-subtitle"),
                            style="display:flex;align-items:center;gap:10px;"
                        ),
                        ui.output_ui("stock_2_analysis", class_="analysis-text stock2-analysis"),
                        ui.output_plot("stock_2_volatility_plot"),
                        class_="content-card hover-card slide-in-up",
                        style="animation-delay: 0.2s; border-left: 4px solid #a78bfa"
                    ),
                    ui.tags.div(
                        ui.tags.div(
                            ui.tags.div(ui.tags.i(class_="fa fa-chart-line"), class_="hover-icon"),
                            ui.tags.h3("Stock 3 Analysis", class_="comparison-subtitle"),
                            style="display:flex;align-items:center;gap:10px;"
                        ),
                        ui.output_ui("stock_3_analysis", class_="analysis-text stock3-analysis"),
                        ui.output_plot("stock_3_volatility_plot"),
                        class_="content-card hover-card slide-in-up",
                        style="animation-delay: 0.4s; border-left: 4px solid #ff9800"
                    ),
                    class_="compare-grid stagger-cards"
                ),
                # Comparison plot
                ui.tags.div(
                    ui.tags.div(
                        ui.tags.div(ui.tags.i(class_="fa fa-chart-area"), class_="hover-icon"),
                        ui.tags.h3("Volatility Comparison", class_="card-title"),
                        style="display:flex;align-items:center;gap:10px;"
                    ),
                    ui.tags.div(
                        ui.HTML("""
                        <div class="legend-container" style="margin-bottom:15px;text-align:center;">
                            <div class="legend-item stock1">Stock 1</div>
                            <div class="legend-item stock2">Stock 2</div>
                            <div class="legend-item stock3">Stock 3</div>
                        </div>
                        """),
                        ui.tags.div(
                            ui.output_plot("comparison_plot"),
                            class_="comparison-plot"
                        )
                    ),
                    class_="content-card hover-card slide-in-up",
                    style="animation-delay:0.6s;"
                ),
                # Financial statistics comparison
                ui.tags.div(
                    ui.tags.div(
                        ui.tags.div(ui.tags.i(class_="fa fa-table"), class_="hover-icon"),
                        ui.tags.h3("Financial Statistics Comparison", class_="card-title"),
                        style="display:flex;align-items:center;gap:10px;"
                    ),
                    ui.tags.div(
                        ui.output_data_frame("metrics_comparison_table"),
                        class_="metrics-comparison-table interactive-table"
                    ),
                    # AI suggestion
                    ui.tags.div(
                        ui.tags.div(
                            ui.tags.div(ui.tags.i(class_="fa fa-lightbulb"), class_="icon"),
                            ui.tags.span("AI Analysis"),
                            class_="ai-suggestion-header"
                        ),
                        ui.output_ui("best_stock_suggestion"),
                        class_="ai-suggestion-content"
                    ),
                    class_="content-card hover-card slide-in-up",
                    style="animation-delay:0.8s;"
                ),
                class_="main-content stagger-cards"
            ),
            class_="module-layout"
        )
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
            avg_vol = data['volatility'].mean()
            return ui.HTML(
                f"""Analysis for <span class="hover-underline">Stock {input.stock_1()}</span>: 
                Average Volatility = <span class="value-highlight">{avg_vol:.4f}</span>"""
            )
        return "No data available for the selected stock."

    @output
    @render.plot
    def stock_1_volatility_plot():
        data = stock_1_data()
        if not data.empty:
            fig, ax = plt.subplots(figsize=(8, 3))
            
            # Set dark background
            fig.patch.set_facecolor('#23272f')
            ax.set_facecolor('#23272f')
            
            # Plot data with enhanced styling
            ax.plot(data['time_id'], data['volatility'], label=f"Stock {input.stock_1()}",
                    color='#1db954', linewidth=2.5, alpha=0.9)
            
            # Add area under the curve
            ax.fill_between(data['time_id'], data['volatility'], alpha=0.2, color='#1db954')
            
            ax.set_xlabel('Time ID', color='white', fontsize=10)
            ax.set_ylabel('Volatility', color='white', fontsize=10)
            ax.set_title(f"Stock {input.stock_1()}", fontsize=11, fontweight='bold', color='#1db954')
            
            ax.tick_params(axis='x', colors='#a78bfa', labelsize=8)
            ax.tick_params(axis='y', colors='#a78bfa', labelsize=8)
            ax.grid(True, alpha=0.2, color='#a78bfa', linestyle='--')
            
            # Style the spines
            for spine in ax.spines.values():
                spine.set_color('#444')
            
            plt.tight_layout()
            return fig
        else:
            # Return empty plot with message
            fig, ax = plt.subplots(figsize=(8, 3))
            fig.patch.set_facecolor('#23272f')
            ax.set_facecolor('#23272f')
            ax.text(0.5, 0.5, "No data available", 
                   ha='center', va='center', color='#a78bfa', fontsize=12)
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)
            return fig

    # Repeat for Stock 2 and Stock 3 with different colors
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
            avg_vol = data['volatility'].mean()
            return ui.HTML(
                f"""Analysis for <span class="hover-underline">Stock {input.stock_2()}</span>: 
                Average Volatility = <span class="value-highlight">{avg_vol:.4f}</span>"""
            )
        return "No data available for the selected stock."

    @output
    @render.plot
    def stock_2_volatility_plot():
        data = stock_2_data()
        if not data.empty:
            fig, ax = plt.subplots(figsize=(8, 3))
            
            # Set dark background
            fig.patch.set_facecolor('#23272f')
            ax.set_facecolor('#23272f')
            
            # Plot data with enhanced styling
            ax.plot(data['time_id'], data['volatility'], label=f"Stock {input.stock_2()}",
                    color='#a78bfa', linewidth=2.5, alpha=0.9)
            
            # Add area under the curve
            ax.fill_between(data['time_id'], data['volatility'], alpha=0.2, color='#a78bfa')
            
            ax.set_xlabel('Time ID', color='white', fontsize=10)
            ax.set_ylabel('Volatility', color='white', fontsize=10)
            ax.set_title(f"Stock {input.stock_2()}", fontsize=11, fontweight='bold', color='#a78bfa')
            
            ax.tick_params(axis='x', colors='#a78bfa', labelsize=8)
            ax.tick_params(axis='y', colors='#a78bfa', labelsize=8)
            ax.grid(True, alpha=0.2, color='#a78bfa', linestyle='--')
            
            # Style the spines
            for spine in ax.spines.values():
                spine.set_color('#444')
            
            plt.tight_layout()
            return fig
        else:
            # Return empty plot with message
            fig, ax = plt.subplots(figsize=(8, 3))
            fig.patch.set_facecolor('#23272f')
            ax.set_facecolor('#23272f')
            ax.text(0.5, 0.5, "No data available", 
                   ha='center', va='center', color='#a78bfa', fontsize=12)
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)
            return fig

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
            avg_vol = data['volatility'].mean()
            return ui.HTML(
                f"""Analysis for <span class="hover-underline">Stock {input.stock_3()}</span>: 
                Average Volatility = <span class="value-highlight">{avg_vol:.4f}</span>"""
            )
        return "No data available for the selected stock."

    @output
    @render.plot
    def stock_3_volatility_plot():
        data = stock_3_data()
        if not data.empty:
            fig, ax = plt.subplots(figsize=(8, 3))
            
            # Set dark background
            fig.patch.set_facecolor('#23272f')
            ax.set_facecolor('#23272f')
            
            # Plot data with enhanced styling
            ax.plot(data['time_id'], data['volatility'], label=f"Stock {input.stock_3()}",
                    color='#ff9800', linewidth=2.5, alpha=0.9)
            
            # Add area under the curve
            ax.fill_between(data['time_id'], data['volatility'], alpha=0.2, color='#ff9800')
            
            ax.set_xlabel('Time ID', color='white', fontsize=10)
            ax.set_ylabel('Volatility', color='white', fontsize=10)
            ax.set_title(f"Stock {input.stock_3()}", fontsize=11, fontweight='bold', color='#ff9800')
            
            ax.tick_params(axis='x', colors='#a78bfa', labelsize=8)
            ax.tick_params(axis='y', colors='#a78bfa', labelsize=8)
            ax.grid(True, alpha=0.2, color='#a78bfa', linestyle='--')
            
            # Style the spines
            for spine in ax.spines.values():
                spine.set_color('#444')
            
            plt.tight_layout()
            return fig
        else:
            # Return empty plot with message
            fig, ax = plt.subplots(figsize=(8, 3))
            fig.patch.set_facecolor('#23272f')
            ax.set_facecolor('#23272f')
            ax.text(0.5, 0.5, "No data available", 
                   ha='center', va='center', color='#a78bfa', fontsize=12)
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)
            return fig

    @output
    @render.plot
    def comparison_plot():
        # Combine all three stock volatility data for comparison
        fig, ax = plt.subplots(figsize=(12, 5))
        
        # Set dark background
        fig.patch.set_facecolor('#23272f')
        ax.set_facecolor('#23272f')

        # Stock 1 plot
        data_1 = stock_1_data()
        if not data_1.empty:
            ax.plot(data_1['time_id'], data_1['volatility'], label=f"Stock {input.stock_1()}",
                    color='#1db954', linewidth=2, alpha=1, marker='o', markersize=3)

        # Stock 2 plot
        data_2 = stock_2_data()
        if not data_2.empty:
            ax.plot(data_2['time_id'], data_2['volatility'], label=f"Stock {input.stock_2()}",
                    color='#a78bfa', linewidth=2, alpha=1, marker='s', markersize=3)

        # Stock 3 plot
        data_3 = stock_3_data()
        if not data_3.empty:
            ax.plot(data_3['time_id'], data_3['volatility'], label=f"Stock {input.stock_3()}",
                    color='#ff9800', linewidth=2, alpha=1, marker='^', markersize=3)

        ax.set_xlabel('Time ID', color='white', fontsize=12)
        ax.set_ylabel('Volatility', color='white', fontsize=12)
        ax.set_title("Comparison of Volatility Over Time", fontsize=14, fontweight='bold', color='#1db954')
        
        # Enhanced legend with custom colors and positioning
        if data_1.empty and data_2.empty and data_3.empty:
            # Handle empty plot case
            ax.text(0.5, 0.5, "No data available for comparison", 
                   ha='center', va='center', color='#a78bfa', fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)
        else:
            # Legend handling is now done via custom HTML legend in the UI
            # We skip the legend here for a more interactive experience
            
            # Style the ticks and grid
            ax.tick_params(axis='x', colors='#a78bfa')
            ax.tick_params(axis='y', colors='#a78bfa')
            ax.grid(True, alpha=0.2, color='#a78bfa', linestyle='--')
            
            # Style the spines
            for spine in ax.spines.values():
                spine.set_color('#444')
        
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
            # Format the response to highlight the recommended stock
            stock_pattern = r'Stock (\d+)'
            import re
            match = re.search(stock_pattern, suggestion)
            if match:
                stock_id = match.group(1)
                color = '#1db954'
                if stock_id == input.stock_1():
                    color = '#1db954'
                elif stock_id == input.stock_2():
                    color = '#a78bfa'
                elif stock_id == input.stock_3():
                    color = '#ff9800'
                
                recommendation = f'<span style="color:{color};font-weight:bold;text-decoration:underline;">Stock {stock_id}</span>'
                suggestion = re.sub(stock_pattern, recommendation, suggestion, 1)
            
            return ui.HTML(f'<p class="typing-effect">{suggestion}</p>')
        except Exception as e:
            return f"Error getting suggestion: {e}"
            
    # Handle reset button
    @reactive.Effect
    @reactive.event(input.reset_stocks)
    def reset_stock_selections():
        # Reset to the first three stocks
        ui.update_select(session, "stock_1", selected=stock_cols[0] if len(stock_cols) > 0 else None)
        ui.update_select(session, "stock_2", selected=stock_cols[1] if len(stock_cols) > 1 else None)
        ui.update_select(session, "stock_3", selected=stock_cols[2] if len(stock_cols) > 2 else None)
