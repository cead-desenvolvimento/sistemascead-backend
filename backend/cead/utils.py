import hashlib
import regex
import unicodedata
from cead import settings


def gerar_hash(key):
    return hashlib.sha256(f"{key}{settings.SECRET_KEY}".encode()).hexdigest()


# Faz com que nomes (pessoas, ruas) tenham as letras maiusculas apropriadas
def maiusculas_nomes(string):
    if not string or string.strip() == "":
        return None

    ROMAN_PATTERN_LOWERCASE = (
        r"^m{0,4}(cm|cd|d?c{0,3})(xc|xl|l?x{0,3})(ix|iv|v?i{0,3})$"
    )
    dont_capitalize = {
        "e",
        "da",
        "de",
        "do",
        "das",
        "dos",
        "dal",
        "del",
        "em",
        "na",
        "no",
        "nas",
        "nos",
    }

    string = unicodedata.normalize("NFC", string)
    string = regex.sub(r"[^\w\s\'´-]", " ", string).lower().strip().replace(" +", " ")
    strings_part = string.split()

    for index_string_part, string_part in enumerate(strings_part):
        if string_part not in dont_capitalize:
            string_part = string_part.title()

        # D'almeida ou D´almeida para D'Almeida ou D´Almeida
        if len(string_part) > 1 and (string_part[1] == "´" or string_part[1] == "'"):
            string_part = string_part[:2] + string_part[2:].capitalize()

        strings_part[index_string_part] = string_part

    # Dom Pedro Ii para Dom Pedro II
    if regex.match(ROMAN_PATTERN_LOWERCASE, strings_part[-1].lower()):
        strings_part[-1] = strings_part[-1].upper()

    return " ".join(strings_part)


# De Konstantin Dmitrievich Levin para konstantin_dmitrievich_levin
def remove_caracteres_especiais(src):
    return regex.sub(
        r"\s+",
        "_",
        regex.sub(
            r"[^a-zA-Z0-9\s]", "", unicodedata.normalize("NFD", src.strip().lower())
        ),
    )
