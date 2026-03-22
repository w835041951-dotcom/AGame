"""Generate bomb sprite PNGs for new bomb types."""
from PIL import Image, ImageDraw

BOMBS = {
    "pierce_h": (255, 242, 26),    # Yellow
    "pierce_v": (178, 242, 26),    # Green-Yellow
    "cross":    (230, 38, 38),     # Red
    "x_shot":   (255, 140, 13),    # Orange
    "bounce":   (26, 217, 217),    # Cyan
}

SIZE = 32

def draw_bomb(name, color):
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Outer circle
    dark = tuple(max(0, int(c * 0.7)) for c in color)
    draw.ellipse([4, 4, 28, 28], fill=dark + (255,))
    # Inner circle highlight
    draw.ellipse([7, 6, 23, 22], fill=color + (255,))
    # Highlight spot
    light = tuple(min(255, int(c * 1.5)) for c in color)
    draw.rectangle([12, 10, 16, 13], fill=light + (180,))
    # Fuse
    draw.rectangle([21, 4, 23, 10], fill=(204, 178, 51, 255))
    img.save(f"assets/sprites/bombs/{name}.png")

for name, col in BOMBS.items():
    draw_bomb(name, col)
    print(f"  Generated {name}.png")

print("Done!")
