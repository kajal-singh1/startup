"""
==========================================================
Module 1 : World Bank Data Acquisition

Startup Growth Analytics System

Downloads official World Bank indicators and stores
raw reproducible datasets.

==========================================================
"""

from pathlib import Path
import json
import time
from datetime import datetime

import pandas as pd
import requests
from tqdm import tqdm

from utils.config import ConfigManager
from utils.logger import ProjectLogger


class WorldBankDownloader:
    """
    World Bank API downloader.
    """


    def __init__(self):

        self.config_manager = ConfigManager()

        self.config = self.config_manager.get_config()

        self.indicators = (
            self.config_manager
            .get_indicators()
        )

        self.logger = (
            ProjectLogger()
            .get_logger()
        )


        self.base_url = (
            self.config["world_bank"]["base_url"]
        )

        self.start_year = (
            self.config["study_period"]["start_year"]
        )

        self.end_year = (
            self.config["study_period"]["end_year"]
        )


        self.timeout = (
            self.config["world_bank"]["timeout"]
        )

        self.max_retries = (
            self.config["world_bank"]["max_retries"]
        )


        self.raw_path = Path(
            self.config["paths"]["raw_data"]
        ) / "world_bank"


        self.metadata_path = Path(
            self.config["paths"]["metadata"]
        )


        self.raw_path.mkdir(
            parents=True,
            exist_ok=True
        )

        self.metadata_path.mkdir(
            parents=True,
            exist_ok=True
        )


        self.session = requests.Session()


        self.logger.info(
            "World Bank downloader initialized"
        )



    def build_api_url(self, indicator, source=None):

        """
        Creates World Bank API URL.
        """

        url = (
            f"{self.base_url}/country/all/"
            f"indicator/{indicator}"
            f"?format=json"
            f"&per_page=20000"
        )

        if source:
            url += f"&source={source}"

        return url
    
    def request_api(self, url):

        """
        API request with retry mechanism.
        """

        for attempt in range(
            1,
            self.max_retries + 1
        ):

            try:

                response = (
                    self.session
                    .get(
                        url,
                        timeout=self.timeout
                    )
                )


                response.raise_for_status()


                return response.json()


            except Exception as error:


                self.logger.warning(
                    f"Attempt {attempt} failed: {error}"
                )


                if attempt < self.max_retries:

                    time.sleep(3)


                else:

                    self.logger.error(
                        "Maximum retries exceeded"
                    )

                    return None
    
    def parse_response(
        self,
        response,
        indicator
    ):

        """
        Converts API JSON response into DataFrame.
        """


        if response is None:

            return None
        
        if isinstance(response, list) and len(response) >= 1 and isinstance(response[0], dict) and "message" in response[0]:
            msg = response[0]["message"][0]
            self.logger.error(
                f"{indicator}: API error {msg['id']} ({msg['key']}) - {msg['value']}"
            )
            return None


        if len(response) < 2:

            return None


        records = response[1]


        data = []


        for item in records:


            if item["value"] is None:

                continue


            data.append(
                {
                    "country_code":
                        item["countryiso3code"],

                    "country_name":
                        item["country"]["value"],

                    "year":
                        int(item["date"]),

                    "indicator_code":
                        indicator,

                    "value":
                        item["value"]
                }
            )


        return pd.DataFrame(data)

    def download_indicator(self, indicator_code):

        """
        Downloads one World Bank indicator.
        """

        self.logger.info(
            f"Downloading indicator: {indicator_code}"
        )

        row = self.indicators[
            self.indicators["indicator_code"] == indicator_code
        ]

        source = (
            75 if not row.empty and row.iloc[0]["category"] == "Governance"
            else None
        )

        url = self.build_api_url(
            indicator_code, source=source
        )

        response = self.request_api(
            url
        )

        df = self.parse_response(
            response,
            indicator_code
        )

        if df is None or df.empty:

            self.logger.warning(
                f"No data found for {indicator_code}"
            )

            return None

        # Restrict study period

        df = df[
            (df["year"] >= self.start_year)
            &
            (df["year"] <= self.end_year)
        ]

        return df

    def save_indicator_data(
        self,
        df,
        indicator_code
    ):

        """
        Saves raw indicator CSV.
        """


        file_path = (
            self.raw_path /
            f"{indicator_code}.csv"
        )


        df.to_csv(
            file_path,
            index=False,
            encoding="utf-8"
        )


        self.logger.info(
            f"Saved {indicator_code}"
        )


        return file_path
    
    def save_metadata(
        self,
        indicator_code,
        df,
        file_path
    ):

        """
        Saves download information.
        """


        metadata = {

            "indicator_code":
                indicator_code,

            "download_time":
                datetime.now()
                .strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

            "study_period":
                f"{self.start_year}-{self.end_year}",

            "rows":
                len(df),

            "countries":
                df["country_code"]
                .nunique(),

            "file":
                str(file_path)

        }


        metadata_file = (
            self.metadata_path /
            f"{indicator_code}_metadata.json"
        )


        with open(
            metadata_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                metadata,
                file,
                indent=4
            )

    def download_all(self):

        """
        Downloads all indicators
        listed in indicators.csv.
        """


        results = []


        total = len(
            self.indicators
        )


        self.logger.info(
            f"Total indicators: {total}"
        )


        for _, row in tqdm(
            self.indicators.iterrows(),
            total=total,
            desc="Downloading Indicators"
        ):


            indicator_code = (
                row["indicator_code"]
            )


            output_file = (
                self.raw_path /
                f"{indicator_code}.csv"
            )


            # Resume capability

            if output_file.exists():

                self.logger.info(
                    f"Skipping existing file: {indicator_code}"
                )

                continue



            df = self.download_indicator(
                indicator_code
            )


            if df is not None:


                file_path = (
                    self.save_indicator_data(
                        df,
                        indicator_code
                    )
                )


                self.save_metadata(
                    indicator_code,
                    df,
                    file_path
                )


                results.append(
                    {
                        "indicator":
                            indicator_code,

                        "status":
                            "success",

                        "rows":
                            len(df)

                    }
                )


            else:

                results.append(
                    {
                        "indicator":
                            indicator_code,

                        "status":
                            "failed",

                        "rows":
                            0
                    }
                )


        self.create_download_report(
            results
        )

    def create_download_report(
        self,
        results
    ):

        """
        Creates final download summary.
        """


        report = pd.DataFrame(
            results
        )


        report_path = (
            self.metadata_path /
            "download_report.csv"
        )


        report.to_csv(
            report_path,
            index=False
        )


        self.logger.info(
            "Download report created"
        )

if __name__ == "__main__":

    start_time = datetime.now()

    print("=" * 70)
    print("Startup Growth Analytics System")
    print("Module 1 : World Bank Data Acquisition")
    print("=" * 70)


    try:

        downloader = WorldBankDownloader()


        downloader.logger.info(
            "Module 1 execution started"
        )


        downloader.download_all()


        end_time = datetime.now()


        duration = (
            end_time - start_time
        )


        print("\n" + "=" * 70)
        print("DOWNLOAD COMPLETED")
        print("=" * 70)

        print(
            f"Start Time : {start_time}"
        )

        print(
            f"End Time   : {end_time}"
        )

        print(
            f"Duration   : {duration}"
        )

        print(
            "\nRaw files saved at:"
        )

        print(
            "data/raw/world_bank/"
        )

        print(
            "\nMetadata saved at:"
        )

        print(
            "data/metadata/"
        )


    except Exception as error:


        print("\nERROR OCCURRED")

        print(error)


        try:

            downloader.logger.exception(
                "Module 1 failed"
            )

        except:

            pass