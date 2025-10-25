import json
from pathlib import Path
from typing import Optional
from zipfile import BadZipFile, ZipFile


class CVSXReader:
    def __init__(self, cvsx_filepath: str | Path):
        self.cvsx_filepath = str(cvsx_filepath)
        self._file_list: Optional[list[str]] = None
        self._zip_file: Optional[ZipFile] = None

    def __enter__(self):
        """Open the archive when entering context"""
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

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close the archive when exiting context"""
        if self._zip_file:
            self._zip_file.close()

    def has_file(self, filename: str) -> bool:
        if self._file_list is None:
            return False
        return filename in self._file_list

    def read_json(self, filename: str) -> dict:
        """Read and parse a JSON file from the archive"""
        if not self._zip_file:
            raise RuntimeError("Archive not opened")

        with self._zip_file.open(filename) as f:
            return json.load(f)

    def read_bytes(self, filename: str) -> bytes:
        """Read binary data from the archive"""
        if not self._zip_file:
            raise RuntimeError("Archive not opened")

        return self._zip_file.read(filename)

    def validate_cvsx_structure(self, verbose: bool = True) -> bool:
        # Step 1: Check index.json exists
        if not self.has_file("index.json"):
            if verbose:
                print("Error: index.json not found in archive")
            return False

        if verbose:
            print("✓ Found index.json")

        # Step 2: Read index.json
        try:
            index_data = self.read_json("index.json")
        except Exception as e:
            if verbose:
                print(f"Error reading index.json: {e}")
            return False

        if verbose:
            print("✓ Successfully parsed index.json")

        # Step 3: Check files referenced in index
        required_fields = {
            "annotations": index_data.get("annotations"),
            "metadata": index_data.get("metadata"),
            "query": index_data.get("query"),
        }

        missing_files = []
        for field_name, filename in required_fields.items():
            if not filename:
                if verbose:
                    print(f"Error: '{field_name}' field not found in index.json")
                missing_files.append(f"{field_name} (not specified)")
                continue

            if not self.has_file(filename):
                if verbose:
                    print(
                        f"Error: {filename} (referenced in '{field_name}') not found in archive"
                    )
                missing_files.append(filename)
            else:
                if verbose:
                    print(f"✓ Found {filename}")

        # Check volume files
        volumes = index_data.get("volumes", {})
        if verbose:
            print(f"\nChecking {len(volumes)} volume file(s)...")
        for volume_key in volumes.keys():
            if not self.has_file(volume_key):
                if verbose:
                    print(f"Error: Volume file {volume_key} not found in archive")
                missing_files.append(volume_key)
            else:
                if verbose:
                    print(f"✓ Found {volume_key}")

        # Check lattice segmentations (optional)
        lattice_segs = index_data.get("latticeSegmentations", {})
        if lattice_segs:
            if verbose:
                print(f"\nChecking {len(lattice_segs)} lattice segmentation(s)...")
            for lattice_key in lattice_segs.keys():
                if not self.has_file(lattice_key):
                    if verbose:
                        print(f"Error: Lattice file {lattice_key} not found in archive")
                    missing_files.append(lattice_key)
                else:
                    if verbose:
                        print(f"✓ Found {lattice_key}")

        # Check mesh segmentations (optional)
        mesh_segs = index_data.get("meshSegmentations", [])
        if mesh_segs:
            if verbose:
                print("\nChecking mesh segmentation(s)...")
            for mesh_seg in mesh_segs:
                for mesh_file in mesh_seg.get("segmentsFilenames", []):
                    if not self.has_file(mesh_file):
                        if verbose:
                            print(f"Error: Mesh file {mesh_file} not found in archive")
                        missing_files.append(mesh_file)
                    else:
                        if verbose:
                            print(f"✓ Found {mesh_file}")

        # Check geometric segmentations (optional)
        geom_segs = index_data.get("geometricSegmentations", {})
        if geom_segs:
            if verbose:
                print(f"\nChecking {len(geom_segs)} geometric segmentation(s)...")
            for geom_key in geom_segs.keys():
                if not self.has_file(geom_key):
                    if verbose:
                        print(
                            f"Error: Geometric segmentation file {geom_key} not found in archive"
                        )
                    missing_files.append(geom_key)
                else:
                    if verbose:
                        print(f"✓ Found {geom_key}")

        if missing_files:
            if verbose:
                print(f"\n✗ Validation failed: {len(missing_files)} file(s) missing")
            return False

        if verbose:
            print("\n✓ All required files present")
        return True


def validate_all_cvsx_files(cvsx_filepath: str, verbose: bool = False) -> bool:
    cvsx_filepath = Path(cvsx_filepath)

    if not cvsx_filepath.exists():
        print(f"Error: Directory {directory} does not exist")
        return False

    try:
        with CVSXReader(cvsx_filepath) as reader:
            if reader is None:
                print(f"Error: Failed to open archive: {cvsx_filepath}")

            return reader.validate_cvsx_structure(verbose=verbose)
    except Exception as e:
        print(f"Error validating {cvsx_filepath}: {e}")


def get_cvsx_statistics(directory: str):
    """
    Get statistics about all CVSX files in a directory

    Args:
        directory: Path to directory containing .cvsx files
    """
    directory_path = Path(directory)
    cvsx_files = sorted(directory_path.glob("*.cvsx"))

    print(f"CVSX Statistics for {directory}")
    print("=" * 80)

    stats = []

    for cvsx_file in cvsx_files:
        try:
            with CVSXReader(str(cvsx_file)) as reader:
                if reader is None:
                    continue

                index_data = reader.read_json("index.json")

                file_stat = {
                    "name": cvsx_file.name,
                    "size_mb": cvsx_file.stat().st_size / (1024 * 1024),
                    "num_volumes": len(index_data.get("volumes", {})),
                    "num_lattices": len(index_data.get("latticeSegmentations", {})),
                    "num_meshes": len(index_data.get("meshSegmentations", [])),
                    "num_geometric": len(index_data.get("geometricSegmentations", {})),
                    "total_files": len(reader._file_list),
                }

                stats.append(file_stat)

        except Exception as e:
            print(f"Error processing {cvsx_file.name}: {e}")
            continue

    # Print statistics table
    if stats:
        print(
            f"\n{'Filename':<30} {'Size (MB)':<12} {'Volumes':<10} {'Lattices':<10} {'Meshes':<10} {'Geometric':<12} {'Total Files':<12}"
        )
        print("-" * 100)

        for stat in stats:
            print(
                f"{stat['name']:<30} {stat['size_mb']:>10.2f}  {stat['num_volumes']:>8}  {stat['num_lattices']:>9}  {stat['num_meshes']:>8}  {stat['num_geometric']:>10}  {stat['total_files']:>11}"
            )

        # Print totals
        print("-" * 100)
        total_size = sum(s["size_mb"] for s in stats)
        total_volumes = sum(s["num_volumes"] for s in stats)
        total_lattices = sum(s["num_lattices"] for s in stats)
        total_meshes = sum(s["num_meshes"] for s in stats)
        total_geometric = sum(s["num_geometric"] for s in stats)

        print(
            f"{'TOTAL':<30} {total_size:>10.2f}  {total_volumes:>8}  {total_lattices:>9}  {total_meshes:>8}  {total_geometric:>10}"
        )


if __name__ == "__main__":
    directory = "data/cvsx/zipped"

    # Option 1: Validate all files (brief output)
    print("VALIDATION RESULTS")
    print("=" * 80)
    results = validate_all_cvsx_files(directory, verbose=False)

    print("\n\n")

    # Option 2: Get statistics about all files
    get_cvsx_statistics(directory)

    # Option 3: Validate with verbose output for a specific file
    # print("\n\nDETAILED VALIDATION")
    # print("=" * 80)
    # validate_all_cvsx_files(directory, verbose=True)
