from app.config import settings
from pathlib import Path
import json
import shutil
import logfire
import os


class GCPService:
    def __init__(self):
        self.raw_bucket: str = settings.RAW_BUCKET
        self.processed_bucket: str = settings.PROCESSED_BUCKET
        self.root_path: Path = Path("./artifacts")


    def _ensure_buckets(self):
        raw_path = self.root_path / self.raw_bucket
        processed_path = self.root_path / self.processed_bucket

        if not raw_path.is_dir():
            raw_path.mkdir(exist_ok=True)
            raw_noisy = raw_path / "noisy_data"
            raw_true = raw_path / "true_data"

            raw_noisy.mkdir(exist_ok=True)
            raw_true.mkdir(exist_ok=True)

        if not processed_path.is_dir():
            processed_path.mkdir(exist_ok=True)
            processed_noisy = processed_path / "noisy_data"
            processed_true = processed_path / "true_data"

            processed_noisy.mkdir(exist_ok=True)
            processed_true.mkdir(exist_ok=True)


    def upload_to_gcs(self, data: str | dict, bucket_name: str, destination_name: str, is_json: bool = False):
        self._ensure_buckets()
        with logfire.span("GCS Upload", bucket=bucket_name, blob=destination_name):
            try:
                final_path = f"{self.root_path}/{bucket_name}/{destination_name}"
                if is_json:
                    with open(final_path, "w") as file:
                        json.dump(data, file)
                else:
                    shutil.copy(data, final_path)
                logfire.info(f"Uploaded to {final_path}")
            except Exception as e:
                logfire.error(f"GCS Upload Failed: {e}")
                raise e



# if __name__ == "__main__":
#     logfire.configure()
#     gcp = GCPService()
#     gcp._ensure_buckets()
#     data = {
#         "name": "Chamika",
#         "age": 35
#     }

#     bucket_name = settings.PROCESSED_BUCKET
#     destination_name = "noisy_data/sample.pdf"

#     #gcp.upload_to_gcs(data, bucket_name, destination_name, True)

#     gcp.upload_to_gcs("./DATA/noisy_data/5-Level Paging and 5-Level EPT - Intel - Revision 1.0 (December, 2016).pdf", bucket_name, destination_name)
