import os
import json
import csv
from pathlib import Path
from typing import Any, Dict, List, Union

def ensure_dir(path: Union[str, Path]) -> None:
    """
    Pastikan direktori ada, kalau belum ada otomatis dibuat.
    """
    Path(path).mkdir(parents=True, exist_ok=True)

def read_json(path: Union[str, Path]) -> Any:
    """
    Baca file JSON.
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json(path: Union[str, Path], data: Any, indent: int = 2) -> None:
    """
    Simpan data ke file JSON.
    """
    ensure_dir(Path(path).parent)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)

def read_csv(path: Union[str, Path]) -> List[Dict[str, str]]:
    """
    Baca file CSV dan return list of dict.
    """
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]

def write_csv(path: Union[str, Path], rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    """
    Simpan list of dict ke file CSV.
    """
    ensure_dir(Path(path).parent)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def file_exists(path: Union[str, Path]) -> bool:
    """
    Cek apakah file ada.
    """
    return Path(path).is_file()

def get_file_size(path: Union[str, Path]) -> int:
    """
    Ambil ukuran file dalam byte.
    """
    return os.path.getsize(path)