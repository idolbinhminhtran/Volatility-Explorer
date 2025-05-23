import os
from pathlib import Path
from shiny import App, ui, reactive
import shinyswatch

from modules.home import home_content_ui, home_server
from modules.screener import ui_screener, server_screener
from modules.individual_stock import ui_individual_stock, server_individual_stock
from modules.comparison import ui_stock_comparison, server_stock_comparison
from modules.portfolio_tracker import ui_portfolio_tracker, server_portfolio_tracker

# Import data
VOL_PATH = os.path.join('data', 'vol_df.csv')
import pandas as pd
vol_df = pd.read_csv(VOL_PATH)
stock_cols = [c for c in vol_df.columns if c != 'time_id']

# App UI
app_ui = ui.page_fluid(
    # Apply custom Bootstrap theme
    shinyswatch.theme.vapor(),
    
    # Load external stylesheets (global app styles + Font Awesome)
    ui.tags.link(rel="stylesheet", href="styles.css"),
    ui.tags.link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"),
    
    # Custom CSS styles
    ui.tags.style("""
    :root {
        --primary-color: #1db954;
        --secondary-color: #a78bfa;
        --dark-bg: #1a1b23;
        --card-bg: rgba(36, 38, 44, 0.92);
        --text-color: #ffffff;
        --text-secondary: rgba(255, 255, 255, 0.7);
        --border-radius: 16px;
        --transition-smooth: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
    }

    body {
        background-color: var(--dark-bg);
        background-image: 
            radial-gradient(circle at 20% 30%, rgba(29, 185, 84, 0.12) 0%, transparent 50%),
            radial-gradient(circle at 80% 70%, rgba(167, 139, 250, 0.12) 0%, transparent 50%);
        background-attachment: fixed;
        color: var(--text-color);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
        min-height: 100vh;
        position: relative;
        overflow-x: hidden;
    }

    /* Subtle grid pattern for depth */
    body::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px);
        background-size: 40px 40px;
        pointer-events: none;
        z-index: -1;
    }

    /* Animated gradient overlay */
    body::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            135deg,
            rgba(29, 185, 84, 0.03) 0%,
            rgba(36, 38, 44, 0.01) 50%,
            rgba(167, 139, 250, 0.03) 100%
        );
        background-size: 400% 400%;
        animation: gradientBackground 15s ease infinite;
        pointer-events: none;
        z-index: -1;
    }

    @keyframes gradientBackground {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Enhanced Topbar */
    .topbar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 70px;
        background: rgba(26, 27, 35, 0.85);
        backdrop-filter: blur(20px) saturate(1.8);
        -webkit-backdrop-filter: blur(20px) saturate(1.8);
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        display: flex;
        align-items: center;
        padding: 0 2rem;
        z-index: 1000;
        box-shadow: 
            0 5px 20px rgba(0, 0, 0, 0.2),
            0 0 0 1px rgba(255, 255, 255, 0.05);
        transition: var(--transition-smooth);
    }

    .topbar::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        opacity: 0.7;
    }

    .logo {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        font-weight: 900;
        font-size: 1.7rem;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-decoration: none;
        position: relative;
        transition: var(--transition-smooth);
    }

    .logo:hover {
        text-decoration: none;
        transform: scale(1.05);
        filter: brightness(1.2);
    }

    .logo-icon {
        font-size: 1.8rem;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 42px;
        height: 42px;
        border-radius: 12px;
        background: rgba(29, 185, 84, 0.15);
        box-shadow: 0 5px 15px rgba(29, 185, 84, 0.2);
        transition: var(--transition-smooth);
    }

    .logo:hover .logo-icon {
        transform: rotate(15deg);
        box-shadow: 0 8px 20px rgba(29, 185, 84, 0.3);
    }

    .nav-links {
        display: flex;
        margin-left: auto;
        gap: 0.3rem;
        height: 100%;
    }

    .nav-item {
        display: flex;
        align-items: center;
        height: 100%;
        position: relative;
    }

    .nav-link {
        color: var(--text-secondary);
        text-decoration: none;
        padding: 0 1rem;
        font-weight: 600;
        font-size: 1rem;
        height: 100%;
        display: flex;
        align-items: center;
        transition: var(--transition-smooth);
        border-radius: 10px;
        margin: 0 5px;
    }

    .nav-link:hover {
        color: #fff;
        text-decoration: none;
        background: rgba(255, 255, 255, 0.05);
        transform: translateY(-2px);
    }

    .nav-link.active {
        color: var(--primary-color);
        font-weight: 700;
        background: rgba(29, 185, 84, 0.1);
    }

    .nav-link.active::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 10%;
        right: 10%;
        height: 3px;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        border-radius: 3px 3px 0 0;
    }

    .container-fluid {
        margin-top: 90px;
        padding: 1.5rem;
    }

    /* Loading indicator */
    .shiny-busy-container {
        position: fixed;
        top: 70px;
        right: 0;
        left: 0;
        height: 3px;
        z-index: 2000;
    }

    .shiny-busy-container::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        height: 100%;
        width: 20%;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        animation: loadingProgress 2s ease-in-out infinite;
        border-radius: 0 3px 3px 0;
    }

    @keyframes loadingProgress {
        0% { width: 0%; left: 0; }
        50% { width: 30%; left: 30%; }
        100% { width: 0%; left: 100%; }
    }

    /* Scroll indicator */
    .scroll-progress-container {
        position: fixed;
        top: 70px;
        left: 0;
        right: 0;
        height: 3px;
        background: rgba(255, 255, 255, 0.05);
        z-index: 1500;
    }
    
    .scroll-progress-bar {
        height: 100%;
        width: 0;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        transition: width 0.1s;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(36, 38, 44, 0.5);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--primary-color), var(--secondary-color));
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, var(--secondary-color), var(--primary-color));
    }

    /* Button and input styling */
    button, .btn {
        border-radius: var(--border-radius);
        transition: var(--transition-smooth);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    input, select, textarea {
        border-radius: calc(var(--border-radius) / 2);
        background: rgba(36, 38, 44, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: var(--text-color);
        transition: var(--transition-smooth);
    }

    input:focus, select:focus, textarea:focus {
        background: rgba(36, 38, 44, 0.9);
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(29, 185, 84, 0.2);
        outline: none;
    }
    """),
    
    # Hide legacy top-bar navigation (now replaced by sidebar)
    ui.tags.style(".nav-links{display:none !important;}"),
    
    # Topbar Navigation
    ui.tags.div(
        ui.tags.a(
            ui.tags.i(class_="fa fa-chart-line logo-icon", style="margin-right: 8px;"),
            "Volatility Explorer",
            href="?tab=dashboard",
            class_="logo"
        ),
        ui.tags.div(
            ui.tags.div(
                ui.tags.a("Dashboard", href="?tab=dashboard", 
                       class_="nav-link", id="nav_link_dashboard"),
                class_="nav-item"
            ),
            ui.tags.div(
                ui.tags.a("Stock Screener", href="?tab=screener", 
                       class_="nav-link", id="nav_link_screener"),
                class_="nav-item"
            ),
            ui.tags.div(
                ui.tags.a("Individual Stock", href="?tab=individual", 
                       class_="nav-link", id="nav_link_individual"),
                class_="nav-item"
            ),
            ui.tags.div(
                ui.tags.a("Stock Comparison", href="?tab=comparison", 
                       class_="nav-link", id="nav_link_comparison"),
                class_="nav-item"
            ),
            ui.tags.div(
                ui.tags.a("Portfolio Tracker", href="?tab=portfolio", 
                       class_="nav-link", id="nav_link_portfolio"),
                class_="nav-item"
            ),
            class_="nav-links"
        ),
        class_="topbar"
    ),
    
    # ---------------- Sidebar ----------------
    ui.tags.div(
        # Logo / Branding
        ui.tags.div(
            ui.tags.i(class_="fa fa-chart-pie logo-icon"),
            ui.tags.div("Volatility", class_="logo-text-primary"),
            ui.tags.div("Explorer", class_="logo-text-secondary"),
            class_="sidebar-logo"
        ),
        # Navigation items
        ui.tags.div(
            # Dashboard
            ui.tags.a(
                ui.tags.div(
                    ui.tags.i(class_="fa fa-home"),
                    ui.tags.span("Dashboard", class_="sidebar-nav-label"),
                    class_="sidebar-nav-content"
                ),
                href="?tab=dashboard",
                id="side_link_dashboard",
                class_="sidebar-nav-item"
            ),
            # Stock Screener
            ui.tags.a(
                ui.tags.div(
                    ui.tags.i(class_="fa fa-search"),
                    ui.tags.span("Stock Screener", class_="sidebar-nav-label"),
                    class_="sidebar-nav-content"
                ),
                href="?tab=screener",
                id="side_link_screener",
                class_="sidebar-nav-item"
            ),
            # Individual Stock Analysis
            ui.tags.a(
                ui.tags.div(
                    ui.tags.i(class_="fa fa-chart-line"),
                    ui.tags.span("Individual Stock", class_="sidebar-nav-label"),
                    class_="sidebar-nav-content"
                ),
                href="?tab=individual",
                id="side_link_individual",
                class_="sidebar-nav-item"
            ),
            # Stock Comparison
            ui.tags.a(
                ui.tags.div(
                    ui.tags.i(class_="fa fa-balance-scale"),
                    ui.tags.span("Stock Comparison", class_="sidebar-nav-label"),
                    class_="sidebar-nav-content"
                ),
                href="?tab=comparison",
                id="side_link_comparison",
                class_="sidebar-nav-item"
            ),
            # Portfolio Tracker
            ui.tags.a(
                ui.tags.div(
                    ui.tags.i(class_="fa fa-wallet"),
                    ui.tags.span("Portfolio Tracker", class_="sidebar-nav-label"),
                    class_="sidebar-nav-content"
                ),
                href="?tab=portfolio",
                id="side_link_portfolio",
                class_="sidebar-nav-item"
            ),
            class_="sidebar-nav-items"
        ),
        class_="sidebar"
    ),
    # ------------- End Sidebar -------------
    
    # Scroll indicator
    ui.tags.div(
        ui.tags.div(class_="scroll-progress-bar"),
        class_="scroll-progress-container"
    ),
    
    # Main Container - will be updated via JavaScript based on URL
    ui.tags.div(
        home_content_ui(),
        class_="container-fluid main-content",
        id="main-content"
    ),
    
    # JavaScript for routing and UI enhancements
    ui.tags.script("""
    $(document).ready(function() {
        // Function to get URL parameter
        function getUrlParameter(name) {
            name = name.replace(/[[]/, '[').replace(/[\]]/, ']');
            var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
            var results = regex.exec(location.search);
            return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
        }
        
        // Set active nav link based on current tab
        function setActiveNavLink() {
            $('.nav-link, .sidebar-nav-item').removeClass('active');
            var tab = getUrlParameter('tab') || 'dashboard';
            $('#nav_link_' + tab).addClass('active');
            $('#side_link_' + tab).addClass('active');
        }
        
        // Update content based on URL parameter
        function loadContent() {
            var tab = getUrlParameter('tab') || 'dashboard';
            
            // Send message to Shiny
            Shiny.setInputValue('current_tab', tab);
            
            setActiveNavLink();
        }
        
        // Initial load
        loadContent();
        
        // Handle navigation clicks
        $('.nav-link, .sidebar-nav-item').on('click', function(e) {
            var href = $(this).attr('href');
            var tab = getUrlParameter('tab') || 'dashboard';
            
            if (href.indexOf('tab=') !== -1) {
                var newTab = href.split('tab=')[1];
                if (newTab !== tab) {
                    // Only reload if changing tabs
                    window.history.pushState({}, '', href);
                    loadContent();
                }
            }
        });
        
        // Handle browser back/forward
        $(window).on('popstate', function() {
            loadContent();
        });
        
        // Scroll progress indicator
        $(window).scroll(function() {
            var scrollTop = $(window).scrollTop();
            var docHeight = $(document).height() - $(window).height();
            var scrollPercent = (scrollTop / docHeight) * 100;
            $('.scroll-progress-bar').css('width', scrollPercent + '%');
        });
        
        // Add a loading indicator
        $(document).on({
            'shiny:busy': function() {
                if (!$('.shiny-busy-container').length) {
                    $('body').append('<div class="shiny-busy-container"></div>');
                }
            },
            'shiny:idle': function() {
                $('.shiny-busy-container').remove();
            }
        });
        
        // Enhance topbar with scroll effect
        $(window).scroll(function() {
            if ($(window).scrollTop() > 10) {
                $('.topbar').css({
                    'background': 'rgba(22, 23, 29, 0.95)',
                    'box-shadow': '0 10px 30px rgba(0, 0, 0, 0.3)'
                });
            } else {
                $('.topbar').css({
                    'background': 'rgba(26, 27, 35, 0.85)',
                    'box-shadow': '0 5px 20px rgba(0, 0, 0, 0.2), 0 0 0 1px rgba(255, 255, 255, 0.05)'
                });
            }
        });
        
        // Add particle effect to the background
        function createBackgroundParticles() {
            const particleContainer = document.createElement('div');
            particleContainer.className = 'background-particles';
            particleContainer.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                z-index: -2;
                overflow: hidden;
            `;
            
            document.body.appendChild(particleContainer);
            
            const particleCount = 20;
            
            for (let i = 0; i < particleCount; i++) {
                const size = Math.random() * 6 + 2;
                const particle = document.createElement('div');
                
                particle.style.cssText = `
                    position: absolute;
                    width: ${size}px;
                    height: ${size}px;
                    background: ${Math.random() > 0.5 ? 'rgba(29,185,84,0.3)' : 'rgba(167,139,250,0.3)'};
                    border-radius: 50%;
                    top: ${Math.random() * 100}vh;
                    left: ${Math.random() * 100}vw;
                    opacity: ${Math.random() * 0.5 + 0.1};
                    filter: blur(${Math.random() * 2 + 1}px);
                    animation: floatParticle ${Math.random() * 100 + 50}s linear infinite;
                `;
                
                particleContainer.appendChild(particle);
            }
            
            const style = document.createElement('style');
            style.textContent = `
                @keyframes floatParticle {
                    0% {
                        transform: translate(0, 0) rotate(0deg);
                    }
                    25% {
                        transform: translate(${Math.random() * 30}vw, ${Math.random() * 30}vh) rotate(90deg);
                    }
                    50% {
                        transform: translate(${Math.random() * -30}vw, ${Math.random() * 30}vh) rotate(180deg);
                    }
                    75% {
                        transform: translate(${Math.random() * -30}vw, ${Math.random() * -30}vh) rotate(270deg);
                    }
                    100% {
                        transform: translate(0, 0) rotate(360deg);
                    }
                }
            `;
            
            document.head.appendChild(style);
        }
        
        // Initialize background particles
        createBackgroundParticles();
    });
    """)
)

# App server logic
def server(input, output, session):
    # Core page content is managed by the home module
    home_server(input, output, session)
    
    # Load module servers
    server_screener(input, output, session)
    server_individual_stock(input, output, session, stock_cols)
    server_stock_comparison(input, output, session, stock_cols)
    server_portfolio_tracker(input, output, session)

# Create Shiny app
app = App(app_ui, server) 