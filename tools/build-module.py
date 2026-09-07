#!/usr/bin/env python3
"""
Build the HiBy R4 Android Auto Magisk module locally.

This script intentionally does NOT download AndroidAutoStub.apk.
The user must extract a compatible copy from a device they own and place it at:

    module/system/product/priv-app/AndroidAutoStub/AndroidAutoStub.apk
"""

from pathlib import Path
import hashlib
import sys
import zipfile

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODULE_ROOT = PROJECT_ROOT / "module"
MODULE_PROP = MODULE_ROOT / "module.prop"
PERMISSION_XML = (
    MODULE_ROOT
    / "system"
    / "product"
    / "etc"
    / "permissions"
    / "privapp-permissions-r4-androidauto.xml"
)
STUB_APK = (
    MODULE_ROOT
    / "system"
    / "product"
    / "priv-app"
    / "AndroidAutoStub"
    / "AndroidAutoStub.apk"
)

DIST_DIR = PROJECT_ROOT / "dist"
OUTPUT_ZIP = DIST_DIR / "R4-AndroidAuto-Enabler-v1.1.zip"

KNOWN_GOOD_STUB_VERSION = "1.2.558700-stub"
KNOWN_GOOD_STUB_SIZE = 3_953_532
KNOWN_GOOD_STUB_SHA256 = (
    "57ea6d176178e52fedb8b351441141aefaf8b6e98cfbed10a9fa1b006a608072"
)

REQUIRED_FILES = (
    MODULE_PROP,
    PERMISSION_XML,
    STUB_APK,
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fail(message: str) -> None:
    print()
    print(f"ERROR: {message}")
    sys.exit(1)


def validate_source_tree() -> None:
    for path in REQUIRED_FILES:
        if not path.is_file():
            relative = path.relative_to(PROJECT_ROOT)
            fail(f"Required file not found: {relative}")

    if STUB_APK.stat().st_size == 0:
        fail("AndroidAutoStub.apk is empty.")


def inspect_stub() -> tuple[int, str]:
    size = STUB_APK.stat().st_size
    digest = sha256_file(STUB_APK)

    print("AndroidAutoStub.apk")
    print("-------------------")
    print(f"Size:    {size:,} bytes")
    print(f"SHA-256: {digest}")
    print()
    print("Known-good Oscar/Lyra development reference")
    print("-------------------------------------------")
    print(f"Version: {KNOWN_GOOD_STUB_VERSION}")
    print(f"Size:    {KNOWN_GOOD_STUB_SIZE:,} bytes")
    print(f"SHA-256: {KNOWN_GOOD_STUB_SHA256}")
    print()

    if size == KNOWN_GOOD_STUB_SIZE and digest.lower() == KNOWN_GOOD_STUB_SHA256:
        print("REFERENCE STATUS: MATCHES KNOWN-GOOD STUB")
    else:
        print("REFERENCE STATUS: UNTESTED STUB VERSION")
        print()
        print("This does NOT prove the APK is bad.")
        print("It means this exact binary was not the one validated by the project.")
        print("Verify its package identity/version and proceed only if you accept that")
        print("you are testing a new variable.")

    return size, digest


def module_files() -> list[Path]:
    files = []

    for path in MODULE_ROOT.rglob("*"):
        if not path.is_file():
            continue

        # Do not package repository instructions/placeholders.
        if path.name == "PUT_ANDROID_AUTO_STUB_HERE.txt":
            continue

        files.append(path)

    return sorted(files)


def validate_archive_name(name: str) -> None:
    if "\\" in name:
        fail(f"Refusing unsafe ZIP entry containing a backslash: {name}")

    if name.startswith("/") or name.startswith("../") or "/../" in name:
        fail(f"Refusing unsafe ZIP entry: {name}")


def build_zip(files: list[Path]) -> None:
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    if OUTPUT_ZIP.exists():
        OUTPUT_ZIP.unlink()

    with zipfile.ZipFile(
        OUTPUT_ZIP,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for source in files:
            # Magisk ZIP paths must be relative to the module root and use POSIX "/".
            archive_name = source.relative_to(MODULE_ROOT).as_posix()
            validate_archive_name(archive_name)
            archive.write(source, archive_name)

    # Re-open and independently verify every stored archive name.
    with zipfile.ZipFile(OUTPUT_ZIP, "r") as archive:
        names = archive.namelist()

    for name in names:
        validate_archive_name(name)

    expected = {
        "module.prop",
        "system/product/etc/permissions/privapp-permissions-r4-androidauto.xml",
        "system/product/priv-app/AndroidAutoStub/AndroidAutoStub.apk",
    }

    missing = expected.difference(names)
    if missing:
        fail(
            "Built ZIP is missing expected entries: "
            + ", ".join(sorted(missing))
        )

    zip_hash = sha256_file(OUTPUT_ZIP)

    print()
    print("Build complete")
    print("--------------")
    print(f"Output:  {OUTPUT_ZIP}")
    print(f"SHA-256: {zip_hash}")
    print()
    print("Archive entries:")

    for name in names:
        print(f"  {name}")

    print()
    print("POSIX PATH CHECK: PASS")
    print("No archive entry contains a Windows backslash.")
    print()
    print("Next:")
    print("  Follow docs/INSTALL.md")
    print("  Preflight the staged Magisk module BEFORE rebooting.")


def main() -> None:
    print("HiBy R4 Android Auto module builder")
    print("===================================")
    print()

    validate_source_tree()
    inspect_stub()

    files = module_files()

    if not files:
        fail("No module files found.")

    build_zip(files)


if __name__ == "__main__":
    main()
