import ghostscript
import os
import subprocess
import uuid

from PIL import Image
from PyPDF2 import PdfReader

from .messages import ERRO_ARQUIVO_INVALIDO, ERRO_ARQUIVO_SENHA


def redimensionar_imagem(image_path, output_path, max_size=(1600, 900)):
    img = Image.open(image_path)
    img.thumbnail(max_size)
    img.save(output_path)


def comprimir_pdf(input_path, output_path):
    try:
        with open(input_path, "rb") as f:
            reader = PdfReader(f)
            if reader.is_encrypted:
                raise ValueError(ERRO_ARQUIVO_SENHA)

        # O gs nao consegue escrever no arquivo em uso,
        # Entao cria outro e depois move para o nome original
        temp_output_path = f"{output_path}_{uuid.uuid4().hex}.pdf"

        args = [
            "gs",
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
