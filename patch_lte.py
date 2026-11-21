#!/usr/bin/env python3
"""
Aetheris 2.0 — SM-P619 (gta4xlvelte) AetherisOS 9.0 LTE Port Patcher
Audits stock SM-P619 (One UI 6.1) vs. port SM-P613 (One UI 9 Beta) files
and prepares the LTE/RIL patch list.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
STOCK_RAW = BASE_DIR / "stock_raw"
STOCK_EXT = BASE_DIR / "stock_extracted"
PORT_EXT = BASE_DIR / "port_extracted"
OUTPUT_DIR = BASE_DIR / "output"

LTE_KEYWORDS = (
    "ril", "qcril", "sec-ril", "radio", "modem", "ims",
    "telephony", "qmi", "diag", "rmnet", "ipa", "netmgr"
)


def check_directories():
    print("=== [1/5] Checking Project Folders ===")
    for folder in [STOCK_RAW, STOCK_EXT, PORT_EXT, OUTPUT_DIR]:
        if not folder.exists():
            print(f"[!] Creating missing folder: {folder.name}/")
            folder.mkdir(parents=True, exist_ok=True)
        else:
            print(f"[OK] {folder.name}/")


def check_stock_images():
    print("\n=== [2/5] Checking Stock SM-P619 Images ===")
    required_files = ["NON-HLOS.bin", "dtbo.img", "boot.img"]
    for fname in required_files:
        fpath = STOCK_EXT / fname
        if fpath.exists():
            size_mb = fpath.stat().st_size / (1024 * 1024)
            print(f"[OK] {fname} ({size_mb:.1f} MB)")
        else:
            print(f"[MISSING] {fname} — run Step 5 in README first.")


def inspect_port_structure():
    print("\n=== [3/5] Inspecting Base SM-P613 One UI 9 Port Files ===")
    items = sorted(PORT_EXT.iterdir())
    if not items:
        print("[MISSING] port_extracted/ is empty — run Step 6 in README first.")
        return

    for item in items:
        if item.is_file():
            size_mb = item.stat().st_size / (1024 * 1024)
            print(f"  - File: {item.name} ({size_mb:.1f} MB)")
        else:
            print(f"  - Dir:  {item.name}/")


def audit_vendor_ril():
    print("\n=== [4/5] Scanning for Missing LTE / RIL Blobs ===")
    stock_vendor = STOCK_EXT / "vendor"
    port_vendor = PORT_EXT / "vendor"

    if not stock_vendor.exists() or not port_vendor.exists():
        print("[INFO] Unpacked vendor/ folders not found yet.")
        print("       Once vendor.img partitions are extracted into stock_extracted/vendor")
        print("       and port_extracted/vendor, re-run this script to generate the LTE diff.")
        return

    stock_ril_files = set()
    for root, _, files in os.walk(stock_vendor):
        for f in files:
            if any(k in f.lower() for k in LTE_KEYWORDS):
                rel_path = Path(root).relative_to(stock_vendor) / f
                stock_ril_files.add(str(rel_path))

    missing_in_port = []
    for rel_str in sorted(stock_ril_files):
        if not (port_vendor / rel_str).exists():
            missing_in_port.append(rel_str)

    report_path = OUTPUT_DIR / "missing_lte_blobs.txt"
    with open(report_path, "w", encoding="utf-8") as out:
        for item in missing_in_port:
            out.write(item + "\n")

    print(f"[DONE] Found {len(missing_in_port)} LTE/RIL files in stock SM-P619 missing from SM-P613 port.")
    print(f"       Saved full report to: output/missing_lte_blobs.txt")


def check_vintf_manifests():
    print("\n=== [5/5] Checking One UI 9 VINTF Radio Manifests ===")
    port_manifest = PORT_EXT / "vendor" / "etc" / "vintf" / "manifest.xml"
    if not port_manifest.exists():
        print("[INFO] vendor/etc/vintf/manifest.xml not unpacked yet — skipping HAL check.")
        return

    content = port_manifest.read_text(encoding="utf-8", errors="ignore")
    if "android.hardware.radio" in content:
        print("[OK] Found radio HAL declarations in port vendor manifest.")
    else:
        print("[WARN] No android.hardware.radio HAL found in port manifest — will need SM-P619 radio HAL entries injected.")


if __name__ == "__main__":
    print("Aetheris 2.0 — AetherisOS 9.0 LTE Port Patcher (SM-P619 / gta4xlvelte)\n")
    check_directories()
    check_stock_images()
    inspect_port_structure()
    audit_vendor_ril()
    check_vintf_manifests()

