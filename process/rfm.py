from baysan_data_shortcuts.marketing.crm import get_rfm_from_customers
import pandas as pd
import click


def get_rfm(base_path, raw_path, analyze_date):
    click.echo(click.style("{} file is reading..".format(raw_path), fg="blue"))
    df = pd.read_pickle(raw_path)
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], format="%Y-%m-%d")
    click.echo(click.style("Applying RFM on {} file...".format(raw_path), fg="blue"))
    try:
        rfm = get_rfm_from_customers(
            df,
            "customer_id",
            "transaction_date",
            "customer_id",
            "customer_tutar",
            analyze_date,
        )
        rfm_path = base_path + "rfm.pickle"
        rfm.to_pickle(rfm_path)

        click.echo(
            click.style(
                "RFM process is done and the result file written under {}".format(
                    rfm_path
                ),
                fg="green",
            )
        )
    except Exception as e:
        click.echo(
            click.style(
                "An error occured while applying RFM!!!!: Error:\n{}".format(e),
                fg="red",
            )
        )
