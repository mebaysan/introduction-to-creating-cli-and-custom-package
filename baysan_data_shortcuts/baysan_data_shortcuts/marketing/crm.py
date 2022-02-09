"""A module for CRM analytics

RFM scores, BG-NBD and Gamma-Gamma functions
"""
import pandas as pd
from datetime import datetime

# pip install lifetimes
from lifetimes import BetaGeoFitter, GammaGammaFitter

# pip install sklearn
from sklearn.preprocessing import MinMaxScaler


def get_rfm_from_customers(
    df,
    customer_id_col,
    transaction_date_col,
    transaction_id_col,
    transaction_amount_col,
    today=datetime.now().date(),
):
    """Creates RFM applied dataset

    Args:
        df (DataFrame): Dataframe
        customer_id_col (str): The column name which holds customer id
        transaction_date_col (str): The column name which holds transaction dates
        transaction_id_col (str): The column name which holds transaction id
        transaction_amount_col (str): The column name which holds transaction amount
        today (Datetime, optional): Datetime object for analyzing date. Defaults to datetime.now().date().

    Returns:
        DataFrame: RFM applied dataframe
    """
    rfm = df.groupby(customer_id_col, as_index=False).agg(
        {
            # recency
            transaction_date_col: lambda x: (today - x.dt.date.max()).days,
            transaction_id_col: lambda x: x.nunique(),  # frequency
            transaction_amount_col: lambda x: x.sum(),  # monetary
        }
    )
    rfm.columns = [customer_id_col, "recency", "frequency", "monetary"]

    rfm = rfm[rfm["monetary"] > 0]

    rfm.loc[:, "recency_score"] = pd.qcut(rfm["recency"], 5, labels=[5, 4, 3, 2, 1])

    rfm.loc[:, "frequency_score"] = pd.qcut(
        rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]
    )

    rfm.loc[:, "monetary_score"] = pd.qcut(rfm["monetary"], 5, labels=[1, 2, 3, 4, 5])

    rfm.loc[:, "RFM_SCORE"] = rfm["recency_score"].astype(str) + rfm[
        "frequency_score"
    ].astype(str)

    seg_map = {
        r"[1-2][1-2]": "hibernating",
        r"[1-2][3-4]": "at_Risk",
        r"[1-2]5": "cant_loose",
        r"3[1-2]": "about_to_sleep",
        r"33": "need_attention",
        r"[3-4][4-5]": "loyal_customers",
        r"41": "promising",
        r"51": "new_customers",
        r"[4-5][2-3]": "potential_loyalists",
        r"5[4-5]": "champions",
    }

    rfm["segment"] = rfm["RFM_SCORE"].replace(seg_map, regex=True)

    return rfm


def get_rawdata_to_bgnbd_gamma(
    data_path,
    filter_list,
    analyze_date,
    write_path=None,
    customer_id_col="customer_id",
    transaction_date_col="transaction_date",
    transaction_id_col="transaction_id",
    transaction_amount_col="transaction_amount",
    round_step=10,
    month_scopes=[1, 3, 6, 12],
):
    """Writes the dataset which the models are applied

    Args:
        data_path (str): The raw data path. The file has to be pickle
        filter_list (list): The filter list
        analyze_date (str): The analyze date as string
        write_path (str): Path for writing the dataset to which the models are applied. The file has to be pickle (EX: applied.pickle) If write_path is None, the function returns the DataFrame created
        round_step (int, optional): The decimal count for rounding the model results'. Defaults to 10.
        customer_id_col (str, optional): The column name which holds customer id. Default: 'customer_id'
        transaction_date_col (str, optional): The column name which holds transaction date. It has to be '%Y-%m-%d'. Default: 'transaction_date'
        transaction_id_col (str, optional): The column name which holds transaction id. Default: 'transaction_id'
        transaction_amount_col (str, optional): The column name which holds transaction amount. Default: 'transaction_amount'
        month_scopes (list, optional): The month scopes to forecast them

    Example:
        get_rawdata_to_bgnbd_gamma(
            'raw_data.pickle',
            [('category','==','Milk')],
            '2021-08-31',
            '../data/model.pickle'
            )
    """

    # * Which filters will be applied
    raw_data = pd.read_pickle(data_path)
    df = raw_data.copy()
    df = df.dropna()
    if len(filter_list) >= 1:
        for fltr in filter_list:
            df = df.query(f"{fltr[0]} {fltr[1]} '{fltr[2]}'")

    # * filtered customers
    filtered_customers = df[customer_id_col]

    # * targeted filters applied
    df = raw_data[raw_data[customer_id_col].isin(filtered_customers)]
    df[transaction_date_col] = pd.to_datetime(
        df[transaction_date_col], format="%Y-%m-%d"
    )
    df[customer_id_col] = df[customer_id_col].astype("int")

    # *  transactions before 'analyze_date'
    df = df[df[transaction_date_col] <= analyze_date].sort_values(
        transaction_date_col, ascending=False
    )

    ########################
    # BG-NBG Model Setup & Apply
    ########################
    # * Analyze date
    date_str = [int(x) for x in analyze_date.split("-")]
    today_date = datetime(date_str[0], date_str[1], date_str[2])

    # * BG-NBD Model Setup
    bgnbd_df = df.groupby(customer_id_col).agg(
        {
            transaction_date_col: [
                lambda x: (x.max() - x.min()).days,  # recency
                lambda x: (today_date - x.min()).days,  # T
            ],
            transaction_id_col: lambda x: x.nunique(),  # frequency
            transaction_amount_col: lambda x: x.sum(),  # monetary
        }
    )

    bgnbd_df.columns = bgnbd_df.columns.droplevel(0)
    bgnbd_df.columns = ["recency", "T", "frequency", "monetary"]

    # we set 'monetary' as the average earning per transaction (for gamma-gamma model)
    bgnbd_df["monetary"] = bgnbd_df["monetary"] / bgnbd_df["frequency"]
    bgnbd_df = bgnbd_df[bgnbd_df["monetary"] > 0]

    # We set recency and T as type of week for BGNBD
    bgnbd_df["recency"] = bgnbd_df["recency"] / 7
    bgnbd_df["T"] = bgnbd_df["T"] / 7

    # frequency has to be greater than 1
    bgnbd_df = bgnbd_df[(bgnbd_df["frequency"] > 1)]
    bgnbd_df = bgnbd_df[bgnbd_df["recency"] > 0]

    bgf = BetaGeoFitter(penalizer_coef=0.001)  # setup model
    bgf.fit(
        bgnbd_df["frequency"], bgnbd_df["recency"], bgnbd_df["T"]  # model parameters
    )
    for month in month_scopes:

        bgnbd_df[
            f"{month}_month_expected_number_of_transactions"
        ] = bgf.conditional_expected_number_of_purchases_up_to_time(
            4 * month, bgnbd_df["frequency"], bgnbd_df["recency"], bgnbd_df["T"]
        )  # estimated transactions in X month
        bgnbd_df[f"{month}_month_expected_number_of_transactions"] = bgnbd_df[
            f"{month}_month_expected_number_of_transactions"
        ].apply(lambda x: round(x, round_step))
    ########################
    # Gamma-Gamma Model Setup ve Apply
    ########################
    ggf = GammaGammaFitter(penalizer_coef=0.01)
    ggf.fit(bgnbd_df["frequency"], bgnbd_df["monetary"])

    bgnbd_df["beklenen_ortalama_deger"] = ggf.conditional_expected_average_profit(
        bgnbd_df["frequency"], bgnbd_df["monetary"]
    )

    ########################
    # CLV Calculating
    ########################
    for month in month_scopes:
        bgnbd_df[f"{month}_month_clv"] = ggf.customer_lifetime_value(
            bgf,
            bgnbd_df["frequency"],
            bgnbd_df["recency"],
            bgnbd_df["T"],
            bgnbd_df["monetary"],
            time=month,  # X month
            # frequency of T information
            freq="W",
            discount_rate=0.01,
        )
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaler.fit(bgnbd_df[[f"{month}_month_clv"]])
        bgnbd_df[f"{month}_month_clv"] = scaler.transform(
            bgnbd_df[[f"{month}_month_clv"]]
        )
    bgnbd_df = bgnbd_df.reset_index()
    if write_path != None:
        bgnbd_df.to_pickle(write_path)
    else:
        return bgnbd_df
