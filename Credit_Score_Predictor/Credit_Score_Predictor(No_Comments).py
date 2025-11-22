import pandas as pd
import numpy as np 
import re
import time
from rapidfuzz import fuzz, process


df = pd.read_csv("credit_score_messy_dataset.csv")

def cleaningnames(df1, data):
    df1[data] = df1[data].str.lower().replace(r'[^a-zA-Z]', '', regex=True)
    return df1[data]

def nullfilling(df1, rows, fill, cliping):
    try:
        df1[rows] = pd.to_numeric(df1[rows], errors='coerce').fillna(fill).clip(cliping)
    except Exception as e:
        df1[rows] = pd.to_numeric(df1[rows], errors='coerce').fillna(fill).clip(cliping[0], cliping[1])
    finally:
        try:
            return df1[rows].round().astype(int)
        except Exception as e:
            return df1[rows]

def valid_naming(df1, row, real_values, threshold, nansub):
    messyvalues = cleaningnames(df1, row).unique()
    mapping = {}
    for messy in messyvalues:
        messy = str(messy).strip().lower()
        best_match, score, aaa = process.extractOne(messy, real_values, scorer=fuzz.ratio)
        if score >= threshold:
            mapping[messy] = best_match.capitalize()
        else:
            mapping[messy] = "Other"
    df1[row] = df1[row].map(lambda x: mapping.get(x, nansub))
    return df1[row]

def defaultvalues(df1, row, defaultvalue, dtype):
    df1[row] = df1[row].fillna(0).astype(dtype)
    return df1[row]

def grouping_data(df1, rows):
    valid = df1.dropna(subset=rows)
    groups = valid.groupby(rows[0])[rows[1:]].agg(['mean', 'median', 'std', 'count'])
    groups = (groups.xs('mean', level=1, axis=1) - groups.xs('std', level=1, axis=1)).abs()
    for data in rows[1:]:
        df1[f"{data}_values"] = df1[rows[0]].map(groups[data])
        df1[data] = np.where(df1[data].notna(), df1[data], df1[f"{data}_values"])
        yield df1[data]

def cleaningnumbers(df1, rows):
    df1[rows] = df1[rows].astype(str).str.replace(r'[^\d.]+', '', regex=True)
    df1[rows] = pd.to_numeric(df1[rows], errors="coerce")
    return df1[rows].abs()

def binnary_values(df1, row, repalcemnt, correct):
    df1[row] = np.where(df1[row].isnull(), repalcemnt, np.where(df1[row].isin(correct), 1, 0))
    return df1[row]

def check(row):
    try:
        print(df[row].mean())
    except Exception as e:
        pass
    finally:
        print(df[row].unique())
        print(df[row].isna().sum())


allcolumns = (df.columns)
df['CustomerID'] = df['CustomerID'].str.replace('CUST', '').str.strip()

All_Occupation = ["analyst", "mechanic", "sales", "nurse", "consultant", "chef",
                  "developer", "accountant", "designer", "engineer", "student", "retired", "teacher",
                  "attorney", "doctor", "unemployed", "manager"]

df['Occupation'] = valid_naming(df, 'Occupation', All_Occupation, 80, 'Others')
df['Age'] = df['Age'].abs().fillna(0)

genderrows = ["female", "male"]
df['Gender'] = valid_naming(df, 'Gender', genderrows, 10, 'Others')
df['PhoneNumber'] = defaultvalues(df1=df, row='PhoneNumber', defaultvalue=0, dtype=str)
df['Email'] = defaultvalues(df1=df, row='Email', defaultvalue='Not_Available', dtype=str)

df['AnnualIncome'] = cleaningnumbers(df, 'AnnualIncome')
df['MonthlyIncome'] = cleaningnumbers(df, "MonthlyIncome")
df['MonthlyIncome'] = df['MonthlyIncome'].fillna(df["AnnualIncome"] / 12)
df['MonthlyIncome'], df['AnnualIncome'] = grouping_data(df, ['Occupation', 'MonthlyIncome', "AnnualIncome"])

df['MonthlyDebtPayment'] = df['MonthlyDebtPayment'].fillna(((df['TotalLoanAmount'] * 0.01) + (df['TotalCreditBalance'] * 0.03)))
df['MonthlyDebtPayment'] = df['MonthlyDebtPayment'].fillna(0)
df['DebtToIncomeRatio'] = np.where(df['MonthlyIncome'] > 0, (((((df['MonthlyDebtPayment'] / df["MonthlyIncome"]) * 100)))), 0)

df['CreditUtilizationRatio'] = cleaningnumbers(df, 'CreditUtilizationRatio')
df['CreditUtilizationRatio'] = np.where((df['CreditUtilizationRatio'] >= 200), 200, df['CreditUtilizationRatio'])

df['InterestRate'] = cleaningnumbers(df, 'InterestRate')
df['InterestRate'] = np.where(df['InterestRate'] > 36, 36, np.where(df['InterestRate'] < 3, 3, df['InterestRate']))

correct = ['YES', 'True', 'Yes', 'yes', 'Y', '1']
df['Bankruptcy'] = binnary_values(df, 'Bankruptcy', np.nan, correct=correct)
df['TaxLiens'] = binnary_values(df, 'TaxLiens', np.nan, correct)

df['TotalCreditBalance'] = pd.to_numeric(df['TotalCreditBalance'], errors='coerce').fillna(0)
df['NumCreditAccounts'] = df['NumCreditAccounts'].fillna(0).clip(0, 20).astype(int)
df['TotalCreditLimit'] = ((df['MonthlyIncome'] * 0.04)) * (df['NumCreditAccounts'])
df['TotalCreditLimit'] = df['TotalCreditLimit'].fillna(0)
df['CreditUtilizationRatio'] = np.where(df['TotalCreditLimit'] > 0, ((df['TotalCreditBalance'] / df["TotalCreditLimit"]) * 100), 0).clip(0, 200)

df['NumMissedPayments'] = nullfilling(df, 'NumMissedPayments', 0, 0)
df['NumLatePayments'] = nullfilling(df, 'NumLatePayments', 0, 0)

df['PaymentHistoryPct'], df['NumLoans'] = grouping_data(df1=df, rows=['Occupation', 'PaymentHistoryPct', 'NumLoans'])
df['NumLoans'] = df['NumLoans'].clip(0, 10).round()

df['TotalLoanAmount'] = df['MonthlyIncome'] * (df['NumLoans'] * 1.2)
df['NumHardInquiries'] = nullfilling(df, 'NumHardInquiries', 0, cliping=(0, 20)).round().astype(int)
df['TotalCreditBalance'] = ((df['CreditUtilizationRatio'] / 100) * df['TotalCreditLimit']).fillna(0).clip(0)
df['NumDerogatoryMarks'] = nullfilling(df, 'NumDerogatoryMarks', 0, cliping=(0, 10)).round().astype(int)
df['CreditHistoryLength_Months'] = nullfilling(df, 'CreditHistoryLength_Months', (df['Age'] * 12), cliping=(0))

creditmix_list = ["Mortgage", "Auto", "Credit Card", "Personal", "Student", "Mixed", "None", "Other"]
df['CreditMix'] = valid_naming(df1=df, row='CreditMix', real_values=creditmix_list, threshold=10, nansub='None')

asclist = ["Active", "Other", "Closed", "Delinquent", "Charged Off", "In Collections"]
df['AccountStatus'] = valid_naming(df1=df, row='AccountStatus', real_values=asclist, threshold=10, nansub='Others')

df['CreditScore'] = pd.to_numeric(
    (df['PaymentHistoryPct'] * 0.35) + (df['CreditUtilizationRatio'] * 0.3) + (df['CreditHistoryLength_Months'] * 0.15) +
    (df["DebtToIncomeRatio"] * 0.1)
).clip(0, 1000)

df['Bankruptcy'] = df['Bankruptcy'].fillna(0)
df['TaxLiens'] = df['TaxLiens'].fillna(0)

required_rows = ['NumLatePayments', 'NumMissedPayments', 'PaymentHistoryPct', 'TotalCreditBalance',
                 'TotalCreditLimit', 'CreditUtilizationRatio', 'NumCreditAccounts', 'CreditHistoryLength_Months',
                 'MonthlyIncome', 'AnnualIncome', 'MonthlyDebtPayment', 'DebtToIncomeRatio', 'NumLoans',
                 'TotalLoanAmount', 'InterestRate', 'NumHardInquiries', 'NumDerogatoryMarks', 'Bankruptcy',
                 'TaxLiens']

print(df['CreditScore'].describe())
Output_Data = df[required_rows].astype(float)
finaldata = df['CreditScore']