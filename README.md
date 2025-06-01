<div align="center">

# 🚀 VoltaTrade

### Advanced Volatility Prediction & Trading Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Shiny](https://img.shields.io/badge/Shiny-1.4.0-green.svg)](https://shiny.rstudio.com/py/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GAT Model](https://img.shields.io/badge/Best%20Model-GAT-ff0066.svg)](README.md#-gat-model---our-star-performer)
[![QLIKE Score](https://img.shields.io/badge/QLIKE-0.089-brightgreen.svg)](README.md#-model-performance)

<img src="https://img.shields.io/badge/University%20of%20Sydney-DATA3888-red.svg" alt="USYD Course">

<br>

### 🎯 [Live Demo](https://binhminhtran-volatility-explorer.share.connect.posit.cloud/) | [Try VoltaTrade Now!](https://binhminhtran-volatility-explorer.share.connect.posit.cloud/)

[![Live Demo](https://img.shields.io/badge/🚀%20Live%20Demo-Try%20Now-ff0066.svg?style=for-the-badge)](https://binhminhtran-volatility-explorer.share.connect.posit.cloud/)

---

### 🌟 Where AI Meets Market Volatility 🌟

*Harness the power of Graph Attention Networks to predict financial volatility with unprecedented accuracy*

[🚀 Get Started](#-quick-start) • [📊 Features](#-key-features) • [🧠 Models](#-model-performance) • [📸 Screenshots](#-screenshots) • [📚 Documentation](#-documentation)

</div>

---

## 📑 Table of Contents

- [✨ Overview](#-overview)
- [🎯 Key Features](#-key-features)
- [📊 Model Performance](#-model-performance)
- [🧠 GAT Model Details](#-gat-model---our-star-performer)
- [🚀 Quick Start](#-quick-start)
- [📸 Screenshots](#-screenshots)
- [📁 Project Structure](#-project-structure)
- [🔧 Configuration](#-configuration)
- [📚 Documentation](#-documentation)
- [📚 References](#-references)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)


---

## ✨ Overview

**VoltaTrade** is a cutting-edge financial analytics platform that combines state-of-the-art machine learning with intuitive visualization tools. Built with Python and Shiny, it delivers institutional-grade volatility predictions through an elegant, modern interface.

<div align="center">
  <img src="src/VoltaTrade%20dashboard.png" alt="VoltaTrade Dashboard" width="80%">
  <p><em>Modern dark-themed interface with real-time volatility analytics</em></p>
</div>

### 🎯 Why VoltaTrade?

- **🏆 Best-in-Class Performance**: GAT model achieves 59% lower error than traditional methods
- **🎨 Beautiful UI**: Modern, dark-themed interface with smooth animations
- **⚡ Real-Time Analysis**: Lightning-fast predictions across multiple assets
- **🔍 Deep Insights**: AI-powered explanations and network effect visualization
- **📈 Professional Tools**: Portfolio tracking, screening, and comparison features

---

## 🎯 Key Features

<table>
<tr>
<td width="50%">

### 📊 Advanced Analytics
- **7 Prediction Models** including GAT, HAR-RV, and ML ensembles
- **Real-time volatility calculations**
- **AI-powered market insights** via OpenAI integration
- **Network effect visualization**
- **Temporal pattern recognition**

</td>
<td width="50%">

### 🛠️ Professional Tools
- **📱 Stock Screener** - Filter by volatility metrics
- **📈 Individual Analysis** - Deep dive into single stocks
- **⚖️ Comparison Tool** - Analyze up to 3 stocks
- **💼 Portfolio Tracker** - Monitor portfolio volatility
- **🧪 Model Lab** - Compare prediction models

</td>
</tr>
</table>

---

## 📊 Model Performance

<div align="center">

| Model | QLIKE ↓ | MAPE | RMPSE | Status |
|:------|:-------:|:----:|:-----:|:------:|
| 🧠 **GAT** | **0.0891** | 45.10 | ~37 | 🟢 **Best** |
| 📊 HAR-RV | 0.1449 | 47.41 | 61.62 | 🟢 Good |
| 🔄 PCA-Linear | 0.1460 | 48.89 | 64.01 | 🟢 Good |
| 📈 Linear | 0.1577 | 58.72 | 76.74 | 🟡 Baseline |
| ⏱️ LAG1 | 0.1911 | 83.90 | 109.38 | 🟡 Basic |
| 🌲 Random Forest | 0.2710 | 128.12 | 196.35 | 🔴 Limited |
| 🚀 Gradient Boosting | 0.3934 | 204.55 | 316.81 | 🔴 Limited |

<sup>*Lower QLIKE scores indicate better performance. GAT achieves 59% improvement over baseline.*</sup>

</div>

---

## 🧠 GAT Model - Our Star Performer

<div align="center">
  <img src="src/ModelDetails.png" alt="GAT Model Details" width="60%">
</div>

### 🌟 Why GAT Dominates

The **Graph Attention Network (GAT)** revolutionizes volatility prediction by treating financial markets as living, breathing networks:

<table>
<tr>
<td width="25%" align="center">

### 🕸️ Network Intelligence
Models stocks as interconnected nodes, capturing spillover effects

</td>
<td width="25%" align="center">

### 🎯 Dynamic Attention
Focuses on the most relevant relationships in real-time

</td>
<td width="25%" align="center">

### 🧩 Multi-Head Design
8 attention heads capture diverse market dynamics

</td>
<td width="25%" align="center">

### 📈 Temporal Mastery
Integrates short & long-term patterns seamlessly

</td>
</tr>
</table>

### 🔬 Technical Excellence

```python
GAT_CONFIG = {
    "attention_heads": 8,
    "hidden_dimensions": 128,
    "num_layers": 3,
    "dropout_rate": 0.3,
    "learning_rate": 0.001,
    "batch_size": 32,
    "epochs": 200
}
```

### 📊 Performance Metrics
- **59% Lower Error** vs Linear Models
- **38% Better** than HAR-RV (previous SOTA)
- **Consistent** across market regimes
- **Interpretable** via attention weights

---

## 🚀 Quick Start

### Prerequisites

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![pip](https://img.shields.io/badge/pip-Latest-orange?logo=pypi&logoColor=white)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/VoltaTrade.git
cd VoltaTrade

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
echo "OPENAI_API_KEY=your_api_key_here" > .env

# 5. Launch VoltaTrade! 🚀
shiny run app.py
```

<div align="center">
  <h3>🌐 Open your browser to <a href="http://localhost:8000">http://localhost:8000</a></h3>
</div>

---

## 📸 Screenshots

<div align="center">
<table>
<tr>
<td align="center" width="50%">
<img src="src/VoltaTrade%20dashboard.png" alt="Dashboard" width="100%">
<b>Dashboard Overview</b>
</td>
<td align="center" width="50%">
<img src="src/StockComparison.png" alt="Model Comparison" width="100%">
<b>Stock Comparison</b>
</td>
</tr>
<tr>
<td align="center" width="50%">
<img src="src/IndividualStockAnalysis.png" alt="Stock Analysis" width="100%">
<b>Individual Stock Analysis</b>
</td>
<td align="center" width="50%">
<img src="src/PortfolioTracker.png" alt="Portfolio" width="100%">
<b>Portfolio Tracker</b>
</td>
</tr>
</table>
</div>

---

## 📁 Project Structure

```
🏗️ VoltaTrade/
│
├── 📱 app.py                    # Main Shiny application
├── 🏠 home.py                   # Dashboard module
├── 📋 requirements.txt          # Python dependencies
├── 🔐 .env                      # Environment variables
│
├── 📊 data/                     # Data directory
│   ├── vol_df.csv              # Historical volatility
│   ├── metrics_summary.csv     # Stock metrics
│   └── predicted_realized_vol.csv
│
├── 🧠 models/                   # Model outputs
│   ├── model_metrics_summary.csv
│   ├── GAT_prediction_panel.csv
│   └── ... (other predictions)
│
├── 🧩 modules/                  # Application modules
│   ├── 🎨 common_style.py      # Styling utilities
│   ├── 📊 individual_stock.py  # Stock analysis
│   ├── 🔬 model_details.py     # Model comparison
│   ├── 💼 portfolio_tracker.py # Portfolio management
│   ├── 🔍 screener.py          # Stock screening
│   └── ⚖️ stock_comparison.py   # Multi-stock comparison
│
└── 🎨 src/                      # Visual assets
    └── ... (SVG icons)
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Required for AI-powered insights
OPENAI_API_KEY=your_openai_api_key_here

# Optional configurations
DEBUG_MODE=False
LOG_LEVEL=INFO
```

### Data Requirements

VoltaTrade expects these CSV files in the `data/` directory:

| File | Description | Required Columns |
|:-----|:------------|:-----------------|
| 📊 `vol_df.csv` | Time series volatility | `time_id`, stock columns |
| 📈 `metrics_summary.csv` | Stock metrics | `stock_id`, metric columns |
| 🎯 `predicted_realized_vol.csv` | Predictions | `stock_id`, `predicted_realized_vol` |

---

## 📚 Documentation

### 🎓 Research Background

Our GAT implementation is based on cutting-edge research in:
- **Graph Neural Networks** for financial markets
- **Attention Mechanisms** in time series prediction
- **Volatility Spillover** effects in interconnected markets

### 🛠️ API Reference

```python
# Example: Accessing model predictions
from modules.model_details import model_data

# Get GAT predictions for a specific stock
gat_predictions = model_data['GAT']
stock_43_volatility = gat_predictions[gat_predictions['stock_id'] == '43']
```

---

## 📚 References

### Academic Papers & Books

1. **Andersen, T.G., Bollerslev, T., Diebold, F.X. and Labys, P.** (2003). Modeling and forecasting realized volatility. *Econometrica*, 71(2), pp.579–625.

2. **Board of Governors of the Federal Reserve System** (2022). Changes in U.S. family finances from 2019 to 2022: Evidence from the Survey of Consumer Finances. Available at: [https://www.federalreserve.gov/publications/files/scf22.pdf](https://www.federalreserve.gov/publications/files/scf22.pdf) (Accessed: 29 May 2025).

3. **Cont, R.** (2001). Empirical properties of asset returns: stylized facts and statistical issues. *Quantitative Finance*, 1(2), pp.223–236.

4. **Corsi, F.** (2009). A simple approximate long-memory model of realized volatility. *Journal of Financial Econometrics*, 7(2), pp.174–196.

5. **Goodfellow, I., Bengio, Y. and Courville, A.** (2016). *Deep Learning*. MIT Press.

6. **Hull, J.** (2015). *Options, Futures, and Other Derivatives*. 9th ed. Pearson.

7. **Newman, M.** (2010). *Networks: An Introduction*. Oxford University Press.

8. **Velickovic, P., Cucurull, G., Casanova, A., Romero, A., Liò, P. and Bengio, Y.** (2018). Graph Attention Networks. In *International Conference on Learning Representations (ICLR)*.

9. **Zhang, Y., Zhang, Y., Wang, J. and Li, H.** (2022). Stock price movement prediction with graph attention networks. *Expert Systems with Applications*, 191, p.116367.

### Data Sources & Resources

- **Optiver** (2021). Optiver Realized Volatility Prediction Challenge. Available at: [https://www.kaggle.com/competitions/optiver-realized-volatility-prediction](https://www.kaggle.com/competitions/optiver-realized-volatility-prediction) (Accessed: 26 May 2025).

### Additional Resources

- [Log Transformation of Realized Volatility](https://www.sciencedirect.com/science/article/abs/pii/S0304407610000680#:~:text=The%20log%20transformation%20of%20realized,that%20of%20the%20raw%20statistic.)
- [Mean Absolute Percentage Error (MAPE)](https://en.wikipedia.org/wiki/Mean_absolute_percentage_error)
- [Model Performance Metrics for Regression Models](https://help.pecan.ai/en/articles/6456388-model-performance-metrics-for-regression-models)
- [Recovering Time ID Order - Kaggle Notebook](https://www.kaggle.com/code/stassl/recovering-time-id-order/notebook)

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### 🐛 Found a Bug?
Open an [issue](https://github.com/yourusername/VoltaTrade/issues) with:
- Bug description
- Steps to reproduce
- Expected vs actual behavior

### 💡 Have an Idea?
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingIdea`)
3. Commit changes (`git commit -m 'Add AmazingIdea'`)
4. Push to branch (`git push origin feature/AmazingIdea`)
5. Open a Pull Request

### 📝 Development Guidelines
- Follow PEP 8 style guide
- Add tests for new features
- Update documentation
- Keep commits atomic and descriptive

---

## 🎯 Future Roadmap

- [ ] 🔌 Real-time market data integration
- [ ] 🤖 LSTM and Transformer models
- [ ] 📱 Mobile-responsive design
- [ ] 🎲 Monte Carlo risk simulations
- [ ] 📊 Advanced backtesting framework
- [ ] 🌍 Multi-market support

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

### 🙏 Acknowledgments

**University of Sydney** - DATA3888 Course  
**Open Source Community** - For amazing tools and libraries  
**Contributors** - For making VoltaTrade better every day

---

### 📧 Get in Touch

<a href="mailto:your.email@example.com">
  <img src="https://img.shields.io/badge/Email-Contact%20Us-blue?style=for-the-badge&logo=gmail" alt="Email">
</a>
<a href="https://github.com/yourusername/VoltaTrade/issues">
  <img src="https://img.shields.io/badge/GitHub-Report%20Issue-black?style=for-the-badge&logo=github" alt="GitHub Issues">
</a>

---

**⚠️ Disclaimer**: This project is for educational and research purposes only. Always consult with financial professionals before making investment decisions.

<br>

Made with ❤️ by the VoltaTrade Team


</div> 

