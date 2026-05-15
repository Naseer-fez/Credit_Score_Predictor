import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import Credit_Score_Predictor as cs

plt.style.use("seaborn-v0_8-darkgrid")

df = cs.Output_Data.copy()
df["CreditScore"] = cs.finaldata

# ========================
# 1. Correlation Heatmap
# ========================
plt.figure(figsize=(18,14))
sns.heatmap(df.corr(numeric_only=True), cmap='coolwarm', annot=False)
plt.title("Correlation Heatmap")
plt.show()

# ========================
# 2. Pairplot (selected columns)
# ========================
sns.pairplot(df[[
    "CreditScore", "PaymentHistoryPct", "CreditUtilizationRatio",
    "MonthlyIncome", "DebtToIncomeRatio"
]])
plt.show()

# ========================
# 3. Histogram for ALL numeric columns
# ========================
df.hist(figsize=(20,20), bins=25, edgecolor='black')
plt.suptitle("Histograms of All Numeric Features")
plt.show()

# ========================
# 4. KDE plots for distribution smoothness
# ========================
plt.figure(figsize=(12,6))
sns.kdeplot(df["CreditScore"], shade=True, color="green")
plt.title("Credit Score Density Plot")
plt.show()

# ========================
# 5. Scatter plots: every feature vs CreditScore
# ========================
numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
numeric_cols.remove("CreditScore")

for col in numeric_cols:
    plt.figure(figsize=(8,5))
    sns.scatterplot(x=df[col], y=df["CreditScore"], alpha=0.6)
    plt.title(f"{col} vs CreditScore")
    plt.show()

# ========================
# 6. Regression plots (trend lines)
# ========================
for col in numeric_cols:
    plt.figure(figsize=(8,5))
    sns.regplot(x=df[col], y=df["CreditScore"], scatter_kws={'alpha':0.3})
    plt.title(f"Regression: {col} → CreditScore")
    plt.show()

# ========================
# 7. Boxplots for outlier detection
# ========================
for col in numeric_cols:
    plt.figure(figsize=(7,4))
    sns.boxplot(x=df[col], color='orange')
    plt.title(f"Boxplot: {col}")
    plt.show()

# ========================
# 8. Categorical Analysis: CreditMix
# ========================
plt.figure(figsize=(10,6))
sns.boxplot(x=df["CreditMix"], y=df["CreditScore"])
plt.title("Credit Score by CreditMix")
plt.xticks(rotation=45)
plt.show()

# ========================
# 9. Categorical Analysis: AccountStatus
# ========================
plt.figure(figsize=(12,6))
sns.boxplot(x=df["AccountStatus"], y=df["CreditScore"])
plt.title("Credit Score by AccountStatus")
plt.xticks(rotation=45)
plt.show()

# ========================
# 10. Jointplot (Correlation + KDE)
# ========================
sns.jointplot(
    data=df,
    x="MonthlyIncome",
    y="CreditScore",
    kind="hex",
    gridsize=20,
    cmap="inferno"
)
plt.show()

# ========================
# 11. Heatmap for Missing Values
# ========================
plt.figure(figsize=(14,7))
sns.heatmap(df.isna(), cbar=False, cmap="viridis")
plt.title("Missing Values Heatmap")
plt.show()
