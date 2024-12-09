# project specific
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


def million_format(x: {int, float}, pos: float) -> str:
    """format ticks to be in million format
    eg 1000000 -> 1m

    Args:
        x (int, float): tick value
        pos (float): tick position

    Returns:
        str: formatted tick value
    """
    s = f"{x / 1000000:,g}m"
    return s


def weekday_date_formatter(x: str, pos: float) -> str:
    """format ticks to be first letter of weekday,
       and to display date below if a Sunday

    Args:
        x (str): tick value
        pos (float): tick position

    Returns:
        str: formatted tick value
    """
    weekday_fmt = mdates.DateFormatter("%a")
    date_fmt = mdates.DateFormatter("%d")
    if weekday_fmt(x) == "Sun":
        s = f"{weekday_fmt(x)[0]}\n {date_fmt(x)}"
    else:
        s = weekday_fmt(x)[0]
    return s


def set_labels(ax: plt.Axes, title: str, fontsize: int) -> plt.Axes:
    """Modify axes labels

    Formats labels from snake_case, sets text color to grey

    Args:
        ax (plt.Axes): axis of plot to update
        title (str): title of plot
        fontsize (int): fontsize of smaller lables (xlabel, ylabel, legend title)

    Returns:
        plt.Axes: axis of plot to update
    """

    ax.set_xlabel(
        xlabel=varname_to_text(ax.get_xlabel()),
        color="grey",
        fontsize=fontsize,
    )
    ax.set_ylabel(
        ylabel=varname_to_text(ax.get_ylabel()),
        color="grey",
        fontsize=fontsize,
    )
    ax.set_title(
        title.title(),
        pad=10,
        fontsize=np.ceil(fontsize * 1.3),
        color="grey",
    )
    # if legend exists then also update
    if ax.get_legend() is not None:
        handles, labels = ax.get_legend_handles_labels()
        labels = [varname_to_text(label) for label in labels]
        ax.legend(
            title=varname_to_text(ax.get_legend().get_title().get_text()),
            handles=handles,
            labels=labels,
            labelcolor="grey",
        )
        ax.get_legend().get_title().set_color("grey")
    return ax


def style_plot(ax: plt.Axes) -> plt.Axes:
    """styles plot

    Sets major x gridlines, modify axis, ticks and labels

    Args:
        ax (Axes):  axis of plot to update

    Returns:
        Axes:  axis of plot to update
    """
    sns.despine()
    ax.grid(which="major", alpha=0.5, linestyle=":", axis="x")
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_linewidth(2)
        ax.spines[spine].set_color("lightgray")
        ax.tick_params(
            width=1,
            color="grey",
            length=4,
            labelcolor="grey",
            labelfontfamily="sans-serif",
        )
    return ax


def text_to_varname(text: str) -> str:
    """convert a string from text format to snake-case"""

    varname = text.lower().replace(" ", "_")
    return varname


def varname_to_text(varname: str) -> str:
    """convert a string from snake-case to formatted text"""

    text = varname.replace("_", " ").capitalize()
    return text
