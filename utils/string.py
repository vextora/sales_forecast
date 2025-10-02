import re
import unicodedata

def slugify(value: str, allow_unicode: bool = False) -> str:
    """
    Convert string ke slug yang aman buat URL.
    Contoh: "Produk Baru 2025!" -> "produk-baru-2025"
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")

def camel_to_snake(name: str) -> str:
    """
    Convert CamelCase ke snake_case.
    Contoh: "ProductName" -> "product_name"
    """
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

def snake_to_camel(name: str) -> str:
    """
    Convert snake_case ke CamelCase.
    Contoh: "product_name" -> "ProductName"
    """
    return "".join(word.capitalize() for word in name.split("_"))

def truncate(text: str, length: int = 100, suffix: str = "...") -> str:
    """
    Potong string jadi panjang tertentu.
    """
    if len(text) <= length:
        return text
    return text[: length - len(suffix)] + suffix

def normalize_whitespace(text: str) -> str:
    """
    Bersihin whitespace berlebih.
    Contoh: "Hello   world" -> "Hello world"
    """
    return re.sub(r"\s+", " ", text).strip()