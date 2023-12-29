from gspread.utils import extract_id_from_url
import streamlit as st
import pandas as pd
from typing import Any
from datetime import datetime
import os
import urllib
import gspread

def load_url() -> str:
    # url = "https://docs.google.com/spreadsheets/d/1RTNrGFkjZS5-FBC5KvpXsEQVkAEYF9tLcVpztuCbliw/edit?usp=sharing"
    with open("sheet_info.txt","r") as fp:
        url = fp.read()
    return url

def load_dataframe(url: str) -> pd.DataFrame:
    print(url)
    sheet_name = "Transactions"
    sheet_id = extract_id_from_url(url)
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(url) 
    return df


def load_data(url: str) -> pd.DataFrame:
    df = load_dataframe(url)
    df = df[["Date","Category","Amount","Account","Description"]]

    # lower all the columns' names
    df = df.rename(columns={col:col.lower() for col in df.columns})

    # replace possible commas in the numbers, so can be correcly casted to numerical
    df["amount"] = df["amount"].apply(lambda value : value.replace(",",".") if isinstance(value, str) else value)

    df["date"] = pd.to_datetime(df["date"], infer_datetime_format=True)
    df["amount"] = pd.to_numeric(df["amount"])

    # flag usefull for code readability
    df["expense"] = df["amount"].apply(lambda value : value < 0)

    def normalize_amount(row: pd.Series):
        row.amount = -row.amount if row.expense else row.amount
        return row

    df = df.apply(lambda row : normalize_amount(row), axis=1)

    # remove transfer entries, are not relevant for the analysis
    df = df.query("category != 'Transfer'")
    return df



def get_trend(df: pd.DataFrame, expense: bool, temporal_period: Any, categories: pd.Series):
    df = df.query(f"expense == {expense}")
    df = df.groupby(by=[temporal_period,categories]).amount.sum().reset_index(name ='amount')
    return df

def plot_trend(df: pd.DataFrame,key):
    import plotly.express as px


    on = st.toggle('Log scale',key=f"plot_{key}")
    fig = px.line(df, x="date", y="amount", color='category', markers=True, log_x=False, log_y=on)

    st.plotly_chart(fig, use_container_width=True)



def overview(df: pd.DataFrame):
    st.header("Overview 🔭")

    st.subheader("Month")

    respect_to = st.radio("Compare to", ["prev month", "Avg prev months (same year)" ,"Prev year"], key="respect_to", horizontal=True)

    current_month = datetime.now().month
    current_year = datetime.now().year

    if current_month == 1:
        prev_month = 12
        prev_year = current_year - 1
    else:
        prev_month = current_month - 1 
        prev_year = current_year if respect_to != "Prev year" else current_year - 1

    incomes = df[~df.expense]
    expenses = df[df.expense]

    current_incomes = incomes.query(f"date.dt.month == {current_month} and date.dt.year == {current_year}").amount.sum()
    current_expenses = expenses.query(f"date.dt.month == {current_month} and date.dt.year == {current_year}").amount.sum()

    if respect_to == "prev month" or respect_to == "Prev year":
        prev_incomes = incomes.query(f"date.dt.month == {prev_month} and date.dt.year == {prev_year}").amount.sum()
        prev_expenses = expenses.query(f"date.dt.month == {prev_month} and date.dt.year == {prev_year}").amount.sum()
    else:
        prev_incomes = incomes.query(f"date.dt.month != {current_month} and date.dt.year == {current_year}")
        prev_expenses = expenses.query(f"date.dt.month != {current_month} and date.dt.year == {current_year}")
        prev_incomes = prev_incomes.groupby(by=[prev_incomes.date.dt.month]).amount.sum().values.mean()
        prev_expenses = prev_expenses.groupby(by=[prev_expenses.date.dt.month]).amount.sum().values.mean()

    current_incomes = round(current_incomes,2)
    prev_incomes = round(prev_incomes,2)
    current_expenses = round(current_expenses,2)
    prev_expenses = round(prev_expenses,2)

    delta_incomes = current_incomes - prev_incomes
    delta_expenses = current_expenses - prev_expenses 

    delta_incomes = round(delta_incomes,2)
    delta_expenses = round(delta_expenses,2)

    _, exp, inc, _= st.columns(4)

    with exp:
        st.metric(label="**:red[Expenses]**", value=current_expenses, delta=delta_expenses, delta_color="inverse")
    with inc:
        st.metric(label="**:green[Incomes]**", value=current_incomes, delta=delta_incomes)

    st.subheader("Year")

    on = st.toggle('Include current month',key="include_current_month")

    if on:
        global_current_incomes = incomes.query(f"date.dt.year == {current_year}").amount.sum()
        global_current_expenses = expenses.query(f"date.dt.year == {current_year}").amount.sum()
    else:
        global_current_incomes = incomes.query(f"date.dt.year == {current_year} and date.dt.month != {current_month}").amount.sum()
        global_current_expenses = expenses.query(f"date.dt.year == {current_year} and date.dt.month != {current_month}").amount.sum()

    global_prev_incomes = incomes.query(f"date.dt.year == {current_year-1}").amount.sum()
    global_prev_expenses = expenses.query(f"date.dt.year == {current_year-1}").amount.sum()

    global_delta_incomes = global_current_incomes - global_prev_incomes
    global_delta_expenses = global_current_expenses - global_prev_expenses
 

    global_current_incomes = round(global_current_incomes,2)
    global_prev_incomes = round(global_prev_incomes,2)
    global_current_expenses = round(global_current_expenses,2)
    global_prev_expenses = round(global_prev_expenses,2)
    global_delta_incomes = round(global_delta_incomes,2)
    global_delta_expenses = round(global_delta_expenses,2)

    _, exp, inc, _= st.columns(4)

    with exp:
        st.metric(label="**:red[Expenses]**", value=global_current_expenses, delta=global_delta_expenses, delta_color="inverse")
    with inc:
        st.metric(label="**:green[Incomes]**", value=global_current_incomes, delta=global_delta_incomes)

    df_tmp = df[df.date.dt.year == current_year]\
            .groupby(by=[df.date.dt.month, df.expense])\
            .amount.sum()\
            .reset_index(name ='amount')

    df_tmp["expense"] = df_tmp["expense"].apply(lambda v : "expense" if v else "income")
    
    df_tmp = df_tmp.groupby(["date","expense"]).amount.sum().reset_index(name="amount")

    import plotly.express as px

    on = st.toggle('Log scale',key=f"plot_summary_year")
    fig = px.line(df_tmp, x="date", y="amount", color="expense", color_discrete_map={
                 "expense": "red",
                 "income": "green"
             }, markers=True, log_x=False, log_y=on, title="Year's trend")
    # fig.show()
    st.plotly_chart(fig, use_container_width=True)


def get_icon(title: str):
    return "📉" if title == "expenses" else "📈"


def incomes_expenses_section(title: str):
    is_expenses = title == "expenses"

    st.header(f"{title.capitalize()} {get_icon(title)}")

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            genre = st.radio("Plot by", ["Year", "Month"], key=f"sort_{title}", horizontal=True)
        with col2:
            option = st.selectbox(
                f'Select {genre}',
                df.date.dt.year.unique() if genre == "Year" else df.date.dt.month.unique(),
                key=f"selectbox_{title}")

    categories_col, accounts_col = st.columns(2)
    with categories_col:
        dont_consider_categories = st.multiselect(
                "Don't consider **categories**:",
                list(df[df.expense == is_expenses].category.unique()),
                key=f"dont_categories_{title}")
    with accounts_col:
        dont_consider_accounts = st.multiselect(
                "Don't consider **accounts**:",
                list(df[df.expense == is_expenses].account.unique()),
                key=f"dont_accounts_{title}")

    time_period_condition = df.date.dt.year if genre == "Year" else df.date.dt.month

    df_tmp = df[
            (time_period_condition == option) & 
            ~df.account.isin(dont_consider_accounts) & 
            ~df.category.isin(dont_consider_categories)]

    temporal_period = df_tmp.date.dt.year if genre == "Month" else df_tmp.date.dt.month

    df_tmp = get_trend(df=df, expense=is_expenses, temporal_period=temporal_period, categories=df.category)

    plot_trend(df_tmp, title)

    st.line_chart(df_tmp, x="date", y="amount", color='category')


    st.subheader(f"Top 5 {title} of the month")

    df_tmp = df[
            (df.expense == is_expenses) &
            (df.date.dt.month == datetime.now().month) &
            (df.date.dt.year == datetime.now().year)][["date","category","amount","description"]]


    st.dataframe(
            df_tmp.sort_values(by=["amount"], ascending=False).head(5),
            column_config = {
                "date": st.column_config.DatetimeColumn(
                    "Date",
                    format="DD MMM YYYY"
                    ),
                "category": "Category",
                "amount": st.column_config.NumberColumn(
                    "Amount",
                    format="🫰 %.2f"
                    ),
                "description": "Description"
                },
            hide_index=True,
            use_container_width=True)




if __name__ == "__main__":
    st.set_page_config(
        page_title="Telexpense Visualizer",
        page_icon="💰"
        )

    st.title("Telexpense Visualizer 📊")
    # st.balloons()

# f 'url' not in st.session_state:
#     st.session_state['key'] = 'value'
    # if 'url' in st.session_state:
    if os.path.exists("sheet_info.txt"):
        with st.spinner('Downloading data...'):
            df = load_data(load_url())

        overview(df)

        st.divider()
        incomes_expenses_section("expenses")
        st.divider()
        incomes_expenses_section("incomes")
        st.divider()

    else:
        st.write("Missing ")
        url = st.text_input("Sheet URL")
        if st.button("Start"):
            # --| url sbagliato
            # --> url invalido
            try:
                print(url)
                _ = load_dataframe(url)
                st.session_state['url'] = url 
                    # with open("sheet_info.txt","w") as fp:
                    #     fp.write(url)
                st.rerun()
            except urllib.error.HTTPError:
                st.error("Error! Check if the sheet is shared and the url is correcte or if the URL is correct")
                st.subheader("A little guide for you 🫡")
                st.image('guide.gif', caption='Guide to use the visualizer')
            except gspread.exceptions.NoValidUrlKeyFound:
                st.error("Error! Something wrong with the URL, check it!")
                st.subheader("A little guide for you 🫡")
                st.image('guide.gif', caption='Guide to use the visualizer')
            except:
                st.error("Error! General error")





