from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable
from PIL import Image, ImageChops
from stegano import lsb

#Where we point to our files and folders.
#My directory.
BASE_DIR = Path(r"C:\Users\rosaf\OneDrive\Documents\GitHub\CS426_Project")
#File that contains the message we want to hide.
DEFAULT_MESSAGE_FILE = BASE_DIR / "message.txt"
#Folder where all the images we want to hide messages in are located.
DEFAULT_DATASET_DIR = BASE_DIR / "DATASET"
#Where we will save the encoded images with hidden messages.
DEFAULT_BATCH_OUTPUT_DIR = BASE_DIR / "ENCODED"
SUPPORTED_IMAGE_TYPES = {".png", ".bmp"}

#Checks if a file exists.
def require_existing_file(path: Path, description: str) -> Path:
    if not path.is_file():
        raise FileNotFoundError(f"{description} not found: {path}")
    return path

#Checks if an image is a support file type.
def ensure_supported_image(path: Path) -> Path:
    if path.suffix.lower() not in SUPPORTED_IMAGE_TYPES:
        allowed = ", ".join(sorted(SUPPORTED_IMAGE_TYPES))
        raise ValueError(
            f"Use a lossless image type ({allowed}). JPEG files are not safe for LSB steganography."
        )
    return path

#Reads the message from the specified text file.
def read_message(message_path: Path) -> str:
    require_existing_file(message_path, "Message file")
    message = message_path.read_text(encoding="utf-8")
    if not message.strip():
        raise ValueError("The message file is empty.")
    return message

# This function counts how many pixels changed between two images.
def count_changed_pixels(original: Image.Image, encoded: Image.Image) -> int:
    diff = ImageChops.difference(original.convert("RGB"), encoded.convert("RGB"))

    return sum(1 for pixel in diff.getdata() if pixel != (0, 0, 0))

# This function compares the original image and the encoded image.
def compare_images(original_path: Path, encoded_path: Path) -> dict[str, object]:
    with Image.open(original_path) as original_image, Image.open(encoded_path) as encoded_image:
        same_size = original_image.size == encoded_image.size
        same_mode = original_image.mode == encoded_image.mode
        changed_pixels = (
            count_changed_pixels(original_image, encoded_image)
            if same_size
            else "unknown"
        )

        return {
            "same_size": same_size,
            "same_mode": same_mode,
            "original_size": original_image.size,
            "encoded_size": encoded_image.size,
            "original_mode": original_image.mode,
            "encoded_mode": encoded_image.mode,
            "changed_pixels": changed_pixels,
        }

#Decides where the output images will be saved and how they will be named.
def build_output_path(image_path: Path, output_path: Path | None) -> Path:
    if output_path is not None:
        return output_path
    return image_path.with_name(f"{image_path.stem}_hidden{image_path.suffix.lower()}")

#Decryption function that reveals the hidden message from the image.
def reveal_message(image_path: Path, save_path: Path | None) -> str:
    require_existing_file(image_path, "Encoded image")
    ensure_supported_image(image_path)

    revealed_message = lsb.reveal(str(image_path))
    if revealed_message is None:
        raise ValueError("No hidden message was found in that image.")

    print("\nHidden message:")
    print(revealed_message)

    if save_path is not None:
        save_path.write_text(revealed_message, encoding="utf-8")
        print(f"\nRecovered message saved to: {save_path}")

    return revealed_message

#Collects all supported images from the specified folder and returns them as a list of paths.
def list_images(dataset_dir: Path) -> list[Path]:
    if not dataset_dir.exists():
        return []

    image_files = [
        path
        for path in dataset_dir.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_IMAGE_TYPES
    ]
    return sorted(image_files)

#For our decryption algorithm, checks whether an encoded image is valid
def verify_hidden_message(
    original_image: Path,
    encoded_image: Path,
    expected_message: str,
) -> dict[str, object]:
    comparison = compare_images(original_image, encoded_image)
    revealed_message = lsb.reveal(str(encoded_image))
    message_matches = revealed_message == expected_message

    return {
        **comparison,
        "message_matches": message_matches,
    }

#This function hides the same message inside every image in the dataset folder.
def batch_hide_messages(dataset_dir: Path, message_path: Path, output_dir: Path) -> None:
    image_files = list_images(dataset_dir)
    if not image_files:
        raise ValueError(
            f"No supported images were found in {dataset_dir}. Add PNG or BMP files first."
        )

    message = read_message(message_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    success_count = 0
    failure_count = 0
    failed_files: list[str] = []

    print(f"\nFound {len(image_files)} supported image(s) in: {dataset_dir}")
    print(f"Encoded files will be saved to: {output_dir}")

    for image_path in image_files:
        output_file = output_dir / f"{image_path.stem}_hidden{image_path.suffix.lower()}"

        try:
            secret_image = lsb.hide(str(image_path), message)
            secret_image.save(str(output_file))

            verification = verify_hidden_message(image_path, output_file, message)
            image_ok = (
                verification["same_size"]
                and verification["same_mode"]
                and verification["message_matches"]
            )

            if image_ok:
                success_count += 1
                print(f"[SUCCESS] {image_path.name} -> {output_file.name}")
            else:
                failure_count += 1
                failed_files.append(image_path.name)
                print(f"[FAILED] {image_path.name} -> verification failed")
        except Exception as error:
            failure_count += 1
            failed_files.append(f"{image_path.name}: {error}")
            print(f"[FAILED] {image_path.name} -> {error}")

    print("\nBatch summary:")
    print(f"- Total images processed: {len(image_files)}")
    print(f"- Successful encodes    : {success_count}")
    print(f"- Failed encodes        : {failure_count}")

    if failed_files:
        print("\nFiles with issues:")
        for entry in failed_files:
            print(f"- {entry}")

# This function creates example commands shown in the help menu.
def format_examples(image_files: Iterable[Path]) -> str:
    first_image = next(iter(image_files), None)

    sample_image = first_image.name if first_image else "your_image.png"

    return (
        "Examples:\n"
        f"  python steganography_tool.py hide --image DATASET/{sample_image}\n"
        "  python steganography_tool.py batch-hide\n"
        f"  python steganography_tool.py reveal --image ENCODED/{Path(sample_image).stem}_hidden.png\n"
        "  python steganography_tool.py reveal --image ENCODED/your_image_hidden.png --save recovered_message.txt"
    )

#Makes our command-line parser
def build_parser() -> argparse.ArgumentParser:
    dataset_images = list_images(DEFAULT_DATASET_DIR)
    parser = argparse.ArgumentParser(
        description="Hide and reveal text messages inside images with the Stegano library.",
        epilog=format_examples(dataset_images),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    hide_parser = subparsers.add_parser("hide", help="Hide the contents of a text file in an image.")
    hide_parser.add_argument(
        "--image",
        type=Path,
        required=True,
        help="Path to a PNG or BMP image, for example DATASET/sample.png",
    )
    hide_parser.add_argument(
        "--message",
        type=Path,
        default=DEFAULT_MESSAGE_FILE,
        help="Path to the text file to hide. Defaults to message.txt in the project folder.",
    )
    batch_parser = subparsers.add_parser(
        "batch-hide",
        help="Hide the same text file in every PNG or BMP image inside a folder.",
    )
    batch_parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET_DIR,
        help="Folder containing source images. Defaults to DATASET in the project folder.",
    )
    batch_parser.add_argument(
        "--message",
        type=Path,
        default=DEFAULT_MESSAGE_FILE,
        help="Path to the text file to hide. Defaults to message.txt in the project folder.",
    )
    batch_parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_BATCH_OUTPUT_DIR,
        help="Folder where encoded images will be saved. Defaults to ENCODED in the project folder.",
    )

    reveal_parser = subparsers.add_parser("reveal", help="Reveal a hidden message from an image.")
    reveal_parser.add_argument(
        "--image",
        type=Path,
        required=True,
        help="Path to the PNG or BMP image that contains the hidden message.",
    )
    reveal_parser.add_argument(
        "--save",
        type=Path,
        help="Optional file path to save the recovered message.",
    )

    return parser

#Our Main Function
def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "hide":
            hide_message(args.image, args.message, args.output)
        elif args.command == "batch-hide":
            batch_hide_messages(args.dataset, args.message, args.output_dir)
        elif args.command == "reveal":
            reveal_message(args.image, args.save)
    except Exception as error:
        parser.exit(status=1, message=f"\nError: {error}\n")


if __name__ == "__main__":
    main()
