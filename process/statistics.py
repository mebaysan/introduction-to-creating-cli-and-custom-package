from baysan_data_shortcuts.marketing.crm import get_rawdata_to_bgnbd_gamma
import click


def get_statistics(base_path, raw_path, analyze_date):
    click.echo(click.style("{} file is reading..".format(raw_path), fg="blue"))
    click.echo(
        click.style(
            "Statistical models (BG-NBD & Gamma-Gamma) are applying on {} ...".format(
                raw_path
            ),
            fg="blue",
        )
    )
    try:
        statistics_path = base_path + "bgnbd.pickle"
        get_rawdata_to_bgnbd_gamma(raw_path, [], analyze_date, statistics_path)
        click.echo(
            click.style(
                "Statistical models are applied and the resulf file written under {}".format(
                    statistics_path
                ),
                fg="green",
            )
        )
    except Exception as e:
        click.echo(
            click.style(
                "An error occured while applying statistical models!!!: Error:\n{}".format(
                    e
                ),
                fg="red",
            )
        )
