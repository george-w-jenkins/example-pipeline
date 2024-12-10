#standard
from pathlib import Path
import datetime as dt
import logging
#custom
from src.run_pipeline import run_pipeline

def main():

    #define the root directory to pass to functions in the pipeline
    base_dir = Path(__file__).parents[0]
    output_dir = base_dir / "output"

    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M")

    logging.basicConfig(
        filename=output_dir / 'example.log',
        encoding="utf-8",
        level=logging.INFO,
    ) 
    logging.info("---------Starting run %s ---------" % (timestamp))

    run_pipeline(base_dir, timestamp)

if __name__ == "__main__":
    main()
    

