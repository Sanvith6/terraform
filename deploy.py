import argparse
import random
import re
import string
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parent
LAMBDA_DIR = ROOT / "lambda"


def run(cmd):
    print(f"\n> {' '.join(cmd)}")
    subprocess.run(cmd, cwd=ROOT, check=True)


def package_lambda(py_file: Path, zip_file: Path):
    if not py_file.exists():
        raise FileNotFoundError(f"Missing Lambda source: {py_file}")
    with ZipFile(zip_file, "w", compression=ZIP_DEFLATED) as zf:
        zf.write(py_file, arcname=py_file.name)
    print(f"Packaged {zip_file.name}")


def sanitize_prefix(prefix: str) -> str:
    cleaned = re.sub(r"[^a-z0-9-]", "-", prefix.lower()).strip("-")
    if not cleaned:
        cleaned = "task-bucket"
    return cleaned[:30].strip("-")


def generate_bucket_name(prefix: str) -> str:
    safe_prefix = sanitize_prefix(prefix)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    name = f"{safe_prefix}-{stamp}-{suffix}"
    return name[:63].strip("-")


def main():
    parser = argparse.ArgumentParser(
        description="Package Lambda code and deploy Terraform with a unique bucket name."
    )
    parser.add_argument(
        "--bucket-name",
        help="Use an explicit bucket name. If omitted, a unique one is generated.",
    )
    parser.add_argument(
        "--bucket-prefix",
        default="task-bucket",
        help="Prefix used when generating a bucket name (default: task-bucket).",
    )
    parser.add_argument(
        "--skip-apply",
        action="store_true",
        help="Run terraform init + plan only.",
    )
    parser.add_argument(
        "--no-auto-approve",
        action="store_true",
        help="Require interactive confirmation for terraform apply.",
    )
    args = parser.parse_args()

    bucket_name = args.bucket_name or generate_bucket_name(args.bucket_prefix)
    print(f"Using bucket name: {bucket_name}")

    package_lambda(LAMBDA_DIR / "processor.py", LAMBDA_DIR / "processor.zip")
    package_lambda(LAMBDA_DIR / "daily_report.py", LAMBDA_DIR / "daily_report.zip")

    run(["terraform", "init"])
    run(["terraform", "plan", "-var", f"bucket_name={bucket_name}"])

    if not args.skip_apply:
        cmd = ["terraform", "apply", "-var", f"bucket_name={bucket_name}"]
        if not args.no_auto_approve:
            cmd.append("-auto-approve")
        run(cmd)
    else:
        print("Skipped terraform apply.")

    print(f"\nDone. Event uploads should target: s3://{bucket_name}/events/")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print(f"Command failed with exit code {exc.returncode}", file=sys.stderr)
        sys.exit(exc.returncode)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
