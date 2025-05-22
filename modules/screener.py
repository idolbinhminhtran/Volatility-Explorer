import os
import pandas as pd
import matplotlib.pyplot as plt
from shiny import ui, render, reactive
from faicons import icon_svg
from modules.common_style import get_common_css
from modules.visual_effects import get_effects_css, get_interactive_js

# ——————————————————————————————————————————————————————————————————————————
# Load your metrics_summary.csv at module load
# ——————————————————————————————————————————————————————————————————————————
_project_dir   = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
METRICS_PATH   = os.path.join(_project_dir, 'data', 'metrics_summary.csv')
metrics_df     = pd.read_csv(METRICS_PATH)
metrics_df['stock_id'] = metrics_df['stock_id'].astype(int)

# all of the metric columns (except stock_id) available to select
metric_choices = [c for c in metrics_df.columns if c not in ('stock_id', 'realized_volatility')]
if 'predicted_volatility' not in metric_choices:
    metric_choices.append('predicted_volatility')

# Load predicted volatility and merge
PRED_VOL_PATH = os.path.join(_project_dir, 'data', 'predicted_realized_vol.csv')
if os.path.exists(PRED_VOL_PATH):
    pred_vol_df = pd.read_csv(PRED_VOL_PATH)
    pred_vol_df['stock_id'] = pred_vol_df['stock_id'].astype(int)
    metrics_df = metrics_df.merge(
        pred_vol_df[['stock_id', 'predicted_realized_vol']],
        on='stock_id', how='left'
    )
    metrics_df['predicted_volatility'] = metrics_df['predicted_realized_vol']
else:
    metrics_df['predicted_volatility'] = 0

# Human-readable labels for metrics
metric_labels = {c: c.replace('_', ' ').title() for c in metric_choices}
metric_labels['predicted_volatility'] = 'Predicted Volatility'
if 'avg_bid_size1' in metric_labels:
    metric_labels['avg_bid_size1'] = 'Avg Bid Size1'
# Add 'Volatility' to metric_labels for selection
metric_labels_with_vol = {'volatility': 'Volatility', **metric_labels}

VOL_PATH = os.path.join(_project_dir, 'data', 'vol_df.csv')
vol_df = pd.read_csv(VOL_PATH)
stock_cols = [c for c in vol_df.columns if c != 'time_id']
min_time = int(vol_df['time_id'].min())
max_time = int(vol_df['time_id'].max())

def ui_screener():
    # Use the common CSS and visual effects along with screener-specific CSS
    custom_css = get_common_css() + get_effects_css() + """
    .screener-metric-box {
        background: rgba(44, 48, 56, 0.92);
        border-radius: 1.2rem;
        box-shadow: 0 1px 8px rgba(29,185,84,0.1);
        padding: 1.2rem 1.3rem 1.2rem 1.3rem;
        margin-bottom: 1.2rem;
        display: flex;
        flex-direction: column;
        gap: 0.7rem;
        transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
        position: relative;
        overflow: hidden;
    }
    
    .screener-metric-box:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(29,185,84,0.18);
    }
    
    .metric-box-title {
        font-size: 1.08rem;
        font-weight: 900;
        color: #1db954;
        margin-bottom: 0.7rem;
        margin-top: 0.1rem;
        letter-spacing: 0.01em;
        text-transform: uppercase;
        font-family: 'Inter', sans-serif;
        background: none;
    }
    
    .metric-checkbox-group label {
        display: flex;
        align-items: center;
        font-weight: 700;
        font-size: 1.09rem;
        border-radius: 2rem;
        padding: 0.32rem 1.2rem 0.32rem 1.2rem;
        margin-bottom: 0.18rem;
        margin-top: 0.08rem;
        background: rgba(36, 38, 44, 0.65);
        color: #1db954;
        box-shadow: 0 1px 4px #1db95411;
        letter-spacing: 0.01em;
        border: 1.5px solid #23272f;
        transition: all 0.2s cubic-bezier(0.2, 0, 0.38, 0.9);
        cursor: pointer;
        min-height: 2.1rem;
        min-width: 0;
        user-select: none;
        position: relative;
        overflow: hidden;
    }
    
    .metric-checkbox-group label:before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, rgba(29,185,84,0.1), rgba(167,139,250,0.1));
        transform: translateX(-100%);
        transition: transform 0.3s ease;
        z-index: -1;
    }
    
    .metric-checkbox-group label:hover:before {
        transform: translateX(0);
    }
    
    .metric-checkbox-group input[type="checkbox"]:checked + label {
        background: rgba(29,185,84,0.15);
        color: #1db954 !important;
        font-weight: 900;
        border: 1.5px solid #1db954;
        box-shadow: 0 0 0 2px rgba(29,185,84,0.2);
        transform: scale(1.02);
    }
    
    .metric-checkbox-group label:hover {
        background: #23272f;
        color: #a78bfa !important;
        border: 1.5px solid #a78bfa;
        transform: translateY(-2px);
    }
    
    .metric-checkbox-group input[type="checkbox"] {
        appearance: none;
        width: 1.25rem;
        height: 1.25rem;
        border: 2px solid #1db954;
        border-radius: 0.35rem;
        background: #23272f;
        margin-right: 0.8rem;
        position: relative;
        cursor: pointer;
        transition: all 0.2s cubic-bezier(0.2, 0, 0.38, 0.9);
        outline: none;
        vertical-align: middle;
    }
    
    .metric-checkbox-group input[type="checkbox"]:checked {
        background: #1db954;
        border-color: #1db954;
        transform: scale(1.1);
    }
    
    .metric-checkbox-group input[type="checkbox"]:checked:after {
        content: '';
        display: block;
        position: absolute;
        left: 0.32rem;
        top: 0.12rem;
        width: 0.35rem;
        height: 0.7rem;
        border: solid #fff;
        border-width: 0 0.18rem 0.18rem 0;
        transform: rotate(45deg);
        opacity: 0;
        animation: checkmark 0.2s forwards ease-in-out;
    }
    
    @keyframes checkmark {
        from { opacity: 0; transform: rotate(45deg) scale(0.8); }
        to { opacity: 1; transform: rotate(45deg) scale(1); }
    }
    
    .screener-title-row {
        display: flex; 
        align-items: center; 
        gap: 1.1rem; 
        margin-bottom: 0.2rem;
    }
    
    .screener-title-icon {
        font-size: 1.8rem;
        color: #1db954;
        animation: pulse 2s infinite ease-in-out;
    }
    
    .screener-title {
        font-size: 2.1rem;
        font-weight: 1000;
        background: linear-gradient(90deg, #1db954 60%, #a78bfa 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        margin-top: 0;
        letter-spacing: -1px;
        display: inline-block;
        animation: gradientShift 3s ease infinite alternate;
    }
    
    .screener-subtitle {
        font-size: 1.13rem;
        color: #a78bfa;
        font-weight: 600;
        margin-bottom: 1.5rem;
        opacity: 0;
        animation: fadeIn 0.8s forwards 0.3s;
    }
    
    /* Enhanced slider styling */
    .module-input .irs {
        height: 50px;
    }
    
    .module-input .irs-line {
        height: 8px;
        background: rgba(167,139,250,0.2);
        border-radius: 4px;
    }
    
    .module-input .irs-bar {
        height: 8px;
        background: linear-gradient(90deg, #1db954, #a78bfa);
        border-top: none;
        border-bottom: none;
    }
    
    .module-input .irs-handle {
        top: 22px;
        width: 18px;
        height: 18px;
        border: 3px solid #1db954;
        background: #fff;
        box-shadow: 0 0 0 rgba(29,185,84,0.5);
        transition: transform 0.2s, box-shadow 0.3s;
    }
    
    .module-input .irs-handle:hover, .module-input .irs-handle.state_hover {
        background: #1db954;
        transform: scale(1.2);
        box-shadow: 0 0 0 4px rgba(29,185,84,0.3);
    }
    
    .module-input .irs-from, .module-input .irs-to, .module-input .irs-single {
        background: #1db954;
        color: white;
        border-radius: 10px;
        padding: 2px 10px;
        transform: translateY(-5px);
        transition: transform 0.2s, background 0.2s;
    }
    
    .module-input .irs-grid-pol {
        background: rgba(167,139,250,0.4);
    }
    
    /* Table animations */
    .dataframe {
        opacity: 0;
        animation: fadeIn 0.8s forwards 0.2s;
    }
    
    .dataframe tbody tr {
        opacity: 0;
        animation: fadeIn 0.5s forwards;
    }
    
    .dataframe tbody tr:nth-child(1) { animation-delay: 0.1s; }
    .dataframe tbody tr:nth-child(2) { animation-delay: 0.15s; }
    .dataframe tbody tr:nth-child(3) { animation-delay: 0.2s; }
    .dataframe tbody tr:nth-child(4) { animation-delay: 0.25s; }
    .dataframe tbody tr:nth-child(5) { animation-delay: 0.3s; }
    .dataframe tbody tr:nth-child(6) { animation-delay: 0.35s; }
    .dataframe tbody tr:nth-child(7) { animation-delay: 0.4s; }
    .dataframe tbody tr:nth-child(8) { animation-delay: 0.45s; }
    .dataframe tbody tr:nth-child(9) { animation-delay: 0.5s; }
    .dataframe tbody tr:nth-child(10) { animation-delay: 0.55s; }
    
    /* Animated sidebar icon */
    .sidebar-card .module-icon {
        position: relative;
    }
    
    .sidebar-card .module-icon:after {
        content: "";
        position: absolute;
        top: -5px;
        left: -5px;
        right: -5px;
        bottom: -5px;
        border-radius: 50%;
        border: 2px solid rgba(29,185,84,0.5);
        opacity: 0;
        animation: ripple 2s infinite ease-out;
    }
    
    @keyframes ripple {
        0% { transform: scale(0.8); opacity: 1; }
        100% { transform: scale(1.4); opacity: 0; }
    }
    
    .module-layout { gap: 0.5rem; }
    .sidebar-card { margin-top: 80px; }
    .main-content { padding-top: 80px; }
    """
    
    # Include interactive JavaScript
    interactive_js = get_interactive_js()
    
    return ui.TagList(
        ui.tags.style(custom_css),
        ui.tags.script(interactive_js),
        ui.tags.div(
            ui.tags.div(
                # Sidebar card with animated border effect
                ui.tags.div(
                    ui.tags.div(
                        ui.tags.div(ui.tags.i(class_="fa fa-magnifying-glass"), class_="module-icon float-effect"),
                        class_="module-icon float-effect"
                    ),
                    ui.h2("Stock Screener", class_="animated-gradient-text"),
                    ui.p("Filter and rank stocks by financial statistics.", class_="module-subtitle"),
                    ui.h4("Time Range"),
                    ui.tags.div(
                        ui.input_slider(
                            "vol_time_range", "Time ID Range (for Volatility):",
                            min=min_time, max=max_time,
                            value=(min_time, max_time), step=1
                        ),
                        class_="module-input"
                    ),
                    ui.h4("Financial Statistics"),
                    ui.tags.div(
                        ui.tags.div("Select financial statistics", class_="metric-box-title"),
                        ui.input_checkbox_group(
                            "scr_metrics", None,
                            choices=metric_labels_with_vol,
                            selected=metric_choices[:2]
                        ),
                        class_="screener-metric-box metric-checkbox-group stagger-cards"
                    ),
                    ui.h4("Top N"),
                    ui.tags.div(
                        ui.input_slider(
                            "top_n", "Top N Stocks:",
                            min=1, max=len(metrics_df), value=10, step=1
                        ),
                        class_="module-input"
                    ),
                    class_="sidebar-card"
                ),
                style="flex:0 0 360px;display:flex;flex-direction:column;align-items:stretch;"
            ),
            ui.tags.div(
                # Main content with fade-in effect
                ui.tags.div(
                    ui.tags.span(ui.tags.i(class_="fa fa-magnifying-glass"), class_="screener-title-icon hover-icon"),
                    ui.tags.h2("Stock Screener", class_="screener-title animated-gradient-text"),
                    class_="screener-title-row"
                ),
                ui.tags.div(
                    "Showing the top N stocks by your chosen financial statistics (ranked by the first).",
                    class_="screener-subtitle"
                ),
                ui.tags.div(
                    ui.tags.div(
                        ui.tags.div(ui.tags.i(class_="fa fa-table"), class_="hover-icon"),
                        ui.tags.h3("Filtered Results", class_="card-title"),
                        style="display:flex;align-items:center;gap:10px;"
                    ),
                    ui.output_data_frame("scr_table"),
                    class_="content-card hover-card slide-in-up interactive-table"
                ),
                ui.tags.div(
                    ui.tags.div(
                        ui.tags.div(ui.tags.i(class_="fa fa-chart-column"), class_="hover-icon"),
                        ui.tags.h3("Visualization", class_="card-title"),
                        style="display:flex;align-items:center;gap:10px;"
                    ),
                    ui.output_plot("scr_plot"),
                    class_="content-card hover-card slide-in-up",
                    style="animation-delay:0.2s;"
                ),
                class_="main-content"
            ),
            class_="module-layout"
        )
    )


def server_screener(input, output, session):

    @reactive.Calc
    def top_metrics():
        sel = list(input.scr_metrics())
        if not sel:
            return pd.DataFrame()

        n = input.top_n()
        result_df = None

        # If volatility is selected, compute it from vol_df over the selected time range
        if 'volatility' in sel:
            start_time, end_time = input.vol_time_range()
            subset = vol_df[(vol_df['time_id'] >= start_time) & (vol_df['time_id'] <= end_time)]
            df_long = subset.melt(id_vars=['time_id'], value_vars=stock_cols, var_name='stock_id', value_name='volatility')
            df_long['stock_id'] = df_long['stock_id'].astype(int)
            vol_mean = df_long.groupby('stock_id')['volatility'].mean().reset_index()
            vol_mean['volatility'] = vol_mean['volatility'].astype(float)
            result_df = vol_mean.rename(columns={'volatility': 'Volatility'})
            sel_no_vol = [m for m in sel if m not in ('volatility', 'realized_volatility')]
            if sel_no_vol:
                metrics_part = metrics_df[['stock_id'] + sel_no_vol]
                result_df = pd.merge(result_df, metrics_part, on='stock_id', how='left')
        else:
            # Only metrics from metrics_df
            result_df = metrics_df[['stock_id'] + sel]

        # Sort by the first selected metric (use actual column name for metrics, 'Volatility' for volatility)
        sort_col = 'Volatility' if sel[0] == 'volatility' else sel[0]
        result_df = result_df.sort_values(sort_col, ascending=False).head(n)

        # Rename columns for display
        col_map = {'stock_id': 'Stock ID'}
        for m in sel:
            if m == 'volatility':
                col_map['Volatility'] = 'Volatility'
            else:
                col_map[m] = m.replace('_', ' ').title()
        result_df = result_df.rename(columns=col_map)
        # Round all numeric columns except 'Stock ID' to 6 decimals
        for col in result_df.columns:
            if col != 'Stock ID':
                result_df[col] = result_df[col].round(6)
        return result_df

    @output
    @render.data_frame
    def scr_table():
        df = top_metrics()
        return df

    @output
    @render.plot
    def scr_plot():
        df = top_metrics()
        fig, ax = plt.subplots(figsize=(10, 5))
        
        if df.empty:
            ax.text(0.5, 0.5, "No metrics selected", ha='center', va='center', fontsize=14, color="#a78bfa")
            ax.set_facecolor("#23272f")
            fig.patch.set_facecolor("#23272f")
            fig.tight_layout()
            return fig

        x = df['Stock ID'].astype(str)
        y = df.iloc[:, 1]
        
        # Set style for the plot
        ax.set_facecolor("#23272f")
        fig.patch.set_facecolor("#23272f")
        
        # Create gradient-colored bars
        colors = ['#1db954', '#23c55e', '#32cc68', '#44d373', '#56da7e', 
                  '#6ade8a', '#7de296', '#91e6a1', '#a5eaad', '#b9eeb9']
        if len(colors) > len(x):
            colors = colors[:len(x)]
        elif len(colors) < len(x):
            colors = colors * (len(x) // len(colors) + 1)
            colors = colors[:len(x)]
            
        bars = ax.bar(x, y, color=colors, alpha=0.85, width=0.7)
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height * 1.01,
                    f'{height:.4f}', ha='center', va='bottom', color='white',
                    fontsize=9, rotation=0)
        
        # Improve aesthetics
        ax.set_xlabel('Stock ID', color='white', fontsize=12)
        ax.set_ylabel(df.columns[1], color='white', fontsize=12)
        ax.set_title(f"Top {len(df)} Stocks by {df.columns[1]}", color='#1db954', fontsize=14, fontweight='bold')
        
        # Style the ticks
        ax.tick_params(axis='x', colors='#a78bfa', rotation=45)
        ax.tick_params(axis='y', colors='#a78bfa')
        
        # Add a subtle grid
        ax.grid(axis='y', linestyle='--', alpha=0.2, color='#a78bfa')
        
        # Add a subtle box around the plot
        for spine in ax.spines.values():
            spine.set_color('#444')
            spine.set_linewidth(0.8)
            
        # Set y-axis to start at 0
        ax.set_ylim(bottom=0)
        
        plt.tight_layout()
        return fig
