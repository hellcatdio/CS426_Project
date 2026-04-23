import subprocess
from pathlib import Path
import datetime
import time
import csv

STEGHIDE_PATH = r"C:\Program Files (x86)\steghide\steghide.exe"

INPUT_DIR = Path("input_dataset")
OUTPUT_DIR = Path("output")
SECRET_FILE = Path("secret.txt")

LOG_FILE = Path("logs/logs.txt")
CSV_FILE = Path("reports/results.csv")

(OUTPUT_DIR / "steghide").mkdir(parents=True, exist_ok=True)
(OUTPUT_DIR / "extracted").mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(exist_ok=True)
CSV_FILE.parent.mkdir(exist_ok=True)


def log(message: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")


def run_steghide(image_path: Path, output_path: Path):
    supported_exts = [".jpg", ".jpeg", ".bmp"]

    if image_path.suffix.lower() not in supported_exts:
        log(f"Steghide | {image_path.name} | SKIPPED (unsupported format: {image_path.suffix})")
        return False, "unsupported_format", 0.0

    cmd = [
        STEGHIDE_PATH,
        "embed",
        "-cf", str(image_path),
        "-ef", str(SECRET_FILE),
        "-sf", str(output_path),
        "-p", ""
    ]

    start = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    end = time.time()

    elapsed = round(end - start, 4)
    success = (result.returncode == 0)

    log(f"Steghide | EMBED | {image_path.name} | rc={result.returncode} | time={elapsed}s")
    return success, result.returncode, elapsed


def extract_steghide(stego_image: Path, extracted_output: Path):
    cmd = [
        STEGHIDE_PATH,
        "extract",
        "-sf", str(stego_image),
        "-xf", str(extracted_output),
        "-p", "" 
    ]

    start = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    end = time.time()

    elapsed = round(end - start, 4)
    success = (result.returncode == 0)

    if success:
        log(f"Steghide | EXTRACT | {stego_image.name} | SUCCESS | time={elapsed}s")
    else:
        log(f"Steghide | EXTRACT | {stego_image.name} | FAIL rc={result.returncode} | stderr={result.stderr}")

    return success, result.returncode, elapsed


def main():
    images = list(INPUT_DIR.iterdir())

    if not images:
        print("No images found in input_dataset/.")
        return

    print(f"Processing {len(images)} images...")

    with open(CSV_FILE, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["image", "operation", "success", "return_code", "time_seconds"])

        for img in images:

            steghide_out = OUTPUT_DIR / "steghide" / img.name

            extracted_out = OUTPUT_DIR / "extracted" / f"{img.stem}_extracted.txt"

            success, rc, t = run_steghide(img, steghide_out)
            writer.writerow([img.name, "steghide_embed", success, rc, t])

            if success:
                success2, rc2, t2 = extract_steghide(steghide_out, extracted_out)
                writer.writerow([img.name, "steghide_extract", success2, rc2, t2])

    print("Processing complete. Check outputs/, logs/, and reports/.")

if __name__ == "__main__":
    main()
