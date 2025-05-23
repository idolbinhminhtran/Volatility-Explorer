from shiny import ui, render, reactive
from faicons import icon_svg
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import os
from htmltools import css
from shinywidgets import output_widget
import openai

# --- Data loading and setup ---
_project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# The file containing the ground-truth realised volatility in the models folder
# is named ``actual_rv.csv`` (confirmed via directory listing).  Load that file
# instead of the previous, incorrectly-named ``actual.csv`` so that the
# ``actual`` column is successfully merged into each model's DataFrame.
ACTUAL_RV_PATH = os.path.join(_project_dir, 'models', 'actual_rv.csv')
MODELS_DIR = os.path.join(_project_dir, 'models')

# Define colors for models with descriptive names
MODEL_NAMES = {
    'GAT': 'GAT',
    'PCA_Linear': 'PCA Linear',
    'EWMA': 'EWMA',
    'LAG1': 'LAG1',
    'HAR_RV': 'HAR-RV',
    'Gradient_Boosting': 'Gradient Boosting',
    'Random_Forest': 'Random Forest',
    'Linear': 'Linear'
}

MODEL_COLORS = {
    'GAT': '#ff0066',           # Hot Pink (our main model)
    'PCA_Linear': '#1db954',    # Green (underscore variant)
    'PCA Linear': '#1db954',   # Green (display name variant)
    'EWMA': '#a78bfa',         # Purple
    'LAG1': '#fbbf24',         # Yellow
    'HAR_RV': '#00bcd4',       # Blue (underscore variant)
    'HAR-RV': '#00bcd4',      # Blue (display name variant)
    'Gradient_Boosting': '#ff6b6b',  # Red (underscore variant)
    'Gradient Boosting': '#ff6b6b', # Red (display name variant)
    'Random_Forest': '#4ecdc4', # Teal (underscore variant)
    'Random Forest': '#4ecdc4',# Teal (display name variant)
    'Linear': '#f39c12'        # Orange
}

print(f"\nInitializing model data loading...")
print(f"Project directory: {_project_dir}")
print(f"Models directory: {MODELS_DIR}")

# Load model prediction data with new file names
MODEL_FILES = {
    'GAT': 'GAT_prediction_panel.csv',
    'PCA Linear': 'PCA_Linear_predictions.csv',
    'EWMA': 'EWMA_predictions.csv',
    'LAG1': 'LAG1_predictions.csv',
    'HAR-RV': 'HAR_RV_predictions.csv',
    'Gradient Boosting': 'Gradient_Boosting_predictions.csv',
    'Random Forest': 'Random_Forest_predictions.csv',
    'Linear': 'Linear_predictions.csv'
}

# Load actual values first
try:
    print(f"\nLoading actual values from {ACTUAL_RV_PATH}")
    if not os.path.exists(ACTUAL_RV_PATH):
        print(f"Warning: Actual values file not found at {ACTUAL_RV_PATH}")
        actual_df = None
    else:
        actual_df = pd.read_csv(ACTUAL_RV_PATH)
        # Melt the dataframe to convert wide format to long format
        actual_df = pd.melt(actual_df, id_vars=['bucket_idx'], var_name='stock_id', value_name='actual')
        actual_df['time_id'] = actual_df['bucket_idx']  # Keep original time index
        print(f"Successfully loaded actual values with shape {actual_df.shape}")
except Exception as e:
    print(f"Error loading actual values: {e}")
    actual_df = None

# Load prediction data for each model
model_data = {}
for model_name, filename in MODEL_FILES.items():
    try:
        filepath = os.path.join(MODELS_DIR, filename)
        print(f"\nLoading {model_name} data from {filepath}")
        
        if not os.path.exists(filepath):
            print(f"Warning: Model file not found at {filepath}")
            model_data[model_name] = None
            continue
            
        # Read the CSV file
        df = pd.read_csv(filepath)
        print(f"Initial data shape: {df.shape}")
        
        # Reset index to get the time_id column and map it to actual_rv time range
        df = df.reset_index()
        # Map time_id from 0-based to actual_rv range (3446-3829)
        df['time_id'] = df['index'] + 3446
        
        # Melt the dataframe to convert wide format to long format
        # Exclude the time_id column from melting
        id_vars = ['time_id']
        value_vars = [col for col in df.columns if col not in id_vars + ['index']]
        
        df = pd.melt(df, id_vars=id_vars, value_vars=value_vars, 
                    var_name='stock_id', value_name='predicted')
        print(f"After melting shape: {df.shape}")
        
        # Merge with actual values if available
        if actual_df is not None:
            print("Merging with actual values...")
            df = pd.merge(
                df,
                actual_df[['time_id', 'stock_id', 'actual']],
                on=['time_id', 'stock_id'],
                how='left'
            )
            print(f"After merging shape: {df.shape}")
        
        model_data[model_name] = df
        print(f"Successfully loaded {model_name} data")
    except Exception as e:
        print(f"Error loading {model_name} data: {e}")
        model_data[model_name] = None

# Get unique stock IDs from actual values
try:
    if actual_df is not None:
        stock_ids = [str(c) for c in actual_df['stock_id'].unique()]
        print(f"\nFound {len(stock_ids)} unique stock IDs")
    else:
        print("\nNo actual values loaded, using default stock ID")
        stock_ids = ["43"]  # Default fallback
except Exception as e:
    print(f"Error getting stock IDs: {e}")
    stock_ids = ["43"]  # Default fallback

# Load model metrics
try:
    metrics_df = pd.read_csv(os.path.join(MODELS_DIR, 'model_metrics_summary.csv'))
    MODEL_METRICS = metrics_df.set_index('Model').to_dict('index')
except Exception as e:
    print(f"Error loading model metrics: {e}")
    MODEL_METRICS = {}

# After model_data is populated, compute overall available time range
try:
    _time_values = set()
    for _df in model_data.values():
        if _df is not None and 'time_id' in _df:
            _time_values.update(_df['time_id'].unique())
    TIME_MIN = int(min(_time_values)) if _time_values else 3446  # Set default minimum to 3446
    TIME_MAX = int(max(_time_values)) if _time_values else 3829  # Set default maximum to 3829
    print(f"\nTime range: {TIME_MIN} to {TIME_MAX}")
except Exception as e:
    print(f"Error computing time range: {e}")
    TIME_MIN, TIME_MAX = 3446, 3829  # Set default range if error occurs

print("\nModel data initialization complete.")

# -----------------------------------------------------------------------------
# NOTE: Global placeholder for the interpretation dataframe. If you have already
# generated SHAP / feature-importance outputs, load them into this variable so
# the Stock-Level Interpretation panel can show meaningful information. Keeping
# a defined variable prevents NameError exceptions when the panel is used even
# when the data is not yet available.
# -----------------------------------------------------------------------------

# Attempt to load feature importance explanations if available
EXPLAIN_PATH = os.path.join(_project_dir, 'data', 'mini_all_explanations.csv')

# Initialize to None; will update if file exists
explain_df = None

try:
    if os.path.exists(EXPLAIN_PATH):
        explain_df = pd.read_csv(EXPLAIN_PATH)

        # Ensure stock identifiers are strings to match UI select input values
        if 'stock_idx' in explain_df.columns:
            explain_df['stock_idx'] = explain_df['stock_idx'].astype(str)

        # Rename any whitespace in column headers just in case
        explain_df.columns = [c.strip() for c in explain_df.columns]

        print(f"Loaded explanation dataframe with shape {explain_df.shape} from {EXPLAIN_PATH}")
    else:
        print(f"Explanation file not found at {EXPLAIN_PATH}. Stock-level interpretation panel will remain disabled.")
except Exception as _e:
    print(f"Error loading explanation data: {_e}. Stock-level interpretation panel will remain disabled.")

# Utility function to convert a human-readable model name to a valid Shiny input
# id fragment (letters, numbers, underscore only).


def _sanitize_model_id(name: str) -> str:
    """Return a safe identifier derived from the display model *name*.

    Shiny IDs cannot contain spaces or hyphens. We therefore replace any space
    or hyphen with an underscore, leaving other characters untouched.
    """

    return name.replace(" ", "_").replace("-", "_")

# Helper to create a consistent panel
def panel_section(panel_id, title, content, open_by_default=False):
    return ui.tags.div(
        ui.tags.div(
            title,
            ui.tags.div(ui.tags.i(class_="fa fa-chevron-right"), id=f"chevron-{panel_id}", class_="collapsible-chevron" + (" open" if open_by_default else "")),
            class_="collapsible-header",
            onclick=f"togglePanel('{panel_id}')"
        ),
        ui.tags.div(
            content,
            class_="collapsible-content" + ("" if open_by_default else " closed"),
            id=f"content-{panel_id}"
        ),
        class_="collapsible-panel"
    )

def ui_model_details():
    custom_css = """
    .model-section-group {
      display: flex;
      flex-direction: column;
      align-items: center;
      width: 100%;
      max-width: 1100px;
      margin: 0 auto;
      gap: 2.2rem;
      justify-content: center;
      margin-left: auto;
      margin-right: auto;
      float: none;
    }
    .model-section-group > .collapsible-panel:first-child {
      margin-top: 2.5rem;
    }
    .collapsible-panel {
      width: 100%;
      border-radius: 1.5rem;
      box-shadow: 0 8px 32px 0 #1db95422, 0 1.5px 0 0 #1db954;
      border: 2.5px solid rgba(167,139,250,0.13);
      background: linear-gradient(120deg, #23272f 80%, #18191c 100%);
      margin: 0 auto;
      margin-bottom: 0;
      transition: box-shadow 0.3s, background 0.5s;
      overflow: visible;
      position: relative;
    }
    .collapsible-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 2.1rem 2.7rem 1.1rem 2.7rem;
      cursor: pointer;
      user-select: none;
      font-family: 'Inter', sans-serif;
      font-size: 2rem;
      font-weight: 1000;
      color: #1db954;
      letter-spacing: 0.01em;
      text-shadow: 0 2px 16px #1db95433;
      border-radius: 1.5rem 1.5rem 0 0;
      transition: color 0.2s;
    }
    .collapsible-header:hover {
      color: #a78bfa;
    }
    .collapsible-chevron {
      font-size: 2.1rem;
      color: #a78bfa;
      margin-left: 1.2rem;
      transition: transform 0.35s cubic-bezier(.77,0,.18,1);
      will-change: transform;
      display: flex;
      align-items: center;
    }
    .collapsible-chevron.open {
      transform: rotate(90deg);
    }
    .collapsible-content {
      padding: 0 2.7rem 2.2rem 2.7rem;
      animation: fadeInPanel 0.5s cubic-bezier(.77,0,.18,1);
      transition: max-height 0.5s cubic-bezier(.77,0,.18,1), opacity 0.5s cubic-bezier(.77,0,.18,1);
      overflow: visible;
    }
    .collapsible-content.closed {
      max-height: 0 !important;
      opacity: 0;
      padding-bottom: 0 !important;
      pointer-events: none;
      overflow: hidden;
    }
    @keyframes fadeInPanel {
      from { opacity: 0; transform: translateY(24px); }
      to { opacity: 1; transform: translateY(0); }
    }
    
    /* --- Page Section Styles --- */
    .page-header {
      width: 100%;
      text-align: center;
      margin-bottom: 1rem;
      padding-top: 0.5rem;
    }
    
    .page-title {
      font-size: 2rem;
      font-weight: 800;
      color: #1db954;
      margin-bottom: 0.5rem;
      text-shadow: 0 0 10px rgba(29, 185, 84, 0.3);
      background: linear-gradient(90deg, #1db954 40%, #a78bfa 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      display: inline-block;
    }
    
    .page-subtitle {
      font-size: 1rem;
      color: #e0e0e0;
      max-width: 800px;
      margin: 0 auto;
      line-height: 1.5;
    }
    
    /* --- Model Info Cards --- */
    .info-cards-container {
      display: flex;
      flex-wrap: wrap;
      gap: 1.2rem;
      margin-bottom: 2rem;
      width: 100%;
      justify-content: center;
    }
    
    .info-card {
      flex: 1;
      min-width: 240px;
      max-width: 300px;
      background: rgba(36, 38, 44, 0.92);
      border-radius: 1rem;
      padding: 1.2rem;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
      display: flex;
      flex-direction: column;
      position: relative;
      border: 1px solid rgba(167, 139, 250, 0.15);
      transition: all 0.3s ease;
    }
    
    .info-card:hover {
      transform: translateY(-5px);
      box-shadow: 0 12px 36px rgba(29, 185, 84, 0.2);
      border-color: rgba(29, 185, 84, 0.4);
    }
    
    .info-card-header {
      display: flex;
      align-items: center;
      margin-bottom: 1rem;
      gap: 0.8rem;
    }
    
    .info-card-icon {
      width: 2.5rem;
      height: 2.5rem;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.2rem;
      background: rgba(29, 185, 84, 0.15);
      color: #1db954;
    }
    
    .info-card-title {
      font-size: 1.2rem;
      font-weight: 700;
      color: #e0e0e0;
    }
    
    .info-card-content {
      color: #a0a0a0;
      font-size: 0.9rem;
      line-height: 1.5;
      margin-bottom: 0.3rem;
      height: 4rem;
      overflow: hidden;
    }
    
    .metric-value {
      font-size: 1.4rem;
      font-weight: 800;
      margin-top: 0.3rem;
      margin-bottom: 0.3rem;
      color: #1db954;
    }
    
    .info-card.purple .info-card-icon {
      background: rgba(167, 139, 250, 0.15);
      color: #a78bfa;
    }
    
    .info-card.purple .metric-value {
      color: #a78bfa;
    }
    
    /* Model Introduction */
    .model-intro-subtitle {
      font-size: 1.25rem;
      font-weight: 700;
      text-align: center;
      margin-bottom: 2.2rem;
      color: #1db954;
      font-family: 'Inter', sans-serif;
    }
    .model-intro-row {
      display: flex;
      flex-direction: row;
      justify-content: center;
      align-items: flex-start;
      gap: 3.5rem;
      width: 100%;
      margin-top: 1.2rem;
    }
    .model-intro-col {
      flex: 1 1 0;
      min-width: 220px;
      max-width: 340px;
      background: rgba(36,38,44,0.92);
      border-radius: 1.2rem;
      box-shadow: 0 2px 12px #1db95422;
      padding: 2.2rem 1.5rem 1.7rem 1.5rem;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      color: #fff;
    }
    .model-intro-icon {
      font-size: 2.5rem;
      margin-bottom: 1.1rem;
      color: #1db954;
      filter: drop-shadow(0 0 8px #a78bfa);
    }
    .model-intro-label {
      font-size: 1.18rem;
      font-weight: 700;
      margin-bottom: 0.7rem;
      color: #a78bfa;
      font-family: 'Inter', sans-serif;
    }
    .model-intro-text {
      font-size: 1.08rem;
      color: #e0e0e0;
      font-family: 'Roboto', sans-serif;
      font-weight: 400;
      line-height: 1.6;
    }
    @media (max-width: 900px) {
      .model-intro-row { flex-direction: column; gap: 2rem; }
      .model-intro-col { max-width: 100%; }
    }
    /* Model Metrics */
    .model-summary-row {
      display: flex;
      gap: 1.2rem;
      margin-bottom: 0;
      justify-content: flex-start;
      flex-wrap: nowrap;
    }
    @media (max-width: 900px) {
      .model-summary-row { flex-wrap: wrap; }
    }
    .model-summary-card {
      background: rgba(36,38,44,0.92);
      border-radius: 1.2rem;
      box-shadow: 0 4px 24px 0 #1db95422, 0 1.5px 0 0 #1db954;
      border: 2.5px solid rgba(167,139,250,0.13);
      padding: 1.1rem 1.2rem 1.1rem 1.2rem;
      min-width: 150px;
      max-width: 220px;
      flex: 1 1 0;
      display: flex;
      align-items: center;
      gap: 0.7rem;
      position: relative;
      transition: box-shadow 0.3s, border 0.3s, background 0.5s;
      cursor: pointer;
      overflow: visible !important;
      z-index: 20;
    }
    .model-summary-card:hover {
      box-shadow: 0 8px 32px 0 #1db95455, 0 2px 8px #a78bfa55;
      border: 2.5px solid #1db954;
      z-index: 30;
    }
    .model-summary-icon {
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
    .model-summary-icon.rmse { background: linear-gradient(135deg, #e3f0ff 60%, #90caf9 100%); color: #1976d2; }
    .model-summary-icon.rmspe { background: linear-gradient(135deg, #e8f5e9 60%, #b9f6ca 100%); color: #1db954; }
    .model-summary-icon.qlike { background: linear-gradient(135deg, #f3e5f5 60%, #ce93d8 100%); color: #a78bfa; }
    .model-summary-icon.f1 { background: linear-gradient(135deg, #fffde7 60%, #ffe082 100%); color: #fbbf24; }
    .model-summary-icon.auc { background: linear-gradient(135deg, #e0f7fa 60%, #80deea 100%); color: #00bcd4; }
    .model-summary-content {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      justify-content: center;
    }
    .model-summary-label {
      font-size: 1.01rem;
      font-weight: 700;
      color: #bdbdbd;
      margin-bottom: 0.18rem;
      letter-spacing: 0.01em;
    }
    .model-summary-value {
      font-size: 1.55rem;
      font-weight: 900;
      color: #fff;
      letter-spacing: 0.01em;
    }
    .metric-tooltip {
      display: block;
      visibility: hidden;
      position: absolute;
      left: 50%;
      top: 110%;
      transform: translateX(-50%) translateY(12px) scale(1.03);
      background: #23272f;
      color: #fff;
      padding: 1rem 1.3rem;
      border-radius: 0.9rem;
      font-size: 1.08rem;
      box-shadow: 0 2px 12px #000a;
      white-space: pre-line;
      z-index: 1000;
      min-width: 220px;
      max-width: 340px;
      text-align: left;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.25s, transform 0.25s;
    }
    .model-summary-card:hover .metric-tooltip {
      visibility: visible;
      opacity: 1;
      pointer-events: auto;
    }
    
    /* Stock Interpretation Styles */
    .model-interp-subtitle {
      font-size: 1.25rem;
      font-weight: 700;
      text-align: center;
      margin-bottom: 1.8rem;
      color: #e0e0e0;
      font-family: 'Inter', sans-serif;
      position: relative;
      padding-bottom: 1rem;
    }
    
    .model-interp-subtitle::after {
      content: "";
      position: absolute;
      left: 50%;
      bottom: 0;
      width: 120px;
      height: 3px;
      background: linear-gradient(90deg, #1db954, #a78bfa);
      transform: translateX(-50%);
      border-radius: 3px;
    }
    
    .stock-interp-header {
      margin-bottom: 2rem;
      text-align: center;
    }
    
    .section-header {
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 1.5rem;
      gap: 0.8rem;
    }
    
    .section-header i {
      font-size: 1.3rem;
      color: #1db954;
    }
    
    .section-title {
      font-size: 1.3rem;
      font-weight: 700;
      color: #1db954;
      text-shadow: 0 0 10px rgba(29, 185, 84, 0.3);
    }
    
    .interp-controls-container {
      width: 100%;
      margin-bottom: 2rem;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    
    .interp-controls-row {
      display: flex;
      gap: 1.5rem;
      width: 100%;
      max-width: 800px;
      align-items: flex-end;
      justify-content: center;
      flex-wrap: wrap;
    }
    
    .interp-control {
      flex: 1;
      min-width: 150px;
      max-width: 250px;
    }
    
    .analyze-btn {
      background: linear-gradient(90deg, #1db954 60%, #43e97b 100%);
      color: white;
      font-weight: 700;
      border: none;
      border-radius: 8px;
      padding: 12px 24px;
      font-size: 1.1rem;
      cursor: pointer;
      transition: all 0.3s ease;
      width: 100%;
      box-shadow: 0 4px 15px rgba(29, 185, 84, 0.3);
      position: relative;
      overflow: hidden;
      letter-spacing: 0.05em;
    }
    
    .analyze-btn::before {
      content: '';
      position: absolute;
      top: -50%;
      left: -50%;
      width: 200%;
      height: 200%;
      background: linear-gradient(
        to bottom right,
        rgba(255, 255, 255, 0) 0%,
        rgba(255, 255, 255, 0.2) 50%,
        rgba(255, 255, 255, 0) 100%
      );
      transform: rotate(45deg);
      transition: transform 0.8s;
      z-index: 1;
    }
    
    .analyze-btn:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(29, 185, 84, 0.5);
    }
    
    .analyze-btn:hover::before {
      transform: rotate(45deg) translateX(100%);
    }
    
    .prediction-metrics-section {
      width: 100%;
      margin: 1rem 0 2rem 0;
    }
    
    .metrics-container {
      display: flex;
      justify-content: center;
      gap: 2rem;
      flex-wrap: wrap;
    }
    
    .metric-card {
      background: rgba(36, 38, 44, 0.92);
      border-radius: 1rem;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
      padding: 1.5rem 1.8rem 1.3rem 1.8rem;
      min-width: 260px;
      max-width: 380px;
      width: 100%;
      border: 1px solid rgba(167, 139, 250, 0.15);
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      height: 150px; /* fixed for alignment */
    }

    .metric-header {
      display: block; /* icon now absolute so simple block */
      margin-bottom: 0.8rem;
    }

    .metric-title {
      font-size: 1.1rem;
      color: #a0a0a0;
      font-weight: 500;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .metric-value {
      font-size: 2.4rem;
      font-weight: 800;
      text-align: left;
      margin-top: auto; /* push to bottom for alignment */
    }

    .metric-value.positive {
      color: #1db954;
      text-shadow: 0 0 10px rgba(29, 185, 84, 0.2);
    }

    .metric-value.neutral {
      color: #a78bfa;
      text-shadow: 0 0 10px rgba(167, 139, 250, 0.2);
    }

    .metric-icon {
      width: 26px;
      height: 26px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
      position: absolute;
      top: 1.2rem;
      right: 1.2rem;
    }

    .metric-icon.success {
      background: rgba(29, 185, 84, 0.15);
      color: #1db954;
    }

    .metric-icon.info {
      background: rgba(167, 139, 250, 0.15);
      color: #a78bfa;
    }

    .metric-icon.warning {
      background: rgba(251, 191, 36, 0.15);
      color: #fbbf24;
    }
    
    .metric-card::after {
      content: "";
      position: absolute;
      inset: 0;
      border-radius: 1rem;
      padding: 1.5px;
      background: linear-gradient(130deg, #1db954, #a78bfa, #1db954);
      background-size: 200% 200%;
      animation: gradient-move 6s ease infinite;
      -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
      mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
      -webkit-mask-composite: xor;
      mask-composite: exclude;
      opacity: 0.5;
      z-index: 0;
    }
    
    .metric-card-title {
      font-size: 1.3rem;
      font-weight: 700;
      color: #1db954;
      margin-bottom: 1.2rem;
      text-align: center;
      position: relative;
      text-shadow: 0 0 10px rgba(29, 185, 84, 0.3);
    }
    
    .metric-values-container {
      display: flex;
      flex-direction: row;
      justify-content: space-around;
      flex-wrap: wrap;
      gap: 1.2rem;
      position: relative;
      z-index: 1;
    }
    
    .metric-value-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 0.8rem;
      background: rgba(30, 32, 39, 0.7);
      border-radius: 0.8rem;
      min-width: 140px;
      transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-value-item:hover {
      transform: translateY(-3px);
      box-shadow: 0 6px 15px rgba(29, 185, 84, 0.15);
    }
    
    .metric-label {
      font-size: 0.95rem;
      font-weight: 600;
      color: #a0a0a0;
      margin-bottom: 0.5rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    
    .metric-value {
      font-size: 1.5rem;
      font-weight: 800;
      letter-spacing: 0.01em;
    }
    
    .metric-value.prediction {
      color: #1db954;
      text-shadow: 0 0 8px rgba(29, 185, 84, 0.3);
    }
    
    .metric-value.actual {
      color: #a78bfa;
      text-shadow: 0 0 8px rgba(167, 139, 250, 0.3);
    }
    
    .metric-value.error {
      color: #f87171;
      text-shadow: 0 0 8px rgba(248, 113, 113, 0.3);
    }
    
    .interp-plots-row {
      display: flex;
      gap: 1.5rem;
      width: 100%;
      justify-content: center;
      flex-wrap: wrap;
      margin-bottom: 2rem;
    }
    
    .plot-container {
      flex: 1;
      min-width: 300px;
      max-width: 600px;
      background: rgba(36, 38, 44, 0.92);
      border-radius: 1rem;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
      padding: 1rem;
      overflow: hidden;
      border: 1px solid rgba(167, 139, 250, 0.15);
      transition: all 0.3s ease;
      position: relative;
    }
    
    .plot-container::before {
      content: none !important;
    }
    
    .plot-container:hover {
      transform: translateY(-5px);
      border-color: rgba(29, 185, 84, 0.4);
      box-shadow: 0 15px 40px rgba(29, 185, 84, 0.2);
    }
    
    .plot-container:hover::before {
      opacity: 1;
    }
    
    @media (max-width: 768px) {
      .plot-container {
        min-width: 100%;
        margin-bottom: 1.5rem;
      }
    }
    
    .interp-neighbors-container {
      width: 100%;
      max-width: 800px;
      margin: 0 auto 2rem;
    }
    
    .neighbors-container {
      background: rgba(36, 38, 44, 0.92);
      border-radius: 1rem;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
      padding: 1.8rem;
      width: 100%;
      border: 1px solid rgba(167, 139, 250, 0.15);
      position: relative;
      overflow: hidden;
    }
    
    .neighbors-container::after {
      content: "";
      position: absolute;
      inset: 0;
      border-radius: 1rem;
      padding: 1.5px;
      background: linear-gradient(130deg, #1db954, #a78bfa, #1db954);
      background-size: 200% 200%;
      animation: gradient-move 6s ease infinite;
      -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
      mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
      -webkit-mask-composite: xor;
      mask-composite: exclude;
      opacity: 0.4;
      z-index: 0;
    }
    
    .neighbors-title {
      font-size: 1.3rem;
      font-weight: 700;
      color: #1db954;
      margin-bottom: 1.8rem;
      text-align: center;
      position: relative;
      text-shadow: 0 0 10px rgba(29, 185, 84, 0.3);
      z-index: 1;
    }
    
    .neighbors-list {
      display: flex;
      flex-direction: column;
      gap: 1.3rem;
      position: relative;
      z-index: 1;
    }
    
    .neighbor-row {
      display: flex;
      align-items: center;
      gap: 1.2rem;
      padding: 0.7rem 1rem;
      border-radius: 0.8rem;
      background: rgba(30, 32, 39, 0.7);
      transition: transform 0.3s ease, background 0.3s ease;
    }
    
    .neighbor-row:hover {
      transform: translateX(5px);
      background: rgba(35, 38, 45, 0.95);
    }
    
    .neighbor-stock {
      font-size: 1.1rem;
      font-weight: 700;
      color: #fff;
      width: 120px;
      text-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
    }
    
    .influence-bar-container {
      flex: 1;
      height: 14px;
      background: rgba(167, 139, 250, 0.1);
      border-radius: 7px;
      overflow: hidden;
      box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.3);
    }
    
    .influence-bar {
      height: 100%;
      background: linear-gradient(90deg, #1db954 60%, #43e97b 100%);
      border-radius: 7px;
      box-shadow: 0 0 8px rgba(29, 185, 84, 0.4);
      transition: width 1s cubic-bezier(0.165, 0.84, 0.44, 1);
    }
    
    .influence-value {
      font-size: 1.2rem;
      font-weight: 800;
      color: #a78bfa;
      width: 60px;
      text-align: right;
      text-shadow: 0 0 8px rgba(167, 139, 250, 0.3);
    }
    
    @media (max-width: 768px) {
      .neighbor-row {
        flex-wrap: wrap;
      }
      
      .neighbor-stock {
        width: 100%;
        margin-bottom: 0.5rem;
      }
      
      .influence-bar-container {
        flex: 1 0 70%;
      }
      
      .influence-value {
        width: auto;
        flex: 1;
        text-align: right;
      }
    }
    /* Model Evaluation */
    .model-eval-section {
      background: rgba(36,38,44,0.97);
      border-radius: 1.5rem;
      box-shadow: 0 8px 32px 0 #1db95422, 0 1.5px 0 0 #1db954;
      border: 2.5px solid rgba(167,139,250,0.13);
      padding: 2.7rem 3.2rem 2.2rem 3.2rem;
      margin-bottom: 0;
      margin-top: 0;
      display: flex;
      flex-direction: column;
      align-items: center;
      max-width: 820px;
      width: 100%;
      align-self: center;
    }
    .model-eval-title {
      font-size: 1.55rem;
      font-weight: 1000;
      color: #1db954;
      margin-bottom: 1.5rem;
      letter-spacing: 0.01em;
      font-family: 'Inter', sans-serif;
      text-align: center;
      width: 100%;
    }
    .split-bar-container {
      width: 100%;
      margin: 1.7rem 0 1.2rem 0;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .split-bar {
      width: 95%;
      max-width: 700px;
      height: 3.5rem;
      border-radius: 2rem;
      background: #23272f;
      display: flex;
      overflow: hidden;
      box-shadow: 0 4px 24px #000a;
      margin-bottom: 1.1rem;
      font-size: 1.25rem;
      font-weight: 900;
      position: relative;
    }
    .split-train { background: linear-gradient(90deg, #1db954 60%, #43e97b 100%); width: 80%; border-top-left-radius: 2rem; border-bottom-left-radius: 2rem; z-index: 3; }
    .split-val { background: linear-gradient(90deg, #a78bfa 60%, #7c3aed 100%); width: 10%; z-index: 2; }
    .split-test { background: linear-gradient(90deg, #fbbf24 60%, #f59e42 100%); width: 10%; border-top-right-radius: 2rem; border-bottom-right-radius: 2rem; z-index: 1; }
    .split-bar.animate-out .split-train,
    .split-bar.animate-out .split-val,
    .split-bar.animate-out .split-test {
      width: 0 !important;
      transition: width 1.2s cubic-bezier(.77,0,.18,1);
    }
    .split-bar.animate-in .split-train { width: 80% !important; transition: width 1.2s cubic-bezier(.77,0,.18,1); }
    .split-bar.animate-in .split-val { width: 10% !important; transition: width 1.2s cubic-bezier(.77,0,.18,1); }
    .split-bar.animate-in .split-test { width: 10% !important; transition: width 1.2s cubic-bezier(.77,0,.18,1); }
    .split-labels {
      display: flex;
      width: 95%;
      max-width: 700px;
      margin-top: 0.2rem;
      align-self: center;
    }
    .split-label {
      font-size: 1.18rem;
      font-family: 'Inter', sans-serif;
      font-weight: 900;
      display: flex;
      flex-direction: column;
      justify-content: flex-start;
    }
    .split-label-train { color: #1db954; width: 80%; text-align: left; align-items: flex-start; }
    .split-label-val { color: #a78bfa; width: 10%; text-align: center; align-items: center; }
    .split-label-test { color: #fbbf24; width: 10%; text-align: right; align-items: flex-end; }
    .model-eval-desc {
      margin-top: 1.2rem;
      color: #e0e0e0;
      font-size: 1.18rem;
      max-width: 700px;
      text-align: center;
      font-family: 'Inter', sans-serif;
      line-height: 1.6;
      font-weight: 500;
      letter-spacing: 0.01em;
    }
    /* Model Comparison Panel */
    .model-comparison-panel {
        background: rgba(36, 38, 44, 0.95);
        border-radius: 1.2rem;
        padding: 2rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(29, 185, 84, 0.15);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        width: 100%;
    }

    .model-comparison-title {
        color: #1db954;
        font-size: 1.8rem;
        font-weight: 800;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }

    .model-comparison-subtitle {
        color: #e0e0e0;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        opacity: 0.9;
    }

    .comparison-controls {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }

    .control-group {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .control-label {
        color: #a78bfa;
        font-weight: 600;
        font-size: 0.95rem;
    }

    .comparison-input {
        background: rgba(36, 38, 44, 0.8);
        border: 1px solid rgba(167, 139, 250, 0.3);
        border-radius: 0.5rem;
        color: white;
        padding: 0.5rem 1rem;
        width: 100%;
    }

    .analyze-btn {
        background: linear-gradient(135deg, #1db954 0%, #a78bfa 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.8rem 2rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .analyze-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(29, 185, 84, 0.2);
    }

    .comparison-charts {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
        margin-top: 2rem;
        width: 100%;
    }

    .chart-container {
        background: rgba(36, 38, 44, 0.8);
        border-radius: 1rem;
        padding: 1.5rem;
        width: 100%;
        border: 1px solid rgba(167, 139, 250, 0.15);
        position: relative;
    }

    .chart-container.prediction-chart {
        min-height: 500px;  /* Increased height */
    }

    .chart-container.error-chart {
        min-height: 300px;
    }

    .chart-title {
        color: #1db954;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
        text-align: center;
    }

    #plotly_prediction, #plotly_error {
        width: 100% !important;
    }

    .js-plotly-plot {
        width: 100% !important;
    }

    /* Training Approach Visualization */
    .training-approach-section {
        width: 100%;
        max-width: 900px;
        margin: 2rem auto;
        padding: 2rem;
    }

    .split-visualization {
        background: rgba(36, 38, 44, 0.92);
        border-radius: 1.2rem;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(167, 139, 250, 0.15);
    }

    .split-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1db954;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 0 0 10px rgba(29, 185, 84, 0.3);
    }

    .split-bar {
        height: 60px;
        background: rgba(30, 32, 39, 0.7);
        border-radius: 30px;
        display: flex;
        overflow: hidden;
        margin-bottom: 1rem;
        position: relative;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
    }

    .split-train {
        width: 80%;
        background: linear-gradient(90deg, #1db954 60%, #43e97b 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        font-size: 1.1rem;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
        position: relative;
        overflow: hidden;
    }

    .split-val {
        width: 10%;
        background: linear-gradient(90deg, #a78bfa 60%, #7c3aed 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        font-size: 1.1rem;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    }

    .split-test {
        width: 10%;
        background: linear-gradient(90deg, #fbbf24 60%, #f59e42 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        font-size: 1.1rem;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    }

    .timeline-wrapper {
        margin-top: 1.5rem;
        padding: 0 1rem;
    }

    .timeline-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: #a78bfa;
    }

    .timeline-label {
        font-size: 1rem;
        font-weight: 600;
    }

    .timeline-arrow {
        font-size: 1.2rem;
        animation: arrow-pulse 2s infinite;
    }

    @keyframes arrow-pulse {
        0% { transform: translateX(0); opacity: 0.5; }
        50% { transform: translateX(10px); opacity: 1; }
        100% { transform: translateX(0); opacity: 0.5; }
    }

    /* Add shine animation to the split sections */
    .split-train::after,
    .split-val::after,
    .split-test::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.2),
            transparent
        );
        animation: shine 3s infinite;
    }

    @keyframes shine {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    """
    custom_js = """
window.togglePanel = function(id) {
  var chevron = document.getElementById('chevron-' + id);
  var content = document.getElementById('content-' + id);
  if (content.classList.contains('closed')) {
    content.classList.remove('closed');
    chevron.classList.add('open');
    // Animate split bar if Model Evaluation panel
    if (id === 'eval') {
      setTimeout(function() {
        var bar = document.querySelector('#content-eval .split-bar');
        var labels = document.querySelector('#content-eval .split-labels');
        if (bar) {
          bar.classList.remove('animate-out');
          bar.classList.add('animate-in');
        }
        if (labels) labels.classList.add('animated');
      }, 100);
    }
    // Animate influence bars if opening the stock interpretation panel
    if (id === 'stock_interp') {
      setTimeout(animateInfluenceBars, 500);
    }
  } else {
    content.classList.add('closed');
    chevron.classList.remove('open');
    // Reset split bar if Model Evaluation panel
    if (id === 'eval') {
      var bar = document.querySelector('#content-eval .split-bar');
      var labels = document.querySelector('#content-eval .split-labels');
      if (bar) {
        bar.classList.remove('animate-in');
        bar.classList.add('animate-out');
      }
      if (labels) labels.classList.remove('animated');
    }
  }
};

// Function to animate influence bars
function animateInfluenceBars() {
  document.querySelectorAll('.influence-bar').forEach(function(bar) {
    if (bar.dataset.value) {
      setTimeout(function() {
        bar.style.width = bar.dataset.value + '%';
      }, 100 + Math.random() * 300);
    }
  });
}

document.addEventListener('DOMContentLoaded', function() {
  setTimeout(function() {
    // Animate split bar if Model Evaluation panel is open by default
    var evalPanel = document.getElementById('content-eval');
    if (evalPanel && !evalPanel.classList.contains('closed')) {
      var bar = document.querySelector('#content-eval .split-bar');
      var labels = document.querySelector('#content-eval .split-labels');
      if (bar) {
        bar.classList.remove('animate-out');
        bar.classList.add('animate-in');
      }
      if (labels) labels.classList.add('animated');
    }
    
    // If stock interpretation panel is open by default, animate the bars
    var stockInterpPanel = document.getElementById('content-stock_interp');
    if (stockInterpPanel && !stockInterpPanel.classList.contains('closed')) {
      animateInfluenceBars();
    }
    
    // Animate bars when clicking Analyze button too
    document.getElementById('analyze_stock_btn').addEventListener('click', function() {
      setTimeout(animateInfluenceBars, 800);
    });
  }, 200);
});
"""
    return ui.TagList(
        ui.tags.style(custom_css),
        ui.tags.script(custom_js),
        ui.tags.div(
            # Page Header
            ui.tags.div(
                ui.tags.h1("Stock Volatility Model Explorer", class_="page-title"),
                ui.tags.p(
                    "Visualize stock volatility predictions and understand the factors that influence model decisions for individual stocks.",
                    class_="page-subtitle"
                ),
                class_="page-header"
            ),
            
            # Key Model Metrics Cards
            ui.tags.div(
                ui.tags.div(
                    ui.tags.div(
                        ui.tags.div(ui.tags.i(class_="fa fa-chart-simple"), class_="info-card-icon"),
                        ui.tags.div("Root Mean Square Error", class_="info-card-title"),
                        class_="info-card-header"
                    ),
                    ui.tags.div(
                        "Measures the average magnitude of prediction errors across all stocks.",
                        class_="info-card-content"
                    ),
                    ui.tags.div("0.3325", class_="metric-value"),
                    class_="info-card"
                ),
                ui.tags.div(
                    ui.tags.div(
                        ui.tags.div(ui.tags.i(class_="fa fa-percent"), class_="info-card-icon"),
                        ui.tags.div("RMSPE", class_="info-card-title"),
                        class_="info-card-header"
                    ),
                    ui.tags.div(
                        "Root Mean Square Percentage Error expresses average error as a percentage of true value.",
                        class_="info-card-content"
                    ),
                    ui.tags.div("33.25%", class_="metric-value"),
                    class_="info-card"
                ),
                ui.tags.div(
                    ui.tags.div(
                        ui.tags.div(ui.tags.i(class_="fa fa-circle-info"), class_="info-card-icon purple"),
                        ui.tags.div("QLIKE", class_="info-card-title"),
                        class_="info-card-header"
                    ),
                    ui.tags.div(
                        "Scale-sensitive error metric that penalizes under-predictions more than over-predictions.",
                        class_="info-card-content"
                    ),
                    ui.tags.div("5.59%", class_="metric-value"),
                    class_="info-card purple"
                ),
                ui.tags.div(
                    ui.tags.div(
                        ui.tags.div(ui.tags.i(class_="fa fa-lightbulb"), class_="info-card-icon purple"),
                        ui.tags.div("Model Approach", class_="info-card-title"),
                        class_="info-card-header"
                    ),
                    ui.tags.div(
                        "Graph-based neural network that captures both temporal trends and cross-asset dependencies to improve volatility predictions.",
                        class_="info-card-content"
                    ),
                    class_="info-card purple"
                ),
                class_="info-cards-container"
            ),
            
            # Stock Interpretation - MAIN SECTION
            panel_section(
                "stock_interp",
                "Stock-Level Interpretation",
                ui.output_ui("stock_interpretation_ui"),
                open_by_default=True
            ),
            
            # Model Comparison Section
            panel_section(
                "model_comparison",
                "Model Comparison",
                ui.tags.div(
                    ui.tags.div(
                        "Compare model predictions across stocks and time periods",
                        class_="model-comparison-subtitle",
                        style="color: #e0e0e0; font-size: 1.1rem; margin-bottom: 1.5rem; text-align: center;"
                    ),
                    # Controls Container
                    ui.tags.div(
                        # Left Panel - Stock and Time Selection
                        ui.tags.div(
                            # Stock Selection
                            ui.tags.div(
                                ui.tags.div(
                                    ui.tags.i(class_="fa fa-chart-line", style="color: #1db954; font-size: 1.2rem;"),
                                    ui.tags.span("Stock Selection", style="margin-left: 0.5rem; font-size: 1.2rem; font-weight: 600; color: #a78bfa;"),
                                    style="display: flex; align-items: center; margin-bottom: 1rem;"
                                ),
                                ui.input_select(
                                    "compare_stock_id", "",
                                    choices={sid: f"Stock {sid}" for sid in stock_ids},
                                    selected="2",
                                    width="100%"
                                ),
                                style="margin-bottom: 2rem; background: rgba(36, 38, 44, 0.6); padding: 1rem; border-radius: 0.8rem;"
                            ),
                            # Time Range Selection
                            ui.tags.div(
                                ui.tags.div(
                                    ui.tags.i(class_="fa fa-clock", style="color: #1db954; font-size: 1.2rem;"),
                                    ui.tags.span("Time Range", style="margin-left: 0.5rem; font-size: 1.2rem; font-weight: 600; color: #a78bfa;"),
                                    style="display: flex; align-items: center; margin-bottom: 1rem;"
                                ),
                                ui.input_slider(
                                    "compare_time_range", "",
                                    min=TIME_MIN, max=TIME_MAX,
                                    value=[TIME_MIN, TIME_MAX],
                                    step=10
                                ),
                                style="background: rgba(36, 38, 44, 0.6); padding: 1rem; border-radius: 0.8rem;"
                            ),
                            style="flex: 1.2; padding-right: 2rem;"
                        ),
                        # Right Panel - Model Selection
                        ui.tags.div(
                            ui.tags.div(
                                ui.tags.i(class_="fa fa-brain", style="color: #1db954; font-size: 1.2rem;"),
                                ui.tags.span("Model Selection", style="margin-left: 0.5rem; font-size: 1.2rem; font-weight: 600; color: #a78bfa;"),
                                style="display: flex; align-items: center; margin-bottom: 1rem;"
                            ),
                            ui.tags.div(
                                # Main Model (GAT)
                                ui.tags.div(
                                    ui.tags.div(
                                        ui.input_checkbox("model_GAT", "GAT", value=True),
                                        ui.tags.div(
                                            "Graph Attention Network",
                                            style="font-size: 0.8rem; color: #666; margin-top: 0.2rem;"
                                        ),
                                        style=f"margin-bottom: 1rem; color: {MODEL_COLORS['GAT']}; font-weight: 700; font-size: 1.1rem; padding: 0.8rem; background: rgba(255, 0, 102, 0.1); border-radius: 0.5rem;"
                                    ),
                                ),
                                # Divider
                                ui.tags.div(
                                    "Traditional Models",
                                    style="color: #666; font-size: 0.9rem; margin: 1rem 0; padding-top: 0.5rem; border-top: 1px solid #444;"
                                ),
                                # Traditional Models Group
                                ui.tags.div(
                                    *[ui.tags.div(
                                        ui.tags.div(
                                            ui.input_checkbox(
                                                f"model_{model_id}", 
                                                model_name,
                                                value=True
                                            ),
                                            ui.tags.div(
                                                f"RMSE: {MODEL_METRICS.get(model_name, {}).get('RMSE', 'N/A'):.6f}" if model_name in MODEL_METRICS else "",
                                                style="font-size: 0.75rem; color: #666; margin-top: 0.2rem;"
                                            ),
                                        ),
                                        style=f"margin-bottom: 0.8rem; color: {MODEL_COLORS[model_name]}; font-weight: 500; padding: 0.5rem; border-radius: 0.3rem; background: rgba(36, 38, 44, 0.3);"
                                    ) for model_id, model_name in [
                                        ('PCA_Linear', 'PCA Linear'),
                                        ('EWMA', 'EWMA'),
                                        ('LAG1', 'LAG1'),
                                        ('HAR_RV', 'HAR-RV')
                                    ]],
                                    style="margin-bottom: 1rem;"
                                ),
                                # Divider
                                ui.tags.div(
                                    "Machine Learning Models",
                                    style="color: #666; font-size: 0.9rem; margin: 1rem 0; padding-top: 0.5rem; border-top: 1px solid #444;"
                                ),
                                # ML Models Group
                                ui.tags.div(
                                    *[ui.tags.div(
                                        ui.tags.div(
                                            ui.input_checkbox(
                                                f"model_{model_id}", 
                                                model_name,
                                                value=True
                                            ),
                                            ui.tags.div(
                                                f"RMSE: {MODEL_METRICS.get(model_name, {}).get('RMSE', 'N/A'):.6f}" if model_name in MODEL_METRICS else "",
                                                style="font-size: 0.75rem; color: #666; margin-top: 0.2rem;"
                                            ),
                                        ),
                                        style=f"margin-bottom: 0.8rem; color: {MODEL_COLORS[model_name]}; font-weight: 500; padding: 0.5rem; border-radius: 0.3rem; background: rgba(36, 38, 44, 0.3);"
                                    ) for model_id, model_name in [
                                        ('Gradient_Boosting', 'Gradient Boosting'),
                                        ('Random_Forest', 'Random Forest'),
                                        ('Linear', 'Linear')
                                    ]],
                                ),
                                style="background: rgba(36, 38, 44, 0.6); padding: 1.2rem; border-radius: 0.8rem;"
                            ),
                            style="flex: 1; border-left: 1px solid #444; padding-left: 2rem;"
                        ),
                        style="padding: 2rem; background: rgba(36, 38, 44, 0.95); border-radius: 1rem; margin-bottom: 1.5rem; display: flex; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);"
                    ),
                    ui.output_plot("model_comparison_plot", width="100%", height="500px"),
                    ui.tags.div(style="height:1.5rem"),  # small spacer
                    ui.tags.div(
                        ui.output_table("model_metrics_table"),
                        style="overflow-x:auto; max-width:100%;"
                    ),
                    class_="model-comparison-content",
                    style="padding: 2rem; background: rgba(36, 38, 44, 0.92); border-radius: 1rem; margin-bottom: 2rem;"
                )
            ),
            
            # Training Approach Section
            panel_section(
                "eval",
                "Training Approach",
                ui.tags.div(
                    ui.output_ui("temporal_split_plot"),
                    ui.output_ui("training_flow_diagram"),
                    ui.output_ui("model_workflow_diagram"),
                    ui.tags.div(
                        "The dataset is split into three contiguous time blocks: 80% for training, 10% for validation, and 10% for testing. This approach preserves the natural temporal order of the data, ensuring that the model is always evaluated on future data it has never seen.",
                        class_="model-eval-desc"
                    )
                )
            ),
            
            # Model Details Section
            panel_section(
                "model",
                "Model Details",
                ui.tags.div(
                    ui.tags.div(
                        "Our graph-based model addresses the limitations of traditional linear approaches by treating assets as interconnected nodes within a financial network.",
                        class_="model-intro-subtitle"
                    ),
                    ui.tags.div(
                        ui.tags.div(
                            ui.tags.div(ui.tags.i(class_="fa fa-brain"), class_="model-intro-icon"),
                            ui.tags.div("Graph Neural Network", class_="model-intro-label"),
                            ui.tags.div("Models complex relationships between stocks, capturing how volatility in one asset can propagate through the market.", class_="model-intro-text"),
                            class_="model-intro-col"
                        ),
                        ui.tags.div(
                            ui.tags.div(ui.tags.i(class_="fa fa-chart-line"), class_="model-intro-icon"),
                            ui.tags.div("Temporal Features", class_="model-intro-label"),
                            ui.tags.div("Incorporates historical price patterns and multiple lagged realized volatility values to capture momentum and seasonality.", class_="model-intro-text"),
                            class_="model-intro-col"
                        ),
                        ui.tags.div(
                            ui.tags.div(ui.tags.i(class_="fa fa-network-wired"), class_="model-intro-icon"),
                            ui.tags.div("Attention Mechanism", class_="model-intro-label"),
                            ui.tags.div("Dynamically weighs connections between stocks based on their historical correlation patterns and market conditions.", class_="model-intro-text"),
                            class_="model-intro-col"
                        ),
                        class_="model-intro-row"
                    )
                )
            ),
            
            class_="model-section-group",
            style="width:100vw;display:flex;flex-direction:column;align-items:center;justify-content:center;"
        )
    )

def empty_plot(message):
    """Helper to create empty plot with message"""
    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor('#23272f')
    ax.set_facecolor('#23272f')
    ax.text(0.5, 0.5, message,
            ha='center', va='center',
            color='#a78bfa', fontsize=12)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    return fig

def setup_dark_plot(fig, ax):
    """Helper to setup dark mode plot styling"""
    fig.patch.set_facecolor('#23272f')
    ax.set_facecolor('#23272f')
    ax.tick_params(colors='#a78bfa')
    ax.grid(True, alpha=0.2, color='#a78bfa', linestyle='--')
    for spine in ax.spines.values():
        spine.set_color('#444')
    return ax

def server_model_details(input, output, session):
    @output
    @render.plot
    def model_comparison_plot():
        # Create figure with dark theme
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(12, 6))
        fig.patch.set_facecolor('#23272f')
        ax.set_facecolor('#23272f')
        
        # Get selected stock and time range
        stock_id = input.compare_stock_id()
        time_range = input.compare_time_range()
        time_start, time_end = time_range[0], time_range[1]
        
        # Get actual data first from any available model
        actual_data = None
        for model_name in MODEL_COLORS.keys():
            if model_name in model_data and model_data[model_name] is not None:
                df = model_data[model_name]
                df_filtered = df[
                    (df['stock_id'] == stock_id) & 
                    (df['time_id'].between(time_start, time_end))
                ]
                if not df_filtered.empty:
                    actual_data = df_filtered[['time_id', 'actual']]
                    break
        
        # Track if any models are selected and plot them
        any_model_selected = False
        max_volatility = 0
        min_volatility = float('inf')
        
        # Plot data for selected models
        for model_name, color in MODEL_COLORS.items():
            # Convert the display name to the checkbox input id suffix used in
            # the UI (spaces / hyphens -> underscores)
            model_id = _sanitize_model_id(model_name)

            # Skip models that are not selected by the user
            try:
                if not getattr(input, f"model_{model_id}")():
                    continue
            except Exception:
                # If the checkbox doesn't exist for some reason, skip safely
                continue

            any_model_selected = True
            if model_name in model_data and model_data[model_name] is not None:
                df = model_data[model_name]
                df_filtered = df[
                    (df['stock_id'] == stock_id) & 
                    (df['time_id'].between(time_start, time_end))
                ]
                if not df_filtered.empty:
                    # Plot model predictions
                    ax.plot(
                        df_filtered['time_id'],
                        df_filtered['predicted'],
                        label=f'{model_name}',
                        color=color,
                        linewidth=2.5,
                        alpha=0.8
                    )
                    max_volatility = max(max_volatility, df_filtered['predicted'].max())
                    min_volatility = min(min_volatility, df_filtered['predicted'].min())
        
        # Always plot actual values if we have them
        if actual_data is not None:
            label = 'Actual' if any_model_selected else 'Actual Values'
            line = ax.plot(
                actual_data['time_id'],
                actual_data['actual'],
                label=label,
                color='white',
                linestyle='--' if any_model_selected else '-',
                linewidth=2.5,
                alpha=0.9
            )
            max_volatility = max(max_volatility, actual_data['actual'].max())
            min_volatility = min(min_volatility, actual_data['actual'].min())
        
        # Customize plot
        title = f'Stock {stock_id} Volatility Predictions'
        if not any_model_selected:
            title += ' (Showing only actual values)'
        ax.set_title(title, color='#1db954', size=16, pad=20, fontweight='bold')
        ax.set_xlabel('Time', color='white', size=12, fontweight='bold')
        ax.set_ylabel('Volatility', color='white', size=12, fontweight='bold')
        
        # Set y-axis limit with padding
        if max_volatility > 0 or min_volatility < float('inf'):
            padding = (max_volatility - min_volatility) * 0.1 if max_volatility > min_volatility else max_volatility * 0.1
            ax.set_ylim(min_volatility - padding, max_volatility + padding)
        
        # Style the plot
        ax.grid(True, alpha=0.15, color='white', linestyle='--', linewidth=0.5)
        ax.tick_params(colors='#a78bfa', labelsize=10)
        
        # Make spines lighter
        for spine in ax.spines.values():
            spine.set_color('#444444')
            spine.set_linewidth(0.5)
            
        # Add legend with better positioning and styling
        if actual_data is not None or any_model_selected:  # Only add legend if there's something to show
            legend = ax.legend(
                facecolor='#23272f',
                edgecolor='#444444',
                fontsize=10,
                loc='upper right',
                bbox_to_anchor=(0.99, 0.99),
                framealpha=0.8,
                borderpad=1,
                labelspacing=0.8
            )
            for text in legend.get_texts():
                text.set_color('white')
        
        # Adjust layout
        plt.tight_layout()
        return fig

    # ------------------------------------------------------------------
    # Model metrics summary table
    # ------------------------------------------------------------------
    @output
    @render.table
    def model_metrics_table():
        """Display the metrics from ``model_metrics_summary.csv`` for the
        models that are currently selected in the checkbox list. If no model is
        selected, fall back to the GAT model so the table never appears empty.
        """

        if metrics_df is None or metrics_df.empty:
            return pd.DataFrame()

        # Determine which models the user has ticked
        selected = []
        for model_name in MODEL_COLORS.keys():
            model_id = _sanitize_model_id(model_name)
            try:
                if getattr(input, f"model_{model_id}")():
                    selected.append(model_name)
            except Exception:
                continue

        if not selected:
            # If no models selected, show all models
            selected = list(MODEL_COLORS.keys())

        # Filter the metrics dataframe (index is 'Model')
        df = metrics_df.copy()
        
        # Map model names to their display names
        model_display_names = {
            'GAT': 'GAT',
            'PCA_Linear': 'PCA Linear',
            'EWMA': 'EWMA',
            'LAG1': 'LAG1',
            'HAR_RV': 'HAR-RV',
            'Gradient_Boosting': 'Gradient Boosting',
            'Random_Forest': 'Random Forest',
            'Linear': 'Linear'
        }
        
        if "Model" in df.columns:
            # guard against unexpected structure
            df_filtered = df[df["Model"].isin(selected)].reset_index(drop=True)
            # Map model names to display names
            df_filtered['Model'] = df_filtered['Model'].map(lambda x: model_display_names.get(x, x))
        else:
            df_filtered = df.loc[df.index.intersection(selected)].reset_index()
            df_filtered['Model'] = df_filtered['Model'].map(lambda x: model_display_names.get(x, x))

        # Format numeric columns with appropriate decimal places
        if not df_filtered.empty:
            df_filtered['RMSE'] = df_filtered['RMSE'].apply(lambda x: f"{float(x):.6f}")
            df_filtered['QLIKE'] = df_filtered['QLIKE'].apply(lambda x: f"{float(x):.4f}")
            df_filtered['RMPSE'] = df_filtered['RMPSE'].apply(lambda x: f"{float(x):.2f}")

        # Add custom styling
        styled_df = df_filtered.style\
            .set_properties(**{
                'background-color': '#23272f',
                'color': 'white',
                'border': '1px solid #444',
                'padding': '12px 15px',
                'font-size': '14px',
                'text-align': 'center'
            })\
            .set_table_styles([
                {'selector': 'thead th', 
                 'props': [
                     ('background-color', '#1e2027'),
                     ('color', '#1db954'),
                     ('font-weight', 'bold'),
                     ('padding', '12px 15px'),
                     ('border', '1px solid #444'),
                     ('font-size', '15px')
                 ]},
                {'selector': 'tbody tr:hover',
                 'props': [('background-color', '#2a2d36')]},
                {'selector': 'tbody tr:nth-child(even)',
                 'props': [('background-color', '#20232b')]},
            ])\
            .hide(axis="index")  # Hide index column

        return styled_df

    # Create interpretation data reactive Calc inside server to access valid input
    @reactive.Calc
    def interp_data():
        if explain_df is None:
            return None
        sid = input.interp_stock_id()
        try:
            time_val = int(input.interp_time_id())
        except Exception:
            time_val = None
        df_sub = explain_df[explain_df['stock_idx'] == sid]
        if df_sub.empty:
            return None
        if time_val is None or time_val not in df_sub['time_idx'].values:
            time_val = df_sub['time_idx'].max()
        row = df_sub[df_sub['time_idx'] == time_val].iloc[0]
        fi_cols = [c for c in df_sub.columns if c.startswith('fi_')]
        fi = {c.replace('fi_',''): row[c] for c in fi_cols}
        neighbors = []
        for i in range(1,4):
            s_col = f'nbr{i}_stock'
            w_col = f'nbr{i}_weight'
            if s_col in row and w_col in row:
                neighbors.append({'stock': str(row[s_col]).replace('Stock ','').strip(), 'influence': float(row[w_col])})
        return {
            'feature_importance': fi,
            'prediction': row['prediction'],
            'actual': row['actual'],
            'history': df_sub.sort_values('time_idx'),
            'neighbors': neighbors,
            'stock_id': sid
        }

    # --- Stock Interpretation Content ---
    @output
    @render.ui
    def stock_interpretation_ui():
        return ui.tags.div(
            ui.tags.div(
                "Select a stock and time period to see detailed model interpretation",
                class_="model-interp-subtitle"
            ),
            ui.tags.div(
                ui.tags.div(
                    ui.input_select(
                        "interp_stock_id",
                        "Stock ID",
                        {sid: f"Stock {sid}" for sid in stock_ids},
                        selected=stock_ids[0] if stock_ids else "43",
                        width="100%"
                    ),
                    class_="interp-control"
                ),
                ui.tags.div(
                    ui.input_numeric("interp_time_id", "Time Index (0-latest)", value=0, min=0, step=1, width="100%"),
                    class_="interp-control"
                ),
                ui.tags.div(
                    ui.input_action_button("analyze_stock_btn", "Analyze", class_="analyze-btn"),
                    class_="interp-control"
                ),
                class_="interp-controls-row"
            ),
            ui.tags.div(
                ui.tags.div(
                    ui.tags.i(class_="fa fa-chart-bar"),
                    ui.tags.div("Feature Importance Analysis", class_="section-title"),
                    class_="section-header"
                ),
                ui.tags.div(
                    ui.tags.div(ui.output_plot("feature_importance_plot"), class_="plot-container"),
                    ui.tags.div(ui.output_plot("prediction_vs_actual_plot"), class_="plot-container"),
                    class_="interp-plots-row"
                ),
                class_="plots-section"
            ),
            ui.tags.div(
                ui.output_ui("influential_neighbors_ui"),
                class_="interp-neighbors-container"
            ),
            id="stock_interp_content"
        )

    @output
    @render.plot
    def feature_importance_plot():
        data = interp_data()
        if data is None:
            return empty_plot('Click Analyze to see Feature Importance')
        fi = data['feature_importance']
        if not fi:
            return empty_plot('No feature importance available')
        keys = list(fi.keys())
        vals = list(fi.values())
        fig, ax = plt.subplots(figsize=(4,3))
        setup_dark_plot(fig, ax)
        ax.barh(keys, vals, color='#1db954')
        ax.set_xlabel('Importance', color='white')
        ax.tick_params(colors='#a78bfa')
        plt.tight_layout()
        return fig

    @output
    @render.plot
    def prediction_vs_actual_plot():
        data = interp_data()
        if data is None:
            return empty_plot('Click Analyze to see Prediction vs Actual')
        hist = data['history']
        fig, ax = plt.subplots(figsize=(4,3))
        setup_dark_plot(fig, ax)
        ax.plot(hist['time_idx'], hist['prediction'], label='Pred', color='#1db954')
        ax.plot(hist['time_idx'], hist['actual'], label='Actual', color='#a78bfa')
        ax.legend(facecolor='#23272f', edgecolor='#23272f')
        ax.set_xlabel('Time', color='white')
        ax.set_ylabel('Volatility', color='white')
        plt.tight_layout()
        return fig

    @output
    @render.ui
    def influential_neighbors_ui():
        data = interp_data()
        if data is None or not data['neighbors']:
            return ui.tags.div(
                ui.tags.div(
                    ui.tags.i(class_='fa fa-network-wired'),
                    ui.tags.div('Network Influence Analysis', class_='section-title'),
                    class_='section-header'
                ),
                ui.tags.div('Analyze a stock to see its influential neighbors', class_='neighbors-placeholder'),
                class_='neighbors-container'
            )
        neighbor_rows = []
        for n in data['neighbors']:
            neighbor_rows.append(
                ui.tags.div(
                    ui.tags.div(f"Stock {n['stock']}", class_='neighbor-stock'),
                    ui.tags.div(
                        ui.tags.div(style=f"width:{n['influence']*100:.0f}%", class_='influence-bar'),
                        class_='influence-bar-container'
                    ),
                    ui.tags.div(f"{n['influence']:.2f}", class_='influence-value'),
                    class_='neighbor-row'
                )
            )
        return ui.tags.div(
            ui.tags.div(
                ui.tags.i(class_='fa fa-network-wired'),
                ui.tags.div('Network Influence Analysis', class_='section-title'),
                class_='section-header'
            ),
            ui.tags.div(*neighbor_rows, class_='neighbors-list'),
            class_='neighbors-container'
        )

    @output
    @render.ui
    def temporal_split_plot():
        return ui.tags.div(
            ui.tags.div(
                ui.tags.div("Data Split Timeline", class_="split-title"),
                ui.tags.div(
                    ui.tags.div("Training (80%)", class_="split-train"),
                    ui.tags.div("Val (10%)", class_="split-val"),
                    ui.tags.div("Test (10%)", class_="split-test"),
                    class_="split-bar"
                ),
                ui.tags.div(
                    ui.tags.div(
                        ui.tags.div("Time", class_="timeline-label"),
                        ui.tags.div(
                            ui.tags.i(class_="fa fa-arrow-right"),
                            class_="timeline-arrow"
                        ),
                        class_="timeline-container"
                    ),
                    class_="timeline-wrapper"
                ),
                class_="split-visualization"
            ),
            class_="training-approach-section"
        )
