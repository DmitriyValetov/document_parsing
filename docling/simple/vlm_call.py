"""
Seems to be using cpu
Can see some missrecognition of docling as doding (cl -> d)

ValueError: Coordinate 'lower' is less than 'upper'
"""

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app_vlm.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


import time
from pathlib import Path
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.vlm_pipeline import VlmPipeline



def write_to_file(text, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)


if __name__ == "__main__":
    input_dir = Path("files")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory {input_dir} does not exist")


    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_cls=VlmPipeline,
            ),
        }
    )

    for source, fp_name in zip([
        "https://arxiv.org/pdf/2408.09869", 
        input_dir/"2408.09869v5.pdf",
        input_dir/"765275.pdf", 
        input_dir/"classic_mem.jpg",
    ], [
        "arxiv_2408.09869.md",
        "2408.09869v5.md",
        "765275.md",
        "classic_mem.md",
    ]):
        start_time = time.time()
        result = converter.convert(source)
        md_content = result.document.export_to_markdown()
        write_to_file(md_content, output_dir / fp_name)
        logger.info(f"{source} {len(md_content)} {time.time() - start_time} seconds")