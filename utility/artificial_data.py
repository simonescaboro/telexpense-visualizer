from lorem_text import lorem
import random
import calendar

accounts = [
    "Revolut",
    "HSBC",
    "Cash",
    "Savings"
]
# Expense Classes
expense_classes = [
    "Housing",
    "Utilities",
    "Transportation",
    "Food and Groceries",
    "Healthcare",
    "Entertainment",
    "Education",
    "Debt Repayment",
    "Personal Care",
    "Miscellaneous"
]

# Expense range assumptions (in dollars)
expense_ranges = {
    "Housing": (500, 2000),
    "Utilities": (50, 300),
    "Transportation": (50, 500),
    "Food and Groceries": (100, 800),
    "Healthcare": (50, 300),
    "Entertainment": (20, 200),
    "Education": (100, 1000),
    "Debt Repayment": (10, 1000),
    "Personal Care": (10, 200),
    "Miscellaneous": (10, 500)
}

# Income Classes
income_classes = [
    "Salary/Wages",
    "Freelance/Contract Work",
    "Investments",
    "Side Hustle",
    "Gifts and Bonuses"
]
# Income range assumptions (in dollars)
income_ranges = {
    "Salary/Wages": (500, 10000),
    "Freelance/Contract Work": (1000, 5000),
    "Investments": (100, 1000),
    "Side Hustle": (90, 2000),
    "Gifts and Bonuses": (50, 500)
}


def generate_description():
    return lorem.sentence()

def generate_random_date(year, month):
    # Get the number of days in the given month
    _, days_in_month = calendar.monthrange(year, month)

    # Generate a random day within the month
    day = random.randint(1, days_in_month)

    # Format the date as 'YYYY-MM-DD'
    date_string = f"{year}-{month:02d}-{day:02d}"

    return date_string

def generate_income(category): 
    return round(random.uniform(*income_ranges[category]),2)

def generate_expense(category): 
    return round(-random.uniform(*expense_ranges[category]),2)

def generate_entry(month,year,typ):
    if typ == "inc":
        category = random.choice(income_classes)
        return category, generate_income(category), generate_description(), generate_random_date(year, month), random.choice(accounts)
    else:
        category = random.choice(expense_classes)
        return category, generate_expense(category), generate_description(), generate_random_date(year, month), random.choice(accounts)

def generate_month(month,year):
    entries = []
    for i in range(random.randint(2,10)):
        entries.append(generate_entry(month, year, "inc"))
    for i in range(random.randint(20,30)):
        entries.append(generate_entry(month, year, "exp"))

    return entries

def generate():
    entries = []
    for year in range(2019,2024):
        for month in range(1,13):
            entries.extend(generate_month(month, year))
    entries.extend(generate_month(1, 2024))


    import pandas as pd
    entries = {k:l for l,k in zip(tuple(zip(*entries)),["Category","Amount","Description","Date","Account"])}
    df = pd.DataFrame(entries)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Date"] = pd.to_datetime(df["Date"].dt.strftime('%m-%d-%Y'))
    df["In main currency"] = df["Amount"]
    print(df.groupby(by=[df.Date.dt.year, df.Date.dt.month]).Category.count())
    df = df[["Date","Description","Category","Amount","Account","In main currency"]]
    df.to_excel("prova.xlsx")


generate()
for cl in income_classes:
    print(cl)
