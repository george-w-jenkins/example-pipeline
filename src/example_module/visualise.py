# general
from pathlib import Path
import logging
import ast

# project specific
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd

# custom
from src.example_module import utils


def make_plots(
    base_dir: Path,
    summary_df: pd.DataFrame,
    nims_monthly_totals: pd.DataFrame,
    config: dict,
):
    """runs the plotting subpipeline"""

    output_dir = base_dir / "output"

    plt.set_loglevel('WARNING')
    
    plot_nims_monthly(nims_monthly_totals, config, output_dir)

    plot_summary(summary_df, config, output_dir)


def plot_nims_monthly(
    nims_monthly_totals: pd.DataFrame, config: dict, output_path: Path
):
    """Creates plot of monthly total gp visits from the nims dataset

    Args:
        nims_monthly_totals (pd.DataFrame): monthly totals
        config (dict): configuration file
        output_path (Path): dir to save plot in -
    """
    logging.info("Plotting nims monthly data")

    # as config stores strings, need to use ast package to evaluate as a list
    year_range = ast.literal_eval(config["plotting"]["nims_year_range"])  # noqa: F841

    fig, ax = plt.subplots()
    nims_plot = sns.lineplot(
        data=nims_monthly_totals.query("year in @year_range"),
        x="month",
        hue="year",
        y="total",
        palette="coolwarm",
        ax=ax,
        linewidth=2,
    )

    y_format = ticker.FuncFormatter(utils.million_format)
    nims_plot.yaxis.set_major_formatter(y_format)

    ax = utils.set_labels(ax, "Number of NIMS GP attendances", fontsize=12)
    ax = utils.style_plot(ax)

    plt.savefig(
        output_path / f"{config['timestamp']}_{config['nims']['file_name']}.svg"
    )


def plot_summary(summary_df: pd.DataFrame, config: dict, output_path: Path):
    """Creates plot of proportion of GP visits by type

    Args:
        summary_df (pd.DataFrame): dataset continaing gp visit summary data
        config (dict): configuration file
        output_path (Path): dir to save plot in
    """
    logging.info("Plotting attendence data")

    for col in ["attended", "did_not_attend", "unknown"]:
        summary_df.loc[:, col] = summary_df[col].div(
            summary_df.total_count_of_appointments
        )

    # unpivot df from wide to long froma to work nicely with sns.lineplot
    melt_df = summary_df.drop(["total_count_of_appointments"], axis=1).melt(
        id_vars=["weekday", "appointment_date"],
        var_name="type",
        value_name="proportion",
    )

    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    summary_plot = sns.lineplot(
        data=melt_df,
        x="appointment_date",
        hue="type",
        y="proportion",
        # palette = 'coolwarm',
        ax=ax,
        linewidth=2,
    )
    plt.xticks(melt_df.appointment_date)

    x_format = ticker.FuncFormatter(utils.weekday_date_formatter)
    summary_plot.xaxis.set_major_formatter(x_format)
    y_format = ticker.PercentFormatter(xmax=1)
    summary_plot.yaxis.set_major_formatter(y_format)

    utils.set_labels(ax, title="Proportion of GP attendances by type", fontsize=12)
    utils.style_plot(ax)
    plt.savefig(
        output_path / f"{config['timestamp']}_{config['summary']['file_name']}.svg"
    )
