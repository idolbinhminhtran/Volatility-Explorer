from shiny import ui, render
from faicons import icon_svg
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

def ui_model_details():
    custom_css = """
    .model-section-group {
      display: flex;
      flex-direction: column;
      align-items: center;
      width: 100%;
      max-width: 900px;
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
      display: none;
    }
    @keyframes fadeInPanel {
      from { opacity: 0; transform: translateY(24px); }
      to { opacity: 1; transform: translateY(0); }
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
      gap: 2.2rem;
      margin-bottom: 0;
      justify-content: flex-start;
      flex-wrap: wrap;
    }
    .model-summary-card {
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
    .model-comparison-placeholder {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 260px;
      background: rgba(36,38,44,0.92);
      border-radius: 1.2rem;
      box-shadow: 0 2px 12px #1db95422;
      margin: 2.2rem 0 1.2rem 0;
      padding: 2.2rem 1.5rem 1.7rem 1.5rem;
      color: #bdbdbd;
      font-size: 1.25rem;
      font-family: 'Inter', sans-serif;
      font-weight: 700;
      text-align: center;
      gap: 1.2rem;
    }
    .model-comparison-placeholder .fa {
      font-size: 3.5rem;
      color: #a78bfa;
      margin-bottom: 0.7rem;
      filter: drop-shadow(0 0 8px #1db954);
    }
    .model-network-plot-wrap {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 260px;
      background: rgba(36,38,44,0.92);
      border-radius: 1.2rem;
      box-shadow: 0 2px 12px #1db95422;
      margin: 2.2rem 0 1.2rem 0;
      padding: 2.2rem 1.5rem 1.7rem 1.5rem;
      color: #bdbdbd;
      font-size: 1.25rem;
      font-family: 'Inter', sans-serif;
      font-weight: 700;
      text-align: center;
      gap: 1.2rem;
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
  }, 200);
});
"""
    return ui.TagList(
        ui.tags.style(custom_css),
        ui.tags.script(custom_js),
        ui.tags.div(
            ui.tags.div(
                # --- Model Introduction Panel ---
                ui.tags.div(
                    ui.tags.div(
                        "Model Introduction",
                        ui.tags.span(icon_svg("chevron-right"), id="chevron-intro", class_="collapsible-chevron"),
                        class_="collapsible-header",
                        onclick="togglePanel('intro')"
                    ),
                    ui.tags.div(
                        ui.tags.div(
                            "Volatility prediction remains a core challenge in financial markets due to its complex and dynamic nature.",
                            class_="model-intro-subtitle"
                        ),
                        ui.tags.div(
                            ui.tags.div(
                                ui.tags.div(icon_svg("lightbulb"), class_="model-intro-icon"),
                                ui.tags.div("Problem:", class_="model-intro-label"),
                                ui.tags.div("Traditional linear models often fall short – they assume independence and static relationships that don't reflect real market conditions.", class_="model-intro-text"),
                                class_="model-intro-col"
                            ),
                            ui.tags.div(
                                ui.tags.div(icon_svg("bullseye"), class_="model-intro-icon"),
                                ui.tags.div("To combat this:", class_="model-intro-label"),
                                ui.tags.div("A graph-based neural network models assets as interconnected nodes, capturing both temporal trends and cross-asset dependencies to improve volatility predictions.", class_="model-intro-text"),
                                class_="model-intro-col"
                            ),
                            class_="model-intro-row"
                        ),
                        class_="collapsible-content closed",
                        id="content-intro"
                    ),
                    class_="collapsible-panel"
                ),
                # --- Model Evaluation Panel (now above Metrics) ---
                ui.tags.div(
                    ui.tags.div(
                        "Model Evaluation",
                        ui.tags.span(icon_svg("chevron-right"), id="chevron-eval", class_="collapsible-chevron"),
                        class_="collapsible-header",
                        onclick="togglePanel('eval')"
                    ),
                    ui.tags.div(
                        ui.tags.div(
                            ui.tags.div(
                                ui.tags.div(
                                    ui.tags.div(class_="split-train"),
                                    ui.tags.div(class_="split-val"),
                                    ui.tags.div(class_="split-test"),
                                    class_="split-bar"
                                ),
                                ui.tags.div(
                                    ui.tags.span("Train (80%)", class_="split-label split-label-train"),
                                    ui.tags.span("Validation (10%)", class_="split-label split-label-val"),
                                    ui.tags.span("Test (10%)", class_="split-label split-label-test"),
                                    class_="split-labels"
                                ),
                                class_="split-bar-container"
                            ),
                            ui.tags.div(
                                "The dataset is split into three contiguous time blocks: 80% for training, 10% for validation, and 10% for testing. This approach preserves the natural temporal order of the data, ensuring that the model is always evaluated on future data it has never seen. By avoiding random shuffling, we prevent data leakage and create a more realistic assessment of model performance in real-world forecasting.",
                                class_="model-eval-desc"
                            ),
                            class_="collapsible-content closed",
                            id="content-eval"
                        ),
                        class_="collapsible-panel"
                    ),
                ),
                # --- Model Metrics Panel (now below Evaluation) ---
                ui.tags.div(
                    ui.tags.div(
                        "Model Metrics",
                        ui.tags.span(icon_svg("chevron-right"), id="chevron-metrics", class_="collapsible-chevron"),
                        class_="collapsible-header",
                        onclick="togglePanel('metrics')"
                    ),
                    ui.tags.div(
                        ui.tags.div(
                            ui.tags.div(
                                ui.tags.div(icon_svg("chart-simple"), class_="model-summary-icon rmse"),
                                ui.tags.div(
                                    ui.tags.div("RMSE", class_="model-summary-label"),
                                    ui.tags.span("0.3325", class_="model-summary-value"),
                                    class_="model-summary-content"
                                ),
                                ui.tags.div("Root Mean Square Error: Measures the average magnitude of prediction errors. Lower is better.", class_="metric-tooltip"),
                                class_="model-summary-card"
                            ),
                            ui.tags.div(
                                ui.tags.div(icon_svg("percent"), class_="model-summary-icon rmspe"),
                                ui.tags.div(
                                    ui.tags.div("RMSPE", class_="model-summary-label"),
                                    ui.tags.span("33.25%", class_="model-summary-value"),
                                    class_="model-summary-content"
                                ),
                                ui.tags.div("Root Mean Square Percentage Error: Expresses average prediction error as a percentage of the true value. Lower is better.", class_="metric-tooltip"),
                                class_="model-summary-card"
                            ),
                            ui.tags.div(
                                ui.tags.div(icon_svg("circle-info"), class_="model-summary-icon qlike"),
                                ui.tags.div(
                                    ui.tags.div("QLIKE", class_="model-summary-label"),
                                    ui.tags.span("5.59%", class_="model-summary-value"),
                                    class_="model-summary-content"
                                ),
                                ui.tags.div("QLIKE: A scale-sensitive error metric. Lower values indicate less scale error.", class_="metric-tooltip"),
                                class_="model-summary-card"
                            ),
                            ui.tags.div(
                                ui.tags.div(icon_svg("star"), class_="model-summary-icon f1"),
                                ui.tags.div(
                                    ui.tags.div("F1 Score", class_="model-summary-label"),
                                    ui.tags.span("0.82", class_="model-summary-value"),
                                    class_="model-summary-content"
                                ),
                                ui.tags.div("F1 Score: Harmonic mean of precision and recall for high-volatility detection.", class_="metric-tooltip"),
                                class_="model-summary-card"
                            ),
                            ui.tags.div(
                                ui.tags.div(icon_svg("chart-area"), class_="model-summary-icon auc"),
                                ui.tags.div(
                                    ui.tags.div("AUC", class_="model-summary-label"),
                                    ui.tags.span("0.91", class_="model-summary-value"),
                                    class_="model-summary-content"
                                ),
                                ui.tags.div("AUC: Probability the model ranks a high-volatility period above a low one.", class_="metric-tooltip"),
                                class_="model-summary-card"
                            ),
                            class_="model-summary-row"
                        ),
                        class_="collapsible-content closed",
                        id="content-metrics"
                    ),
                    class_="collapsible-panel"
                ),
                # --- Model Comparison Panel ---
                ui.tags.div(
                    ui.tags.div(
                        "Model Comparison",
                        ui.tags.span(icon_svg("chevron-right"), id="chevron-comparison", class_="collapsible-chevron"),
                        class_="collapsible-header",
                        onclick="togglePanel('comparison')"
                    ),
                    ui.tags.div(
                        ui.tags.div(
                            ui.tags.i(class_="fa fa-chart-bar"),
                            ui.tags.div("Comparison plot coming soon...", style="margin-top:1.2rem;font-size:1.18rem;color:#bdbdbd;font-family:'Inter',sans-serif;font-weight:700;"),
                            class_="model-comparison-placeholder"
                        ),
                        class_="collapsible-content closed",
                        id="content-comparison"
                    ),
                    class_="collapsible-panel"
                ),
                # --- Network View Panel ---
                ui.tags.div(
                    ui.tags.div(
                        "Network View",
                        ui.tags.span(icon_svg("chevron-right"), id="chevron-network", class_="collapsible-chevron"),
                        class_="collapsible-header",
                        onclick="togglePanel('network')"
                    ),
                    ui.tags.div(
                        ui.output_ui("network_graph_ui"),
                        class_="collapsible-content closed",
                        id="content-network"
                    ),
                    class_="collapsible-panel"
                ),
                class_="model-section-group"
            ),
            style="width:100vw;display:flex;flex-direction:column;align-items:center;justify-content:center;"
        )
    )

# --- Server logic for network graph ---
def server_model_details(input, output, session):
    @output
    @render.ui
    def network_graph_ui():
        try:
            df = pd.read_csv("data/high_attention_pairs.csv")
            if df.empty:
                return ui.tags.div("No data in high_attention_pairs.csv", style="text-align:center;color:#a78bfa;font-size:1.2rem;padding:2.5rem 0;", class_="model-network-plot-wrap")
            top_pairs = df.nlargest(7, "WEIGHT")
            G = nx.Graph()
            for _, row in top_pairs.iterrows():
                G.add_edge(str(row["SOURCE"]), str(row["TARGET"]), weight=row["WEIGHT"])
            pos = nx.spring_layout(G, seed=42)
            plt.figure(figsize=(6, 4))
            edges = G.edges(data=True)
            weights = [d['weight']*10 for (_, _, d) in edges]
            nx.draw_networkx_edges(G, pos, width=weights, edge_color="#a78bfa", alpha=0.6)
            nx.draw_networkx_nodes(G, pos, node_color="#1db954", node_size=600, alpha=0.85)
            nx.draw_networkx_labels(G, pos, font_color="#fff", font_weight="bold")
            plt.axis('off')
            import io
            buf = io.BytesIO()
            plt.tight_layout()
            plt.savefig(buf, format="png", bbox_inches="tight", transparent=True)
            plt.close()
            buf.seek(0)
            import base64
            img_b64 = base64.b64encode(buf.read()).decode("utf-8")
            return ui.tags.div(
                ui.tags.img(src=f"data:image/png;base64,{img_b64}", style="display:block;margin:0 auto;max-width:100%;height:auto;border-radius:1.2rem;box-shadow:0 2px 12px #1db95422;"),
                class_="model-network-plot-wrap",
                style="display:flex;justify-content:center;align-items:center;text-align:center;min-height:260px;"
            )
        except Exception as e:
            return ui.tags.div(f"Error rendering network: {e}", style="text-align:center;color:#a78bfa;font-size:1.2rem;padding:2.5rem 0;", class_="model-network-plot-wrap")
