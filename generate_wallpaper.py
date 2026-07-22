#!/usr/bin/env python3
"""Generate a daily iPhone year-progress wallpaper."""

from __future__ import annotations

import argparse
import calendar
import math
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont


WIDTH = 1170
HEIGHT = 2532
TIMEZONE = "Asia/Tokyo"

BG = (8, 9, 10)
WHITE = (239, 239, 236)
MUTED = (125, 126, 126)
GRID = (77, 78, 77)
GOLD = (205, 169, 91)
GOLD_LIGHT = (227, 199, 135)

FONT_REGULAR_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
]
FONT_BOLD_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
]


def find_font(candidates: list[str]) -> str:
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    raise FileNotFoundError(
        "Japanese font not found. Install fonts-noto-cjk or edit FONT_*_CANDIDATES."
    )


REGULAR_FONT = find_font(FONT_REGULAR_CANDIDATES)
BOLD_FONT = find_font(FONT_BOLD_CANDIDATES)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(BOLD_FONT if bold else REGULAR_FONT, size)


def centered_text(
    draw: ImageDraw.ImageDraw,
    y: int,
    text: str,
    fnt: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
    spacing: int = 0,
) -> None:
    if spacing <= 0:
        box = draw.textbbox((0, 0), text, font=fnt)
        x = (WIDTH - (box[2] - box[0])) // 2
        draw.text((x, y), text, font=fnt, fill=fill)
        return

    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = (WIDTH - total) / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += w + spacing


def draw_metric(
    draw: ImageDraw.ImageDraw,
    cx: int,
    label: str,
    value: str,
    unit: str,
    accent: bool = False,
) -> None:
    label_font = font(31)
    value_font = font(70)
    unit_font = font(30)
    color = GOLD if accent else WHITE

    label_box = draw.textbbox((0, 0), label, font=label_font)
    draw.text(
        (cx - (label_box[2] - label_box[0]) / 2, 1960),
        label,
        font=label_font,
        fill=WHITE,
    )

    value_width = draw.textlength(value, font=value_font)
    unit_width = draw.textlength(unit, font=unit_font)
    gap = 10
    x = cx - (value_width + unit_width + gap) / 2
    draw.text((x, 2030), value, font=value_font, fill=color)
    draw.text((x + value_width + gap, 2077), unit, font=unit_font, fill=WHITE)


def generate(target_date: date, output_path: Path) -> None:
    year = target_date.year
    total_days = 366 if calendar.isleap(year) else 365
    day_of_year = target_date.timetuple().tm_yday
    remaining_days = total_days - day_of_year
    remaining_weeks = math.ceil(remaining_days / 7)
    total_weeks = math.ceil((total_days - 1) / 7)
    progress = round(day_of_year / total_days * 100)

    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)

    # Header: leave the upper area calm enough for the lock-screen clock.
    draw.line((180, 235, 390, 235), fill=GOLD, width=2)
    draw.line((780, 235, 990, 235), fill=GOLD, width=2)
    centered_text(draw, 175, str(year), font(88), WHITE, spacing=14)
    centered_text(draw, 305, "PROGRESS OF THE YEAR", font(29), WHITE, spacing=5)
    centered_text(draw, 385, "1年の進捗", font(33), GOLD)

    # One square per day: 26 columns × 15 rows accommodates leap years.
    cols = 26
    rows = math.ceil(total_days / cols)
    cell = 31
    gap = 8
    grid_width = cols * cell + (cols - 1) * gap
    start_x = (WIDTH - grid_width) // 2
    start_y = 680

    for i in range(total_days):
        row, col = divmod(i, cols)
        x0 = start_x + col * (cell + gap)
        y0 = start_y + row * (cell + gap)
        x1 = x0 + cell
        y1 = y0 + cell

        if i < day_of_year - 1:
            draw.rectangle((x0, y0, x1, y1), fill=GOLD_LIGHT)
        elif i == day_of_year - 1:
            draw.rectangle((x0, y0, x1, y1), fill=GOLD)
            draw.rectangle((x0 - 3, y0 - 3, x1 + 3, y1 + 3), outline=WHITE, width=3)
        else:
            draw.rectangle((x0, y0, x1, y1), outline=GRID, width=2)

    # Current day
    centered_text(draw, 1600, "今日は", font(31), WHITE)
    number_font = font(128)
    day_text = str(day_of_year)
    day_w = draw.textlength(day_text, font=number_font)
    unit_font = font(42)
    unit_w = draw.textlength("日目", font=unit_font)
    x = (WIDTH - day_w - unit_w - 14) / 2
    draw.line((135, 1718, 345, 1718), fill=MUTED, width=2)
    draw.line((825, 1718, 1035, 1718), fill=MUTED, width=2)
    draw.text((x, 1643), day_text, font=number_font, fill=GOLD_LIGHT)
    draw.text((x + day_w + 14, 1741), "日目", font=unit_font, fill=WHITE)

    # Metrics
    draw.line((390, 1945, 390, 2145), fill=MUTED, width=2)
    draw.line((780, 1945, 780, 2145), fill=MUTED, width=2)
    draw_metric(draw, 245, "残り日数", f"{remaining_days}/{total_days}", "日")
    draw_metric(draw, 585, "残り週間", f"{remaining_weeks}/{total_weeks}", "週間")
    draw_metric(draw, 925, "進捗率", str(progress), "%", accent=True)

    # Footer
    draw.line((135, 2245, 1035, 2245), fill=MUTED, width=2)
    centered_text(draw, 2295, "今日も、未来の自分への投資。", font(31), WHITE)
    centered_text(
        draw, 2360, "EVERY DAY IS A STEP TOWARD YOUR FUTURE.", font(21), GOLD, spacing=3
    )
    draw.line((135, 2432, 1035, 2432), fill=MUTED, width=2)
    centered_text(draw, 2462, "365 DAYS / MAKE IT COUNT", font(20), GOLD, spacing=5)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "PNG", optimize=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="output/latest.png")
    parser.add_argument(
        "--date",
        help="Date in YYYY-MM-DD. Default: current date in Asia/Tokyo.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    target_date = (
        date.fromisoformat(args.date)
        if args.date
        else datetime.now(ZoneInfo(TIMEZONE)).date()
    )
    generate(target_date, Path(args.output))
    print(f"Generated {args.output} for {target_date.isoformat()}")


if __name__ == "__main__":
    main()
