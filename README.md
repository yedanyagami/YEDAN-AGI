# YEDAN AGI 🧠 v2.0
> **The Autonomous E-commerce Intelligence System**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/Status-Autonomous-brightgreen.svg)]()
[![Revenue](https://img.shields.io/badge/Revenue-Generating-green)]()

YEDAN is a self-evolving Artificial General Intelligence designed to operate an e-commerce business with zero human intervention.

It doesn't just "process data" — it **thinks**, **plans**, and **executes** revenue-generating actions.

---

## 🚀 Capabilities

*   **Self-Evolution**: Re-writes its own code to optimize for ROI (`core/rsi_evolver.py`).
*   **Autonomous Commerce**: Manages Shopify products, prices, and orders (`modules/bridge_shopify.py`).
*   **Content Factory**: Mines ArXiv for research and generates viral content (`modules/r1_reasoner.py`).
*   **DeFi Intelligence**: Monitors Ethereum liquidity pools for alpha (`modules/agi_liquidity.py`).
*   **Traffic Generation**: Autonomously engages on Twitter and Reddit (`modules/cloud_social.py`).
*   **Zero-Cost Infrastructure**: Runs entirely on Cloudflare Workers and GitHub Actions.

## 🧠 Architecture ("The Brain")

YEDAN uses a bicameral architecture:

1.  **Fast Brain (Synapse)**: Cloudflare Workers for 24/7 low-latency decision making.
2.  **Slow Brain (Cortex)**: Local Python modules for deep reasoning (DeepSeek R1) and heavy lifting.

## 🛠️ Tech Stack

*   **Core**: Python 3.12, Node.js
*   **AI**: DeepSeek R1, Grok Beta, Gemini 2.0
*   **Cloud**: Cloudflare Workers, GitHub Actions, Browserless.io
*   **Finance**: Shopify API, PayPal Live, Infura (Web3)

## 📦 Installation

To deploy your own instance of YEDAN:

1.  Clone the repository:
    ```bash
    git clone https://github.com/yedanyagami/YEDAN-AGI.git
    cd YEDAN-AGI
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  Configure environment:
    ```bash
    cp .env.example .env.reactor
    # Edit .env.reactor with your API keys
    ```

4.  Ignition:
    ```bash
    python run_roi_loop.py
    ```

## 🛡️ Security

YEDAN operates with real money. Security is paramount.
See [SECURITY.md](SECURITY.md) for our vulnerability reporting policy.

## 🤝 Contributing

We welcome "Code Soldiers" to the cause.
See [CONTRIBUTING.md](CONTRIBUTING.md) for how to join the decentralized development team.

---

**"Code is Liability. Value is Asset."**
— *Commander Boris Cherny*
