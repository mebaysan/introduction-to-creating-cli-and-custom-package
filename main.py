"""
        A CLI to segment customers
"""
import click
from datetime import datetime
from process.rfm import get_rfm
from process.statistics import get_statistics


@click.command()
@click.option(
    "--start_date",
    prompt="Analyze start date",
    help="Start date to fetch data: 1 March 2022 -> '20220301'",
)
@click.option(
    "--end_date",
    prompt="Analyze end date",
    help="End date to fetch data: 31 January 2023 -> '20230131'",
)
@click.option(
    "--rfm_date",
    prompt="RFM analyze date",
    help="Analyze date for RFM analysis: 31 January 2023 -> '2023-01-31'",
)
@click.option(
    "--statistics_date",
    prompt="Statistical analyze date",
    help="Analyze date for statistical analysis (BG-NBD & Gamma-Gamma): 31 January 2023 -> '2023-01-31'",
)
def main(
    start_date="202180101",
    end_date="20221231",
    rfm_date="2022-01-01",
    statistics_date="2022-01-01",
):
    """
    An Example CLI
    """
    BASE_PATH = "./data/"
    RAW_PATH = BASE_PATH + "raw.pickle"
    QUERY = "exec Proc '',''".format(start_date, end_date)
    rfm_date = datetime.strptime(rfm_date, "%Y-%m-%d").date()
    get_rfm(BASE_PATH, RAW_PATH, rfm_date)
    get_statistics(BASE_PATH, RAW_PATH, statistics_date)


if __name__ == "__main__":
    main()
