import os
import subprocess
import uuid
import shutil

from PIL import Image
from PyPDF2 import PdfReader
from .messages import ERRO_ARQUIVO_INVALIDO, ERRO_ARQUIVO_SENHA, ERRO_GS_NAO_ENCONTRADO


def redimensionar_imagem(image_path, output_path, max_size=(1600, 900)):
    img = Image.open(image_path)
    img.thumbnail(max_size)
    img.save(output_path)


def comprimir_pdf(input_path: str, output_path: str):
    try:
        with open(input_path, "rb") as f:
            reader = PdfReader(f)
            if reader.is_encrypted:
                raise ValueError(ERRO_ARQUIVO_SENHA)

        gs_path = shutil.which("gs") or "/usr/local/bin/gs"
        if not os.path.exists(gs_path):
            raise ValueError(ERRO_GS_NAO_ENCONTRADO)

        # O gs não consegue escrever no arquivo em uso,
        # então cria outro e depois move para o nome original
        temp_output_path = os.path.join(
            os.path.dirname(output_path), f"{uuid.uuid4().hex}.pdf"
        )

        args = [
            gs_path,
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS=/ebook",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={temp_output_path}",
            input_path,
        ]

        subprocess.run(args, check=True)
        os.replace(temp_output_path, output_path)

    except Exception as e:
        raise ValueError(f"{ERRO_ARQUIVO_INVALIDO}: {str(e)}")
