import os
from shiny import App, ui, render, reactive
from shinyswatch import theme
from faicons import icon_svg
from modules.screener import ui_screener, server_screener
from modules.portfolio_tracker import ui_portfolio_tracker, server_portfolio_tracker
from modules.individual_stock import ui_individual_stock, server_individual_stock
from modules.screener import stock_cols, vol_df
from modules.stock_comparison import ui_stock_comparison, server_stock_comparison
from modules.model_details import ui_model_details, server_model_details
import pandas as pd
import numpy as np

css = """
:root {
  --primary: #1db954; /* Spotify green */
  --accent: #a78bfa;  /* Soft purple */
  --background: #f5f7fa;
  --background-sidebar: linear-gradient(135deg, #f5f7fa 0%, #e3e6f3 100%);
  --background-card: #fff;
  --background-topbar: linear-gradient(90deg, #f5f7fa 0%, #e3e6f3 100%);
  --shadow: 0 4px 24px rgba(29,185,84,0.10);
  --shadow-hover: 0 8px 32px rgba(29,185,84,0.18);
  --text: #23272f;
  --text-accent: #1db954;
  --text-highlight: #a78bfa;
  --border: #e2e8f0;
  --sidebar-link-bg: #e3e6f3;
  --sidebar-link-hover: #e0e7ef;
  --sidebar-link-active: linear-gradient(90deg, #1db954 80%, #a78bfa 100%);
  --sidebar-link-color: #23272f;
  --sidebar-link-active-color: #fff;
  --button-bg: #a78bfa;
  --button-bg-hover: #1db954;
  --button-text: #fff;
}
.dark-mode {
  --primary: #1db954; /* Spotify green */
  --accent: #a78bfa;  /* Soft purple */
  --background: #18191c;
  --background-sidebar: #18191c; /* Make sidebar blend with background */
  --background-card: #23272f;
  --background-topbar: linear-gradient(90deg, #18191c 0%, #23272f 100%);
  --shadow: 0 4px 24px rgba(29,185,84,0.10);
  --shadow-hover: 0 8px 32px rgba(29,185,84,0.18);
  --text: #f5f7fa;
  --text-accent: #1db954;
  --text-highlight: #a78bfa;
  --border: #23272f;
  --sidebar-link-bg: #23272f; /* Blend nav buttons with background */
  --sidebar-link-hover: #23272f;
  --sidebar-link-active: #23272f; /* Active nav button blends in */
  --sidebar-link-color: #f5f7fa;
  --sidebar-link-active-color: #1db954;
  --button-bg: #a78bfa;
  --button-bg-hover: #1db954;
  --button-text: #fff;
}
body, .dashboard-layout {
  background: var(--background) !important;
  color: var(--text);
  transition: background 0.5s cubic-bezier(.77,0,.18,1), color 0.5s cubic-bezier(.77,0,.18,1);
}
.dashboard-layout {
  display: flex;
  flex-direction: row;
  min-height: 100vh;
  transition: background 0.5s cubic-bezier(.77,0,.18,1);
}
.sidebar {
  width: 260px;
  background: var(--background-sidebar);
  border-radius: 0;
  box-shadow: none;
  border: none;
  display: flex;
  flex-direction: column;
  padding: 2rem 1.2rem 1.2rem 1.2rem;
  min-height: 80vh;
  z-index: 10;
  position: relative;
  overflow: visible;
  margin: 2rem 0 2rem 1.5rem;
  gap: 2.2rem;
}
.sidebar-section {
  margin-bottom: 1.5rem;
}
.sidebar-divider {
  border: none;
  border-top: 1.5px solid rgba(167,139,250,0.12);
  margin: 1.2rem 0;
}
.watchlist-section {
  margin-top: 0.5rem;
}
.watchlist-title {
  font-size: 1.15rem;
  font-weight: 900;
  color: var(--primary);
  margin-bottom: 0.7rem;
  letter-spacing: 0.03em;
  position: relative;
  background: linear-gradient(90deg, var(--primary) 60%, var(--accent) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.watchlist-title::after {
  content: "";
  display: block;
  width: 32px;
  height: 3px;
  background: linear-gradient(90deg, var(--primary), var(--accent));
  border-radius: 2px;
  margin-top: 0.3rem;
}
.watchlist-list {
  list-style: none;
  padding: 0;
  margin: 0 0 0.5rem 0;
}
.watchlist-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1.08rem;
  margin-bottom: 0.5rem;
  border-bottom: 1px solid rgba(167,139,250,0.08);
  padding: 0.2rem 0.1rem 0.2rem 0.1rem;
  transition: background 0.2s;
  border-radius: 0.5rem;
}
.watchlist-list li:last-child {
  border-bottom: none;
}
.watchlist-list li:hover {
  background: rgba(167,139,250,0.10);
}
.watchlist-list .pos, .watchlist-list .neg {
  font-weight: 700;
  padding: 0.1rem 0.7rem;
  border-radius: 1rem;
  font-size: 1.05rem;
  margin-left: 0.5rem;
  display: flex;
  align-items: center;
}
.watchlist-list .pos {
  color: #1db954;
  background: rgba(29,185,84,0.10);
}
.watchlist-list .neg {
  color: #c62828;
  background: rgba(198,40,40,0.10);
}
.watchlist-list .pos::before {
  content: '\f062';
  font-family: 'Font Awesome 6 Free';
  font-weight: 900;
  margin-right: 0.4em;
  font-size: 0.95em;
}
.watchlist-list .neg::before {
  content: '\f063';
  font-family: 'Font Awesome 6 Free';
  font-weight: 900;
  margin-right: 0.4em;
  font-size: 0.95em;
}
.watchlist-viewall {
  color: #fff;
  font-size: 1.01rem;
  text-align: center;
  margin-top: 0.9rem;
  cursor: pointer;
  text-decoration: none;
  background: linear-gradient(90deg, var(--primary), var(--accent));
  border-radius: 1.2rem;
  padding: 0.45rem 1.2rem;
  display: inline-block;
  font-weight: 700;
  letter-spacing: 0.01em;
  box-shadow: 0 2px 8px var(--shadow);
  transition: background 0.2s, color 0.2s, box-shadow 0.2s;
}
.watchlist-viewall:hover {
  background: linear-gradient(90deg, var(--accent), var(--primary));
  color: #fff;
  box-shadow: 0 4px 16px var(--shadow-hover);
}
.sidebar::before {
  content: "";
  position: absolute;
  top: -2px; left: -2px; right: -2px; bottom: -2px;
  border-radius: 1.7rem 0 0 1.7rem;
  pointer-events: none;
  z-index: 0;
  box-shadow: 0 0 16px 2px var(--accent), 0 0 32px 4px var(--primary);
  opacity: 0.18;
  animation: sidebar-glow 3s ease-in-out infinite alternate;
}
@keyframes sidebar-glow {
  0% { box-shadow: 0 0 16px 2px var(--accent), 0 0 32px 4px var(--primary); }
  100% { box-shadow: 0 0 32px 8px var(--primary), 0 0 16px 2px var(--accent); }
}
.sidebar-section-title {
  font-size: 1.25rem;
  font-weight: 900;
  color: var(--primary);
  margin-bottom: 0.7rem;
  letter-spacing: 0.04em;
  position: relative;
  text-transform: uppercase;
  background: linear-gradient(90deg, var(--primary) 60%, var(--accent) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.sidebar-section-title::after {
  content: "";
  display: block;
  width: 38px;
  height: 3px;
  background: linear-gradient(90deg, var(--primary), var(--accent));
  border-radius: 2px;
  margin-top: 0.3rem;
}
.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
  margin-bottom: 1.5rem;
}
.sidebar-link {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.9rem;
  background: rgba(36, 38, 44, 0.85);
  color: var(--sidebar-link-color) !important;
  border: none;
  border-radius: 0.9rem;
  font-size: 1.08rem;
  font-weight: 600;
  padding: 0.95rem 1.3rem;
  margin: 0;
  text-align: left;
  box-shadow: 0 2px 12px var(--shadow);
  transition: background 0.3s, color 0.3s, box-shadow 0.3s, transform 0.3s, border 0.3s;
  cursor: pointer;
  outline: none;
  opacity: 0.96;
  position: relative;
  overflow: hidden;
  z-index: 1;
  border: 1.5px solid transparent;
  backdrop-filter: blur(2px);
}
.sidebar-link .fa {
  font-size: 1.25em;
  opacity: 0.88;
  transition: color 0.18s, transform 0.18s;
}
.sidebar-link:hover {
  background: linear-gradient(90deg, rgba(29,185,84,0.12) 0%, rgba(167,139,250,0.10) 100%);
  color: var(--primary) !important;
  transform: translateX(4px) scale(1.05);
  box-shadow: 0 6px 24px var(--shadow-hover);
  opacity: 1;
  border: 1.5px solid var(--primary);
}
.sidebar-link:hover .fa {
  color: var(--primary);
  animation: icon-bounce 0.4s;
}
@keyframes icon-bounce {
  0% { transform: scale(1) rotate(-8deg);}
  50% { transform: scale(1.25) rotate(-8deg);}
  100% { transform: scale(1.18) rotate(-8deg);}
}
.sidebar-link.active, .sidebar-link[aria-pressed="true"] {
  background: linear-gradient(90deg, var(--primary) 80%, var(--accent) 100%);
  color: #fff !important;
  font-weight: 700;
  box-shadow: 0 10px 36px var(--shadow-hover), 4px 0 0 0 var(--primary);
  border-left: 4px solid var(--primary);
  border: 1.5px solid var(--primary);
  transform: scale(1.06);
  opacity: 1;
}
.sidebar-link.active .fa, .sidebar-link[aria-pressed="true"] .fa {
  color: #fff;
  opacity: 1;
  transform: scale(1.18) rotate(-8deg);
}
.sidebar-profile {
  margin-top: auto;
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 1.2rem 0 0.7rem 0;
  border-top: 1px solid rgba(167,139,250,0.18);
  justify-content: flex-start;
}
.sidebar-profile-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 1.3rem;
  font-weight: 700;
  box-shadow: 0 2px 8px var(--shadow);
  border: 2px solid #fff2;
}
.sidebar-profile-name {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--primary);
  margin-left: 0.2rem;
}
.topbar {
  border-radius: 0;
  width: 100%;
  margin: 0;
  background: rgba(32,34,38,0.98);
  box-shadow: 0 6px 32px 0 rgba(167,139,250,0.10), 0 1.5px 0 0 var(--accent);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.1rem 2.5rem 1.1rem 2.2rem;
  position: relative;
  min-height: 64px;
  border: 1.5px solid rgba(167,139,250,0.18);
  transition: box-shadow 0.3s, background 0.3s;
}
.topbar:hover {
  box-shadow: 0 12px 48px 0 rgba(167,139,250,0.18), 0 1.5px 0 0 var(--primary);
  background: rgba(32,34,38,1);
}
.topbar-gradient-bar {
  position: absolute;
  left: 0; right: 0; bottom: 0;
  height: 4px;
  border-radius: 0 0 1.2rem 1.2rem;
  background: linear-gradient(90deg, var(--primary), var(--accent), var(--primary));
  opacity: 0.85;
  animation: gradient-move 4s linear infinite;
}
@keyframes gradient-move {
  0% { background-position: 0% 50%; }
  100% { background-position: 100% 50%; }
}
.topbar-title {
  font-size: 2.2rem !important;
  font-weight: 1000;
  letter-spacing: 0.02em;
  background: linear-gradient(90deg, var(--primary) 60%, var(--accent) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: flex;
  align-items: center;
  gap: 0.7rem;
  line-height: 1.1;
  padding-bottom: 0.1rem;
  text-transform: uppercase;
}
.topbar-left {
  display: flex;
  align-items: center;
  gap: 1.1rem;
}
.topbar-left .fa-chart-pie {
  font-size: 2.5rem !important;
  color: var(--primary);
  filter: drop-shadow(0 0 8px var(--accent));
  margin-right: 0.7rem;
}
.topbar-updated {
  font-size: 1.05rem;
  color: var(--primary);
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  opacity: 0.85;
  margin-right: 1.5rem;
}
.topbar-right {
  display: flex;
  align-items: center;
  gap: 0.7rem;
}
.topbar-icon-btn {
  background: rgba(167,139,250,0.10);
  border: none;
  border-radius: 50%;
  width: 2.3rem;
  height: 2.3rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: var(--primary);
  cursor: pointer;
  transition: background 0.2s, color 0.2s, box-shadow 0.2s;
  box-shadow: 0 2px 8px var(--shadow);
}
.topbar-icon-btn:hover {
  background: var(--accent);
  color: #fff;
  box-shadow: 0 4px 16px var(--shadow-hover);
  transform: scale(1.08);
}
.topbar-pro {
  background: var(--accent);
  color: #fff;
  font-size: 1.05rem;
  font-weight: 700;
  border-radius: 0.7rem;
  padding: 0.25rem 0.9rem;
  box-shadow: 0 2px 8px var(--shadow);
  letter-spacing: 0.03em;
}
.topbar-darkmode {
  font-size: 1.3rem;
  margin-left: 1.5rem;
  color: var(--primary);
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.18s, transform 0.18s;
  outline: none;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}
.topbar-darkmode .fa {
  transition: transform 0.5s cubic-bezier(.77,0,.18,1), color 0.5s cubic-bezier(.77,0,.18,1);
}
.topbar-darkmode.animated .fa {
  transform: rotate(180deg) scale(1.3);
  color: var(--accent);
}
.topbar-darkmode:hover {
  color: var(--accent);
  transform: scale(1.15) rotate(-10deg);
}
.main-content {
  flex: 1 1 0%;
  padding: 2.5rem 1rem;
  background: var(--background);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  animation: main-fade-in 0.7s cubic-bezier(.77,0,.18,1) 1;
  transition: background 0.5s cubic-bezier(.77,0,.18,1), color 0.5s cubic-bezier(.77,0,.18,1);
  width: 100%;
  box-sizing: border-box;
}
@keyframes main-fade-in {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}
.summary-cards-row {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 2.2rem;
}
.summary-card {
  background: var(--background-card);
  border-radius: 1.2rem;
  box-shadow: var(--shadow);
  padding: 1.5rem 2.2rem;
  min-width: 180px;
  flex: 1 1 0;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  border: none;
  transition: box-shadow 0.3s, background 0.5s cubic-bezier(.77,0,.18,1), color 0.5s cubic-bezier(.77,0,.18,1);
}
.summary-card:hover {
  box-shadow: var(--shadow-hover);
  transform: translateY(-4px) scale(1.03);
}
.summary-card-title {
  font-size: 1.08rem;
  color: var(--primary);
  font-weight: 600;
  margin-bottom: 0.3rem;
}
.summary-card-value {
  font-size: 2rem;
  font-weight: 900;
  color: var(--primary);
  background: linear-gradient(90deg, var(--primary) 60%, var(--accent) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.main-row {
  display: flex;
  gap: 2.2rem;
  margin-bottom: 2.5rem;
}
.main-chart-card {
  background: var(--background-card);
  border-radius: 1.2rem;
  box-shadow: var(--shadow);
  padding: 2rem 2.5rem;
  flex: 2 1 0;
  min-width: 0;
  display: flex;
  flex-direction: column;
  border: none;
  transition: box-shadow 0.3s, background 0.5s cubic-bezier(.77,0,.18,1), color 0.5s cubic-bezier(.77,0,.18,1);
}
.main-chart-card:hover {
  box-shadow: var(--shadow-hover);
  transform: translateY(-4px) scale(1.02);
}
.main-chart-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 1rem;
}
.side-card {
  background: var(--background-card);
  border-radius: 1.2rem;
  box-shadow: var(--shadow);
  padding: 2rem 1.5rem;
  flex: 1 1 0;
  min-width: 220px;
  display: flex;
  flex-direction: column;
  border: none;
  transition: box-shadow 0.3s, background 0.5s cubic-bezier(.77,0,.18,1), color 0.5s cubic-bezier(.77,0,.18,1);
}
.side-card:hover {
  box-shadow: var(--shadow-hover);
  transform: translateY(-4px) scale(1.02);
}
.side-card-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 1rem;
}
.heatmap-cards-row {
  margin-top: 1.5rem;
}
.heatmap-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 1.2rem;
}
.forecast-card {
  background: var(--background-card);
  border-radius: 1rem;
  box-shadow: 0 2px 8px var(--shadow);
  padding: 1.2rem 1.5rem;
  margin-bottom: 1.2rem;
  display: flex;
  flex-direction: column;
  min-width: 220px;
  transition: box-shadow 0.3s, background 0.5s cubic-bezier(.77,0,.18,1), color 0.5s cubic-bezier(.77,0,.18,1);
}
.forecast-card:hover {
  box-shadow: var(--shadow-hover);
  transform: translateY(-4px) scale(1.02);
}
.forecast-card.negative {
  background: linear-gradient(135deg, #ffebee 60%, var(--background-card) 100%);
}
.forecast-card .stock-symbol {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--primary);
}
.forecast-card .stock-change {
  font-size: 1rem;
  font-weight: 600;
  margin-left: 0.7rem;
}
.forecast-card .stock-change.positive { color: var(--primary); }
.forecast-card .stock-change.negative { color: #c62828; }
@media (max-width: 1100px) {
  .main-row { flex-direction: column; }
  .side-card { min-width: 0; margin-top: 1.5rem; }
  .summary-cards-row { flex-direction: column; gap: 1rem; }
}
@media (max-width: 900px) {
  .dashboard-layout { flex-direction: column; }
  .sidebar { width: 100%; min-height: unset; flex-direction: row; padding: 1rem; }
  .main-content { padding: 1.2rem; }
  .topbar-title { font-size: 1.3rem !important; }
  .topbar-left .fa-chart-pie { font-size: 1.5rem !important; }
  .section-separator { margin: 1.2rem 0 1.2rem 0; }
}
@media (max-width: 600px) {
  .summary-card-value { font-size: 1.2rem; }
  .main-content { padding: 0.5rem; }
  .sidebar { padding: 0.5rem; }
}
.main-content-container {
  padding: 0;
  flex: 1 1 0%;
  display: flex;
  flex-direction: column;
  width: 100%;
}
.dashboard-container {
  max-width: none;
  margin: 0;
  padding: 0;
  width: 100%;
}
.overview-card {
  background: rgba(36, 38, 44, 0.95);
  border-radius: 1.5rem;
  box-shadow: 0 6px 32px 0 rgba(29,185,84,0.10), 0 1.5px 0 0 var(--primary);
  border: 2.5px solid rgba(167,139,250,0.10);
  padding: 2.2rem 2.2rem 1.7rem 2.2rem;
  min-width: 260px;
  min-height: 180px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  transition: box-shadow 0.3s, border 0.3s, transform 0.3s, background 0.5s;
  position: relative;
  margin: 0.5rem;
}
.overview-card:hover {
  box-shadow: 0 16px 48px 0 var(--primary), 0 0 32px 4px var(--accent);
  border: 2.5px solid var(--primary);
  transform: translateY(-8px) scale(1.045);
  z-index: 2;
}
.overview-card.negative {
  background: linear-gradient(135deg, #c62828 80%, #ff8a65 100%);
  color: #fff;
  border: 2.5px solid #c62828;
  box-shadow: 0 8px 32px 0 rgba(198,40,40,0.18), 0 4px 16px #c62828;
}
.overview-card.negative:hover {
  box-shadow: 0 16px 48px 0 #c62828, 0 0 32px 4px #ff8a65;
  border: 2.5px solid #ff8a65;
  background: linear-gradient(120deg, #ff8a65 60%, #c62828 100%);
}
.overview-card .stock-symbol {
  font-size: 1.5rem;
  font-weight: 1000;
  color: var(--primary);
  margin-bottom: 0.2rem;
  letter-spacing: 0.02em;
  text-shadow: 0 1px 4px #000a;
}
.overview-card.negative .stock-symbol {
  color: #fff;
  text-shadow: 0 1px 4px #c62828;
}
.overview-card .company-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: #bdbdbd;
  margin-bottom: 0.5rem;
}
.overview-card .stat-row {
  font-size: 1.05rem;
  color: #e0e0e0;
  margin-bottom: 0.1rem;
}
.overview-card .error-label {
  font-size: 1.1rem;
  font-weight: 700;
  margin-top: 0.7rem;
  color: #fff;
  opacity: 0.7;
}
.overview-card .error-value {
  font-size: 2rem;
  font-weight: 1000;
  margin-top: 0.2rem;
  color: var(--primary);
}
.overview-card.negative .error-value {
  color: #fff;
  text-shadow: 0 1px 4px #c62828;
}
.overview-card-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 1.2rem 1.2rem;
  justify-content: flex-start;
  width: 100%;
}
.summary-cards-row-overview {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 2.2rem;
  flex-wrap: wrap;
}
.summary-card-overview {
  position: relative;
  overflow: hidden;
  border: 2.5px solid transparent;
  background: rgba(60, 65, 80, 0.55);
  background-clip: padding-box;
  box-shadow: 0 8px 32px 0 rgba(29,185,84,0.12), 0 1.5px 0 0 var(--accent);
  border-radius: 1.2rem;
  transition: box-shadow 0.3s, transform 0.3s, border 0.3s, background 0.5s;
}
.summary-card-overview::before {
  content: "";
  position: absolute;
  inset: -2px;
  border-radius: 1.3rem;
  z-index: 1;
  pointer-events: none;
  background: linear-gradient(120deg, var(--primary), var(--accent), var(--primary));
  opacity: 0.22;
  filter: blur(2.5px);
  animation: border-glow-2 3.5s linear infinite alternate;
}
@keyframes border-glow-2 {
  0% { filter: blur(2.5px); opacity: 0.18; }
  100% { filter: blur(4.5px); opacity: 0.32; }
}
.summary-card-overview::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: 1.2rem;
  pointer-events: none;
  z-index: 0;
  background: linear-gradient(120deg, rgba(167,139,250,0.13) 0%, rgba(29,185,84,0.13) 100%);
  opacity: 0.18;
  animation: card-shimmer 7s ease-in-out infinite alternate;
}
@keyframes card-shimmer {
  0% { background-position: 0% 50%; }
  100% { background-position: 100% 50%; }
}
.summary-card-overview:hover {
  box-shadow: 0 24px 64px 0 var(--shadow-hover), 0 0 32px 4px var(--accent);
  border-color: var(--accent);
  transform: translateY(-8px) scale(1.045);
}
.summary-card-content {
  padding: 1.1rem 4.2rem 0.9rem 1.2rem;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  min-height: 90px;
  justify-content: center;
  z-index: 2;
  position: relative;
}
.summary-card-overview .summary-card-title {
  color: var(--text) !important;
  font-weight: 900;
  font-size: 1.13rem;
  margin-bottom: 0.1rem;
  letter-spacing: 0.01em;
  line-height: 1.2;
  z-index: 2;
}
.summary-card-overview .summary-card-value {
  font-size: 3.2rem;
  font-weight: 1200;
  color: #fff;
  letter-spacing: 0.01em;
  background: none !important;
  -webkit-background-clip: unset;
  -webkit-text-fill-color: unset;
  text-shadow: none;
  margin-bottom: 0.1rem;
  z-index: 2;
  transition: color 0.4s;
  box-shadow: none !important;
  border-radius: 0.5rem;
  padding: 0.2rem 0.5rem;
}
.summary-card-overview:hover .summary-card-value {
  color: var(--primary);
  text-shadow: 0 0 32px var(--accent), 0 2px 32px var(--primary), 0 1px 0 #fff9;
}
.summary-card-overview .summary-card-icon {
  position: absolute;
  top: 50%;
  right: 1.1rem;
  transform: translateY(-50%);
  z-index: 3;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.8rem;
  height: 2.8rem;
  border-radius: 50%;
  font-size: 1.55rem;
  color: var(--primary) !important;
  background: #fff;
  box-shadow: 0 0 24px 6px var(--accent), 0 2px 12px 0 rgba(29,185,84,0.10);
  border: 2px solid var(--accent);
  transition: box-shadow 0.3s, transform 0.3s, background 0.3s, color 0.3s;
}
.summary-card-overview .summary-card-icon.blue { color: #4f8cff !important; }
.summary-card-overview .summary-card-icon.purple { color: var(--accent) !important; }
.summary-card-overview .summary-card-icon.yellow { color: #fbbf24 !important; }
.summary-card-overview:hover .summary-card-icon {
  box-shadow: 0 0 48px 12px var(--accent), 0 2px 8px var(--shadow);
  background: #f5f7fa;
  color: var(--primary) !important;
  transform: translateY(-50%) scale(1.13);
  animation: icon-pulse-2 0.7s;
}
@keyframes icon-pulse-2 {
  0% { transform: translateY(-50%) scale(1); }
  50% { transform: translateY(-50%) scale(1.18) rotate(-8deg);}
  100% { transform: translateY(-50%) scale(1.13); }
}
.attention-pairs-card {
  background: linear-gradient(135deg, #23272f 60%, #232f27 100%);
  border-radius: 1.5rem;
  box-shadow: 0 8px 32px 0 rgba(29,185,84,0.10), 0 1.5px 0 0 var(--primary);
  border: 2.5px solid rgba(167,139,250,0.10);
  padding: 2.2rem 2.2rem 1.7rem 2.2rem;
  max-width: 520px;
  margin-top: 2.5rem;
  position: relative;
  overflow: hidden;
}
.attention-pairs-title {
  font-weight: 1000;
  font-size: 1.35rem;
  color: var(--primary);
  margin-bottom: 1.1rem;
  letter-spacing: 0.01em;
}
.attention-pairs-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0 0.7rem;
  font-size: 1.13rem;
}
.attention-pairs-table th {
  text-align: left;
  padding: 0.7rem 1rem 0.7rem 0.5rem;
  font-size: 1.08rem;
  font-weight: 1000;
  color: #fff;
  letter-spacing: 0.04em;
  background: none;
  border: none;
  opacity: 0.95;
}
.attention-pairs-table td {
  padding: 0.7rem 1rem 0.7rem 0.5rem;
  font-weight: 700;
  color: #fff;
  background: none;
  border: none;
  vertical-align: middle;
  transition: background 0.2s;
}
.attention-pairs-table tr {
  border-radius: 0.7rem;
  transition: background 0.2s, transform 0.2s;
}
.attention-pairs-table tr:hover {
  background: rgba(29,185,84,0.08);
  transform: scale(1.01);
}
.attention-pairs-bar-bg {
  background: #23272f;
  width: 110px;
  height: 1.1rem;
  border-radius: 0.7rem;
  display: inline-block;
  margin-right: 0.6rem;
  vertical-align: middle;
  overflow: hidden;
  position: relative;
  box-shadow: 0 2px 8px #0003;
}
.attention-pairs-bar {
  height: 100%;
  border-radius: 0.7rem;
  background: linear-gradient(90deg, #1db954 60%, #a78bfa 100%);
  width: 0%;
  transition: width 1.2s cubic-bezier(.77,0,.18,1);
  position: absolute;
  left: 0;
  top: 0;
}
.attention-pairs-bar.green {
  background: linear-gradient(90deg, #1db954 80%, #43e97b 100%);
}
.attention-pairs-bar-label {
  position: absolute;
  right: 6px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.02rem;
  color: #fff;
  font-weight: 900;
  z-index: 2;
  pointer-events: none;
  background: transparent;
  border-radius: 0.7rem;
  padding: 0.05rem 0.3rem;
  box-shadow: none;
  text-shadow: 0 1px 2px #0008;
}
.attention-pairs-bar-label.purple {
  color: #a78bfa;
}
.attention-pairs-bar-label.green {
  color: #1db954;
}
.main-content-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2.2rem 2.5rem 2.2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  margin-top: 2.5rem;
}
.summary-cards-row-overview {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 2.2rem;
  flex-wrap: wrap;
  justify-content: center;
  width: 100%;
}
.overview-card-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 1.2rem 1.2rem;
  justify-content: center;
  width: 100%;
  margin-bottom: 2.5rem;
}
.attention-pairs-card {
  align-self: flex-start;
  margin-left: 0;
}
@media (max-width: 1300px) {
  .main-content-inner { max-width: 98vw; padding: 0 1rem 2rem 1rem; }
}
@media (max-width: 900px) {
  .main-content-inner { padding: 0 0.5rem 1.5rem 0.5rem; margin-top: 1.2rem; }
}
.section-separator {
  width: 100%;
  height: 5px;
  margin: 2.2rem 0 2.2rem 0;
  border-radius: 2px;
  background: linear-gradient(90deg, var(--primary), var(--accent), var(--primary));
  opacity: 0.85;
  box-shadow: 0 2px 16px 0 var(--accent);
  animation: gradient-move 4s linear infinite;
}
@media (max-width: 900px) {
  .section-separator { margin: 1.2rem 0 1.2rem 0; }
}
/* --- Improved Dark Mode, Contrast, and Palette --- */
body, .dashboard-layout {
  background: #181a20 !important;
  color: #f5f7fa;
  font-family: 'Roboto', sans-serif;
}
.topbar-title, h1, h2, .sidebar-section-title, .watchlist-title {
  font-family: 'Inter', sans-serif;
}
.summary-card-overview, .overview-card, .attention-pairs-card {
  box-shadow: 0 2px 12px rgba(0,0,0,0.18);
  background: #23272f;
  border: 1.5px solid #23272f;
}
.summary-card-overview .summary-card-value {
  color: #fff;
  text-shadow: 0 1px 4px #000a;
  font-size: 2.2rem;
  font-weight: 900;
}
.summary-card-overview .summary-card-title {
  color: #fff;
  text-shadow: none;
}
.summary-card-overview .summary-card-icon {
  background: #23272f;
  color: var(--primary) !important;
  box-shadow: 0 2px 8px #000a;
  border: 2px solid var(--accent);
}
.summary-card-overview .summary-card-icon.blue { color: var(--accent) !important; }
.summary-card-overview .summary-card-icon.purple { color: var(--accent) !important; }
.summary-card-overview .summary-card-icon.yellow { color: #fbbf24 !important; }
.overview-card.positive .company-name {
  color: #fff !important;
}

/* --- Padding/White-space --- */
.main-content-inner { gap: 2.5rem; }
.summary-cards-row-overview, .overview-card-grid { gap: 2rem; }
.attention-pairs-card { margin-top: 2.5rem; }

/* --- Heatmap Legend --- */
.heatmap-legend {
  margin: 1.2rem 0 2.2rem 0;
  display: flex;
  align-items: center;
  gap: 1.2rem;
  font-size: 1.08rem;
  color: #fff;
  font-family: 'Inter', sans-serif;
}
.heatmap-legend .legend-low { color: var(--primary); font-weight: 700; }
.heatmap-legend .legend-high { color: #c62828; font-weight: 700; }

/* --- Card Hover/Tooltip --- */
.overview-card {
  position: relative;
  cursor: pointer;
  transition: box-shadow 0.2s, border 0.2s, transform 0.2s;
}
.overview-card:hover {
  box-shadow: 0 4px 24px var(--accent);
  border: 1.5px solid var(--accent);
  z-index: 2;
  transform: translateY(-4px) scale(1.03);
}
.overview-card .card-tooltip {
  display: none;
  position: absolute;
  left: 50%;
  top: 100%;
  transform: translateX(-50%);
  background: #23272f;
  color: #fff;
  padding: 0.7rem 1.1rem;
  border-radius: 0.7rem;
  font-size: 1rem;
  box-shadow: 0 2px 12px #000a;
  margin-top: 0.5rem;
  white-space: nowrap;
  z-index: 10;
}
.overview-card:hover .card-tooltip { display: block; }

/* --- Table Gridlines & Bars --- */
.attention-pairs-table td, .attention-pairs-table th {
  border-bottom: 1px solid #2d3340;
}
.attention-pairs-bar-bg {
  position: relative;
  background: #23272f;
  width: 90px;
  height: 0.7rem;
  border-radius: 0.5rem;
  display: inline-block;
  margin-right: 0.6rem;
  vertical-align: middle;
  overflow: hidden;
}
.attention-pairs-bar {
  height: 100%;
  border-radius: 0.5rem;
  background: var(--gradient-main);
  width: 0%;
  transition: width 1.2s cubic-bezier(.77,0,.18,1);
}
.attention-pairs-bar-label {
  position: absolute;
  right: 6px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.02rem;
  color: #fff;
  font-weight: 900;
  z-index: 2;
  pointer-events: none;
  background: transparent;
  border-radius: 0.7rem;
  padding: 0.05rem 0.3rem;
  box-shadow: none;
  text-shadow: 0 1px 2px #0008;
}
.attention-pairs-bar-label.purple {
  color: #a78bfa;
}
.attention-pairs-bar-label.green {
  color: #1db954;
}

/* --- Responsive Layout & Collapsible Sidebar --- */
.sidebar-toggle {
  display: none;
  position: absolute;
  top: 1.2rem;
  left: 1.2rem;
  z-index: 100;
  background: none;
  border: none;
  color: var(--primary);
  font-size: 2rem;
  cursor: pointer;
}
@media (max-width: 900px) {
  .sidebar { display: none; position: fixed; left: 0; top: 0; height: 100vh; z-index: 200; }
  .sidebar.open { display: flex; }
  .sidebar-toggle { display: block; }
  .main-content-inner { padding: 0 0.5rem 1.5rem 0.5rem; margin-top: 1.2rem; }
  .summary-cards-row-overview, .overview-card-grid { gap: 1rem; }
}

/* --- Typography --- */
body { font-size: 1.08rem; }
h1, h2, .topbar-title { font-size: 2rem; font-family: 'Inter', sans-serif; }
.summary-card-title, .overview-card .stock-symbol { font-size: 1.15rem; font-family: 'Inter', sans-serif; }

/* --- Micro-animations for Tabs/Loading --- */
.tab-content { transition: opacity 0.4s; }
.loading-spinner {
  border: 4px solid #23272f;
  border-top: 4px solid var(--primary);
  border-radius: 50%;
  width: 36px; height: 36px;
  animation: spin 1s linear infinite;
  margin: 2rem auto;
}
@keyframes spin { 100% { transform: rotate(360deg); } }

/* --- Search Bar Styling --- */
.stock-search { display: flex; justify-content: center; align-items: center; margin: 2rem 0 2.5rem 0; }
.stock-search label { color: #fff; font-size: 1.1rem; font-weight: 700; margin-right: 1rem; }
.stock-search input[type="text"] {
  background: #23272f;
  color: #fff;
  border: 1.5px solid var(--accent);
  border-radius: 0.7rem;
  padding: 0.6rem 1.2rem;
  font-size: 1.08rem;
  outline: none;
  transition: border 0.2s, box-shadow 0.2s;
  box-shadow: 0 2px 8px #000a;
}
.stock-search input[type="text"]:focus {
  border: 1.5px solid var(--primary);
  box-shadow: 0 0 8px var(--primary);
}

/* --- Heatmap Card Grid --- */
.overview-card-grid { gap: 2.5rem 2.5rem; margin-bottom: 2.5rem; }
.overview-card { background: #23272f; color: #fff; border-radius: 1.2rem; box-shadow: 0 2px 12px #000a; padding: 1.2rem 1.5rem; min-width: 220px; transition: box-shadow 0.2s, border 0.2s, transform 0.2s; }
.overview-card.negative { background: linear-gradient(135deg, #c62828 80%, #ff8a65 100%); color: #fff; }
.overview-card .stock-symbol { color: var(--primary); font-size: 1.15rem; font-family: 'Inter', sans-serif; }
.overview-card.negative .stock-symbol { color: #fff; }

/* --- High Attention Pairs Table --- */
.attention-pairs-table td, .attention-pairs-table th { border-bottom: 1px solid #2d3340; padding: 0.8rem 1rem; }
.attention-pairs-bar-bg { background: #23272f; width: 110px; height: 0.8rem; border-radius: 0.5rem; display: inline-block; margin-right: 0.6rem; vertical-align: middle; overflow: hidden; position: relative; }
.attention-pairs-bar { height: 100%; border-radius: 0.5rem; background: linear-gradient(90deg, var(--primary), var(--accent)); width: 0%; transition: width 1.2s cubic-bezier(.77,0,.18,1); position: absolute; left: 0; top: 0; }
.attention-pairs-bar-label { position: absolute; right: 6px; top: 50%; transform: translateY(-50%); font-size: 1.02rem; color: #fff; font-weight: 900; z-index: 2; pointer-events: none; background: transparent; border-radius: 0.7rem; padding: 0.05rem 0.3rem; box-shadow: none; text-shadow: 0 1px 2px #0008; }
.attention-pairs-bar-label.purple { color: #a78bfa; }
.attention-pairs-bar-label.green { color: #1db954; }
.attention-pairs-card { margin-top: 3.5rem; padding: 2.2rem 2.2rem 1.7rem 2.2rem; }
.attention-pairs-title { margin-bottom: 1.2rem; }

/* --- Section Spacing --- */
.section-separator { margin: 2.5rem 0 2.5rem 0; }
.heatmap-legend { margin: 1.5rem 0 2.5rem 0; }

/* --- Responsive --- */
@media (max-width: 900px) {
  .overview-card-grid { gap: 1.2rem; }
  .attention-pairs-card { margin-top: 2rem; padding: 1.2rem 0.7rem 1.2rem 0.7rem; }
  .stock-search { margin: 1.2rem 0 1.5rem 0; }
}

.overview-card.positive {
  background: linear-gradient(135deg, #1db954 80%, #43e97b 100%);
  color: #fff;
  border: 2.5px solid #1db954;
  box-shadow: 0 8px 32px 0 rgba(29,185,84,0.18), 0 4px 16px #1db954;
}
.overview-card.positive:hover {
  box-shadow: 0 16px 48px 0 #43e97b, 0 0 32px 4px #1db954;
  border: 2.5px solid #43e97b;
  background: linear-gradient(120deg, #43e97b 60%, #1db954 100%);
}
.overview-card.positive .error-value {
  color: #fff !important;
}
"""
stock_ids = [str(col) for col in vol_df.columns if col != 'time_id']

# Sidebar with icons
sidebar_nav_items = [
    ("nav_home", "Overview", "fa-home"),
    ("nav_screener", "Stock Screener", "fa-search"),
    ("nav_individual", "Individual Stock Analysis", "fa-chart-line"),
    ("nav_compare", "Stock Comparison", "fa-balance-scale"),
    ("nav_portfolio", "Portfolio Tracker", "fa-wallet"),
    ("nav_model", "Model Details", "fa-brain"),
]

def sidebar_nav(current_page):
    return ui.tags.div(
        # Logo
        ui.tags.div(
            ui.tags.i(class_="fa fa-chart-pie", style="font-size:2.2rem;color:var(--primary);background:rgba(167,139,250,0.12);border-radius:50%;padding:0.7rem;margin-bottom:1.2rem;box-shadow:0 2px 8px var(--shadow);"),
            style="display:flex;justify-content:center;align-items:center;margin-bottom:1.2rem;"
        ),
        # Navigation
        ui.tags.div("Navigation", class_="sidebar-section-title"),
        ui.tags.div(
            *[
                ui.input_action_button(
                    item_id,
                    ui.tags.span(
                        ui.tags.i(class_=f"fa {icon_class}"),
                        label,
                        style="display:flex;align-items:center;gap:0.7rem;"
                    ),
                    class_=("sidebar-link active" if current_page == item_id.replace("nav_", "") else "sidebar-link")
                )
                for item_id, label, icon_class in sidebar_nav_items
            ],
            class_="sidebar-nav"
        ),
        ui.tags.hr(class_="sidebar-divider"),
        # Watchlist
        ui.tags.div(
            ui.tags.div("Watchlist", class_="watchlist-title"),
            ui.output_ui("watchlist_ui"),
            ui.tags.div("View all stocks", class_="watchlist-viewall"),
            class_="watchlist-section"
        ),
        class_="sidebar"
    )

app_ui = ui.TagList(
    ui.tags.head(
        ui.tags.style(css),
        ui.tags.link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"),
        # --- Add JS for animated number count-up and pairs bar animation ---
        ui.tags.script(r"""
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.summary-card-value').forEach(function(el) {
    let text = el.textContent.trim();
    let match = text.match(/([+-]?\d+(\.\d+)?)/);
    if (!match) return;
    let num = parseFloat(match[1]);
    let isPercent = text.includes('%');
    let isAgo = text.includes('ago');
    if (isAgo) return; // skip "2h ago"
    let start = 0, end = num, duration = 1200;
    let startTime = null;
    function animate(ts) {
      if (!startTime) startTime = ts;
      let progress = Math.min((ts - startTime) / duration, 1);
      let val = (end - start) * progress + start;
      el.textContent = (num < 10 ? val.toFixed(1) : Math.round(val)) + (isPercent ? '%' : '');
      if (progress < 1) requestAnimationFrame(animate);
      else el.textContent = text; // restore original
    }
    el.textContent = (isPercent ? '0%' : '0');
    requestAnimationFrame(animate);
  });
  // Animate High Attention Pairs bars
  setTimeout(function() {
    document.querySelectorAll('.attention-pairs-bar').forEach(function(bar) {
      var width = bar.getAttribute('data-width');
      bar.style.width = width + '%';
      bar.classList.add('animated');
    });
  }, 400);
});
""")
    ),
    ui.output_ui("app_root")
)

def server(input, output, session):
    # Track which module is selected
    current_page = reactive.Value("home")
    dark_mode = reactive.Value(True)  # Dark mode enabled by default
    darkmode_anim = reactive.Value(False)

    @reactive.Effect
    @reactive.event(input.nav_home)
    def _():
        current_page.set("home")

    @reactive.Effect
    @reactive.event(input.nav_screener)
    def _():
        current_page.set("screener")

    @reactive.Effect
    @reactive.event(input.nav_individual)
    def _():
        current_page.set("individual")

    @reactive.Effect
    @reactive.event(input.nav_compare)
    def _():
        current_page.set("compare")

    @reactive.Effect
    @reactive.event(input.nav_portfolio)
    def _():
        current_page.set("portfolio")

    @reactive.Effect
    @reactive.event(input.nav_model)
    def _():
        current_page.set("model")

    @reactive.Effect
    @reactive.event(input.toggle_darkmode)
    def _():
        dark_mode.set(not dark_mode())
        darkmode_anim.set(True)

    @reactive.Effect
    def _():
        if darkmode_anim():
            import time
            time.sleep(0.5)
            darkmode_anim.set(False)

    @output
    @render.ui
    def topbar_ui():
        icon_class = "fa fa-sun" if dark_mode() else "fa fa-moon"
        anim_class = "topbar-darkmode animated" if darkmode_anim() else "topbar-darkmode"
        return ui.tags.div(
            ui.tags.div(
                ui.tags.i(class_="fa fa-chart-pie", style="font-size:1.5rem;color:var(--primary);"),
                ui.tags.span("Stock Screening", class_="topbar-title"),
                class_="topbar-left"
            ),
                ui.tags.div(
                ui.tags.span(
                    ui.tags.i(class_="fa fa-clock"),
                    "Last updated: May 12, 2025 09:30 EST",
                    class_="topbar-updated"
                ),
                ui.input_action_button("toggle_darkmode", ui.tags.i(class_=icon_class), class_=anim_class + " topbar-icon-btn", aria_label="Toggle dark mode"),
                ui.tags.button(
                    ui.tags.i(class_="fa fa-bell"),
                    class_="topbar-icon-btn"
                ),
                class_="topbar-right"
            ),
            ui.tags.div(class_="topbar-gradient-bar"),
            class_="topbar"
        )

    @output
    @render.ui
    def app_root():
        class_name = "app-root dark-mode" if dark_mode() else "app-root"
        return ui.tags.div(
            ui.output_ui("topbar_ui"),
            ui.output_ui("dashboard_container"),
            class_=class_name
        )

    @output
    @render.ui
    def dashboard_container():
        class_name = "dashboard-layout dark-mode" if dark_mode() else "dashboard-layout"
        return ui.tags.div(
            ui.output_ui("sidebar_ui"),
            ui.output_ui("main_content"),
            class_=class_name
        )

    @output
    @render.ui
    def sidebar_ui():
        # Map current_page value to nav id
        page = current_page()
        nav_id = "home" if page == "home" else page
        return sidebar_nav(nav_id)

    @output
    @render.ui
    def main_content():
        page = current_page()
        if page == "home":
            try:
                pred_df = pd.read_csv("data/predicted_realized_vol.csv")
                vol_df = pd.read_csv("data/vol_df.csv")
                stock_cols = [str(c) for c in vol_df.columns if c != "time_id"]
                latest_row = vol_df.iloc[-1]
                realized_vols = {str(col): latest_row[col] for col in stock_cols}
                real_stocks = []
                for _, row in pred_df.iterrows():
                    symbol = str(int(row["stock_id"]))
                    name = f"Stock {symbol}"
                    forecasted_rv = row["predicted_realized_vol"] * 100
                    current_rv = realized_vols.get(symbol, None)
                    if current_rv is not None:
                        current_rv = current_rv * 100
                        error = forecasted_rv - current_rv
                        real_stocks.append({
                            "symbol": symbol,
                            "name": name,
                            "forecasted_rv": forecasted_rv,
                            "current_rv": current_rv,
                            "error": error
                        })
                # Sort and select top 5 positive and top 5 negative error cards
                positive_cards = sorted([s for s in real_stocks if s["error"] >= 0], key=lambda x: -x["error"])[:5]
                negative_cards = sorted([s for s in real_stocks if s["error"] < 0], key=lambda x: x["error"])[:5]
                real_stocks = positive_cards + negative_cards
            except Exception as e:
                return ui.tags.div(f"Error: {e}", style="color:red;font-size:1.5rem;text-align:center;")
            return ui.tags.div(
                # Summary cards row at the top
                ui.tags.div(
                    *[
                    ui.tags.div(
                                ui.tags.div(
                                ui.tags.div("Average Forecast Error", class_="summary-card-title"),
                                ui.tags.div("+9%", class_="summary-card-value"),
                                class_="summary-card-content"
                            ),
                            ui.tags.div(ui.tags.i(class_="fa fa-chart-line"), class_="summary-card-icon"),
                            class_="summary-card-overview"
                        ),
                                ui.tags.div(
                                    ui.tags.div(
                                ui.tags.div("Root Mean Square Percentage Error", class_="summary-card-title"),
                                ui.tags.div("33%", class_="summary-card-value"),
                                class_="summary-card-content"
                            ),
                            ui.tags.div(ui.tags.i(class_="fa fa-wave-square"), class_="summary-card-icon blue"),
                            class_="summary-card-overview"
                        ),
                                ui.tags.div(
                                    ui.tags.div(
                                ui.tags.div("Model Confidence", class_="summary-card-title"),
                                ui.tags.div("67%", class_="summary-card-value"),
                                class_="summary-card-content"
                            ),
                            ui.tags.div(ui.tags.i(class_="fa fa-chart-line"), class_="summary-card-icon purple"),
                            class_="summary-card-overview"
                        ),
                                ui.tags.div(
                                    ui.tags.div(
                                ui.tags.div("Last Training", class_="summary-card-title"),
                                ui.tags.div("2h ago", class_="summary-card-value"),
                                class_="summary-card-content"
                            ),
                            ui.tags.div(ui.tags.i(class_="fa fa-calendar"), class_="summary-card-icon yellow"),
                            class_="summary-card-overview"
                        ),
                    ],
                    class_="summary-cards-row-overview"
                ),
                ui.tags.div(class_="section-separator"),
                ui.tags.h2("Next-Day Volatility Forecast Heatmap", style="margin-bottom:1.2rem;color:var(--primary);font-weight:800;text-align:center;"),
                ui.tags.div(
                    ui.tags.div(
                        *([
                            ui.tags.div(
                                ui.tags.div(stock["symbol"], class_="stock-symbol"),
                                ui.tags.div(stock["name"], class_="company-name"),
                                ui.tags.div(f"Forecasted RV: {stock['forecasted_rv']:.2f}%", class_="stat-row"),
                                ui.tags.div(f"Current RV: {stock['current_rv']:.2f}%", class_="stat-row"),
                                ui.tags.div("Error", class_="error-label"),
                                ui.tags.div(f"{stock['error']:+.2f}%", class_="error-value"),
                                ui.tags.div("Extra stats: ...", class_="card-tooltip"),
                                class_=("overview-card positive" if stock['error'] >= 0 else "overview-card negative"),
                                title=f"{stock['symbol']} | Error: {stock['error']:.2f}% | Forecasted: {stock['forecasted_rv']:.2f}% | Current: {stock['current_rv']:.2f}%"
                            ) for stock in real_stocks
                        ] if real_stocks else [
                            ui.tags.div("No data available for heatmap cards.", style="color:red;font-size:1.5rem;text-align:center;")
                        ]),
                        class_="overview-card-grid"
                    ),
                    style="width:100%;display:flex;flex-direction:column;align-items:center;"
                ),
                ui.tags.div(class_="section-separator"),
                # --- High Attention Pairs Placeholder ---
                ui.tags.div(
                    ui.tags.div("High Attention Pairs", class_="attention-pairs-title"),
                    ui.output_ui("attention_pairs_table"),
                    class_="attention-pairs-card"
                ),
                class_="main-content-inner"
            )
        elif page == "model":
            return ui_model_details()
        elif page == "screener":
            return ui_screener()
        elif page == "individual":
            return ui_individual_stock(stock_ids=stock_ids)
        elif page == "compare":
            return ui_stock_comparison(stock_ids=stock_ids)
        elif page == "portfolio":
            return ui_portfolio_tracker()
        else:
            return ui.tags.div("Page not found.")

    @output
    @render.ui
    def watchlist_ui():
        # Use the same real_stocks logic as in main_content
        try:
            pred_df = pd.read_csv("data/predicted_realized_vol.csv")
            vol_df = pd.read_csv("data/vol_df.csv")
            stock_cols = [str(c) for c in vol_df.columns if c != "time_id"]
            latest_row = vol_df.iloc[-1]
            realized_vols = {str(col): latest_row[col] for col in stock_cols}
            real_stocks = []
            for _, row in pred_df.iterrows():
                symbol = str(int(row["stock_id"]))
                name = f"Stock {symbol}"
                forecasted_rv = row["predicted_realized_vol"] * 100
                current_rv = realized_vols.get(symbol, None)
                if current_rv is not None:
                    current_rv = current_rv * 100
                    error = forecasted_rv - current_rv
                    real_stocks.append({
                        "symbol": symbol,
                        "name": name,
                        "error": error
                    })
            # Top 7 by absolute error
            top7 = sorted(real_stocks, key=lambda x: -abs(x["error"]))[:7]
            return ui.tags.ul(
                *[
                    ui.tags.li([
                        stock["symbol"],
                        ui.tags.span(
                            f"{stock['error']:+.2f}%",
                            class_=("pos" if stock["error"] >= 0 else "neg")
                        )
                    ]) for stock in top7
                ],
                class_="watchlist-list"
            )
        except Exception as e:
            return ui.tags.div(f"Error loading watchlist: {e}", style="color:red;")

    @output
    @render.ui
    def attention_pairs_table():
        try:
            pairs_df = pd.read_csv("data/high_attention_pairs.csv")
            # Sort by absolute weight, take top 7
            pairs = pairs_df.sort_values(by="WEIGHT", key=abs, ascending=False).head(7)
            return ui.tags.table(
                ui.tags.thead(
                    ui.tags.tr(
                        ui.tags.th("SOURCE"),
                        ui.tags.th("TARGET"),
                        ui.tags.th("WEIGHT")
                    )
                ),
                ui.tags.tbody(
                    *[
                        ui.tags.tr(
                            ui.tags.td(row["SOURCE"]),
                            ui.tags.td(row["TARGET"]),
                            ui.tags.td(
            ui.tags.div(
                                    ui.tags.div(
                                        class_="attention-pairs-bar" + (" green" if row["WEIGHT"] >= 0.7 else " purple"),
                                        style=f"width:0%",
                                        **{"data-width": f"{int(row['WEIGHT']*100)}"}
                                    ),
                                    ui.tags.span(
                                        f"{row['WEIGHT']:.2f}",
                                        class_="attention-pairs-bar-label" + (" green" if row["WEIGHT"] >= 0.7 else " purple")
                                    ),
                                    class_="attention-pairs-bar-bg"
                                ),
                            )
                        ) for _, row in pairs.iterrows()
                    ]
                ),
                class_="attention-pairs-table"
            )
        except Exception as e:
            return ui.tags.div(f"Error loading attention pairs: {e}", style="color:red;")

    # Call server logic for each module (if needed)
    server_screener(input, output, session)
    server_individual_stock(input, output, session)
    server_stock_comparison(input, output, session)
    server_portfolio_tracker(input, output, session)
    server_model_details(input, output, session)

here = os.path.dirname(__file__)
www_path = os.path.join(here, "www")
app = App(
        app_ui,
        server, 
        static_assets=www_path
    )

if __name__ == "__main__":
    app.run()
