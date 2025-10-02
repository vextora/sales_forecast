import pkgutil
import importlib
from .sales import Sale
from .products import Product
from .forecast import Forecast

__all__ = []

for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    # skip __init__.py
    if module_name == "__init__":
        continue

    # import modulnya
    module = importlib.import_module(f"{__name__}.{module_name}")

    # ambil semua atribut yg huruf awalnya kapital (class)
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, type):
            globals()[attr_name] = attr
            __all__.append(attr_name)