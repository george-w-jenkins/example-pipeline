# standard
from pathlib import Path
import logging
import datetime

# project specific
import pandas as pd

# custom
from src.example_module import utils


def load_and_process(base_dir: Path) -> pd.DataFrame:
    """
    loads and cleans data

    Loads the summary and nims datasets as dfs from the data directory
    Cleans dataframes ready for analysis
    Calculates a monthly total df from the nims dataset

    Returns:
        pd.DataFrame: dataframe containing summary data
        pd.DataFrame: dataframe containing nims data
        pd.DataFrame: dataframe containing monthly totals of nims data
    """

    input_dir = base_dir / "input"

    summary_df = load_summary_data(input_dir / "data")
    nims_df = load_nims_df(input_dir / "data")
    nims_monthly_totals = get_monthly_totals(nims_df)

    return summary_df, nims_df, nims_monthly_totals


def load_summary_data(data_path: Path) -> pd.DataFrame:
    """
    Loads summary dataset and cleans

    Renames columns, drops unnecessary rows and cols,
    and explictly casts column data types

    Args:
        data_path (Path): path to data directory

    Returns:
        pd.DataFrame: dataframe of cleaned summary data
    """
    logging.info("Reading table 2a from %s summary.xlsx" % (data_path))

    # imported excel file is messy with lots of NaNs, we only want the data
    raw_summary_df = pd.read_excel(data_path / "summary.xlsx", sheet_name="Table 2a")

    # finding index in the 'date' column that are dates,
    # (not NaN or str) selects the data we want
    date_mask = raw_summary_df.iloc[:, 1].apply(
        lambda x: isinstance(x, datetime.datetime)
    )

    # column names are spread across two rows above the data
    start_index = date_mask.index[date_mask][0]
    column_labels = raw_summary_df.loc[start_index - 2 : start_index - 1, :]
    # combine_first selects the column labels from the two rows and excludes NaNs
    final_column_labels = column_labels.iloc[0].combine_first(column_labels.iloc[1])

    summary_df = raw_summary_df[date_mask].copy()
    summary_df.columns = [utils.text_to_varname(x) for x in final_column_labels]
    # One NaN column remains  - remove using dropna
    summary_df.dropna(axis=1, inplace=True)

    summary_df = summary_df.rename(columns={"date": "weekday", "unknown1": "unknown"})
    summary_df = summary_df.astype(
        {
            "weekday": "object",
            "appointment_date": "datetime64[ns]",
            "total_count_of_appointments": "int64",
            "attended": "float",
            "did_not_attend": "float",
            "unknown": "float",
        }
    )
    return summary_df


def load_nims_df(data_path: Path) -> pd.DataFrame:
    """Loads nims data

    Args:
        data_path (Path): path to data directory

    Returns:
        pd.DataFrame: dataframe of nims data
    """

    logging.info("Reading file %s" % (data_path / "nims.csv"))

    nims_df = pd.read_csv(data_path / "nims.csv")
    nims_df.columns = [utils.text_to_varname(x) for x in nims_df.columns]
    nims_df = nims_df.astype(
        {
            "date": "datetime64[ns]",
            "type": "object",
            "nhs_area_code": "object",
            "ons_code": "object",
            "name": "object",
            "total": "int64",
        }
    )
    return nims_df


def get_monthly_totals(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates totals by month

    Args:
        df (DataFrame): _description_

    Returns:
        pd.DataFrame: dataframe holding monthly totals of input data
    """
    logging.info("Creating monthly totals")

    grouped_df = df.groupby(
        [df["date"].dt.year, df["date"].dt.month],
    )["total"].sum()

    # groupby results in two 'date' indexs - renaming them as more informative
    # using reset_index to get month/year as columns - more useful for future plotting
    grouped_df = grouped_df.rename_axis(["year", "month"]).reset_index()
    grouped_df.month = grouped_df.month.astype("object")

    # before plotting - converting month from number to 3 letter str (eg 1 → Jan)
    grouped_df.loc[:, "month"] = (
        pd.to_datetime(grouped_df[["year", "month"]].assign(DAY=1))
        .dt.month_name()
        .str.slice(stop=3)
    )

    return grouped_df
