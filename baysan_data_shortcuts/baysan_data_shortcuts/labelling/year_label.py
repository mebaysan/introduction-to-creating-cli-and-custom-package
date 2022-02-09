"""
Filter out customers by using their unique years.
"""
import pandas as pd
import numpy as np
from datetime import date


def get_loyal_customers(
    df, customer_id_col, customer_year_col, target_year=date.today().year
):
    """Return customers with labelling by year

    Args:
     df (DataFrame): Dataframe that contains customer information
     customer_id_col (str): the column name that holds customer ids
     customer_year_col (str): the column name that holds year information
     target_year (int, optional): The target year for setting the analyze date. Default today's year

    Returns:
     dataframe that labeled with year range
    """

    customers = df[[customer_id_col, customer_year_col]]
    # drop rows that customer_id_col col is null
    customers = customers[~customers[customer_id_col].isna()]
    customers[customer_id_col] = customers[customer_id_col].astype(
        "int"
    )  # it can be float therefore convert to int
    customers = customers.groupby(customer_id_col, as_index=False).agg(
        {customer_year_col: "unique"}
    )

    def get_still_customers_filter(_df, col):
        return _df[col].apply(lambda x: target_year in x)

    # customers who has payment in target_year
    customers = customers[get_still_customers_filter(customers, customer_year_col)]

    customers[customer_year_col] = customers[customer_year_col].apply(
        lambda x: np.sort(x)
    )

    customers.loc[:, "UniqueYearCount"] = customers[customer_year_col].apply(
        lambda x: len(x)
    )  # how many unique years have they

    customers = customers.sort_values("UniqueYearCount", ascending=False)

    def get_regular_customers_filter(_df, col):
        return _df[col].apply(
            lambda x: [_ for _ in range(np.min(x), np.max(x) + 1, 1)]
            == list(np.sort(x))
        )

    # are their payments uninterrupted? EX: 2018,2019,2020,2021
    customers = customers[get_regular_customers_filter(customers, customer_year_col)]

    # Label customers
    customers["YearCategory"] = pd.cut(
        x=customers["UniqueYearCount"],
        bins=[0, 1, 3, customers["UniqueYearCount"].max()],
        labels=["NewCustomer", "2-3", "4+"],
    )

    return customers


def get_loyal_customers_by_merge(old_df, new_df, customer_id_col, drop_cols):
    """Merge old and new dataframes.

    Args
        old_df (DataFrame): unlabeled dataframe
        new_df (DataFrame): labeled dataframe
        customer_id_col (int): column name that holds customer ids
        drop_cols (list): list that holds columns names. We don't want to take them from new_df
    """
    new_df = new_df.copy()
    old_df = old_df.copy()
    new_df = new_df.loc[:, [col for col in new_df.columns if col not in drop_cols]]
    old_df = old_df[old_df[customer_id_col].isin(new_df[customer_id_col])]
    old_df.loc[:, customer_id_col] = old_df.loc[:, customer_id_col].astype("int")
    new_df = pd.merge(old_df, new_df, on=customer_id_col)
    return new_df
