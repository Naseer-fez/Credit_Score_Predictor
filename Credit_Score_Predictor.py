import pandas as pd
import numpy as np 
import re
import time
from rapidfuzz import fuzz, process
df=pd.read_csv("credit_score_messy_dataset.csv")

allcolumns=(df.columns)
df['CustomerID'] = df['CustomerID'].str.replace('CUST', '').str.strip()
# print(df.info())
# for i in df.columns:
#     print(f"{df[i].head(2)}")
#     time.sleep(2.2)
#to understand the data 

# print(df['Occupation'].unique()) this data is very messy 
def cleaningnames(df1,data):
        # data=tuple(data)
        # print((data))
        # cleanedtext=re.sub(r'[^a-zA-Z]', '', data)
        df1[data]=df1[data].str.lower().replace(r'[^a-zA-Z]', '', regex=True)
        # df1[data]=df1[data].str.lower()
        return df1[data]
        
# df['Occupation']=cleaningnames(df,'Occupation')
# print(len(df['Occupation'].unique()))
# print(df['Occupation'].unique()) now that we have removed all the spaces adn numbers 
#it is better to use a hard coded version and put all the values in and geta proper match
# i got this plan inwhich i am gonna find and correct the messy data only 
All_Occupation=["analyst","mechanic","sales","nurse","consultant","chef",
"developer","accountant","designer","engineer","student","retired","teacher",
"attorney","doctor","unemployed","manager"]
    
def valid_naming(df1,row,real_values,threshold,nansub):
    
    # messyvalues=df1[row].unique()
    messyvalues=cleaningnames(df1,row).unique()
    # threshold=80
    mapping={}
    
    for messy in messyvalues:
        messy = str(messy).strip().lower()# need to convert everthing in to a string 
        best_match, score, aaa = process.extractOne(messy, real_values, scorer=fuzz.ratio)# a   function for find the best match word
        # will automaical compre everthing 
        if(score>=threshold):
            mapping[messy]=best_match.capitalize()
        else:
            mapping[messy]="Other"
         
           
    # print(len(mapping))        
    df1[row]=df1[row].map(lambda x: mapping.get(x, nansub))   
    # z=(lambda x: mapping.get(x, "other")) 
    # print(z)
    #     pass
    # # print(messyvalues)
    # pass
    return df1[row]
        
      
df['Occupation']=valid_naming(df,'Occupation',All_Occupation,80,'Others')
# print(df['Occupation'].unique())
# print(df['Occupation'].unique()) all the names have been cleaned , now , moving to the next row
# print(df[df['Occupation']==np.nan])
# Age
# df['Age']=df['Age'].abs()
df['Age']=df['Age'].abs().fillna(0)
# print(df['Age'].unique())
genderrows=["female","male"]
# print(df['Gender'].unique())
df['Gender']=valid_naming(df,'Gender',genderrows,10,'Others')
# print(df["Gender"].value_counts(dropna=False))
# data=df.groupby('Gender')['Age'].count()
# # print((df['Gender']!='other').count())

# filtered_df = df[df['Gender'] == 'other']

# # Count the number of rows in the filtered DataFrame
# len(filtered_df)
# # OR
# print(filtered_df.shape[0])
#PhoneNumber
# print(df['PhoneNumber'].isna().sum())
def defaultvalues(df1,row,defaultvalue,dtype):
    df1[row] = df1[row].fillna(0).astype(dtype)
    return df1[row]
df['PhoneNumber']=defaultvalues(df1=df,row='PhoneNumber',defaultvalue=0,dtype=str)

df['Email']=defaultvalues(df1=df,row='Email',defaultvalue='Not_Available',dtype=str)
# print(df['PhoneNumber'].isna().sum())
# print(df['NumLatePayments'].isna().sum())
# print(df['NumLatePayments'].unique())
"""So late payments the logic should be that 
it should be paired with monthly incomes, but even that wont be easy  """
# print(df.info())

# valid = df.dropna(subset=['NumLatePayments', 'MonthlyIncome'])
# print(df['MonthlyIncome'])
# df['MonthlyIncome']=df['MonthlyIncome'].fillna()
# print(df.info())
# print(df['AnnualIncome'].isna().sum())
def grouping_data(df1,rows):
    valid=df1.dropna(subset=rows)
    groups=valid.groupby(rows[0])[rows[1:]].agg(['mean', 'median','std','count'])
    
    groups=(groups.xs('mean', level=1, axis=1) - groups.xs('std', level=1, axis=1)).abs()
    for data in rows[1:]:
        df1[f"{data}_values"] = df1[rows[0]].map(groups[data])
        df1[data]=np.where(df1[data].notna(),df1[data],df1[f"{data}_values"])
        yield df1[data]
    

#     prices=valid.groupby('PropertyType')['SalePrice'].agg(['mean', 'median','std','count'])
# prices=(prices['mean']-prices['std'])
#df['SalePrice']=np.where(df['SalePrice'].notna(),df['SalePrice'],df['sales_types'])
# df["sales_types"]=df['PropertyType'].map(prices)
    
    pass

def cleaningnumbers(df1,rows):
        df1[rows]=df1[rows].astype(str).str.replace(r'[^\d.]+', '', regex=True)
        df1[rows]=pd.to_numeric(df1[rows], errors="coerce")
        return df1[rows].abs()
df['AnnualIncome']=cleaningnumbers(df,'AnnualIncome')
df['MonthlyIncome']=cleaningnumbers(df,"MonthlyIncome")

# print(df['MonthlyIncome'].isna().sum())
df['MonthlyIncome']=df['MonthlyIncome'].fillna( df["AnnualIncome"] / 12)
# print(df[(df['MonthlyIncome'].isnull())&(df['AnnualIncome'].isnull())])
# df['MonthlyIncome']=grouping_data(df,['Occupation','MonthlyIncome'])
df['MonthlyIncome'],df['AnnualIncome']=grouping_data(df,['Occupation','MonthlyIncome',"AnnualIncome"])

# print(df.info())
# print(df['DebtToIncomeRatio'])
# MonthlyDebtPayment = L * 0.01 + B * 0.03
# print((df['MonthlyDebtPayment'].isna().sum()))
df['MonthlyDebtPayment']=df['MonthlyDebtPayment'].fillna(((df['TotalLoanAmount']*0.01)+(df['TotalCreditBalance']*0.03)))
df['MonthlyDebtPayment']=df['MonthlyDebtPayment'].fillna(0)
# print((df['MonthlyDebtPayment'].isna().sum()))
# DTI (%) = (MonthlyDebtPayment / MonthlyIncome) * 100ll
# print((df['DebtToIncomeRatio']))
# df['DebtToIncomeRatio']=(df['MonthlyDebtPayment']/df['MonthlyIncome'])*100
df['DebtToIncomeRatio']=np.where(df['MonthlyIncome']>0,(((((df['MonthlyDebtPayment']/df["MonthlyIncome"])*100)))),0)
# print((df['DebtToIncomeRatio']))
df['CreditUtilizationRatio']=cleaningnumbers(df,'CreditUtilizationRatio')
# print((df['CreditUtilizationRatio'].isna().sum()))
df['CreditUtilizationRatio']=np.where((df['CreditUtilizationRatio']>=200),200,df['CreditUtilizationRatio'])

df['InterestRate']=cleaningnumbers(df,'InterestRate')
# df['InterestRate']=np.where(((df['InterestRate']>=36),((df['InterestRate']<=3))),(36,3),df['InterestRate'])
# print((df['InterestRate'].isna().sum()))
df['InterestRate'] = np.where(
    df['InterestRate'] > 36,  36,                       
    np.where(df['InterestRate'] < 3, 3,df['InterestRate']))
# df['InterestRate'] = df['InterestRate'].clip(lower=3, upper=36) easiest 
# print((df['InterestRate'].isna().sum()))
# print(df['TaxLiens'].unique())
correct=['YES','True','Yes','yes','Y','1']
def binnary_values(df1,row,repalcemnt,correct):
    df1[row]=np.where(df1[row].isnull(),repalcemnt,np.where(df1[row].isin(correct),1,0))
    return df1[row]
# print((df['PaymentHistoryPct'].isna().sum()))
df['Bankruptcy']=binnary_values(df,'Bankruptcy',np.nan,correct=correct)
# print((df['CreditUtilizationRatio'].isna().sum()))
df['TaxLiens']=binnary_values(df,'TaxLiens',np.nan,correct)
# 35% Payment History
# 30% Credit Utilization
# 15% Credit History Length
# 10% Credit Mix & Debt Burden (DTI)
# 10% New Credit (Inquiries, Derogs)
# CreditUtilizationRatio (%) = (TotalCreditBalance / TotalCreditLimit) * 100
# print(df['CreditUtilizationRatio'].unique())
# CreditLimitPerAccount = MonthlyIncome * random.uniform(0.2, 0.6)
# TotalCreditLimit = NumCreditAccounts * CreditLimitPerAccount
def check(row):
    try:
        print(df[row].mean())
    except Exception as e:
        pass
    finally:
        print(df[row].unique())
        print(df[row].isna().sum())
        # try:
        #     print(df[row].mean())
        # except Exception as e:
        #     pass
# for quick views
# print(df['NumCreditAccounts'])
df['TotalCreditBalance'] = pd.to_numeric(df['TotalCreditBalance'], errors='coerce').fillna(0)
df['NumCreditAccounts']=df['NumCreditAccounts'].fillna(0).clip(0,20).astype(int)
df['TotalCreditLimit']=((df['MonthlyIncome']*0.04))*(df['NumCreditAccounts'])
df['TotalCreditLimit'] = df['TotalCreditLimit'].fillna(0)

df['CreditUtilizationRatio']=np.where(df['TotalCreditLimit']>0,((df['TotalCreditBalance']/df["TotalCreditLimit"])*100),0).clip(0, 200)
# print((df['CreditUtilizationRatio'].head()))
# 1. NumLatePayments
# 2. NumMissedPayments
# 3. PaymentHistoryPct
# print(df['NumLatePayments'].unique())
def nullfilling(df1,rows,fill,cliping):
    try:
        df1[rows]=pd.to_numeric(df1[rows], errors='coerce').fillna(fill).clip(cliping)
        # df1[rows]=df1[rows]
        
    except Exception as e:
        df1[rows]=pd.to_numeric(df1[rows], errors='coerce').fillna(fill).clip(cliping[0],cliping[1])
        # df1[rows]=df1[rows]
    finally:# once look for this at last 
        try :
            return df1[rows].round().astype(int)
        except Exception as e:
            return df1[rows]
        
        
    
df['NumMissedPayments']=nullfilling(df,'NumMissedPayments',0,0)
# check('NumMissedPayments')
df['NumLatePayments']=nullfilling(df,'NumLatePayments',0,0)
# print(df['PaymentHistoryPct'].unique())
# print((df['PaymentHistoryPct'].isna().sum()))
df['PaymentHistoryPct'],df['NumLoans']=grouping_data(df1=df,rows=['Occupation','PaymentHistoryPct','NumLoans'])
# print((df['NumLoans'].isna().sum()))
df['NumLoans']=df['NumLoans'].clip(0,10).round()
# df['NumLoans']=nullfilling(df,'NumLoans',0)
# print(df['NumLoans'].unique())
# print(df.info())
# TotalLoanAmount = MonthlyIncome * (NumLoans * 1.2)
df['TotalLoanAmount']=df['MonthlyIncome']*(df['NumLoans']*1.2)
# print((df['TotalLoanAmount'].isna().sum()))
# print(len(df['TotalLoanAmount'].round().unique()))
# print((df['LastPaymentDate'].isna().sum()))
# print(len(df['LastPaymentDate'].unique()))
# df['LastPaymentDate']=pd.to_datetime(df['LastPaymentDate'])

# df['LastPaymentDate']=np.where(df['LastPaymentDate'].notnull(),pd.to_datetime(df['LastPaymentDate']),pd.to_datetime(df['ApplicationDate']))
# print(df['LastPaymentDate'].isna().sum())
# df['LastPaymentDate'] = pd.to_datetime(
#     df['LastPaymentDate'].fillna(df['ApplicationDate']),format='%d-%m-%Y', errors='coerce'
# )
# print(df['LastPaymentDate'].isna().sum())
# df['NumHardInquiries']=pd.to_numeric(df['NumHardInquiries'], errors='coerce').fillna(0).clip(0,20).round().astype(int)
df['NumHardInquiries']=nullfilling(df,'NumHardInquiries',0,cliping=(0,20)).round().astype(int)
# print(df['NumHardInquiries'].unique())

# TotalCreditBalance = (CreditUtilizationRatio / 100) * TotalCreditLimit
# df['NumHardInquiries']=pd.to_numeric(df['NumHardInquiries'], errors='coerce').fillna(0).clip(0,20).round()
df['TotalCreditBalance']=((df['CreditUtilizationRatio']/100)*df['TotalCreditLimit']).fillna(0).clip(0)
# check('NumDerogatoryMarks')

df['NumDerogatoryMarks']=nullfilling(df,'NumDerogatoryMarks',0,cliping=(0,10)).round().astype(int)
# Credit history begins after age 18.
# df['CreditHistoryLength_Months']=pd.to_numeric(df['CreditHistoryLength_Months'], errors='coerce').fillna(
#    (((df['Age']))*12) ).clip(0).round().astype(int)
# nullfilling(df1,rows,fill,cliping)
df['CreditHistoryLength_Months']=nullfilling(df,'CreditHistoryLength_Months',(df['Age']*12),cliping=(0))
# check('CreditHistoryLength_Months')
# df['CreditHistoryLength_Months']=np.where(df['CreditHistoryLength_Months'].isnull(),(((df['Age']))*12),df['CreditHistoryLength_Months'] )
creditmix_list=["Mortgage","Auto","Credit Card","Personal","Student","Mixed","None","Other"]
# print(df['CreditMix'].head(10))
df['CreditMix']=valid_naming(df1=df,row='CreditMix',real_values=creditmix_list,threshold=10,nansub='None')

asclist=["Active","Other""Closed","Delinquent","Charged Off","In Collections",]
# print(df.columns)
df['AccountStatus']=valid_naming(df1=df,row='AccountStatus',real_values=asclist,threshold=10,nansub='Others')

# print(df.info())
# CreditScore = 
#     + PaymentHistoryPct (35%)
#     + CreditUtilizationRatio (30%)
#     + CreditHistoryLength_Months (15%)
#     + New Credit (10%)
#     + Credit Mix + DTI (10%)
# check('CreditScore')

df['CreditScore']=pd.to_numeric(
    
    (df['PaymentHistoryPct']*0.35)+(df['CreditUtilizationRatio']*0.3)+(df['CreditHistoryLength_Months']*0.15)+
    (df["DebtToIncomeRatio"]*0.1)
    
).clip(0,1000)
df['Bankruptcy'] = df['Bankruptcy'].fillna(0)
df['TaxLiens'] = df['TaxLiens'].fillna(0)
# df['ApplicationDate'] = pd.to_datetime(df['ApplicationDate'], errors='coerce')
# df['AccountAgeDays'] = ("01-01-2025" - df['ApplicationDate']).dt.days
# check('CreditScore')
# print(((df['CreditScore'].isna() )& (df['DebtToIncomeRatio'].isna())).sum())
# print(df['LastPaymentDate'].isna().sum())

# NOt using dates as it is not valid well


required_rows=['NumLatePayments','NumMissedPayments','PaymentHistoryPct','TotalCreditBalance',
               'TotalCreditLimit','CreditUtilizationRatio','NumCreditAccounts','CreditHistoryLength_Months',
'MonthlyIncome','AnnualIncome','MonthlyDebtPayment','DebtToIncomeRatio','NumLoans',
'TotalLoanAmount','InterestRate','NumHardInquiries','NumDerogatoryMarks','Bankruptcy',
'TaxLiens']
# print(df['CreditScore'].describe())
# print(df.info())
Output_Data=df[required_rows].astype(float)
finaldata=df['CreditScore']
