from src.barcode_v3 import process_files


def main(input_path):
    process_files(input_path)


if __name__ == "__main__":
    input_path = "/app/examples"
    main(input_path)
