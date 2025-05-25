import os
from shiny import ui, render, reactive
from modules.common_style import get_common_css
from modules.visual_effects import get_effects_css, get_interactive_js

def home_content_ui():
    """
    UI for the home/dashboard page
    """
    custom_css = get_common_css() + get_effects_css() + """
    .dashboard-header {
        text-align: center;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        position: relative;
    }
    
    .dashboard-header::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 150px;
        height: 3px;
        background: linear-gradient(90deg, #1db954, #a78bfa);
        border-radius: 3px;
    }
    
    .dashboard-title {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(90deg, #1db954 30%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        animation: text-shimmer 3s infinite;
        background-size: 200% auto;
    }
    
    @keyframes text-shimmer {
        0% { background-position: 0% 50%; }
        100% { background-position: 100% 50%; }
    }
    
    .dashboard-subtitle {
        font-size: 1.5rem;
        color: rgba(255, 255, 255, 0.8);
        font-weight: 500;
    }
    
    .dashboard-cards {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 2rem;
        margin-bottom: 3rem;
    }
    
    .dashboard-card {
        background: rgba(36, 38, 44, 0.85);
        border-radius: 1.5rem;
        box-shadow: 
            0 15px 35px rgba(0, 0, 0, 0.2),
            0 0 0 1px rgba(167, 139, 250, 0.15);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        padding: 2rem;
        transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
        display: flex;
        flex-direction: column;
        position: relative;
        overflow: hidden;
    }
    
    .dashboard-card:hover {
        transform: translateY(-10px);
        box-shadow: 
            0 25px 50px rgba(29, 185, 84, 0.2),
            0 0 0 2px rgba(29, 185, 84, 0.2);
    }
    
    .dashboard-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 5px;
        background: linear-gradient(90deg, #1db954, #a78bfa);
        transform: scaleX(0);
        transform-origin: left;
        transition: transform 0.6s cubic-bezier(0.165, 0.84, 0.44, 1);
    }
    
    .dashboard-card:hover::before {
        transform: scaleX(1);
    }
    
    .card-icon {
        font-size: 2.5rem;
        width: 60px;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, rgba(29, 185, 84, 0.15), rgba(167, 139, 250, 0.15));
        border-radius: 1rem;
        margin-bottom: 1.5rem;
        color: #1db954;
        transition: all 0.3s ease;
    }
    
    .dashboard-card:hover .card-icon {
        transform: scale(1.1) rotate(10deg);
        color: #a78bfa;
    }
    
    .card-title {
        font-size: 1.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1db954 30%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    
    .card-description {
        font-size: 1rem;
        color: rgba(255, 255, 255, 0.8);
        line-height: 1.6;
        flex-grow: 1;
        margin-bottom: 1.5rem;
    }
    
    .card-action {
        display: inline-block;
        padding: 0.8rem 1.5rem;
        background: linear-gradient(90deg, #1db954 0%, #a78bfa 100%);
        color: white;
        border-radius: 1rem;
        font-weight: 700;
        text-decoration: none;
        transition: all 0.3s ease;
        border: none;
        cursor: pointer;
        align-self: flex-start;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        box-shadow: 0 8px 20px rgba(29, 185, 84, 0.2);
    }
    
    .card-action:hover {
        background: linear-gradient(90deg, #a78bfa 0%, #1db954 100%);
        transform: translateY(-3px);
        box-shadow: 0 12px 25px rgba(29, 185, 84, 0.3);
        text-decoration: none;
        color: white;
    }
    """
    
    interactive_js = get_interactive_js() + """
    $(document).ready(function() {
        // Add staggered animation to dashboard cards
        const cards = document.querySelectorAll('.dashboard-card');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(30px)';
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            card.style.transitionDelay = `${index * 0.1}s`;
            
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 100);
        });
        
        // Add 3D tilt effect to cards
        cards.forEach(card => {
            card.addEventListener('mousemove', function(e) {
                const rect = this.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                
                const rotateX = (y - centerY) / 20;
                const rotateY = (centerX - x) / 20;
                
                this.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-10px)`;
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0)';
            });
        });
    });
    """
    
    return ui.TagList(
        ui.tags.style(custom_css),
        ui.tags.script(interactive_js),
        ui.div(
            ui.div(
                ui.h1("VoltaTrade", class_="dashboard-title"),
                ui.p("Interactive Financial Data Analysis & Visualization", class_="dashboard-subtitle"),
                class_="dashboard-header"
            ),
            
            # Dashboard Cards
            ui.div(
                # Screener Card
                ui.div(
                    ui.div(ui.tags.i(class_="fa fa-search"), class_="card-icon"),
                    ui.h3("Stock Screener", class_="card-title"),
                    ui.p("Filter and rank stocks based on financial metrics and volatility indicators. Find the best performers according to your criteria.", 
                         class_="card-description"),
                    ui.a("Explore Screener", href="?tab=screener", class_="card-action"),
                    class_="dashboard-card depth-card glass-card"
                ),
                
                # Individual Stock Card
                ui.div(
                    ui.div(ui.tags.i(class_="fa fa-chart-line"), class_="card-icon"),
                    ui.h3("Individual Stock Analysis", class_="card-title"),
                    ui.p("Dive deep into individual stock performance with detailed volatility metrics, historical data, and predictive insights.", 
                         class_="card-description"),
                    ui.a("Analyze Stocks", href="?tab=individual", class_="card-action"),
                    class_="dashboard-card depth-card glass-card"
                ),
                
                # Comparison Card
                ui.div(
                    ui.div(ui.tags.i(class_="fa fa-balance-scale"), class_="card-icon"),
                    ui.h3("Stock Comparison", class_="card-title"),
                    ui.p("Compare multiple stocks side by side with visual indicators of volatility, returns, and key financial metrics.", 
                         class_="card-description"),
                    ui.a("Compare Stocks", href="?tab=comparison", class_="card-action"),
                    class_="dashboard-card depth-card glass-card"
                ),
                
                # Portfolio Card
                ui.div(
                    ui.div(ui.tags.i(class_="fa fa-briefcase"), class_="card-icon"),
                    ui.h3("Portfolio Tracker", class_="card-title"),
                    ui.p("Track your portfolio performance with advanced volatility analytics and risk assessment tools.", 
                         class_="card-description"),
                    ui.a("Track Portfolio", href="?tab=portfolio", class_="card-action"),
                    class_="dashboard-card depth-card glass-card"
                ),
                
                class_="dashboard-cards"
            ),
            
            # Welcome Section
            ui.div(
                ui.h2("Welcome to VoltaTrade", class_="content-title"),
                ui.p("""
                VoltaTrade is a powerful tool for analyzing stock market volatility and financial metrics. 
                Use the navigation menu above to access different modules, or click on the cards to jump straight to a specific feature.
                """, class_="content-subtitle"),
                class_="content-header"
            ),
            
            class_="main-content grid-background animated-bg"
        )
    )

def home_server(input, output, session):
    """
    Server logic for the home/dashboard page
    """
    @reactive.Effect
    def _():
        # Get the current tab from the URL
        tab = input.current_tab()
        
        # Update the content based on the tab
        if tab == "dashboard":
            ui.update_ui(ui.TagList(home_content_ui()), selector="#main-content")
        elif tab == "screener":
            from modules.screener import ui_screener
            ui.update_ui(ui_screener(), selector="#main-content")
        elif tab == "individual":
            from modules.individual_stock import ui_individual_stock
            ui.update_ui(ui_individual_stock(), selector="#main-content")
        elif tab == "comparison":
            from modules.comparison import ui_stock_comparison
            ui.update_ui(ui_stock_comparison(), selector="#main-content")
        elif tab == "portfolio":
            from modules.portfolio_tracker import ui_portfolio_tracker
            ui.update_ui(ui_portfolio_tracker(), selector="#main-content") 