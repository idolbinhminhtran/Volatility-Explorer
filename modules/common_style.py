"""
Common CSS styles shared across all modules for consistent design.
"""

def get_common_css():
    return """
    /* Common Layout */
    .module-layout {
        display: flex;
        flex-direction: row;
        gap: 2.5rem;
        width: 100%;
        min-height: calc(100vh - 80px);
        background: linear-gradient(135deg, rgba(22, 24, 29, 0.9) 0%, rgba(31, 33, 40, 0.95) 100%);
        padding: 1rem;
        position: relative;
    }
    
    /* Subtle background pattern */
    .module-layout::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(29, 185, 84, 0.01) 0%, transparent 40%),
            radial-gradient(circle at 90% 80%, rgba(167, 139, 250, 0.01) 0%, transparent 40%);
        pointer-events: none;
        z-index: -1;
    }
    
    /* Sidebar Card */
    .sidebar-card {
        background: rgba(36, 38, 44, 0.92);
        backdrop-filter: blur(14px) saturate(1.2);
        border-radius: 2rem;
        box-shadow: 0 8px 32px 0 rgba(29,185,84,0.18);
        border: 2.5px solid;
        border-image: linear-gradient(120deg, #1db954 60%, #a78bfa 100%) 1;
        padding: 2.7rem 2rem 2.7rem 2rem;
        width: 350px;
        min-width: 320px;
        margin: 2.5rem 0 2.5rem 2.5rem;
        color: #fff;
        font-family: 'Inter', 'Roboto', sans-serif;
        position: relative;
        overflow: visible;
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        align-items: stretch;
        justify-content: flex-start;
        z-index: 10;
    }
    
    /* Sidebar hover effect */
    .sidebar-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(29,185,84,0.22), 0 0 0 5px rgba(29,185,84,0.05);
        border-image: linear-gradient(120deg, #a78bfa 60%, #1db954 100%) 1;
    }
    
    /* Sidebar glow effect */
    .sidebar-card::after {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        border-radius: 2.2rem;
        background: linear-gradient(120deg, #1db95433 60%, #a78bfa33 100%);
        z-index: -1;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .sidebar-card:hover::after {
        opacity: 1;
    }
    
    /* Sidebar Icon */
    .sidebar-card .module-icon {
        display: flex; 
        align-items: center; 
        justify-content: center;
        background: linear-gradient(135deg, #1db954 60%, #a78bfa 100%);
        border-radius: 50%;
        padding: 1.2rem;
        font-size: 2.8rem;
        box-shadow: 0 8px 20px rgba(29,185,84,0.3);
        width: 4.8rem; 
        height: 4.8rem;
        margin: 0 auto 1.8rem auto;
        transition: all 0.5s ease;
    }
    
    .sidebar-card:hover .module-icon {
        transform: rotate(5deg) scale(1.05);
        box-shadow: 0 12px 30px rgba(29,185,84,0.4);
        background: linear-gradient(135deg, #a78bfa 60%, #1db954 100%);
    }
    
    /* Sidebar Card Title */
    .sidebar-card h2 {
        font-weight: 900;
        font-size: 2.3rem;
        margin-bottom: 0.6rem;
        letter-spacing: 0.02em;
        text-transform: uppercase;
        background: linear-gradient(90deg, #1db954 60%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        text-shadow: 0 0 16px #1db95444, 0 0 32px #a78bfa44;
        transition: all 0.3s ease;
    }
    
    .sidebar-card:hover h2 {
        letter-spacing: 0.03em;
        background: linear-gradient(90deg, #a78bfa 60%, #1db954 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Sidebar Card Subtitle */
    .sidebar-card .module-subtitle {
        color: #fff;
        font-size: 1.15rem;
        font-weight: 500;
        text-align: center;
        margin-bottom: 2.3rem;
        opacity: 0.9;
        transition: opacity 0.3s ease;
    }
    
    .sidebar-card:hover .module-subtitle {
        opacity: 1;
    }
    
    /* Sidebar Card Section Labels */
    .sidebar-card label, .sidebar-card h4 {
        color: #1db954 !important;
        font-weight: 900;
        font-size: 1.1rem;
        letter-spacing: 0.01em;
        margin-bottom: 0.6rem;
        text-shadow: 0 0 8px #1db95433;
        transition: color 0.3s ease;
    }
    
    .sidebar-card:hover label, .sidebar-card:hover h4 {
        color: #a78bfa !important;
    }
    
    /* Sidebar Card Section Headers */
    .sidebar-card h4 {
        margin-top: 2rem;
        margin-bottom: 1.2rem;
        font-size: 1.2rem;
        background: linear-gradient(90deg, #1db954 60%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-transform: uppercase;
        transition: all 0.3s ease;
    }
    
    .sidebar-card:hover h4 {
        background: linear-gradient(90deg, #a78bfa 60%, #1db954 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Input Styling */
    .module-input {
        margin-bottom: 1.5rem;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        position: relative;
    }
    
    .module-input label {
        color: #1db954 !important;
        font-weight: 800;
        font-size: 1.1rem;
        letter-spacing: 0.04em;
        margin-bottom: 0.2rem;
        text-shadow: 0 0 8px #1db95433;
        text-transform: uppercase;
        transition: all 0.3s ease;
    }
    
    .module-input:focus-within label {
        color: #a78bfa !important;
        text-shadow: 0 0 12px #a78bfa55;
    }
    
    .module-input select, .module-input input[type="number"], .module-input input[type="text"] {
        background: rgba(36, 38, 44, 0.85);
        border: 2px solid #1db954;
        border-radius: 0.9rem;
        color: #fff;
        font-size: 1.15rem;
        font-family: 'Inter', 'Roboto', sans-serif;
        padding: 0.8rem 1.2rem;
        outline: none;
        box-shadow: 0 2px 12px 0 rgba(29,185,84,0.15);
        transition: all 0.3s ease;
        position: relative;
        background-image: linear-gradient(120deg, rgba(255,255,255,0.08) 0%, rgba(29,185,84,0.05) 100%);
    }
    
    .module-input select:focus, .module-input input:focus {
        border: 2px solid #a78bfa;
        box-shadow: 0 0 0 4px #a78bfa55, 0 2px 15px 0 #a78bfa33;
        background: rgba(36, 38, 44, 0.95);
        transform: translateY(-2px);
    }
    
    .module-input select:hover, .module-input input:hover {
        border-color: #a78bfa;
        box-shadow: 0 5px 15px rgba(29,185,84,0.2);
        transform: translateY(-2px);
    }
    
    /* Button Styling */
    .module-btn {
        width: 100%;
        background: linear-gradient(90deg, #1db954 60%, #a78bfa 100%);
        color: #fff;
        font-weight: 900;
        font-size: 1.15rem;
        border: none;
        border-radius: 1rem;
        padding: 0.9rem 0;
        margin-bottom: 0.6rem;
        box-shadow: 0 5px 20px 0 rgba(29,185,84,0.2);
        letter-spacing: 0.04em;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        text-transform: uppercase;
    }
    
    .module-btn:hover {
        background: linear-gradient(90deg, #a78bfa 60%, #1db954 100%);
        box-shadow: 0 8px 25px 0 #a78bfa44, 0 0 0 5px #a78bfa22;
        transform: translateY(-3px) scale(1.02);
    }
    
    .module-btn:active {
        transform: translateY(-1px);
        box-shadow: 0 2px 10px 0 #1db95444;
    }
    
    /* Button ripple effect */
    .module-btn::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 5px;
        height: 5px;
        background: rgba(255, 255, 255, 0.5);
        opacity: 0;
        border-radius: 100%;
        transform: scale(1, 1) translate(-50%);
        transform-origin: 50% 50%;
    }
    
    @keyframes ripple {
        0% {
            transform: scale(0, 0);
            opacity: 0.5;
        }
        100% {
            transform: scale(200, 200);
            opacity: 0;
        }
    }
    
    .module-btn:active::after {
        animation: ripple 0.6s ease-out;
    }
    
    /* Main Content Area */
    .main-content {
        flex: 1 1 0%;
        padding: 2.5rem 2.5rem 2.5rem 0;
        display: flex;
        flex-direction: column;
        align-items: stretch;
        gap: 2.2rem;
        min-width: 0;
        opacity: 0;
        animation: fadeIn 0.5s forwards 0.2s;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Card Styling */
    .content-card {
        background: rgba(36, 38, 44, 0.95);
        border-radius: 1.5rem;
        box-shadow: 0 10px 30px 0 rgba(0,0,0,0.15);
        border: 2px solid rgba(167,139,250,0.1);
        padding: 2.2rem 2.2rem 2rem 2.2rem;
        color: #fff;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
        transform: translateY(0);
    }
    
    .content-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px 0 rgba(29,185,84,0.15);
        border-color: rgba(29,185,84,0.2);
    }
    
    /* Card hover glow */
    .content-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #1db954, #a78bfa);
        transform: scaleX(0);
        transform-origin: left;
        transition: transform 0.6s ease;
    }
    
    .content-card:hover::before {
        transform: scaleX(1);
    }
    
    /* Card Title */
    .card-title {
        font-size: 1.4rem;
        font-weight: 900;
        margin-bottom: 1.3rem;
        letter-spacing: 0.01em;
        background: linear-gradient(90deg, #1db954 60%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        transition: all 0.3s ease;
        display: inline-block;
    }
    
    .content-card:hover .card-title {
        background: linear-gradient(90deg, #a78bfa 60%, #1db954 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Table Styling */
    .content-card table, .content-card .dataframe {
        background: transparent !important;
        color: #fff !important;
        font-size: 1.1rem;
        border-radius: 1rem;
        overflow: hidden;
        border-collapse: separate;
        border-spacing: 0;
        width: 100%;
    }
    
    .content-card th {
        background: linear-gradient(90deg, #1db954 60%, #a78bfa 100%) !important;
        color: #fff !important;
        font-weight: 900;
        font-size: 1.1rem;
        border: none;
        padding: 1rem 1.5rem;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        position: relative;
    }
    
    .content-card td {
        background: transparent !important;
        color: #fff !important;
        border: none;
        padding: 0.9rem 1.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        transition: all 0.2s ease;
    }
    
    .content-card tr {
        transition: all 0.3s ease;
    }
    
    .content-card tbody tr:hover {
        background: rgba(167,139,250,0.1) !important;
        transform: translateX(5px);
    }
    
    .content-card tbody tr:hover td {
        color: #a78bfa !important;
    }
    
    /* AI Suggestion Section */
    .ai-suggestion {
        background: rgba(36, 38, 44, 0.95);
        border-radius: 1.5rem;
        box-shadow: 0 10px 30px 0 rgba(167,139,250,0.15);
        border: 2px solid rgba(167,139,250,0.2);
        padding: 2.2rem 2.2rem 2rem 2.2rem;
        color: #fff;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .ai-suggestion:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px 0 rgba(167,139,250,0.25);
        border-color: rgba(167,139,250,0.3);
    }
    
    /* AI glow effect */
    .ai-suggestion::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #a78bfa, #1db954);
        transform: scaleX(0);
        transform-origin: right;
        transition: transform 0.6s ease;
    }
    
    .ai-suggestion:hover::before {
        transform: scaleX(1);
    }
    
    .ai-suggestion-header {
        font-size: 1.3rem;
        font-weight: 900;
        color: #a78bfa;
        margin-bottom: 1.3rem;
        letter-spacing: 0.01em;
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }
    
    .ai-suggestion-header .icon {
        font-size: 1.6rem;
        color: #a78bfa;
        background: rgba(167,139,250,0.15);
        border-radius: 50%;
        padding: 0.5rem;
        box-shadow: 0 5px 15px rgba(167,139,250,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
    }
    
    .ai-suggestion:hover .ai-suggestion-header .icon {
        transform: rotate(15deg);
        background: rgba(167,139,250,0.2);
    }
    
    .ai-suggestion-section {
        font-size: 1.1rem;
        font-weight: 800;
        color: #a78bfa;
        margin-top: 1.2rem;
        margin-bottom: 0.4rem;
        letter-spacing: 0.01em;
        display: block;
    }
    
    .ai-suggestion-content {
        font-size: 1.15rem;
        color: #e1e1e6;
        font-weight: 400;
        margin-bottom: 0.8rem;
        line-height: 1.7;
        letter-spacing: 0.01em;
    }
    
    /* Common animations */
    @keyframes float {
        0% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
        100% { transform: translateY(0); }
    }
    
    .float-effect {
        animation: float 3s infinite ease-in-out;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(29,185,84,0.7); }
        70% { transform: scale(1.05); box-shadow: 0 0 0 10px rgba(29,185,84,0); }
        100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(29,185,84,0); }
    }
    
    .pulse-effect {
        animation: pulse 2s infinite;
    }
    
    /* Responsive Layout */
    @media (max-width: 1200px) {
        .module-layout { flex-direction: column; }
        .main-content { padding: 1.5rem; }
        .sidebar-card { 
            margin: 1.5rem auto; 
            width: calc(100% - 3rem);
            max-width: 600px;
        }
    }
    
    @media (max-width: 700px) {
        .main-content { padding: 0.8rem; }
        .sidebar-card { padding: 1.5rem; }
        .sidebar-card .module-icon { width: 4rem; height: 4rem; font-size: 2.2rem; }
        .sidebar-card h2 { font-size: 2rem; }
    }
    """ 