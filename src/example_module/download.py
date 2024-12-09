# standard
from pathlib import Path
import logging
import os

# project specific
import requests
from bs4 import BeautifulSoup
import pandas as pd


def download_nhs_data(base_dir: Path, config: dict):
    """Runs the download sub-pipeline"""

    input_dir = base_dir / "input"

    file_links = scrape_file_links(config["url"])

    for file in ["summary", "nims"]:
        download_file(
            file_links,
            config[file]["regex"],
            config[file]["file_name"],
            input_dir / "data",
        )


def scrape_file_links(url: str) -> pd.DataFrame:
    """
    Scrape website links

    Scrape the links to valid file formats (.xlsx, .csv) from supplied url

    Args:
        url (str): url of target website

    Returns:
        pd.DataFrame: df with colums for 'title' and 'link; (href)

    Raises:
        TypeError: The name variable is not a str
    """
    if not isinstance(url, str):
        raise TypeError("The url entered was not a string")

    html = requests.get(url=url, timeout=5)

    soup = BeautifulSoup(html.content, "html.parser")

    # data will be in .csv or .xlsx so can select links using regex on the file ext
    link_results = soup.select('a[href$=".xlsx"], a[href$=".csv"]')

    file_links_df = pd.DataFrame()

    file_links_df.loc[:, "title"] = [x.find("p").text for x in link_results]
    # stripping trailing whitespace from title column for future regex matching
    file_links_df.loc[:, "title"] = [x.strip() for x in file_links_df.title]

    file_links_df.loc[:, "link"] = [x["href"] for x in link_results]

    return file_links_df


def download_file(
    file_links_df: pd.DataFrame, file_regex: str, file_name: str, data_path: Path
):
    """
    Download file of interest

    Uses a regular expression to find file of interest in `file_links_df`,
    then downloads and saves to named directory

    Args:
        file_links_df (pd.DataFrame): df with a 'title' column and a 'link' column
        file_regex (str): regular expression to match against file_links_df 'title'
        file_name (str): name to save file under
        data_path (Path): directory to save file in
    """

    file_regex_match_mask = file_links_df.title.str.contains(file_regex)

    # as regex should only match one file, can just select first row using iloc[0]
    file_url = file_links_df[file_regex_match_mask].link.iloc[0]

    # if regex matches multiple files raise an error in the log
    if file_regex_match_mask.sum() > 1:
        logging.error("! regex %s matches multiple links !" % (file_regex))

    file = requests.get(file_url, timeout=5)
    file_ext = os.path.splitext(file_url)[1]
    with open(data_path / f"{file_name}{file_ext}", "wb") as output:
        output.write(file.content)

    logging.info("file downloaded to %s\\%s%s" % (data_path, file_name, file_ext))
