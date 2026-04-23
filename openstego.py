import subprocess
from pathlib import Path
import datetime
import time
import csv
import shutil

OPENSTEGO_JAR = Path("openstego.jar")
SECRET_FILE = Path("secret.txt")

INPUT_DIR = Path("input_dataset")
RESULTS_DIR = Path("results_openstego")
EXTRACT_DIR = Path("extracted_openstego")

LOG_FILE = Path("logs/openstego_logs.txt")
CSV_FILE = Path("reports/openstego_results.csv")

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(exist_ok=True)
CSV_FILE.parent.mkdir(exist_ok=True)

def log(message: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")


def run_openstego_embed(cover_image: Path, stego_output: Path):
    cmd = [
        "java", "-jar", str(OPENSTEGO_JAR),
        "embed",
        "-a", "RandomLSB",
        "-mf", str(SECRET_FILE),
        "-cf", str(cover_image),
        "-sf", str(stego_output)
    ]

    start = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    end = time.time()

    elapsed = round(end - start, 4)
    success = (result.returncode == 0)

    if success:
        log(f"OpenStego | EMBED | {cover_image.name} | SUCCESS | time={elapsed}s")
    else:
        log(f"OpenStego | EMBED | {cover_image.name} | FAIL rc={result.returncode} | stderr={result.stderr}")

    return success, result.returncode, elapsed


def run_openstego_extract(stego_image: Path, extracted_output: Path):
    cmd = [
        "java", "-jar", str(OPENSTEGO_JAR),
        "extract",
        "-sf", str(stego_image),
        "-xf", str(extracted_output)
    ]

    start = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    end = time.time()

    elapsed = round(end - start, 4)
    success = (result.returncode == 0)

    if success:
        log(f"OpenStego | EXTRACT | {stego_image.name} | SUCCESS | time={elapsed}s")
    else:
        log(f"OpenStego | EXTRACT | {stego_image.name} | FAIL rc={result.returncode} | stderr={result.stderr}")

    return success, result.returncode, elapsed



def main():
    images = list(INPUT_DIR.iterdir())

    if not images:
        print("No images found in input_dataset/.")
        return

    print(f"Processing {len(images)} images with OpenStego...")

    with open(CSV_FILE, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["image", "operation", "success", "return_code", "time_seconds"])


        for img in images:

            temp_path = Path(img.name)
            shutil.move(str(img), temp_path)

            stego_output = RESULTS_DIR / f"{img.stem}_openstego.png"

            success, rc, t = run_openstego_embed(temp_path, stego_output)
            writer.writerow([img.name, "embed", success, rc, t])

            shutil.move(str(temp_path), INPUT_DIR / img.name)


        stego_images = list(RESULTS_DIR.iterdir())

        for stego in stego_images:

            temp_stego = Path(stego.name)
            shutil.move(str(stego), temp_stego)

            extracted_output = EXTRACT_DIR / f"{stego.stem}_extracted.txt"

            success, rc, t = run_openstego_extract(temp_stego, extracted_output)
            writer.writerow([stego.name, "extract", success, rc, t])

            shutil.move(str(temp_stego), RESULTS_DIR / stego.name)

    print("OpenStego embedding + extraction complete. Check results_openstego/, extracted_openstego/, logs/, and reports/.")

if __name__ == "__main__":
    main()
