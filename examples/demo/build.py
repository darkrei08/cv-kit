"""Build the demonstration CV and check the result.

Run it directly to see the whole pipeline:

    python examples/demo/build.py            # documents and, if possible, PDFs
    python examples/demo/build.py --no-pdf   # documents only, no office suite needed

This is also what continuous integration runs, so it must never depend on a real
person's data: the assets it needs are generated here.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(HERE))

import cv_data  # noqa: E402  (imported after sys.path is set)

from cvkit.builder import build_all  # noqa: E402
from cvkit.qa import qa_cv  # noqa: E402

ASSETS = HERE / "assets"
PORTRAIT = ASSETS / "placeholder-portrait.jpg"
SIGNATURE = ASSETS / "placeholder-signature.png"


def make_assets() -> None:
    """Generate a neutral portrait and a signature mark.

    A grey rectangle with a slightly darker head-and-shoulders shape: obviously not a
    person, which is the point — the demonstration must not look like a real CV.
    """
    from PIL import Image, ImageDraw

    ASSETS.mkdir(parents=True, exist_ok=True)
    if not PORTRAIT.exists():
        image = Image.new("RGB", (413, 531), (232, 236, 240))
        draw = ImageDraw.Draw(image)
        draw.ellipse((140, 90, 273, 240), fill=(180, 188, 196))
        draw.polygon([(83, 531), (330, 531), (300, 300), (113, 300)],
                     fill=(180, 188, 196))
        image.save(PORTRAIT, "JPEG", quality=92, dpi=(300, 300))
    if not SIGNATURE.exists():
        image = Image.new("RGB", (600, 200), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        draw.line([(30, 150), (90, 60), (150, 160), (230, 70), (330, 150),
                   (430, 60), (560, 140)], fill=(20, 20, 20), width=5)
        image.save(SIGNATURE, "PNG", dpi=(300, 300))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-pdf", action="store_true",
                        help="write .docx only (no office suite required)")
    parser.add_argument("--output", default=None)
    args = parser.parse_args(argv)

    make_assets()
    cv = cv_data.cv
    cv.contact.photo = str(PORTRAIT)
    cv.contact.signature = str(SIGNATURE)

    out = Path(args.output) if args.output else HERE / "out"
    exports = ("docx",) if args.no_pdf else ("docx", "pdf")
    result = build_all(cv, out, exports=exports, timeline_png=None, asset_dir=HERE)
    for note in result.notes:
        print(f"note: {note}")

    print(f"built {len(result.files)} file(s) in {out}:")
    for kind, path in sorted(result.files.items()):
        print(f"  {path.name:44s} {kind}")

    checks = {kind: path for kind, path in result.files.items()
              if path.suffix in {".pdf", ".docx"}}
    # Portal variants are capped at two pages, not required to fill two: a short
    # career legitimately fits on one page.
    reports = qa_cv(cv, checks, max_pages=2)

    print("\nquality checks")
    failures = 0
    for report in reports:
        print(report.text())
        if not report.ok:
            failures += 1
    if failures:
        print(f"\n{failures} file(s) failed")
        return 1
    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
