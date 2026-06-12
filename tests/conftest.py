import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))            # _helpers importable under pytest
sys.path.insert(0, str(HERE.parent / "src"))  # package importable without install
