# standard
import logging

# project specific
import yaml

# custom
from src.example_module import download, process, visualise


def run_pipeline(base_dir, timestamp):
    """Runs analysis pipline accoridng to config file settings"""

    input_dir = base_dir / "input"
    output_dir = base_dir / "output"

    with open(
        input_dir / "configs" / "example_config.yml", "r", encoding="utf-8"
    ) as file:
        config = yaml.safe_load(file)
    config["timestamp"] = timestamp

    logging.info("Running analyis")

    download.download_nhs_data(base_dir, config)

    # Don't need the 2nd output,
    # so indicating it should be ignored by using _ as the varname
    summary_df, _, nims_monthly_df = process.load_and_process(base_dir)

    visualise.make_plots(base_dir, summary_df, nims_monthly_df, config)

    # save the timestamped config so settings are recorded
    with open(
        output_dir / f"{timestamp}_config.yml",
        "w",
        encoding="utf-8",
    ) as outfile:
        yaml.dump(config, outfile)

    logging.info("Finished")
