import json
import os
from pathlib import Path
from typing import Type, TypeVar
from zipfile import BadZipFile, ZipFile

from pydantic import ValidationError

from src.models.cvsx.cvsx_annotations import CVSXAnnotations
from src.models.cvsx.cvsx_entry import CVSXEntry
from src.models.cvsx.cvsx_index import CVSXIndex
from src.models.cvsx.cvsx_metadata import CVSXMetadata
from src.models.cvsx.cvsx_query import CVSXQuery

T = TypeVar("T")


def check_zip_file_exists(zip_path: str) -> None:
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"ZIP archive not found: '{zip_path}'")

    if not os.path.isfile(zip_path):
        raise ValueError(f"Path exists but is not a file: '{zip_path}'")


def check_zip_integrity(zip_path: str) -> None:
    try:
        with ZipFile(zip_path, "r") as z:
            bad_file = z.testzip()
            if bad_file is not None:
                raise ValueError(
                    f"ZIP archive is corrupted. First bad file: '{bad_file}'"
                )
    except BadZipFile:
        raise ValueError(f"File '{zip_path}' is not a valid ZIP archive")


def check_file_exists_in_zip(zip_path: str, file_path: str) -> None:
    with ZipFile(zip_path, "r") as z:
        zip_contents = set(z.namelist())

    if file_path not in zip_contents:
        raise FileNotFoundError(
            f"File '{file_path}' not found in ZIP archive '{zip_path}'"
        )


def check_all_files_in_index(zip_path: str, cvsx_index: CVSXIndex) -> None:
    with ZipFile(zip_path, "r") as z:
        zip_contents = set(z.namelist())

    expected_files = set()

    expected_files.update(
        [
            cvsx_index.annotations,
            cvsx_index.metadata,
            cvsx_index.query,
        ]
    )

    expected_files.update(cvsx_index.volumes.keys())

    if cvsx_index.latticeSegmentations:
        expected_files.update(cvsx_index.latticeSegmentations.keys())
    if cvsx_index.geometricSegmentations:
        expected_files.update(cvsx_index.geometricSegmentations.keys())
    if cvsx_index.meshSegmentations:
        for mesh_info in cvsx_index.meshSegmentations:
            expected_files.update(mesh_info.segmentsFilenames)

    for file in expected_files:
        if not is_path_safe(file):
            raise ValueError(f"Unsafe path detected in index: '{file}'")
        if file not in zip_contents:
            raise FileNotFoundError("File missing from ZIP archive: '{f}'")


def is_path_safe(base_directory: str, untrusted_path: str) -> bool:
    base = Path(base_directory).resolve()

    try:
        target = (base / untrusted_path).resolve()
        target.relative_to(base)
        return True
    except (ValueError, OSError):
        return False


def load_model_from_zip(zip_path: str, inner_path: str, model_class: Type[T]) -> T:
    with ZipFile(zip_path, "r") as z:
        with z.open(inner_path) as f:
            try:
                json_data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in '{inner_path}' of '{zip_path}': {e}")
    try:
        return model_class.model_validate(json_data)
    except ValidationError as e:
        raise ValueError(
            f"Invalid data format in '{inner_path}' inside '{zip_path}': {e}"
        )


def load_cvsx_entry(zip_path: str) -> CVSXEntry:
    check_zip_file_exists(zip_path)
    check_zip_integrity(zip_path)

    check_file_exists_in_zip(zip_path, "index.json")

    cvsx_index = load_model_from_zip(zip_path, "index.json", CVSXIndex)

    check_all_files_in_index(zip_path, cvsx_index)

    annotations = cvsx_index.annotations
    metadata = cvsx_index.metadata
    query = cvsx_index.query

    cvsx_annotations = load_model_from_zip(zip_path, annotations, CVSXAnnotations)
    cvsx_metadata = load_model_from_zip(zip_path, metadata, CVSXMetadata)
    cvsx_query = load_model_from_zip(zip_path, query, CVSXQuery)

    return CVSXEntry(
        filepath=zip_path,
        index=cvsx_index,
        annotations=cvsx_annotations,
        metadata=cvsx_metadata,
        query=cvsx_query,
    )
