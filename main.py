#!/usr/bin/env python3
"""Copy the pre-rendered front page to the output directory.

Standard library only. The image is drawn at build time by render.py;
this program just copies entry.png beside it to $MAKEFUN_OUTPUT_DIR
(default /output) as entry.png, and fails if the copy is not identical.
"""
import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SRC, dst)
    # Size guard first, then a byte-level guard: the copy must be exact.
    if os.path.getsize(dst) != os.path.getsize(SRC):
        print("copy size mismatch", file=sys.stderr)
        return 1
    if sha256(dst) != sha256(SRC):
        print("copy hash mismatch", file=sys.stderr)
        return 1
    print("wrote", dst, os.path.getsize(dst), "bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
