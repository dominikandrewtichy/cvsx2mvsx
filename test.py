from src.io.cvsx.cvsx_loader import load_cvsx_entry
from src.utils.print_utils import print_cvsx_entry


def main():
    # Load a CVSX entry from the zipped data directory
    cvsx_path = "data/cvsx/zipped/emd-1832.cvsx"

    print(f"Loading CVSX entry from: {cvsx_path}")
    print("=" * 80)

    entry = load_cvsx_entry(cvsx_path)

    print_cvsx_entry(entry)
    print("=" * 80)
    print("Successfully loaded and printed CVSX entry!")


if __name__ == "__main__":
    main()