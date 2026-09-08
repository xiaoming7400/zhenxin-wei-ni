"""检查静态展示页的资源、锚点和 SVG 格式，不替代浏览器视觉测试。"""

from html.parser import HTMLParser
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if "id" in values:
            assert values["id"] not in self.ids, f"Duplicate ID: {values['id']}"
            self.ids.add(values["id"])
        for key in ("src", "href"):
            if values.get(key):
                self.links.append(values[key])


def main():
    page = Page()
    page.feed((DOCS / "index.html").read_text(encoding="utf-8"))
    for link in page.links:
        if link.startswith("https://"):
            continue
        if link.startswith("#"):
            assert link == "#" or link[1:] in page.ids, f"Missing anchor: {link}"
        else:
            target = (DOCS / link).resolve()
            assert target.is_relative_to(DOCS.resolve()), f"Path escapes docs: {link}"
            assert target.is_file(), f"Missing asset: {link}"
    for asset in (DOCS / "assets").glob("*.svg"):
        ET.parse(asset)
    print(f"PASS: {len(page.links)} links/assets, unique IDs, anchors and SVG syntax")


if __name__ == "__main__":
    main()
