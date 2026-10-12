import logfire
import os
import tempfile
import shutil
import sys

from app.config import settings
from app.ingestion.loaders.html import parse_html
from app.ingestion.loaders.pdf import parse_pdf
from app.ingestion.loaders.office import parse_office
from app.ingestion.loaders.text import parse_text
from app.ingestion.chunking.splitter import chunk_text


from app.services.retrieval.qdrant_service import QdrantService
from app.services.gcp.gcp_service import GCPService




def process_file(
        file_path: str,
        filename: str,
        source_type: str,
        quadrant_service: QdrantService,
        gcp_service: GCPService,
        skip_raw_upload: bool = False
) -> None:

    with logfire.span("Processing File", file=filename, source=source_type, cloude_mode=skip_raw_upload):
        try:
            quadrant_service.ensure_collection()

            # Upload the file to gcs
            destination_name = f"{source_type}/{filename}"
            if not skip_raw_upload:
                gcp_service.upload_to_gcs(file_path, settings.RAW_BUCKET, destination_name)
            else:
                logfire.info(f"Skipping RAW upload (cloude mode) - file already at 'artifacts//{settings.RAW_BUCKET}/{destination_name}'")

            # Read file text
            ext = filename.lower().split(".")[-1]
            if ext == "pdf":
                full_text = parse_pdf(file_path)
            elif ext in ("html", "htm"):
                full_text = parse_html(file_path)
            elif ext == "txt":
                full_text = parse_text(file_path)
            elif ext in ("docx", "pptx"):
                full_text = parse_office(file_path)
            else:
                logfire.warning(f"Skipping unsupported file type: {filename}")
                return

            if not full_text or not full_text.strip():
                logfire.warning(f"No text extracted from {filename}")
                return

            # Chunking
            chunks = chunk_text(full_text)
            if not chunks:
                return

            # Upload processed metadata to GCS
            processed_data = {
                "filename": filename,
                "chunks": chunks,
                "source_type": source_type
            }
            processed_gcs_path = f"{source_type}/{filename}.json"
            gcp_service.upload_to_gcs(processed_data, settings.PROCESSED_BUCKET, processed_gcs_path, is_json=True)

            # Embed and index in Qdrant
            quadrant_service.insert_enterpirse_knowledge(
                filename,
                source_type,
                chunks
            )

        except Exception as e:
            logfire.error(f"Failed to process {filename}: {e}")
            raise e



def process_from_gcs(bucket_name: str, filename: str, source_type: str, quadrant_service: QdrantService, gcp_service: GCPService):
    """
    Cloud/webhook helper: downloads file from GCS to a temp path, then processes it.
    skip_raw_upload=True ensures we never write back to the RAW bucket.
    """
    with logfire.span("Cloude Mode: Download and Process", file=filename):
        try:
            ext = filename.lower().split(".")[-1]
            with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp:
                tmp_path = tmp.name

            gcs_path = f"./artifacts/{bucket_name}/{source_type}/{filename}"
            shutil.copy(gcs_path, tmp_path)
            logfire.info(f"Download {gcs_path} -> {tmp_path}")

            process_file(tmp_path, filename, source_type, quadrant_service, gcp_service, skip_raw_upload=True)

        except Exception as e:
            logfire.error(f"Cloud processing failed for {filename}: {e}")
            raise e
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass


# ---------------------------------------------- CLI functions --------------------------------------------------------------

def run_universal_ingestion(base_dir: str, quadrant_service: QdrantService, gcp_service: GCPService, wipe: bool = None):
    with logfire.span("Universal Ingestion Started", base_directory=base_dir):
        if wipe:
            logfire.span("Wiping Collection")
            quadrant_service.clean_collection()

        quadrant_service.ensure_collection()

        subdirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]

        if not subdirs:
            logfire.warning(f"No subdirectories found: {base_dir}")
            return
        else:
            for subdir in subdirs:
                source_type = "true_data" if "true" in subdir.lower() else "noisy_data" if "noisy" in subdir.lower() else subdir
                _process_directory(os.path.join(base_dir, subdir), source_type, quadrant_service, gcp_service)


def _process_directory(dir_path: str, source_type: str, quadrant_service: QdrantService, gcp_service: GCPService):
    with logfire.span("Scaning Directory", path=dir_path, source=source_type):
        files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
        logfire.info(f"Found {len(files)} files")
        for filename in files:
            process_file(os.path.join(dir_path,filename), filename, source_type, quadrant_service, gcp_service, skip_raw_upload=False)
    

if __name__ == "__main__":
    logfire.configure()
    quadrant_service = QdrantService()
    gcp_service = GCPService()

    wipe_requested = "--wipe" in sys.argv
    clean_args = [a for a in sys.argv if a != "--wipe"]
    target_dir = clean_args[1] if len(clean_args) > 1 else "DATA"

    if not os.path.exists(target_dir):
        print(f"Error: Paht {target_dir} does not exist.")
        sys.exit(1)

    run_universal_ingestion(target_dir, quadrant_service, gcp_service, wipe=wipe_requested)





    # file_path = "./DATA/noisy_data/5-Level Paging and 5-Level EPT - Intel - Revision 1.1 (May, 2017).pdf"
    # filename = "5-Level Paging and 5-Level EPT - Intel - Revision 1.1 (May, 2017).pdf"
    # source_type = "noisy_data"
    # # process_from_gcs(settings.RAW_BUCKET, filename, source_type, quadrant_service, gcp_service)

    # # _process_directory("./DATA/", "true_data")

    # process_file(
    #     file_path,
    #     filename,
    #     source_type,
    #     quadrant_service,
    #     gcp_service
    # )

    # query = "This enhanced support for DMA remapping will be detailed in a future revision of the"
    # res = quadrant_service.search_enterpirse_knowledge(query, limit=3)
    # for r in res:
    #     print("="*70)
    #     print(r['content'])
    #     print("\n")





        




    