import json
from pathlib import Path
from zipfile import BadZipFile, ZipFile


class CVSXReader:
    def __init__(self, cvsx_filepath: str | Path):
        self.cvsx_filepath = str(cvsx_filepath)
        self._file_list: list[str] | None = None
        self._zip_file: ZipFile | None = None

    def __enter__(self):
        try:
            self._zip_file = ZipFile(self.cvsx_filepath, "r")
            self._file_list = self._zip_file.namelist()
            return self
        except FileNotFoundError:
            print(f"Error: File {self.cvsx_filepath} does not exist")
            return None
        except BadZipFile:
            print(f"Error: {self.cvsx_filepath} is not a valid zip file")
            return None

    def __exit__(self):
        if self._zip_file:
            self._zip_file.close()
        self._zip_file = None

    def has_file(self, filename: str) -> bool:
        if self._file_list is None:
            return False
        return filename in self._file_list

    def read_json(self, filename: str) -> dict:
        if not self._zip_file:
            raise RuntimeError("Archive not opened")
        with self._zip_file.open(filename) as f:
            return json.load(f)

    def read_bytes(self, filename: str) -> bytes:
        """Read binary data from the archive"""
        if not self._zip_file:
            raise RuntimeError("Archive not opened")

        return self._zip_file.read(filename)
