import random
import json
import os
import csv
from faker import Faker

fake = Faker()

# -----------------------------
# Create folders
# -----------------------------

os.makedirs("synthetic_data/policies", exist_ok=True)
os.makedirs("synthetic_data/regulations", exist_ok=True)

# -----------------------------
# Loan policies
# -----------------------------

loan_policy = """
Personal Loan Policy

Minimum Credit Score: 700
Minimum Monthly Income: 40000
Maximum Loan Amount: 1500000

Eligibility Rules:

1. Customer must be between age 21 and 60
2. Debt to Income ratio must not exceed 50%
3. Customer must have stable employment
4. Credit history should not contain major defaults
5. KYC verification must be completed
"""

risk_policy = """
Loan Risk Assessment Policy

Risk Categories

Low Risk:
Credit Score above 750
Stable income
Low existing liabilities

Medium Risk:
Credit Score between 680 and 750
Moderate existing EMIs

High Risk:
Credit Score below 680
High debt-to-income ratio
History of late payments
"""

regulatory_guidelines = """
Responsible Lending Guidelines

1. Financial institutions must ensure affordability checks
2. Debt-to-income ratio should remain below 50%
3. Transparent explanation must be provided for loan rejection
4. Customers must be informed of their credit evaluation
5. All lending must comply with regulatory standards
"""

# Save policies
with open("synthetic_data/policies/loan_policy.txt","w") as f:
    f.write(loan_policy)

with open("synthetic_data/policies/risk_policy.txt","w") as f:
    f.write(risk_policy)

with open("synthetic_data/regulations/lending_guidelines.txt","w") as f:
    f.write(regulatory_guidelines)

# -----------------------------
# Synthetic Loan Cases
# -----------------------------

credit_scores = [620,650,680,700,720,750,780]
loan_amounts = [200000,400000,600000,800000,1000000,1200000]
incomes = [30000,40000,50000,60000,80000,100000,120000]

loan_cases = []
loan_cases_text = []

for i in range(10000):

    income = random.choice(incomes)
    credit = random.choice(credit_scores)
    loan = random.choice(loan_amounts)
    emi = random.randint(5000,25000)

    debt_ratio = emi / income

    decision = "APPROVED"
    reason = "Customer meets eligibility requirements."

    if credit < 680:
        decision = "REJECTED"
        reason = "Credit score below acceptable threshold."

    elif debt_ratio > 0.5:
        decision = "REJECTED"
        reason = "Debt-to-income ratio too high."

    elif income < 40000:
        decision = "REJECTED"
        reason = "Income below minimum eligibility requirement."

    case = {
        "case_id": f"LN{i+1000}",
        "customer_name": fake.name(),
        "age": random.randint(22,55),
        "monthly_income": income,
        "credit_score": credit,
        "existing_emi": emi,
        "loan_requested": loan,
        "decision": decision,
        "reason": reason
    }

    loan_cases.append(case)

    # text format useful for RAG
    text_case = f"""
Loan Case ID: LN{i+1000}

Customer Name: {case['customer_name']}
Age: {case['age']}

Monthly Income: {income}
Credit Score: {credit}
Existing EMI: {emi}

Loan Requested: {loan}

Decision: {decision}

Reason:
{reason}
"""

    loan_cases_text.append(text_case)


# -----------------------------
# Save CSV file
# -----------------------------

csv_file_path = "synthetic_data/loan_cases.csv"

with open(csv_file_path, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=loan_cases[0].keys())

    writer.writeheader()  # write column names
    writer.writerows(loan_cases)  # write data

print("CSV file generated successfully!")

# -----------------------------
# Save files
# -----------------------------

with open("synthetic_data/loan_cases.json","w") as f:
    json.dump(loan_cases,f,indent=4)

with open("synthetic_data/loan_cases_text.txt","w") as f:
    f.write("\n\n".join(loan_cases_text))

print("Synthetic dataset generated successfully!")
print("10,000 loan cases created")
print("Policies and regulations added")