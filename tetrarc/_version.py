# The below is used to pull the version from the package (pyproject.toml)
import importlib.metadata as importlib_metadata

try:
    # __package__ allows for the case where __name__ is "__main__"
    __version__ = importlib_metadata.version(__package__ or __name__)
except importlib_metadata.PackageNotFoundError:
    __version__ = "0.0.0"

__build_date__ = "2026.03.23.13:22"

