# Volatility Explorer 📊

An advanced financial volatility modeling and prediction platform built with Python and Shiny. This project implements state-of-the-art machine learning models to predict stock volatility and provides an intuitive web interface for analysis, screening, and portfolio management.

## 🌟 Overview

Volatility Explorer combines cutting-edge volatility forecasting models with interactive visualization tools to help traders, researchers, and financial analysts understand and predict market volatility patterns. The platform features a modern, dark-themed UI and supports real-time analysis of multiple stocks.

## ✨ Key Features

### 1. **Multiple Volatility Prediction Models**
- **GAT (Graph Attention Network)** - Our best performing model with QLIKE: 0.089148
- **HAR-RV (Heterogeneous Autoregressive - Realized Volatility)** - QLIKE: 0.144863
- **PCA-Linear** - Dimensionality reduction with linear regression (QLIKE: 0.146002)
- **Linear Regression** - Baseline model (QLIKE: 0.157675)
- **LAG1** - Simple lag-based prediction (QLIKE: 0.191133)
- **Random Forest** - Ensemble tree-based model (QLIKE: 0.271033)
- **Gradient Boosting** - Advanced ensemble method (QLIKE: 0.393428)

### 2. **Interactive Dashboard Modules**
- **Stock Screener**: Filter and discover stocks based on volatility metrics
- **Individual Stock Analysis**: Deep dive into single stock volatility patterns
- **Stock Comparison**: Compare up to 3 stocks side-by-side
- **Portfolio Tracker**: Track and analyze portfolio volatility
- **Model Performance Viewer**: Visualize and compare model predictions

### 3. **Advanced Analytics**
- Real-time volatility calculations
- Prediction vs actual comparisons
- Model accuracy metrics (QLIKE, MAPE, RMPSE)
- Interactive time-series visualizations
- AI-powered insights using OpenAI integration

## 📈 Model Performance

| Model | QLIKE | MAPE | RMPSE |
|-------|-------|------|-------|
| GAT | 0.089148 | 45.10 | ~37 |
| HAR-RV | 0.144863 | 47.41 | 61.62 |
| PCA-Linear | 0.146002 | 48.89 | 64.01 |
| Linear | 0.157675 | 58.72 | 76.74 |
| LAG1 | 0.191133 | 83.90 | 109.38 |
| Random Forest | 0.271033 | 128.12 | 196.35 |
| Gradient Boosting | 0.393428 | 204.55 | 316.81 |

## 🧠 GAT Model - Our Star Performer

### Graph Attention Network (GAT) Architecture

The GAT model is the crown jewel of our volatility prediction system, achieving the best performance with a QLIKE score of 0.089148. This model revolutionizes volatility forecasting by treating the financial market as an interconnected network of assets.

### Key Innovations:

1. **Graph-Based Representation**
   - Treats each stock as a node in a financial network
   - Captures complex inter-asset dependencies that traditional models miss
   - Models how volatility in one asset propagates through the market

2. **Attention Mechanism**
   - Dynamically weighs connections between stocks based on their historical correlation patterns
   - Adapts to changing market conditions in real-time
   - Focuses on the most relevant relationships for each prediction

3. **Multi-Head Attention**
   - Uses multiple attention heads to capture different types of relationships
   - Combines diverse perspectives for more robust predictions
   - Reduces overfitting and improves generalization

4. **Temporal Feature Integration**
   - Incorporates historical price patterns and multiple lagged realized volatility values
   - Captures momentum, mean reversion, and seasonality effects
   - Uses both short-term and long-term temporal dependencies

### Technical Specifications:

- **Input Features**: 
  - Historical volatility (multiple lags)
  - Price-based features (returns, spreads)
  - Market microstructure variables
  - Cross-asset correlation matrices

- **Architecture Details**:
  - Number of attention heads: 8
  - Hidden dimensions: 128
  - Number of GAT layers: 3
  - Dropout rate: 0.3
  - Learning rate: 0.001 with adaptive scheduling

- **Training Process**:
  - Temporal train/validation/test split: 80%/10%/10%
  - Batch size: 32
  - Training epochs: 200 with early stopping
  - Loss function: QLIKE (Quasi-likelihood)

### Performance Advantages:

- **59% Lower Error** than traditional Linear models (QLIKE: 0.089 vs 0.158)
- **38% Better** than HAR-RV, the previous state-of-the-art
- **Consistent Performance** across different market conditions
- **Interpretable Results** through attention weight visualization

### Why GAT Excels at Volatility Prediction:

1. **Network Effects**: Financial markets are inherently interconnected. GAT captures these relationships naturally.
2. **Dynamic Adaptation**: The attention mechanism adjusts to changing market regimes automatically.
3. **Non-linear Patterns**: Unlike linear models, GAT can model complex, non-linear volatility dynamics.
4. **Spillover Effects**: Captures how volatility shocks propagate through the financial network.

## 🚀 Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/Volatility-Explorer.git
cd Volatility-Explorer
```

2. **Create a virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

5. **Run the application**
```bash
shiny run app.py
```

The application will be available at `http://localhost:8000`

## 📁 Project Structure

```
Volatility-Explorer/
│
├── app.py                 # Main Shiny application entry point
├── home.py               # Home dashboard module
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (create this)
├── .gitignore           # Git ignore file
│
├── data/                 # Data directory
│   ├── vol_df.csv       # Historical volatility data
│   ├── metrics_summary.csv  # Stock metrics summary
│   └── predicted_realized_vol.csv  # Model predictions
│
├── models/              # Model outputs
│   ├── model_metrics_summary.csv  # Model performance metrics
│   ├── actual_rv.csv    # Actual realized volatility
│   ├── GAT_prediction_panel.csv
│   ├── HAR_RV_predictions.csv
│   ├── PCA_Linear_predictions.csv
│   └── ... (other model predictions)
│
├── modules/             # Application modules
│   ├── common_style.py  # Common styling utilities
│   ├── home.py         # Home page module
│   ├── individual_stock.py  # Individual stock analysis
│   ├── model_details.py    # Model comparison and details
│   ├── portfolio_tracker.py  # Portfolio management
│   ├── screener.py        # Stock screening functionality
│   ├── stock_comparison.py  # Multi-stock comparison
│   └── visual_effects.py   # Visual effects and animations
│
├── src/                # Source assets
│   ├── analysis.svg
│   ├── compare.svg
│   ├── portfolio.svg
│   └── screener.svg
│
└── www/               # Web assets (if any)
```

## 📊 Data Requirements

The application expects the following data files in the `data/` directory:

1. **vol_df.csv**: Time series volatility data with columns:
   - `time_id`: Time identifier
   - Stock columns (numeric IDs): Volatility values

2. **metrics_summary.csv**: Stock metrics including:
   - `stock_id`: Stock identifier
   - Various metrics (avg_bid_size1, avg_ask_size1, avg_spread, etc.)

3. **predicted_realized_vol.csv**: Model predictions with:
   - `stock_id`: Stock identifier
   - `predicted_realized_vol`: Predicted volatility value

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Required for AI-powered insights and analysis

### Customization
- Modify `modules/common_style.py` to customize the UI theme
- Add new models by creating prediction CSV files in the `models/` directory
- Extend functionality by adding new modules in the `modules/` directory

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide for Python code
- Add docstrings to all functions and classes
- Write unit tests for new features
- Update documentation as needed

## 📝 Research & Methodology

This project implements several state-of-the-art volatility forecasting models:

- **GAT (Graph Attention Networks)**: Leverages attention mechanisms to capture complex dependencies in financial time series
- **HAR-RV**: Exploits the heterogeneous nature of market participants operating at different time horizons
- **PCA-Linear**: Reduces dimensionality while preserving key volatility patterns

For detailed methodology and research background, please refer to our technical documentation.

## 🎯 Future Enhancements

- [ ] Real-time data integration with market APIs
- [ ] Additional ML models (LSTM, Transformer-based)
- [ ] Risk management tools
- [ ] Backtesting framework
- [ ] Mobile-responsive design
- [ ] Export functionality for reports

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- University of Sydney - DATA3888 Course
- Contributors and maintainers
- Open-source community for the amazing tools and libraries

## 📧 Contact

For questions, suggestions, or collaborations, please reach out to:
- Email: your.email@example.com
- GitHub Issues: [Create an issue](https://github.com/yourusername/Volatility-Explorer/issues)

---

**Note**: This project is for educational and research purposes. Always consult with financial professionals before making investment decisions based on model predictions. 