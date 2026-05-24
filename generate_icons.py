"""Generate PNG icons from SVG for PWA manifest.

Run: python generate_icons.py
Requires: pip install cairosvg (or Pillow)

If you don't have cairosvg, the app still works — just won't have
a pretty icon when added to home screen.
"""

import os

SVG_PATH = os.path.join(os.path.dirname(__file__), "static", "icon-192.svg")

def generate():
    try:
        import cairosvg
        for size in [192, 512]:
            out = os.path.join(os.path.dirname(__file__), "static", f"icon-{size}.png")
            cairosvg.svg2png(url=SVG_PATH, write_to=out, output_width=size, output_height=size)
            print(f"Generated {out}")
    except ImportError:
        # Fallback: create simple solid-color PNGs with Pillow
        try:
            from PIL import Image, ImageDraw
            for size in [192, 512]:
                img = Image.new('RGB', (size, size), '#00a884')
                draw = ImageDraw.Draw(img)
                # Draw a simple "W" for WhatsApp
                cx, cy = size // 2, size // 2
                r = int(size * 0.35)
                draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline='white', width=max(3, size//50))
                out = os.path.join(os.path.dirname(__file__), "static", f"icon-{size}.png")
                img.save(out)
                print(f"Generated {out}")
        except ImportError:
            print("Install cairosvg or Pillow to generate icons:")
            print("  pip install cairosvg")
            print("  pip install Pillow")

if __name__ == "__main__":
    generate()
