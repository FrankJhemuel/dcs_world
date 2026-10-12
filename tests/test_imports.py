import importlib
import pkgutil
import dcs_world


def test_import_all_modules():
    for module in pkgutil.walk_packages(
        dcs_world.__path__,
        prefix=dcs_world.__name__ + ".",
    ):
        importlib.import_module(module.name)