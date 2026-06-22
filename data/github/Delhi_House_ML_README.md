# Delhi House Price Prediction

A complete machine learning pipeline to predict residential property prices in Delhi — from raw CSV data to a deployable prediction function.

---

## Project Structure

```
delhi-house-price/
├── Delhi house data.csv               # Raw dataset (~1250 rows)
├── Delhi_House_Price_Prediction.ipynb # Main notebook (full pipeline)
└── README.md
```

---

## Dataset

| Attribute | Description |
|-----------|-------------|
| `Area` | Property size in square feet |
| `BHK` | Number of bedrooms |
| `Bathroom` | Number of bathrooms |
| `Furnishing` | Furnished / Semi-Furnished / Unfurnished |
| `Locality` | Neighbourhood in Delhi |
| `Parking` | Number of parking spots |
| `Price` | Sale price in Rs. *(target variable)* |
| `Status` | Ready to Move / Under Construction |
| `Transaction` | New Property / Resale |
| `Type` | Apartment / Villa / Builder Floor / etc. |
| `Per_Sqft` | Price per square foot |

---

## Pipeline Overview

```
Raw CSV  ->  Cleaning  ->  EDA  ->  Feature Engineering  ->  Training  ->  Tuning  ->  Predict
```

### 1. Data Cleaning
- Fill missing numeric values with **median**, categoricals with **mode**
- Remove duplicate rows
- Standardise string casing across all categorical columns
- Remove `Price` outliers using **IQR method**

### 2. Exploratory Data Analysis
- Price distribution (raw + log-transformed)
- Count plots for all categorical features
- Box plots — Price by Furnishing, Status, Type, Transaction
- Scatter plots — numeric features vs Price
- Correlation heatmap
- Top 10 localities by median price
- Price by BHK configuration

### 3. Feature Engineering

| Feature | Formula |
|---------|---------|
| `Bath_BHK_Ratio` | `Bathroom / BHK` |
| `Area_per_BHK` | `Area / BHK` |
| `Log_Area` | `log(Area + 1)` |
| `*_enc` | Label-encoded low-cardinality categoricals |
| `Locality_freq` | Frequency encoding for Locality |

### 4. Models Trained

| Model | Notes |
|-------|-------|
| Linear Regression | Baseline |
| Ridge Regression | L2 regularisation |
| Lasso Regression | L1 regularisation |
| Decision Tree | `max_depth=8` |
| Random Forest | 200 estimators |
| Gradient Boosting | 200 estimators, `lr=0.1` |

All models are compared on **MAE**, **RMSE**, **R2**, and **5-fold CV R2**.

### 5. Hyperparameter Tuning
`GridSearchCV` (5-fold) is applied to the best-performing model.

---

## Getting Started

### Prerequisites
```bash
pip install pandas numpy matplotlib seaborn scikit-learn
```

### Run
1. Place `Delhi house data.csv` in the same directory as the notebook
2. Open `Delhi_House_Price_Prediction.ipynb` in Jupyter
3. Run all cells (`Kernel -> Restart & Run All`)

---

## Making Predictions

The notebook exposes a `predict_price()` function you can call directly:

```python
price = predict_price(
    area        = 1200,
    bhk         = 2,
    bathroom    = 2,
    furnishing  = 'Semi-Furnished',
    locality    = 'Dwarka',
    parking     = 1,
    status      = 'Ready To Move',
    transaction = 'Resale',
    prop_type   = 'Apartment',
    per_sqft    = 6500
)

print(f'Predicted Price: Rs. {price:,.0f}')
```

---

## Example Results

| Model | R2 | MAE | RMSE |
|-------|----|-----|------|
| Gradient Boosting | ~0.87 | -- | -- |
| Random Forest | ~0.85 | -- | -- |
| Ridge Regression | ~0.72 | -- | -- |
| Linear Regression | ~0.71 | -- | -- |

> Actual values will vary based on your dataset. Results shown are approximate.

---

## Tech Stack

- **Python 3.10+**
- **pandas** — data manipulation
- **numpy** — numerical computing
- **matplotlib / seaborn** — visualisation
- **scikit-learn** — ML models, preprocessing, evaluation

---

## License

This project is for educational purposes. Dataset credits go to the original source.