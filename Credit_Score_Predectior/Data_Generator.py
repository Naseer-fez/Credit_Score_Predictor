import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# Number of records
n = 3500

# Helper functions for messy data
def add_typos(text, prob=0.05):
    if random.random() < prob and isinstance(text, str) and len(text) > 0:
        typos = {'a': '@', 'e': '3', 'i': '1', 'o': '0', 's': '$'}
        chars = list(text)
        # Pick a random position that might be typo-able
        idxs = [i for i, c in enumerate(chars) if c.lower() in typos]
        if not idxs:
            return text
        idx = random.choice(idxs)
        chars[idx] = typos[chars[idx].lower()]
        return "".join(chars)
    return text

def random_case(text, prob=0.1):
    if random.random() < prob and isinstance(text, str):
        return random.choice([text.upper(), text.lower(), text.title()])
    return text

def add_missing(value, prob=0.08):
    if random.random() < prob:
        return random.choice([np.nan, '', 'null', 'NULL', 'N/A', None, 'NA'])
    return value

# Generate base data
data = {}

# Personal Information
first_names = [
    'James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda',
    'William', 'Elizabeth', 'David', 'Barbara', 'Richard', 'Susan', 'Joseph',
    'Jessica', 'Thomas', 'Sarah', 'Charles', 'Karen', 'Christopher', 'Nancy',
    'Daniel', 'Lisa', 'Matthew', 'Betty', 'Anthony', 'Margaret', 'Mark', 'Sandra',
    'Donald', 'Ashley', 'Steven', 'Kimberly', 'Paul', 'Emily', 'Andrew', 'Donna',
    'Joshua', 'Michelle'
]

last_names = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
    'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
    'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
    'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson'
]

data['CustomerID'] = [
    f'CUST{str(i).zfill(6)}' if random.random() > 0.02 else f'CST{i}'
    for i in range(1, n + 1)
]

data['FirstName'] = [
    random_case(add_typos(random.choice(first_names)), 0.05) for _ in range(n)
]
data['LastName'] = [
    random_case(add_typos(random.choice(last_names)), 0.05) for _ in range(n)
]

# Generate dates of birth (ages 18-75)
start_date = datetime.now() - timedelta(days=75 * 365)
end_date = datetime.now() - timedelta(days=18 * 365)
date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y', '%B %d, %Y', '%m-%d-%y']

dobs = []
for _ in range(n):
    dob = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
    fmt = random.choice(date_formats)
    dob_str = dob.strftime(fmt)
    if random.random() > 0.03:
        dobs.append(dob_str)
    else:
        dobs.append(add_missing(dob_str, 0.15))

data['DateOfBirth'] = dobs

# Age (derived with some errors)
ages = []
for dob in dobs:
    if pd.isna(dob) or dob in ['', 'null', 'NULL', 'N/A', None, 'NA']:
        ages.append(add_missing(np.nan, 0.5))
    else:
        parsed = False
        for fmt in date_formats:
            try:
                birth = datetime.strptime(dob, fmt)
                age = (datetime.now() - birth).days // 365
                # Add occasional calculation errors
                if random.random() < 0.03:
                    age += random.randint(-5, 5)
                ages.append(age if random.random() > 0.05 else str(age))
                parsed = True
                break
            except Exception:
                continue
        if not parsed:
            ages.append(add_missing(np.nan, 0.8))

data['Age'] = ages

# Gender with inconsistent formats
genders = []
for _ in range(n):
    g = random.choice(['Male', 'Female'])
    if random.random() < 0.3:
        g = random.choice(['M', 'F', 'male', 'female', 'MALE', 'FEMALE', g])
    genders.append(add_missing(g, 0.06))
data['Gender'] = genders

# Contact Information
emails = []
for i in range(n):
    fname = data['FirstName'][i] if not pd.isna(data['FirstName'][i]) else 'user'
    lname = data['LastName'][i] if not pd.isna(data['LastName'][i]) else 'test'
    domain = random.choice(
        ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com', 'icloud.com']
    )
    email = f"{str(fname).lower()}.{str(lname).lower()}@{domain}"
    if random.random() < 0.05:
        email = email.replace('@', random.choice(['@', '@@', '']))
    emails.append(add_missing(email, 0.07))
data['Email'] = emails

# Phone numbers with various formats
phones = []
for _ in range(n):
    num = f"{random.randint(200, 999)}{random.randint(200, 999)}{random.randint(1000, 9999)}"
    fmt = random.choice([
        f"({num[:3]}) {num[3:6]}-{num[6:]}",
        f"{num[:3]}-{num[3:6]}-{num[6:]}",
        f"{num[:3]}.{num[3:6]}.{num[6:]}",
        num,
        f"+1{num}"
    ])
    phones.append(add_missing(fmt, 0.08))
data['PhoneNumber'] = phones

# Address components
states = ['CA', 'TX', 'FL', 'NY', 'PA', 'IL', 'OH', 'GA', 'NC', 'MI']
state_full = {
    'CA': 'California',
    'TX': 'Texas',
    'FL': 'Florida',
    'NY': 'New York',
    'PA': 'Pennsylvania'
}

cities = [
    'Los Angeles', 'New York', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia',
    'San Antonio', 'Dallas', 'Austin', 'Miami'
]

addresses = []
for _ in range(n):
    num = random.randint(1, 9999)
    street = random.choice(['Main St', 'Oak Ave', 'Maple Dr', 'Washington Blvd', 'Park Ln', 'Elm Street'])
    addr = f"{num} {street}"
    addresses.append(add_missing(add_typos(addr, 0.03), 0.05))
data['Address'] = addresses

data['City'] = [
    add_missing(random_case(add_typos(random.choice(cities), 0.04), 0.08), 0.06)
    for _ in range(n)
]

states_list = []
for _ in range(n):
    st = random.choice(states)
    if random.random() < 0.3:
        st = state_full.get(st, st)
    states_list.append(add_missing(st, 0.05))
data['State'] = states_list

data['ZipCode'] = [
    add_missing(
        str(random.randint(10000, 99999)) if random.random() > 0.02 else random.randint(10000, 99999),
        0.07
    )
    for _ in range(n)
]

# Employment & Income
occupations = [
    'Engineer', 'Teacher', 'Nurse', 'Sales', 'Manager', 'Developer', 'Analyst',
    'Consultant', 'Designer', 'Accountant', 'Attorney', 'Doctor', 'Mechanic',
    'Chef', 'Student', 'Retired', 'Unemployed'
]

# Keep a canonical occupation per row for logic, but store messy text in the column
occ_canonical = []
occ_display = []
for _ in range(n):
    base_occ = random.choice(occupations)
    occ_canonical.append(base_occ)
    messy_occ = add_missing(random_case(add_typos(base_occ, 0.03), 0.1), 0.08)
    occ_display.append(messy_occ)

data['Occupation'] = occ_display

# Realistic occupation-based MONTHLY income ranges (in whatever currency)
occupation_monthly_income_ranges = {
    'Engineer':    (5000, 12000),
    'Developer':   (5000, 15000),
    'Analyst':     (4000, 10000),
    'Teacher':     (3000, 8000),
    'Nurse':       (3000, 9000),
    'Consultant':  (6000, 15000),
    'Manager':     (7000, 20000),
    'Designer':    (3500, 9000),
    'Accountant':  (3500, 9000),
    'Attorney':    (8000, 25000),
    'Doctor':      (12000, 30000),
    'Mechanic':    (2000, 7000),
    'Chef':        (2000, 6000),
    'Sales':       (2000, 8000),
    'Student':     (0, 1500),
    'Retired':     (0, 2000),
    'Unemployed':  (0, 1000)
}

# Annual Income (realistic by occupation + age, still messy format)
incomes = []
annual_numeric_cache = []  # keep numeric for internal logic
for i in range(n):
    # age
    try:
        age_val = data['Age'][i]
        age = float(age_val) if not pd.isna(age_val) and age_val not in ['', 'null', 'NULL', 'N/A', None, 'NA'] else 35
    except Exception:
        age = 35

    base_occ = occ_canonical[i]
    low, high = occupation_monthly_income_ranges.get(base_occ, (3000, 8000))

    # age factor: younger people tend to be nearer low, older nearer high
    age_factor = min(max((age - 22) / 30, 0), 1)  # 0 to 1
    # pick a base monthly income inside range
    monthly_base = low + (high - low) * (0.3 + 0.7 * random.random() * age_factor)
    monthly_base = max(0, monthly_base + np.random.normal(0, 400))

    annual_income_real = monthly_base * 12

    # occasional outliers
    if random.random() < 0.02:
        annual_income_real = annual_income_real * random.choice([0.2, 3, 5])

    annual_income_real = max(0, annual_income_real)

    # store numeric version for internal use
    annual_numeric_cache.append(annual_income_real)

    # Format inconsistently (like before)
    if random.random() < 0.3:
        income = f"${annual_income_real:,.2f}"
    elif random.random() < 0.15:
        income = f"{annual_income_real:,.0f}"
    else:
        income = round(annual_income_real, 2)

    incomes.append(add_missing(income, 0.06))

data['AnnualIncome'] = incomes

# Monthly Income (derived from AnnualIncome, with small noise + messy formatting)
monthly_incomes = []
for ann in incomes:
    if pd.isna(ann) or ann in ['', 'null', 'NULL', 'N/A', None, 'NA']:
        monthly_incomes.append(add_missing(np.nan, 0.5))
    else:
        try:
            val = float(str(ann).replace('$', '').replace(',', ''))
            monthly = val / 12.0
            # Add small calculation errors occasionally
            if random.random() < 0.05:
                monthly = monthly * random.uniform(0.8, 1.3)
            monthly = max(0, monthly)
            monthly_incomes.append(
                round(monthly, 2) if random.random() > 0.05 else str(round(monthly, 2))
            )
        except Exception:
            monthly_incomes.append(add_missing(np.nan, 0.8))

data['MonthlyIncome'] = monthly_incomes

# Employment Length (months)
emp_lengths = []
for i in range(n):
    try:
        age_val = data['Age'][i]
        age = float(age_val) if not pd.isna(age_val) and age_val not in ['', 'null', 'NULL', 'N/A', None, 'NA'] else 35
    except Exception:
        age = 35

    max_months = max(0, int((age - 18) * 12))
    length = random.randint(0, max_months)

    # Negative values as errors
    if random.random() < 0.01:
        length = -abs(length)

    emp_lengths.append(
        add_missing(length if random.random() > 0.05 else str(length), 0.07)
    )

data['EmploymentLength_Months'] = emp_lengths

# Credit History
# Number of Credit Accounts
data['NumCreditAccounts'] = [
    add_missing(
        random.randint(0, 25) if random.random() > 0.03 else random.randint(-1, 50),
        0.06
    )
    for _ in range(n)
]

# Credit History Length (months) - correlated with age
credit_history = []
for i in range(n):
    try:
        age_val = data['Age'][i]
        age = float(age_val) if not pd.isna(age_val) and age_val not in ['', 'null', 'NULL', 'N/A', None, 'NA'] else 35
    except Exception:
        age = 35

    max_hist = max(0, int((age - 18) * 12))
    hist = random.randint(0, max_hist)
    credit_history.append(
        add_missing(hist if random.random() > 0.04 else str(hist), 0.07)
    )

data['CreditHistoryLength_Months'] = credit_history

# Total Credit Limit
credit_limits = []
for i in range(n):
    num_accounts = data['NumCreditAccounts'][i]
    try:
        num = int(num_accounts) if not pd.isna(num_accounts) else 5
    except Exception:
        num = 5

    limit = num * random.uniform(1000, 15000)
    limit = max(0, limit + np.random.normal(0, 5000))

    # occasional extreme outliers
    if random.random() < 0.02:
        limit = limit * random.choice([0.01, 15])

    credit_limits.append(
        add_missing(
            round(limit, 2) if random.random() > 0.06 else str(round(limit, 2)),
            0.06
        )
    )

data['TotalCreditLimit'] = credit_limits

# Credit Utilization (Total Balance / Total Limit)
balances = []
utilization = []
for i in range(n):
    try:
        limit = float(str(data['TotalCreditLimit'][i]).replace('$', '').replace(',', ''))
        if limit <= 0:
            limit = 1000
    except Exception:
        limit = 10000

    util = random.uniform(0, 1.5)  # Can exceed 100%
    balance = limit * util

    balances.append(
        add_missing(
            round(balance, 2) if random.random() > 0.05 else str(round(balance, 2)),
            0.06
        )
    )

    util_pct = util * 100
    if random.random() < 0.3:
        utilization.append(
            add_missing(f"{util_pct:.1f}%", 0.07)
        )
    else:
        utilization.append(
            add_missing(
                round(util_pct, 2) if random.random() > 0.05 else str(round(util_pct, 2)),
                0.07
            )
        )

data['TotalCreditBalance'] = balances
data['CreditUtilizationRatio'] = utilization

# Payment History
data['NumLatePayments'] = [
    add_missing(
        random.randint(0, 15) if random.random() > 0.02 else random.randint(-1, 30),
        0.07
    )
    for _ in range(n)
]

data['NumMissedPayments'] = [
    add_missing(
        random.randint(0, 10) if random.random() > 0.02 else random.randint(-1, 20),
        0.08
    )
    for _ in range(n)
]

# Payment History Percentage (derived with errors)
payment_pct = []
for i in range(n):
    late = data['NumLatePayments'][i]
    missed = data['NumMissedPayments'][i]

    try:
        late_val = int(late) if not pd.isna(late) else 0
        missed_val = int(missed) if not pd.isna(missed) else 0

        total_payments = random.randint(50, 500)
        bad_payments = max(0, late_val + missed_val)
        total_payments = max(total_payments, bad_payments + 1)

        pct = ((total_payments - bad_payments) / total_payments) * 100

        # Add errors
        if random.random() < 0.05:
            pct = pct + random.uniform(-10, 10)

        pct = max(0, min(100, pct))
        payment_pct.append(
            add_missing(
                round(pct, 1) if random.random() > 0.05 else str(round(pct, 1)),
                0.08
            )
        )
    except Exception:
        payment_pct.append(add_missing(np.nan, 0.8))

data['PaymentHistoryPct'] = payment_pct

# Loan Information
data['NumLoans'] = [
    add_missing(
        random.randint(0, 10) if random.random() > 0.02 else random.randint(-1, 20),
        0.07
    )
    for _ in range(n)
]

loan_amounts = []
for i in range(n):
    num_loans = data['NumLoans'][i]
    try:
        num = int(num_loans) if not pd.isna(num_loans) else 2
    except Exception:
        num = 2

    if num <= 0:
        amount = 0
    else:
        amount = num * random.uniform(5000, 50000)

    loan_amounts.append(
        add_missing(
            round(amount, 2) if random.random() > 0.05 else str(round(amount, 2)),
            0.07
        )
    )

data['TotalLoanAmount'] = loan_amounts

# Monthly Debt Payments (correlated with loans and credit balance)
monthly_debt = []
for i in range(n):
    try:
        loans = float(str(data['TotalLoanAmount'][i]).replace('$', '').replace(',', ''))
    except Exception:
        loans = 10000

    try:
        balance = float(str(data['TotalCreditBalance'][i]).replace('$', '').replace(',', ''))
    except Exception:
        balance = 5000

    debt = (loans * 0.01) + (balance * 0.03) + np.random.normal(0, 200)
    debt = max(0, debt)

    monthly_debt.append(
        add_missing(
            round(debt, 2) if random.random() > 0.05 else str(round(debt, 2)),
            0.07
        )
    )

data['MonthlyDebtPayment'] = monthly_debt

# Debt-to-Income Ratio (derived)
dti = []
for i in range(n):
    try:
        monthly_inc = data['MonthlyIncome'][i]
        monthly_inc_val = float(str(monthly_inc).replace('$', '').replace(',', ''))
        if monthly_inc_val <= 0:
            monthly_inc_val = 1.0
    except Exception:
        monthly_inc_val = 4000

    try:
        monthly_dbt = float(str(data['MonthlyDebtPayment'][i]).replace('$', '').replace(',', ''))
    except Exception:
        monthly_dbt = 800

    ratio = (monthly_dbt / monthly_inc_val) * 100

    # Add calculation errors
    if random.random() < 0.05:
        ratio = ratio * random.uniform(0.7, 1.4)

    ratio = max(0, ratio)
    dti.append(
        add_missing(
            round(ratio, 2) if random.random() > 0.05 else str(round(ratio, 2)),
            0.08
        )
    )

data['DebtToIncomeRatio'] = dti

# Inquiries and Derogatory Marks
data['NumHardInquiries'] = [
    add_missing(
        random.randint(0, 10) if random.random() > 0.02 else random.randint(-1, 20),
        0.07
    )
    for _ in range(n)
]

data['NumDerogatoryMarks'] = [
    add_missing(
        random.randint(0, 5) if random.random() > 0.02 else random.randint(-1, 15),
        0.08
    )
    for _ in range(n)
]

# Bankruptcies
bankruptcies = []
for _ in range(n):
    b = random.choice([0, 0, 0, 0, 0, 0, 0, 0, 0, 1])  # ~10% have bankruptcy
    if random.random() < 0.2:
        b = random.choice(['Yes', 'No', 'TRUE', 'FALSE', '1', '0', b])
    bankruptcies.append(add_missing(b, 0.06))
data['Bankruptcy'] = bankruptcies

# Tax Liens
tax_liens = []
for _ in range(n):
    t = random.choice([0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
    if random.random() < 0.2:
        t = random.choice(['Yes', 'No', 'TRUE', 'FALSE', '1', '0', t])
    tax_liens.append(add_missing(t, 0.07))
data['TaxLiens'] = tax_liens

# Account Application Date
app_dates = []
for _ in range(n):
    days_ago = random.randint(1, 3650)
    app_date = datetime.now() - timedelta(days=days_ago)
    fmt = random.choice(date_formats)
    app_dates.append(add_missing(app_date.strftime(fmt), 0.06))

data['ApplicationDate'] = app_dates

# Last Payment Date
last_payment_dates = []
for _ in range(n):
    days_ago = random.randint(1, 365)
    payment_date = datetime.now() - timedelta(days=days_ago)
    fmt = random.choice(date_formats)
    last_payment_dates.append(add_missing(payment_date.strftime(fmt), 0.08))

data['LastPaymentDate'] = last_payment_dates

# Credit Mix (types of credit)
credit_types = ['Mortgage', 'Auto', 'Credit Card', 'Personal', 'Student', 'Mixed', 'None']
data['CreditMix'] = [
    add_missing(random_case(random.choice(credit_types), 0.1), 0.07)
    for _ in range(n)
]

# Account Status
statuses = ['Active', 'Closed', 'Delinquent', 'Charged Off', 'In Collections']
data['AccountStatus'] = [
    add_missing(random_case(random.choice(statuses), 0.1), 0.06)
    for _ in range(n)
]

# Interest Rate (for loans/credit cards)
interest_rates = []
for _ in range(n):
    rate = random.uniform(3, 29.99)
    if random.random() < 0.3:
        rate = f"{rate:.2f}%"
    elif random.random() < 0.15:
        rate = str(round(rate, 2))
    else:
        rate = round(rate, 2)
    interest_rates.append(add_missing(rate, 0.07))

data['InterestRate'] = interest_rates

# Credit Score (target variable)
# Ranges: 300-579 (Poor), 580-669 (Fair), 670-739 (Good), 740-799 (Very Good), 800-850 (Excellent)
credit_scores = []
for i in range(n):
    score = 650  # base

    # Credit history length
    try:
        ch_val = data['CreditHistoryLength_Months'][i]
        credit_hist = int(ch_val) if not pd.isna(ch_val) else 60
        score += min(credit_hist / 12, 50)  # up to +50
    except Exception:
        pass

    # Payment history
    try:
        ph_val = data['PaymentHistoryPct'][i]
        payment_hist = float(str(ph_val)) if not pd.isna(ph_val) else 85
        score += (payment_hist - 50) * 1.5
    except Exception:
        pass

    # Utilization
    try:
        util_val = data['CreditUtilizationRatio'][i]
        util = float(str(util_val).replace('%', ''))
        if util > 30:
            score -= (util - 30) * 0.8
    except Exception:
        pass

    # Late / missed payments
    try:
        late_val = data['NumLatePayments'][i]
        missed_val = data['NumMissedPayments'][i]
        late = int(late_val) if not pd.isna(late_val) else 0
        missed = int(missed_val) if not pd.isna(missed_val) else 0
        score -= (late * 5 + missed * 10)
    except Exception:
        pass

    # Hard inquiries
    try:
        inq_val = data['NumHardInquiries'][i]
        inq = int(inq_val) if not pd.isna(inq_val) else 0
        score -= inq * 3
    except Exception:
        pass

    # Derogatory marks
    try:
        derog_val = data['NumDerogatoryMarks'][i]
        derog = int(derog_val) if not pd.isna(derog_val) else 0
        score -= derog * 40
    except Exception:
        pass

    # Income effect (slight)
    try:
        inc_val = data['MonthlyIncome'][i]
        inc = float(str(inc_val).replace('$', '').replace(',', ''))
        if inc < 2000:
            score -= 20
        elif inc > 12000:
            score += 10
    except Exception:
        pass

    # Debt-to-income effect (high DTI is bad)
    try:
        dti_val = data['DebtToIncomeRatio'][i]
        dti_num = float(str(dti_val))
        if dti_num > 40:
            score -= (dti_num - 40) * 0.5
    except Exception:
        pass

    # Bankruptcy / Tax Liens penalties
    try:
        bval = data['Bankruptcy'][i]
        bstr = str(bval).strip().lower()
        if bstr in ['1', 'true', 'yes']:
            score -= 80
    except Exception:
        pass

    try:
        tval = data['TaxLiens'][i]
        tstr = str(tval).strip().lower()
        if tstr in ['1', 'true', 'yes']:
            score -= 40
    except Exception:
        pass

    # Add noise
    score += np.random.normal(0, 30)

    # Ensure in valid range
    score = max(300, min(850, score))

    # Add rare anomalies
    if random.random() < 0.01:
        score = random.choice([150, 999, -100, 950])

    # Format inconsistently
    if random.random() < 0.05:
        score = str(int(score))
    else:
        score = int(score)

    credit_scores.append(add_missing(score, 0.05))

data['CreditScore'] = credit_scores

# Credit Score Category (derived from score)
categories = []
for score in data['CreditScore']:
    try:
        s = int(str(score).replace(',', ''))
        if s < 580:
            cat = 'Poor'
        elif s < 670:
            cat = 'Fair'
        elif s < 740:
            cat = 'Good'
        elif s < 800:
            cat = 'Very Good'
        else:
            cat = 'Excellent'

        # Add inconsistencies
        cat = random_case(cat, 0.15)
        categories.append(add_missing(cat, 0.08))
    except Exception:
        categories.append(add_missing(np.nan, 0.8))

data['CreditScoreCategory'] = categories

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV (force UTF-8 to avoid encoding problems)
df.to_csv('credit_score_messy_dataset.csv', index=False, encoding='utf-8')

print("Dataset generated successfully!")
print(f"Shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
print("\nSample of messiness:")
total_missing = df.isnull().sum().sum()
total_cells = df.shape[0] * df.shape[1]
print(f"   - Missing values: {total_missing}")
print(f"   - Total cells: {total_cells}")
print(f"   - Missing percentage: {(total_missing / total_cells) * 100:.2f}%")
print("\nFile saved as: credit_score_messy_dataset.csv")
print("\nFirst few rows:")
print(df.head(3))
