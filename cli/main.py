import argparse
from backend import normalizer
from backend import aggregate
from backend import analyzer

DEFAULT_FILE = "data/messy_data.csv"

def main():
    parser = argparse.ArgumentParser(description="Clean a messy CSV file")
    parser.add_argument(
        "input_file", 
        nargs="?",  # Makes the argument optional
        default=DEFAULT_FILE,  # Default file if none is provided
        help=f"Path to the CSV file to clean (default: {DEFAULT_FILE})"
    )
    args = parser.parse_args()

    normalizer.normalize_csv(args.input_file)
    aggregate.aggregate_data("data/cleaned_data.csv")
    analyzer.generate_spending_report("data/cleaned_data.csv")


if __name__ == "__main__":
    main()
