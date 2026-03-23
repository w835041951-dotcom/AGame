#!/usr/bin/env python3
"""
generate_import_files.py
Scans asset directories for PNG files without .import files and generates them.
Safe to re-run: skips files that already have a .import file.
"""

import os
import hashlib

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))

ASSET_DIRS = [
    "assets/sprites/boss",
    "assets/sprites/bombs",
    "assets/sprites/vfx",
    "assets/sprites/ui",
    "assets/sprites/bg",
    "assets/sprites/story",
]

IMPORT_TEMPLATE = """\
[remap]

importer="texture"
type="CompressedTexture2D"
uid="{uid}"
path="res://.godot/imported/{basename}-{file_hash}.ctex"
metadata={{
"vram_texture": false
}}

[deps]

source_file="res://{rel_path}"
dest_files=["res://.godot/imported/{basename}-{file_hash}.ctex"]

[params]

compress/mode=0
compress/high_quality=false
compress/lossy_quality=0.7
compress/uastc_level=0
compress/rdo_quality_loss=0.0
compress/hdr_compression=1
compress/normal_map=0
compress/channel_pack=0
mipmaps/generate=false
mipmaps/limit=-1
roughness/mode=0
roughness/src_normal=""
process/channel_remap/red=0
process/channel_remap/green=1
process/channel_remap/blue=2
process/channel_remap/alpha=3
process/fix_alpha_border=true
process/premult_alpha=false
process/normal_map_invert_y=false
process/hdr_as_srgb=false
process/hdr_clamp_exposure=false
process/size_limit=0
detect_3d/compress_to=1
"""


def make_uid(rel_path: str) -> str:
    """
    Deterministic UID derived from the file's relative path.
    Format: uid://xxxxxxxxxxxxxxx  (13 lowercase alphanumeric chars)
    Godot uses base-62 style UIDs; we use a 13-char hex subset which is safe.
    """
    digest = hashlib.md5(rel_path.encode()).hexdigest()  # 32 hex chars
    # Take first 13 chars to mimic Godot UID length
    return "uid://" + digest[:13]


def make_file_hash(rel_path: str) -> str:
    """
    The .ctex filename contains a 32-char md5-like hash of the source path.
    We generate it deterministically from the relative path.
    """
    return hashlib.md5(rel_path.encode()).hexdigest()


def generate_import(png_abs: str) -> None:
    import_path = png_abs + ".import"
    if os.path.exists(import_path):
        print(f"  [skip] {os.path.basename(png_abs)} — .import already exists")
        return

    # Relative path from project root (forward slashes, no leading slash)
    rel_path = os.path.relpath(png_abs, PROJECT_ROOT).replace("\\", "/")
    basename = os.path.basename(png_abs)          # e.g. boss_lich.png
    file_hash = make_file_hash(rel_path)          # 32 hex chars
    uid = make_uid(rel_path)                       # uid://xxxxxxxxxxxxx

    content = IMPORT_TEMPLATE.format(
        uid=uid,
        basename=basename,
        file_hash=file_hash,
        rel_path=rel_path,
    )

    with open(import_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)

    print(f"  [created] {os.path.basename(import_path)}")


def main():
    created = 0
    skipped = 0

    for rel_dir in ASSET_DIRS:
        abs_dir = os.path.join(PROJECT_ROOT, rel_dir)
        if not os.path.isdir(abs_dir):
            print(f"[warn] directory not found, skipping: {abs_dir}")
            continue

        print(f"\nScanning: {rel_dir}")
        for fname in sorted(os.listdir(abs_dir)):
            if not fname.lower().endswith(".png"):
                continue
            png_abs = os.path.join(abs_dir, fname)
            import_abs = png_abs + ".import"
            if os.path.exists(import_abs):
                skipped += 1
                print(f"  [skip] {fname}")
            else:
                generate_import(png_abs)
                created += 1

    print(f"\nDone. Created: {created}, Skipped (already had .import): {skipped}")


if __name__ == "__main__":
    main()
