from gspread.utils import extract_id_from_url
import streamlit as st
import pandas as pd
from pandas import DataFrame, Series
from typing import Optional, Sequence
import os
import gspread
import urllib
from pathlib import Path
from utils import (
        _r,
        delta,
        get_icon,
        get_curr_month_year,
        get_prev_month_year
        )

from typing import  Tuple

def get_placeholder() -> str:
    path = Path("sheet.txt")
    if path.exists():
        with path.open() as fp:
            url = fp.read()
            st.session_state.url = url
            return url


def set_placeholder(url: str):
    with open("sheet.txt", "w") as fp:
        fp.write(url)


def load_url(local_cache: bool = True):
    st.write("Insert the URL of your Telexpense Sheet 💸")

    field, button = st.columns([0.8,0.2])
    with field:
        if local_cache:
            placeholder = get_placeholder() 
        else:
            placeholder = None
        url = st.text_input("Sheet URL", placeholder, label_visibility='collapsed')

    with button:
        if st.button("Start"):
            st.session_state.url = url
            if local_cache:
                set_placeholder(url)


def error_page(error: str):
    st.error(f"""
             ⚠️ *Error*   {error}
             """)
    st.subheader("A little tutorial for you 🫡")
    st.image('guide.gif', caption='Guide to use the visualizer')


def load_dataframe(url: str) -> DataFrame:
    sheet_name = "Transactions"
    try:
        sheet_id = extract_id_from_url(url)
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        df = pd.read_csv(url) 
        return df
    except urllib.error.HTTPError:
        error_page("Check if the sheet is **shared** or if the URL is correct")
    except gspread.exceptions.NoValidUrlKeyFound:
        error_page("Something wrong with the URL, check it!")
    except:
        error_page("General error")
    return None


def header(title: str):
    st.header(title, divider="rainbow")


def load_data(df: DataFrame) -> DataFrame:
    df = df[["Date","Category","Amount","Account","Description"]]

    # lower all the columns' names
    df = df.rename(columns={col:col.lower() for col in df.columns})

    df = df.query("category != 'Transfer'")
    # replace possible commas in the numbers, so can be correcly casted to numerical
    df["amount"] = df["amount"].apply(lambda value : value.replace(",",".") if isinstance(value, str) else value)

    df["date"] = pd.to_datetime(df["date"], dayfirst=True)
    df["amount"] = pd.to_numeric(df["amount"])

    # flag usefull for code readability
    df["expense"] = df["amount"].apply(lambda value : value < 0)

    df["amount"] = df["amount"].apply(lambda amount : abs(amount))

    # remove transfer entries, are not relevant for the analysis
    return df



def get_trend(
        df: DataFrame,
        temporal_period: Sequence[int],
        categories: Series
        ) -> DataFrame:
    df = df.groupby(by=[temporal_period, categories]).amount.sum().reset_index(name ='amount')
    return df


def plot_trend_line(df: DataFrame, key: str):
    import plotly.express as px

    on = st.toggle('Log scale',key=f"plot_{key}")
    fig = px.line(df, x="date", y="amount", color='category', markers=True, log_x=False, log_y=on)

    st.plotly_chart(fig, use_container_width=True)


def plot_trend_bars(df: DataFrame):
    import plotly.graph_objects as go

    df = df.groupby("category").amount.sum().reset_index(name="amount")
    values = list(zip(df["amount"].values,df["category"].values))
    values = sorted(values, reverse=False)

    fig = go.Figure(go.Bar(
                x=[v for v,_ in values],
                y=[k for _,k in values],
                orientation='h',
                marker=dict(
                    color="rgba(90,10,170,0.4)",
                    line=dict(
                        color="rgba(90,10,170,1.0)",
                        width=1),
                ),
                ))

    st.plotly_chart(fig, use_container_width=True)



def category_inspector_aux(df: DataFrame, title: str):

    st.subheader(title.capitalize())

    selectbox = lambda label, values : st.selectbox(
            label,
            ["All"] + values,
            key=f"selectbox_{label}_{title}")

    select_category = selectbox("Category", list(df.category.unique()))

    col1, col2 = st.columns(2)
    with col1:
        select_month = selectbox("Month", list(df.date.dt.month.unique()))
    with col2:
        select_year = selectbox("Year", list(df.date.dt.year.unique()))

    df_tmp = df
    if select_category != "All":
        df_tmp = df[df.category == select_category]
    if select_year != "All":
        df_tmp = df[df.date.dt.year == select_year]
    if select_month != "All":
        df_tmp = df[df.date.dt.month == select_month]

    df_tmp = df_tmp[["date","category","amount","description"]]
    
    plot_dataframe(df_tmp.sort_values(by=["amount"], ascending=False))


def plot_dataframe(df: DataFrame):
    st.dataframe(
            df,
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


def category_inspector_section(df: DataFrame):
    header("Category inspector 🕵")

    df_incomes = df[~df.expense]
    df_expenses = df[df.expense]

    category_inspector_aux(df_incomes, "incomes")
    category_inspector_aux(df_expenses, "expenses")


def select_month_year(
        df: DataFrame,
        month: Optional[int] = None,
        year: Optional[int] = None,
        same_month: bool = True,
        same_year: bool = True,
        ) -> DataFrame:
    
    if month:
        month_op = "==" if same_month else "!="
        df = df.query(f"date.dt.month {month_op} {month}")

    if year:
        year_op = "==" if same_year else "!="
        df = df.query(f"date.dt.year {year_op} {year}")

    return df



def get_sum(df: DataFrame) -> float:
    return _r(df.amount.sum())

def inc_exp(
        df_incomes: DataFrame,
        df_expenses: DataFrame,
        month: Optional[int] = None,
        year: Optional[int] = None,
        same_month: bool = True,
        same_year: bool = True,
        ) -> Tuple[DataFrame, DataFrame]:
    inc = select_month_year(df_incomes, month, year, same_month, same_year)
    exp = select_month_year(df_expenses, month, year, same_month, same_year)
    return inc, exp


def inc_exp_sum(
        df_incomes: DataFrame,
        df_expenses: DataFrame,
        month: Optional[int] = None,
        year: Optional[int] = None,
        same_month: bool = True,
        same_year: bool = True,
        ) -> Tuple[float,float]:
    inc, exp = inc_exp(df_incomes, df_expenses, month, year, same_month, same_year)
    inc =  get_sum(inc)
    exp =  get_sum(exp)
    return inc, exp


def month_overview(
        df_incomes: DataFrame,
        df_expenses: DataFrame
        ):

    header("Month Overview")

    options = {k:option for k,option in zip(["month", "monthavg" ,"year"],["Previous month", "Average previous months (same year)" ,"Previous year"])}
    respect_to = st.selectbox(
            "Compare to",
            options.values(), 
            key="respect_to")

    curr_month, curr_year = get_curr_month_year() 
    prev_month, prev_year = get_prev_month_year() 

    curr_incomes, curr_expenses = inc_exp_sum(df_incomes, df_expenses, curr_month, curr_year)

    if respect_to == options["month"]:
        prev_year = prev_year if curr_month == 1 else curr_year
        prev_incomes, prev_expenses = inc_exp_sum(df_incomes, df_expenses, prev_month, prev_year)

    elif respect_to == options["year"]:
        prev_incomes, prev_expenses = inc_exp_sum(df_incomes, df_expenses, curr_month, prev_year)

    else:# respect_to == options["monthavg"]:
        df_prev_incomes, df_prev_expenses = inc_exp(df_incomes, df_expenses, curr_month, curr_year, False)

        prev_incomes = prev_expenses = 0.0
        if not df_prev_incomes.empty:
            prev_incomes = _r(df_prev_incomes.groupby(by=[df_prev_incomes.date.dt.month]).amount.sum().values.mean())
        if not df_prev_expenses.empty:
            prev_expenses = _r(df_prev_expenses.groupby(by=[df_prev_expenses.date.dt.month]).amount.sum().values.mean())

    delta_incomes = delta(curr_incomes,prev_incomes)
    delta_expenses = delta(curr_expenses, prev_expenses)

    _, exp, inc, _= st.columns(4)

    with exp:
        st.metric(
                label="**:red[Expenses]**",
                value=curr_expenses,
                delta=delta_expenses,
                delta_color="inverse")
    with inc:
        st.metric(
                label="**:green[Incomes]**",
                value=curr_incomes,
                delta=delta_incomes)

    plot_table("incomes", select_month_year(df_incomes, curr_month, curr_year))
    plot_table("expenses", select_month_year(df_expenses, curr_month, curr_year))


def year_overview(
        df_incomes: DataFrame,
        df_expenses: DataFrame,
        ):

    import plotly.express as px
    
    header("Year Overview")

    curr_month, curr_year = get_curr_month_year()
    _, prev_year = get_prev_month_year()

    on = st.toggle('Include current month',key="include_curr_month")

    if on:
        gbl_curr_incomes, gbl_curr_expenses = inc_exp_sum(df_incomes, df_expenses, year=curr_year)
    else:
        gbl_curr_incomes, gbl_curr_expenses = inc_exp_sum(df_incomes, df_expenses,curr_month, curr_year, False)

    gbl_prev_incomes, gbl_prev_expenses = inc_exp_sum(df_incomes, df_expenses, year=prev_year)


    gbl_delta_incomes = delta(gbl_curr_incomes, gbl_prev_incomes)
    gbl_delta_expenses = delta(gbl_curr_expenses, gbl_prev_expenses)
 
    _, exp, inc, _= st.columns(4)

    with exp:
        st.metric(
                label="**:red[Expenses]**",
                value=gbl_curr_expenses,
                delta=gbl_delta_expenses,
                delta_color="inverse")
    with inc:
        st.metric(
                label="**:green[Incomes]**",
                value=gbl_curr_incomes,
                delta=gbl_delta_incomes)

    df = pd.concat([df_incomes,df_expenses])
    df_tmp = df[df.date.dt.year == curr_year]\
            .groupby(by=[df.date.dt.month, df.expense])\
            .amount.sum()\
            .reset_index(name ='amount')

    df_tmp["expense"] = df_tmp["expense"].apply(lambda v : "expense" if v else "income")
    
    df_tmp = df_tmp.groupby(["date","expense"]).amount.sum().reset_index(name="amount")


    on = st.toggle('Log scale',key=f"plot_summary_year")
    fig = px.line(df_tmp, x="date", y="amount", color="expense", color_discrete_map={
                 "expense": "red",
                 "income": "green"
             }, markers=True, log_x=False, log_y=on, title="Year's trend")

    st.plotly_chart(fig, use_container_width=True)


def overview_section(df: DataFrame):


    df_incomes = df[~df.expense]
    df_expenses = df[df.expense]

    with st.container(border=True):
        month_overview(df_incomes, df_expenses)

    with st.container(border=True):
        year_overview(df_incomes, df_expenses)



    
def plot_table(title: str, df: DataFrame):
    st.write(f"**Top 5 {title}** {get_icon(title)}")

    curr_month, curr_year = get_curr_month_year()

    df_tmp = df[
            (df.date.dt.month == curr_month) &
            (df.date.dt.year == curr_year)][["date","category","amount","description"]]

    plot_dataframe(df_tmp.sort_values(by=["amount"], ascending=False).head(5))


def incomes_expenses_section(df: DataFrame, title: str):
    is_expenses = title == "expenses"

    df = df.query(f"expense == {is_expenses}")

    header(f"{title.capitalize()} {get_icon(title)}")

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            genre = st.radio("Plot by", ["Year", "Month"], key=f"sort_{title}", horizontal=True)
        with col2:
            option = st.selectbox(
                f'Select {genre}',
                df.date.dt.year.unique() if genre == "Year" else df.date.dt.month.unique(),
                key=f"selectbox_{title}")

    multiselect = lambda t : st.multiselect(
            f"Don't consider **{t}**",
            list(df[t].unique()),
            key=f"dont_{str(is_expenses)}_{t}"
            )

    categories_col, accounts_col = st.columns(2)
    with categories_col:
        dont_consider_categories = multiselect("category")
    with accounts_col:
        dont_consider_accounts = multiselect("account")

    time_period_condition = df.date.dt.year if genre == "Year" else df.date.dt.month

    df_tmp = df[
            (time_period_condition == option) & 
            ~df.account.isin(dont_consider_accounts) & 
            ~df.category.isin(dont_consider_categories)]

    temporal_period = df_tmp.date.dt.year if genre == "Month" else df_tmp.date.dt.month

    df_tmp = get_trend(df=df_tmp, temporal_period=temporal_period, categories=df.category)

    plot_trend_line(df_tmp, title)
    plot_trend_bars(df_tmp)


def body():
    with st.spinner('Downloading data...'):
        df = load_dataframe(st.session_state.url)
    if df is not None:
        df = load_data(df)
        overview_section(df)
        with st.container(border=True):
            incomes_expenses_section(df, "expenses")
        with st.container(border=True):
            incomes_expenses_section(df, "incomes")
        with st.container(border=True):
            category_inspector_section(df)


def page_config():
    st.set_page_config(
        page_title="Telexpense Visualizer",
        page_icon="💰"
        )

    st.title("Telexpense Visualizer 📊")
