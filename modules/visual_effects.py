"""
Visual effects and animations to enhance the user interface across all modules.
"""

def get_effects_css():
    return """
    /* Card Hover Effects */
    .content-card {
        transition: transform 0.4s cubic-bezier(0.165, 0.84, 0.44, 1), 
                    box-shadow 0.4s cubic-bezier(0.165, 0.84, 0.44, 1), 
                    border-color 0.4s;
        position: relative;
        overflow: hidden;
        z-index: 1;
    }
    
    /* Spotlight hover effect */
    .content-card::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at var(--x) var(--y), 
                    rgba(255, 255, 255, 0.08) 0%, 
                    rgba(255, 255, 255, 0) 50%);
        opacity: 0;
        transition: opacity 0.4s;
        z-index: -1;
        pointer-events: none;
    }
    
    .content-card:hover::after {
        opacity: 1;
    }
    
    /* Tooltip styling */
    .tooltip-container {
        position: relative;
        display: inline-block;
    }
    
    .tooltip {
        visibility: hidden;
        width: 200px;
        background-color: rgba(29, 34, 44, 0.95);
        color: #fff;
        text-align: center;
        border-radius: 0.8rem;
        padding: 0.8rem 1rem;
        position: absolute;
        z-index: 1000;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transform: translateY(10px) scale(0.95);
        transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        border: 1px solid rgba(167,139,250,0.2);
    }
    
    .tooltip::after {
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -8px;
        border-width: 8px;
        border-style: solid;
        border-color: rgba(29, 34, 44, 0.95) transparent transparent transparent;
    }
    
    .tooltip-container:hover .tooltip {
        visibility: visible;
        opacity: 1;
        transform: translateY(0) scale(1);
    }
    
    /* Button Hover Animation */
    .module-btn {
        position: relative;
        overflow: hidden;
        z-index: 1;
    }
    
    .module-btn::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, rgba(167,139,250,0.2), rgba(29,185,84,0.2));
        z-index: -1;
        transform: translateX(-100%);
        transition: transform 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
    }
    
    .module-btn:hover::before {
        transform: translateX(0);
    }
    
    /* Text link hover effect */
    .hover-link {
        position: relative;
        color: #1db954;
        text-decoration: none;
        transition: color 0.3s;
        cursor: pointer;
    }
    
    .hover-link:hover {
        color: #a78bfa;
    }
    
    .hover-link::after {
        content: '';
        position: absolute;
        width: 100%;
        height: 2px;
        bottom: -2px;
        left: 0;
        background-image: linear-gradient(90deg, #1db954, #a78bfa);
        transform: scaleX(0);
        transform-origin: bottom right;
        transition: transform 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
    }
    
    .hover-link:hover::after {
        transform: scaleX(1);
        transform-origin: bottom left;
    }
    
    /* Card entrance animations */
    @keyframes slideInUp {
        from {
            transform: translateY(30px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    .slide-in-up {
        animation: slideInUp 0.6s cubic-bezier(0.165, 0.84, 0.44, 1) forwards;
    }
    
    /* Staggered entry for multiple cards */
    .stagger-cards > *:nth-child(1) { animation-delay: 0.1s; }
    .stagger-cards > *:nth-child(2) { animation-delay: 0.2s; }
    .stagger-cards > *:nth-child(3) { animation-delay: 0.3s; }
    .stagger-cards > *:nth-child(4) { animation-delay: 0.4s; }
    .stagger-cards > *:nth-child(5) { animation-delay: 0.5s; }
    
    /* Interactive hover card effect */
    .hover-card {
        transition: transform 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
        transform-style: preserve-3d;
        perspective: 1000px;
    }
    
    .hover-card:hover {
        transform: rotateX(5deg) rotateY(-5deg);
    }
    
    /* Input and select focus effects */
    .module-input select:focus, 
    .module-input input[type="number"]:focus, 
    .module-input input[type="text"]:focus {
        animation: focusGlow 2s infinite alternate;
    }
    
    @keyframes focusGlow {
        0% { box-shadow: 0 0 0 4px rgba(167,139,250,0.3), 0 5px 15px rgba(167,139,250,0.2); }
        100% { box-shadow: 0 0 0 6px rgba(29,185,84,0.25), 0 5px 20px rgba(29,185,84,0.15); }
    }
    
    /* Chart and data point animations */
    .data-point {
        transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
        cursor: pointer;
    }
    
    .data-point:hover {
        transform: scale(1.5);
        filter: drop-shadow(0 0 8px rgba(167,139,250,0.8));
    }
    
    /* Icon hover effect */
    .hover-icon {
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        display: inline-block;
    }
    
    .hover-icon:hover {
        transform: scale(1.2) rotate(15deg);
        color: #1db954;
    }
    
    /* Shimmer effect for loading states */
    @keyframes shimmer {
        0% {
            background-position: -200% 0;
        }
        100% {
            background-position: 200% 0;
        }
    }
    
    .shimmer-effect {
        background: linear-gradient(90deg,
            rgba(255,255,255,0.05) 25%,
            rgba(255,255,255,0.1) 50%,
            rgba(255,255,255,0.05) 75%);
        background-size: 200% 100%;
        animation: shimmer 2s infinite;
    }
    
    /* Badge notification */
    .notification-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #1db954, #a78bfa);
        color: white;
        font-size: 0.8rem;
        font-weight: bold;
        height: 20px;
        min-width: 20px;
        padding: 0 6px;
        border-radius: 10px;
        position: absolute;
        top: -8px;
        right: -8px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.2);
        animation: pulseScale 2s infinite;
    }
    
    @keyframes pulseScale {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    
    /* Interactive table rows */
    .interactive-table tr {
        transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
        cursor: pointer;
    }
    
    .interactive-table tr:hover {
        background: rgba(167,139,250,0.1);
        transform: translateX(10px) scale(1.01);
    }
    
    /* Value change animations */
    @keyframes valueChange {
        0% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.2);
            color: #1db954;
        }
        100% {
            transform: scale(1);
        }
    }
    
    .value-change {
        animation: valueChange 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    
    /* 3D card effect */
    .card-3d {
        transform-style: preserve-3d;
        perspective: 1000px;
    }
    
    .card-3d-inner {
        transition: transform 0.6s cubic-bezier(0.165, 0.84, 0.44, 1);
        transform-style: preserve-3d;
    }
    
    .card-3d:hover .card-3d-inner {
        transform: rotateY(180deg);
    }
    
    .card-3d-front, .card-3d-back {
        -webkit-backface-visibility: hidden;
        backface-visibility: hidden;
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
    }
    
    .card-3d-back {
        transform: rotateY(180deg);
    }
    
    /* Gradient text animation */
    .animated-gradient-text {
        background: linear-gradient(90deg, #1db954, #a78bfa, #1db954);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-size: 200% auto;
        animation: gradientShift 3s linear infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        100% { background-position: 200% 50%; }
    }

    /* Notification panel styles */
    .notification-panel {
        position: fixed;
        right: 1.5rem;
        top: 4.5rem;
        width: 320px;
        background: rgba(24, 26, 32, 0.95);
        border-radius: 1.2rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.35);
        border: 2px solid rgba(167,139,250,0.25);
        padding: 1rem 1rem 0.5rem 1rem;
        z-index: 1500;
        color: #fff;
        backdrop-filter: blur(15px) saturate(1.2);
        animation: slideInRight 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
    }

    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(40px); }
        to { opacity: 1; transform: translateX(0); }
    }

    .notification-panel h4 {
        font-size: 1.3rem;
        font-weight: 900;
        margin-bottom: 1rem;
        text-align: center;
        background: linear-gradient(90deg, #1db954 0%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .notification-list {
        list-style: none;
        margin: 0;
        padding: 0;
        max-height: 300px;
        overflow-y: auto;
    }

    .notification-item {
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 1rem;
        position: relative;
        background: rgba(36, 38, 44, 0.8);
        border: 1px solid rgba(255,255,255,0.05);
        box-shadow: 0 6px 18px rgba(0,0,0,0.25);
        overflow: hidden;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .notification-item::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, var(--primary), var(--accent));
        opacity: 0.9;
    }

    .notification-item:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 28px rgba(0,0,0,0.4);
    }

    .notification-item.up::before { background: #1db954; }
    .notification-item.down::before { background: #e53e3e; }

    .notif-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.4rem;
    }

    .notif-symbol {
        font-weight: 800;
        font-size: 1.15rem;
        color: #1db954;
    }

    .notification-item.down .notif-symbol { color: #e53e3e; }

    .notif-time {
        font-size: 0.75rem;
        color: #888;
    }

    .notif-body {
        font-size: 0.9rem;
        color: #e0e0e0;
        margin-bottom: 0.3rem;
    }

    .notif-diff {
        font-size: 0.9rem;
        font-weight: 600;
    }

    .notif-diff.up { color: #1db954; }
    .notif-diff.down { color: #e53e3e; }

    /* Advanced card effect with depth and shadows */
    .depth-card {
        background: rgba(36, 38, 44, 0.95);
        border-radius: 1.5rem;
        box-shadow: 
            0 8px 30px rgba(0,0,0,0.2),
            0 0 0 1px rgba(167,139,250,0.1);
        transform-style: preserve-3d;
        transition: transform 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275),
                    box-shadow 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
    }

    .depth-card:hover {
        transform: translateY(-10px) scale(1.02) rotateX(5deg) rotateY(-5deg);
        box-shadow: 
            0 15px 35px rgba(0,0,0,0.3),
            0 0 0 2px rgba(29,185,84,0.2);
    }

    .depth-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            135deg,
            rgba(255,255,255,0.1) 0%,
            rgba(255,255,255,0) 50%,
            rgba(255,255,255,0) 100%
        );
        transform: translateY(-100%);
        transition: transform 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        z-index: 1;
    }

    .depth-card:hover::before {
        transform: translateY(0);
    }

    /* Glassmorphism effect */
    .glass-card {
        background: rgba(36, 38, 44, 0.85);
        backdrop-filter: blur(15px) saturate(1.5);
        -webkit-backdrop-filter: blur(15px) saturate(1.5);
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    }

    /* Floating animation */
    @keyframes floating {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-15px); }
        100% { transform: translateY(0px); }
    }

    .floating {
        animation: floating 5s ease-in-out infinite;
    }

    /* Glowing border effect */
    .glow-border {
        position: relative;
        overflow: hidden;
        z-index: 1;
    }

    .glow-border::after {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(
            45deg,
            #1db954, #a78bfa, #1db954, #a78bfa
        );
        background-size: 400% 400%;
        z-index: -1;
        animation: glowingBorder 3s ease infinite;
        filter: blur(10px);
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .glow-border:hover::after {
        opacity: 1;
    }

    @keyframes glowingBorder {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Modern table styles with hover effects */
    .modern-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0 5px;
    }

    .modern-table th {
        background: linear-gradient(90deg, #1db954 0%, #a78bfa 100%);
        color: white;
        font-weight: bold;
        padding: 15px;
        text-align: left;
        border-radius: 10px 10px 0 0;
        position: sticky;
        top: 0;
        z-index: 10;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }

    .modern-table tr {
        transition: all 0.3s ease;
    }

    .modern-table td {
        padding: 15px;
        background: rgba(36, 38, 44, 0.7);
        border-bottom: 1px solid rgba(255,255,255,0.05);
        position: relative;
        overflow: hidden;
    }

    .modern-table tr:hover td {
        background: rgba(167,139,250,0.15);
        transform: scale(1.01);
    }

    .modern-table tr td:first-child {
        border-top-left-radius: 10px;
        border-bottom-left-radius: 10px;
    }

    .modern-table tr td:last-child {
        border-top-right-radius: 10px;
        border-bottom-right-radius: 10px;
    }

    /* Particle effect */
    .particle-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
    }

    @keyframes animateParticles {
        0% {
            transform: translateY(0) rotate(0deg);
            opacity: 1;
            border-radius: 50%;
        }
        100% {
            transform: translateY(-1000px) rotate(720deg);
            opacity: 0;
            border-radius: 50%;
        }
    }

    /* Neon text effect */
    .neon-text {
        color: #fff;
        text-shadow: 
            0 0 5px #1db954,
            0 0 10px #1db954,
            0 0 20px #1db954,
            0 0 40px #1db954;
    }

    .neon-purple {
        color: #fff;
        text-shadow: 
            0 0 5px #a78bfa,
            0 0 10px #a78bfa,
            0 0 20px #a78bfa,
            0 0 40px #a78bfa;
    }

    /* Gradient card */
    .gradient-card {
        background: linear-gradient(135deg, rgba(29,185,84,0.3) 0%, rgba(167,139,250,0.3) 100%);
        position: relative;
        z-index: 1;
    }

    .gradient-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: inherit;
        z-index: -1;
        filter: blur(10px);
        opacity: 0.7;
        transform: scale(0.95);
        transition: all 0.3s ease;
    }

    .gradient-card:hover::before {
        opacity: 1;
        transform: scale(1.05);
    }

    /* Subtle background animation */
    @keyframes gradientAnimation {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }

    .animated-bg {
        background: linear-gradient(-45deg, rgba(29,185,84,0.05), rgba(167,139,250,0.05));
        background-size: 400% 400%;
        animation: gradientAnimation 15s ease infinite;
    }

    /* Subtle grid lines for depth */
    .grid-background {
        position: relative;
    }

    .grid-background::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
        background-size: 20px 20px;
        z-index: -1;
    }
    """

def get_interactive_js():
    return """
    // Add event listeners when the document is loaded
    document.addEventListener('DOMContentLoaded', function() {
        // Add spotlight effect to cards
        const cards = document.querySelectorAll('.content-card, .sidebar-card');
        
        cards.forEach(card => {
            card.addEventListener('mousemove', function(e) {
                const rect = this.getBoundingClientRect();
                const x = ((e.clientX - rect.left) / this.offsetWidth) * 100;
                const y = ((e.clientY - rect.top) / this.offsetHeight) * 100;
                this.style.setProperty('--x', x + '%');
                this.style.setProperty('--y', y + '%');
            });
        });
        
        // Add ripple effect to buttons
        const buttons = document.querySelectorAll('.module-btn');
        
        buttons.forEach(button => {
            button.addEventListener('click', function(e) {
                const rect = this.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                const ripple = document.createElement('span');
                ripple.style.cssText = `
                    position: absolute;
                    background: rgba(255, 255, 255, 0.3);
                    border-radius: 50%;
                    transform: translate(-50%, -50%);
                    pointer-events: none;
                    width: 0;
                    height: 0;
                    left: ${x}px;
                    top: ${y}px;
                `;
                
                this.appendChild(ripple);
                
                const size = Math.max(this.offsetWidth, this.offsetHeight) * 2;
                ripple.style.width = ripple.style.height = `${size}px`;
                
                ripple.classList.add('ripple-animation');
                
                setTimeout(() => {
                    ripple.remove();
                }, 600);
            });
        });
        
        // Add interactive data point highlighting
        const tableRows = document.querySelectorAll('table tbody tr');
        const dataPoints = document.querySelectorAll('.data-point');
        
        if (tableRows.length > 0 && dataPoints.length > 0) {
            tableRows.forEach((row, idx) => {
                if (idx < dataPoints.length) {
                    row.addEventListener('mouseenter', () => {
                        dataPoints[idx].classList.add('active');
                        dataPoints[idx].style.r = '8';
                        dataPoints[idx].style.fill = '#1db954';
                    });
                    
                    row.addEventListener('mouseleave', () => {
                        dataPoints[idx].classList.remove('active');
                        dataPoints[idx].style.r = '5';
                        dataPoints[idx].style.fill = '';
                    });
                }
            });
        }
        
        // Animate numbers on page load
        const animateCounter = (el, final) => {
            let start = 0;
            const duration = 1500;
            const step = (final / duration) * 10;
            const counter = setInterval(() => {
                start += step;
                if (start > final) {
                    el.textContent = final.toLocaleString('en-US', {
                        minimumFractionDigits: el.dataset.decimals || 0,
                        maximumFractionDigits: el.dataset.decimals || 0
                    });
                    clearInterval(counter);
                } else {
                    el.textContent = start.toLocaleString('en-US', {
                        minimumFractionDigits: el.dataset.decimals || 0,
                        maximumFractionDigits: el.dataset.decimals || 0
                    });
                }
            }, 10);
        };
        
        const countElements = document.querySelectorAll('.animate-counter');
        countElements.forEach(el => {
            const finalValue = parseFloat(el.getAttribute('data-value') || el.innerText);
            el.innerText = '0';
            setTimeout(() => {
                animateCounter(el, finalValue);
            }, 500);
        });
        
        // Add 3D tilt effect to cards with class hover-card
        const hoverCards = document.querySelectorAll('.hover-card');
        
        hoverCards.forEach(card => {
            card.addEventListener('mousemove', function(e) {
                const rect = this.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                
                const rotateX = (y - centerY) / 15;
                const rotateY = (centerX - x) / 15;
                
                this.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'perspective(1000px) rotateX(0) rotateY(0)';
            });
        });
        
        // Add parallax effect to elements with parallax class
        const parallaxElements = document.querySelectorAll('.parallax');
        
        window.addEventListener('scroll', () => {
            const scrollY = window.scrollY;
            
            parallaxElements.forEach(el => {
                const speed = parseFloat(el.getAttribute('data-speed') || 0.1);
                el.style.transform = `translateY(${scrollY * speed}px)`;
            });
        });

        // Add particles effect
        addParticleEffect();
        
        // Apply glass card effect
        document.querySelectorAll('.content-card').forEach(card => {
            card.classList.add('glass-card');
        });
        
        // Add modern table styling
        document.querySelectorAll('.screener-table-container table').forEach(table => {
            table.classList.add('modern-table');
        });
        
        // Add grid background to main content
        document.querySelectorAll('.main-content').forEach(content => {
            content.classList.add('grid-background', 'animated-bg');
        });
        
        // Add floating animation to AI card
        document.querySelectorAll('.ai-suggestion').forEach(card => {
            card.classList.add('floating');
        });
        
        // Add glow border effect to buttons
        document.querySelectorAll('.module-btn').forEach(btn => {
            btn.classList.add('glow-border');
        });
    });
    
    // Function to create ripple effect for buttons
    function createRipple(event) {
        const button = event.currentTarget;
        
        const circle = document.createElement("span");
        const diameter = Math.max(button.clientWidth, button.clientHeight);
        const radius = diameter / 2;
        
        circle.style.width = circle.style.height = `${diameter}px`;
        circle.style.left = `${event.clientX - button.offsetLeft - radius}px`;
        circle.style.top = `${event.clientY - button.offsetTop - radius}px`;
        circle.classList.add("ripple");
        
        const ripple = button.querySelector(".ripple");
        
        if (ripple) {
            ripple.remove();
        }
        
        button.appendChild(circle);
    }

    // Initialize particle effect
    function addParticleEffect() {
        const particleContainer = document.createElement('div');
        particleContainer.className = 'particle-container';
        document.body.appendChild(particleContainer);
        
        const particleCount = 20;
        
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.style.cssText = `
                position: absolute;
                background: ${Math.random() > 0.5 ? 'rgba(29,185,84,0.5)' : 'rgba(167,139,250,0.5)'};
                width: ${Math.random() * 10 + 5}px;
                height: ${Math.random() * 10 + 5}px;
                left: ${Math.random() * 100}vw;
                top: ${Math.random() * 100}vh;
                border-radius: 50%;
                pointer-events: none;
                opacity: ${Math.random() * 0.5 + 0.3};
                animation: animateParticles ${Math.random() * 15 + 10}s linear infinite;
                animation-delay: ${Math.random() * 5}s;
            `;
            particleContainer.appendChild(particle);
        }
    }
    """ 