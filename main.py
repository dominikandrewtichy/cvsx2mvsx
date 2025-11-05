from src.convert.volume import cvsx_to_mvsx_volumes
from src.io.cvsx.cvsx_loader import load_cvsx_entry
from src.utils.print_utils import print_cvsx_entry


def main():
    # Load a CVSX entry from the zipped data directory
    cvsx_path = "data/cvsx/zipped/custom-tubhiswt.cvsx"

    print(f"Loading CVSX entry from: {cvsx_path}")
    print("=" * 80)

    entry = load_cvsx_entry(cvsx_path)

    print_cvsx_entry(entry)
    print("=" * 80)
    print("Successfully loaded and printed CVSX entry!")

    # Test cvsx_to_mvsx_volumes
    print("\n" + "=" * 80)
    print("Testing cvsx_to_mvsx_volumes...")
    print("=" * 80)

    mvsx_volumes = cvsx_to_mvsx_volumes(entry)

    print(f"\nConverted {len(mvsx_volumes)} volumes:")
    for i, volume in enumerate(mvsx_volumes, 1):
        print(f"\nVolume {i}:")
        print(f"  Source: {volume.source_filepath}")
        print(f"  Destination: {volume.destination_filepath}")
        print(f"  Channel ID: {volume.channel_id}")
        print(f"  Timeframe ID: {volume.timeframe_id}")
        print(f"  Isovalue: {volume.isovalue}")
        print(f"  Color: {volume.color}")
        print(f"  Opacity: {volume.opacity}")


if __name__ == "__main__":
    main()
