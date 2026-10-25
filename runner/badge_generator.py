"""
Badge Generator.
Generates SVG status badges for GitHub README and dashboards.
"""

import os
from html import escape


class BadgeGenerator:
    @staticmethod
    def generate_svg(label: str, status: str, color: str = "#4c1") -> str:
        """Generates standard SVG badge XML."""
        label, status, color = escape(label, quote=True), escape(status, quote=True), escape(color, quote=True)
        # Simple SVG pill template
        label_width = max(len(label) * 7 + 10, 50)
        status_width = max(len(status) * 7 + 10, 50)
        total_width = label_width + status_width

        label_x = label_width / 2
        status_x = label_width + (status_width / 2)

        return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="20" role="img" aria-label="{label}: {status}">
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r">
    <rect width="{total_width}" height="20" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#r)">
    <rect width="{label_width}" height="20" fill="#555"/>
    <rect x="{label_width}" width="{status_width}" height="20" fill="{color}"/>
    <rect width="{total_width}" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" text-rendering="geometricPrecision" font-size="110">
    <text aria-hidden="true" x="{label_x * 10}" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="{(label_width - 10) * 10}">{label}</text>
    <text x="{label_x * 10}" y="140" transform="scale(.1)" fill="#fff" textLength="{(label_width - 10) * 10}">{label}</text>
    <text aria-hidden="true" x="{status_x * 10}" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="{(status_width - 10) * 10}">{status}</text>
    <text x="{status_x * 10}" y="140" transform="scale(.1)" fill="#fff" textLength="{(status_width - 10) * 10}">{status}</text>
  </g>
</svg>"""

    @classmethod
    def save_conformance_badge(cls, label: str, passed: int, total: int, output_path: str, expected_failures: int = 0):
        """Generates and writes an SVG badge to file based on pass rate."""
        rate = (passed / total * 100) if total > 0 else 0
        if rate == 100:
            color = "#4c1" # Green
            status = f"{rate:.0f}% passing"
        elif rate >= 80:
            color = "#dfb317" # Yellow
            status = f"{rate:.0f}% passing"
        elif passed == 0 and expected_failures > 0 and (passed + expected_failures >= total):
            color = "#007ec6" # Blue
            status = "baseline accepted"
        else:
            color = "#e05d44" # Red
            status = f"{rate:.0f}% passing"

        svg_content = cls.generate_svg(label, status, color)
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        return output_path
