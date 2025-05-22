from shiny import ui, render, reactive
from faicons import icon_svg
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go

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
      padding: 1.5rem;
      min-width: 280px;
      max-width: 600px;
      width: 100%;
      border: 1px solid rgba(167, 139, 250, 0.15);
      position: relative;
      overflow: hidden;
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
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: linear-gradient(90deg, #1db954, #a78bfa);
      border-radius: 1rem 1rem 0 0;
      opacity: 0.7;
      transition: opacity 0.3s ease;
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
            
            # Key Model Details in Collapsibles
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
                    ),
                )
            ),
            
            # Compact Model Introduction
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

# --- Server logic for network graph ---
def server_model_details(input, output, session):
    # --- Load real explanations data ---
    try:
        explain_df = pd.read_csv("data/mini_all_explanations.csv")
    except Exception as _:
        explain_df = None

    # Precompute choices for stock and time ids
    if explain_df is not None:
        STOCK_CHOICES = {str(s): f"Stock {s}" for s in sorted(explain_df["stock_idx"].unique())}
        MAX_TIME = int(explain_df["time_idx"].max())
    else:
        STOCK_CHOICES = {"43": "Stock 43"}
        MAX_TIME = 0

    # Track selected stock and time_id
    selected_stock = reactive.Value("43")
    selected_time = reactive.Value("-1")
    last_analyzed = reactive.Value(False)
    
    # React to the analyze button click
    @reactive.Effect
    @reactive.event(input.analyze_stock_btn)
    def _():
        selected_stock.set(input.interp_stock_id())
        selected_time.set(input.interp_time_id())
        last_analyzed.set(True)
        # In a real application, this would trigger an API call
        # or data loading operation to get the specific model outputs
        print(f"Analyzing stock {selected_stock()} at time {selected_time()}")
    
    @reactive.Calc
    def get_stock_interpretation_data():
        if not last_analyzed() or explain_df is None:
            return None

        try:
            sid = int(selected_stock())
            # obtain subset for stock
            sub = explain_df[explain_df["stock_idx"] == sid].sort_values("time_idx")
            if sub.empty:
                return None

            # determine offset based on selected_time (string like "-1")
            idx = int(selected_time())
            if idx not in sub["time_idx"].values:
                idx = int(sub["time_idx"].max())
            row = sub[sub["time_idx"] == idx].iloc[0]

            # extract values
            pred = float(row["prediction"])
            actual = float(row["actual"])
            err_pct = float(row["error_pct"])

            # feature importance columns start with 'fi_'
            fi_cols = [c for c in explain_df.columns if c.startswith("fi_")]
            fi_dict = {c.replace("fi_", "").strip(): float(row[c]) for c in fi_cols}

            # neighbors
            neighbors = []
            for i in range(1,4):
                stock_col = f"nbr{i}_stock"
                weight_col = f"nbr{i}_weight"
                if stock_col in row and weight_col in row:
                    neighbors.append({"stock": str(row[stock_col]).replace("Stock ", "").strip(), "influence": float(row[weight_col])})

            return {
                "stock_id": selected_stock(),
                "time_id": row["time_idx"],
                "prediction": pred,
                "actual": actual,
                "error_pct": err_pct,
                "feature_importance": fi_dict,
                "influential_neighbors": neighbors,
                "history": sub  # full df for plotting
            }
        except Exception as _:
            return None
    
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

    @output
    @render.ui
    def temporal_split_plot():
        return ui.HTML("""
<div class="temporal-split-bar-wrap">
  <div class="temporal-split-bar">
    <div class="split-segment train">
      <span class="split-tooltip">Train: 80%</span>
    </div>
    <div class="split-segment val">
      <span class="split-tooltip">Validation: 10%</span>
    </div>
    <div class="split-segment test">
      <span class="split-tooltip">Test: 10%</span>
    </div>
  </div>
</div>
<style>
.temporal-split-bar-wrap { width: 100%; max-width: 700px; margin: 0 auto 2.2rem auto; }
.temporal-split-bar {
  display: flex; height: 3.5rem; border-radius: 2rem; overflow: visible;
  box-shadow: 0 4px 24px #000a; background: #23272f;
  position: relative;
}
.split-segment {
  height: 100%; transition: background 0.3s, box-shadow 0.3s, transform 0.2s; position: relative;
  box-shadow: 0 0 16px 0 rgba(29,185,84,0.12), 0 2px 8px 0 rgba(167,139,250,0.10);
  overflow: visible;
}
.split-segment.train { width: 80%; background: linear-gradient(90deg, #1db954 60%, #43e97b 100%); box-shadow: 0 0 24px 0 #1db95455; }
.split-segment.val { width: 10%; background: linear-gradient(90deg, #a78bfa 60%, #7c3aed 100%); box-shadow: 0 0 24px 0 #a78bfa55; }
.split-segment.test { width: 10%; background: linear-gradient(90deg, #fbbf24 60%, #f59e42 100%); box-shadow: 0 0 24px 0 #fbbf2455; }
.split-segment:hover {
  filter: brightness(1.12);
  transform: scale(1.03);
  z-index: 2;
  box-shadow: 0 0 32px 0 #fff5, 0 0 24px 0 #1db95455;
}
.split-tooltip {
  visibility: hidden;
  opacity: 0;
  position: absolute;
  left: 50%;
  top: 110%;
  transform: translateX(-50%);
  background: #23272f;
  color: #fff;
  padding: 0.7rem 1.2rem;
  border-radius: 0.9rem;
  font-size: 1.13rem;
  font-weight: 900;
  white-space: nowrap;
  box-shadow: 0 2px 12px #1db95422;
  z-index: 10;
  transition: opacity 0.2s, visibility 0.2s;
  pointer-events: none;
}
.split-segment:hover .split-tooltip {
  visibility: visible;
  opacity: 1;
  pointer-events: auto;
}
</style>
""")

    @output
    @render.ui
    def training_flow_diagram():
        return ui.HTML("""
<div class="training-flow-diagram">
  <div class="flow-block train" title="Train: 80%">Train</div>
  <svg class="flow-arrow" width="60" height="32"><polygon points="0,16 50,16 40,8 40,24" fill="#fff"/></svg>
  <div class="flow-block val" title="Validation: 10%">Validation</div>
  <svg class="flow-arrow" width="60" height="32"><polygon points="0,16 50,16 40,8 40,24" fill="#fff"/></svg>
  <div class="flow-block test" title="Test: 10%">Test</div>
</div>
<style>
.training-flow-diagram {
  display: flex; align-items: center; justify-content: center; gap: 0.7rem; margin: 2.2rem 0;
}
.flow-block {
  padding: 0.9rem 2.2rem; border-radius: 1.2rem; font-size: 1.18rem; font-weight: 900;
  font-family: 'Inter', sans-serif; color: #23272f; box-shadow: 0 2px 12px #1db95422;
  transition: filter 0.2s;
}
.flow-block.train { background: linear-gradient(135deg, #1db954 60%, #43e97b 100%); }
.flow-block.val { background: linear-gradient(135deg, #a78bfa 60%, #7c3aed 100%); }
.flow-block.test { background: linear-gradient(135deg, #fbbf24 60%, #f59e42 100%); }
.flow-block:hover { filter: brightness(1.15); cursor: pointer; }
.flow-arrow { display: inline-block; vertical-align: middle; }
</style>
""")

    @output
    @render.ui
    def model_workflow_diagram():
        return ui.HTML("""
<div class="workflow-diagram-container">
  <div class="workflow-diagram">
    <!-- Top row -->
    <div class="workflow-row">
      <div class="workflow-box train-box">
        Train model<br>on Training Set
      </div>
      <div class="workflow-arrow">→</div>
      <div class="workflow-box validate-box">
        Evaluate model<br>on Validation Set
      </div>
    </div>
    
    <!-- Loop arrow -->
    <div class="workflow-loop-container">
      <div class="workflow-loop-arrow"></div>
    </div>
    
    <!-- Middle row with transparent box -->
    <div class="workflow-row center-row">
      <div class="workflow-transparent-box">
        Tweak model according<br>to results on <span class="highlight-validation">Validation Set</span>
      </div>
    </div>
    
    <!-- Bottom row -->
    <div class="workflow-row">
      <div class="workflow-box train-box">
        Pick model that does<br>best on <span class="highlight-validation">Validation Set</span>
      </div>
      <div class="workflow-arrow">→</div>
      <div class="workflow-box test-box">
        Confirm results<br>on <span class="highlight-test">Test Set</span>
      </div>
    </div>
  </div>
</div>
<style>
.workflow-diagram-container {
  width: 100%;
  max-width: 650px;
  margin: 2rem auto;
}

.workflow-diagram {
  background-color: rgba(30, 32, 42, 0.5);
  border: 2px dashed rgba(68, 85, 137, 0.7);
  border-radius: 16px;
  padding: 30px 25px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.workflow-row {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  margin-bottom: 10px;
  position: relative;
  z-index: 2;
}

.workflow-box {
  padding: 1.1rem 1rem;
  border-radius: 8px;
  text-align: center;
  font-weight: 600;
  color: white;
  line-height: 1.5;
  width: 45%;
  max-width: 240px;
  font-size: 0.95rem;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.25);
}

.train-box {
  background: linear-gradient(to bottom, #0c6e32, #0e5a2a);
  border: 2px solid #1db954;
}

.validate-box {
  background: linear-gradient(to bottom, #543ba3, #412c82);
  border: 2px solid #7c3aed;
}

.test-box {
  background: linear-gradient(to bottom, #9c6614, #805111);
  border: 2px solid #fbbf24;
}

.workflow-transparent-box {
  text-align: center;
  font-weight: 500;
  line-height: 1.5;
  color: #e0e0e0;
  font-size: 0.95rem;
  padding: 10px;
  margin: 5px 0 15px 0;
}

.highlight-validation {
  color: #a78bfa;
  font-weight: 700;
  text-decoration: underline;
  text-decoration-color: #a78bfa;
  text-underline-offset: 3px;
}

.highlight-test {
  color: #fbbf24;
  font-weight: 700;
  text-decoration: underline;
  text-decoration-color: #fbbf24;
  text-underline-offset: 3px;
}

.workflow-arrow {
  margin: 0 15px;
  color: white;
  font-size: 1.6rem;
  font-weight: bold;
}

.workflow-loop-container {
  position: relative;
  width: 60%;
  height: 50px;
  margin-top: 10px;
}

.workflow-loop-container::before {
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  top: -5px;
  height: 5px;
  border-left: 3px solid #7c3aed;
  border-right: 3px solid #7c3aed;
}

.workflow-loop-container::after {
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  height: 30px;
  border-left: 3px solid #7c3aed;
  border-right: 3px solid #7c3aed;
  border-bottom: 3px solid #7c3aed;
  border-bottom-left-radius: 10px;
  border-bottom-right-radius: 10px;
}

.workflow-loop-arrow {
  position: absolute;
  top: -5px;
  left: -2px;
  width: 0;
  height: 0;
  border-top: 10px solid transparent;
  border-bottom: 10px solid transparent;
  border-right: 15px solid #7c3aed;
  transform: rotate(270deg);
  z-index: 3;
}

.center-row {
  margin-top: -20px;
  z-index: 1;
}

@media (max-width: 768px) {
  .workflow-box {
    width: 42%;
    padding: 0.8rem 0.6rem;
    font-size: 0.85rem;
  }
  
  .workflow-arrow {
    margin: 0 10px;
    font-size: 1.4rem;
  }
  
  .workflow-transparent-box {
    font-size: 0.85rem;
  }
}
</style>
""")

    # --- Add interactive stock selection for model interpretation ---
    @output
    @render.ui
    def stock_interpretation_ui():
        return ui.tags.div(
            ui.tags.div(
                ui.tags.div(
                    "Select a stock and time period to see detailed model interpretation",
                    class_="model-interp-subtitle"
                ),
                ui.tags.div(
                    ui.tags.div(
                        ui.input_select(
                            "interp_stock_id", 
                            "Stock ID",
                            STOCK_CHOICES,
                            selected="43",
                            width="100%"
                        ),
                        class_="interp-control"
                    ),
                    ui.tags.div(
                        ui.input_numeric("interp_time_id", "Time Index (0-latest)", value=MAX_TIME, min=0, max=MAX_TIME, step=1, width="100%"),
                        class_="interp-control"
                    ),
                    ui.tags.div(
                        ui.input_action_button(
                            "analyze_stock_btn",
                            "Analyze",
                            class_="analyze-btn"
                        ),
                        class_="interp-control"
                    ),
                    class_="interp-controls-row"
                ),
                class_="stock-interp-header"
            ),
            ui.output_ui("stock_prediction_metrics"),
            ui.tags.div(
                ui.tags.div(
                    ui.tags.i(class_="fa fa-chart-bar"),
                    ui.tags.div("Feature Importance Analysis", class_="section-title"),
                    class_="section-header"
                ),
                ui.tags.div(
                    ui.tags.div(
                        ui.output_ui("feature_importance_plot"),
                        class_="plot-container"
                    ),
                    ui.tags.div(
                        ui.output_ui("prediction_vs_actual_plot"),
                        class_="plot-container"
                    ),
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
    @render.ui
    def stock_prediction_metrics():
        data = get_stock_interpretation_data()
        if data is None:
            return ui.tags.div(
                ui.tags.div("Click 'Analyze' to view model prediction details", class_="metrics-placeholder"),
                class_="prediction-metrics-section"
            )
        
        pred_val = data["prediction"]
        actual_val = data["actual"]
        return ui.tags.div(
            ui.tags.div(
                ui.tags.div(
                    ui.tags.div(f"Stock {data['stock_id']} Prediction Analysis", class_="metric-card-title"),
                    ui.tags.div(
                        ui.tags.div(
                            ui.tags.div("Predicted", class_="metric-label"),
                            ui.tags.div(f"{pred_val:.6f}", class_="metric-value prediction"),
                            class_="metric-value-item"
                        ),
                        ui.tags.div(
                            ui.tags.div("Actual", class_="metric-label"),
                            ui.tags.div(f"{actual_val:.6f}", class_="metric-value actual"),
                            class_="metric-value-item"
                        ),
                        ui.tags.div(
                            ui.tags.div("Error", class_="metric-label"),
                            ui.tags.div(f"{data['error_pct']:.2f}%", class_="metric-value error"),
                            class_="metric-value-item"
                        ),
                        class_="metric-values-container"
                    ),
                    class_="metric-card"
                ),
                class_="metrics-container"
            ),
            class_="prediction-metrics-section"
        )
    
    @output
    @render.ui
    def feature_importance_plot():
        data = get_stock_interpretation_data()
        if data is None:
            # Return an empty plot if no data
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.update_layout(
                title='Click "Analyze" to see Feature Importance',
                template='plotly_dark',
                plot_bgcolor='rgba(36,38,44,0.8)',
                paper_bgcolor='rgba(36,38,44,0.8)',
                height=400,
                width=500
            )
            return ui.HTML(fig.to_html(include_plotlyjs="cdn"))
        
        import plotly.graph_objects as go
        import pandas as pd
        
        # Get feature importance data
        feature_importance = data["feature_importance"]
        
        # Create a DataFrame for plotting
        df = pd.DataFrame({
            'Feature': list(feature_importance.keys()),
            'Importance': list(feature_importance.values())
        })
        
        # Sort by importance
        df = df.sort_values('Importance', ascending=True)
        
        # Create a horizontal bar chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=df['Feature'],
            x=df['Importance'],
            orientation='h',
            marker_color=['rgba(29,185,84,0.8)' if x > 0.5 else 'rgba(167,139,250,0.8)' for x in df['Importance']],
            text=[f"{x:.3f}" for x in df['Importance']],
            textposition='auto'
        ))
        
        fig.update_layout(
            title=f'Feature Importance for Stock {data["stock_id"]}',
            xaxis_title='Importance Score',
            yaxis_title='Feature',
            template='plotly_dark',
            plot_bgcolor='rgba(36,38,44,0.8)',
            paper_bgcolor='rgba(36,38,44,0.8)',
            font=dict(
                family="Inter, sans-serif",
                size=12,
                color="#ffffff"
            ),
            margin=dict(l=10, r=10, t=50, b=10),
            height=400,
            width=500,
            xaxis=dict(
                range=[0, max(df['Importance']) * 1.1],
                showgrid=True,
                gridcolor='rgba(255,255,255,0.1)'
            )
        )
        
        return ui.HTML(fig.to_html(include_plotlyjs="cdn"))
    
    @output
    @render.ui
    def prediction_vs_actual_plot():
        data = get_stock_interpretation_data()
        if data is None:
            # Return an empty plot if no data
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.update_layout(
                title='Click "Analyze" to see Prediction vs Actual',
                template='plotly_dark',
                plot_bgcolor='rgba(36,38,44,0.8)',
                paper_bgcolor='rgba(36,38,44,0.8)',
                height=400,
                width=500
            )
            return ui.HTML(fig.to_html(include_plotlyjs="cdn"))
            
        # Build historical series from data['history']
        import plotly.graph_objects as go
        hist = data["history"].sort_values("time_idx")
        dates = pd.to_datetime(hist["time_idx"], unit='D', origin='unix', errors='coerce') if 'time_idx' in hist else list(range(len(hist)))
        if hasattr(dates, "tolist"):
            dates = dates.tolist()
        predictions = hist["prediction"].tolist()
        actuals = hist["actual"].tolist()
        
        # Create a line chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=predictions,
            mode='lines+markers',
            name='Predicted',
            line=dict(color='#1db954', width=3),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=actuals,
            mode='lines+markers',
            name='Actual',
            line=dict(color='#a78bfa', width=3),
            marker=dict(size=8)
        ))
        
        # Highlight the last point (current prediction)
        fig.add_trace(go.Scatter(
            x=[dates[-1]],
            y=[predictions[-1]],
            mode='markers',
            name='Current Prediction',
            marker=dict(color='#1db954', size=14, line=dict(color='white', width=2))
        ))
        
        fig.add_trace(go.Scatter(
            x=[dates[-1]],
            y=[actuals[-1]],
            mode='markers',
            name='Current Actual',
            marker=dict(color='#a78bfa', size=14, line=dict(color='white', width=2))
        ))
        
        fig.update_layout(
            title=f'Prediction vs Actual Over Time for Stock {data["stock_id"]}',
            xaxis_title='Date',
            yaxis_title='Realized Volatility',
            template='plotly_dark',
            plot_bgcolor='rgba(36,38,44,0.8)',
            paper_bgcolor='rgba(36,38,44,0.8)',
            font=dict(
                family="Inter, sans-serif",
                size=12,
                color="#ffffff"
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=10, r=10, t=50, b=50),
            height=400,
            width=500
        )
        
        return ui.HTML(fig.to_html(include_plotlyjs="cdn"))
    
    @output
    @render.ui
    def influential_neighbors_ui():
        data = get_stock_interpretation_data()
        if data is None:
            return ui.tags.div(
                ui.tags.div(
                    ui.tags.i(class_="fa fa-network-wired"),
                    ui.tags.div("Network Influence Analysis", class_="section-title"),
                    class_="section-header"
                ),
                ui.tags.div("Analyze a stock to see its influential neighbors", class_="neighbors-placeholder"),
                class_="neighbors-container"
            )
            
        # Get influential neighbors data
        neighbors = data["influential_neighbors"]
        
        neighbor_elements = []
        for neighbor in neighbors:
            neighbor_elements.append(
                ui.tags.div(
                    ui.tags.div(f"Stock {neighbor['stock']}", class_="neighbor-stock"),
                    ui.tags.div(
                        ui.tags.div(
                            style=f"width: {neighbor['influence']*100:.0f}%",
                            class_="influence-bar",
                            id=f"bar-{neighbor['stock']}",
                            **{"data-value": f"{neighbor['influence']:.2f}"}
                        ),
                        class_="influence-bar-container"
                    ),
                    ui.tags.div(f"{neighbor['influence']:.2f}", class_="influence-value"),
                    class_="neighbor-row"
                )
            )
        
        return ui.tags.div(
            ui.tags.div(
                ui.tags.i(class_="fa fa-network-wired"),
                ui.tags.div("Network Influence Analysis", class_="section-title"),
                class_="section-header"
            ),
            ui.tags.div(f"Influential Neighbors for Stock {data['stock_id']}", class_="neighbors-title"),
            ui.tags.div(
                *neighbor_elements,
                class_="neighbors-list"
            ),
            class_="neighbors-container"
        )
