from datetime import datetime, timedelta
import pytz

DEFAULT_TZ = pytz.timezone("Asia/Jakarta")

def now(tz: str = "Asia/Jakarta") -> datetime:
    """
    Return current datetime with timezone awareness.
    Default: Asia/Jakarta
    """
    return datetime.now(pytz.timezone(tz))

def parse(date_str: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """
    Parse string ke datetime.
    Default format: '2025-09-30 14:30:00'
    """
    return datetime.strptime(date_str, fmt)

def format(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime ke string sesuai format.
    """
    return dt.strftime(fmt)

def add_days(dt: datetime, days: int) -> datetime:
    """
    Tambah atau kurang hari dari datetime.
    """
    return dt + timedelta(days=days)

def diff_in_days(dt1: datetime, dt2: datetime) -> int:
    """
    Hitung selisih hari antara dua datetime.
    """
    return (dt1 - dt2).days

def to_timezone(dt: datetime, tz: str = "Asia/Jakarta") -> datetime:
    """
    Convert datetime ke timezone tertentu.
    """
    return dt.astimezone(pytz.timezone(tz))