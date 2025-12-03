# ⚽ Football-Predictor-Model-XGB

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Model](https://img.shields.io/badge/Model-XGBoost-orange?style=for-the-badge&logo=xgboost&logoColor=white)
![Hybrid](https://img.shields.io/badge/Engine-Poisson%20%2B%20ML-purple?style=for-the-badge)
![API](https://img.shields.io/badge/API-Football--Data.org-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**Football-Predictor-Model-XGB** is an advanced sports analytics tool that combines statistical probability (**Poisson Distribution**) with machine learning (**XGBoost**) to predict match outcomes with high accuracy.

Unlike simple form-based predictors, this tool features a **Hybrid Ensemble Engine** that accounts for "Squad Strength," "League Tiers," "Fatigue," and "Home/Away" dynamics to correct international match predictions.

✅ **Interface:** Full Turkish Support (Türkçe Arayüz & Yorumlama)
✅ **Ideal for:** Match Analysis, Data Science Portfolios, and Strategic Forecasting

---

## 🧠 Overview & Methodology

The system uses a weighted blending approach to generate predictions:

1.  **📈 Poisson Distribution (60% Weight):** Calculates theoretical scoring probabilities based on attack/defense strength relative to league averages.
2.  **🤖 XGBoost Regressor (40% Weight):** Predicts goals based on recent rolling form (last 5 games), momentum, and venue-specific performance.
3.  **⚖️ Contextual Logic:**
    * **Elite Club Override:** Automatically boosts stats for global giants (e.g., Real Madrid, Man City) to prevent illogical upsets.
    * **Fatigue Detection:** Penalizes teams playing with <4 days of rest.
    * **Smart Commentary:** An AI logic that interprets decimal xG (Expected Goals) into human-readable insights.

---

## ⚙️ Key Features

* **Hybrid Prediction Engine:** Combines Statistical & ML models.
* **Smart Decimal Analysis:** Dynamic text commentary interpreting xG (e.g., *"2.85 -> 3. gole göz kırpıyor"*).
* **Squad Power Logic:** Auto-detects "Elite Clubs" and applies power multipliers (x1.5).
* **Venue Specifics:** Distinguishes between *Home-Only* and *Away-Only* statistics.
* **Global Coverage:** Supports 10+ leagues (Premier League, Champions League, La Liga, Serie A, etc.).
* **Full Localization:** Complete Turkish interface with smart menu labeling.

---

## 🖥️ Visual Preview

### 1. League Selection Menu
*User-friendly interactive menu with country/region context.*

![League Menu](BURAYA_MENU_EKRAN_GORUNTUSU_LINKI.png)
### 2. Detailed Match Analysis Report
*A comprehensive breakdown including H2H, Standings, Squad Strength, and AI Prediction.*

![Match Report](BURAYA_RAPOR_EKRAN_GORUNTUSU_LINKI.png)
---

## 🧰 Tech Stack

| Technology | Purpose |
| :--- | :--- |
| **Python 3.x** | Core logic & Orchestration |
| **XGBoost** | Gradient Boosting framework for regression |
| **Pandas / NumPy** | Data manipulation & Statistical calc |
| **Requests** | API Communication |
| **Football-Data.org** | Real-time Data Source |

---

## 🚀 Installation & Usage
### 1.Install required dependencies:
```bash
pip install pandas numpy requests xgboost
```

### 2. Clone the repository
```bash
git clone [https://github.com/OmerFarukKarakoy/Football-Predictor-Model-XGB.git](https://github.com/OmerFarukKarakoy/Football-Predictor-Model-XGB.git)
cd Football-Predictor-Model-XGB
```

### 3. Get your API key
```bash
Create a free key from: 👉 https://www.football-data.org/
```

### 4. Add your key inside SkorTahmin.py
```bash
Open the file and replace the placeholder:
API_KEY = "YOUR_API_KEY_HERE"
```

### 5. Usage (Run the Program)
```bash
Execute the main script in your terminal:
python SkorTahmin.py
```
