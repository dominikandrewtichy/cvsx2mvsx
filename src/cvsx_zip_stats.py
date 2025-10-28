from pathlib import Path

from lib.io.cvsx_reader import CVSXReader


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
            with CVSXReader(cvsx_file) as reader:
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

    get_cvsx_statistics(directory)
