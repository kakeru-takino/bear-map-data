#!/usr/bin/env python3
"""KMLを今年(令和N年)のPlacemarkだけに絞り込む。

盛岡のKMLは各Placemarkの<name>に「令和6年4月12日」のように和暦の年が
入っているため、今年の和暦年に一致するものだけを残す。
雫石のKMLは<name>に年情報が無い(月日のみ)ため、フィルタせず全件を残す。
"""
import re
import sys
from datetime import datetime
from typing import Optional

# 令和の開始年(2019)。今年の西暦から令和Nを算出する。
REIWA_BASE = 2018


def main(src: str, dst: str, year: Optional[int] = None) -> None:
    if year is None:
        year = datetime.now().year
    reiwa = year - REIWA_BASE
    era_token = f"令和{reiwa}年"

    with open(src, encoding="utf-8") as f:
        text = f.read()

    placemarks = re.findall(r"<Placemark>.*?</Placemark>", text, re.S)

    # <name>に和暦年を持つPlacemarkが1件でもあれば年フィルタ対象(盛岡)とみなす。
    has_era = any(
        re.search(r"<name>\s*令和\d+年", pm) for pm in placemarks
    )

    if not has_era:
        # 雫石: 年情報が無いのでフィルタせずそのままコピー。
        with open(dst, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"{src}: 年情報なし、全{len(placemarks)}件をそのまま保存 -> {dst}")
        return

    kept = [pm for pm in placemarks if era_token in pm]

    # 元ファイルのPlacemark群を、今年分だけに差し替える。
    # 最初のPlacemarkの直前までをヘッダ、最後のPlacemark直後をフッタとして保持する。
    first = text.index("<Placemark>")
    last = text.rindex("</Placemark>") + len("</Placemark>")
    header, footer = text[:first], text[last:]
    body = "\n      ".join(kept)
    result = header + body + footer

    with open(dst, "w", encoding="utf-8") as f:
        f.write(result)
    print(
        f"{src}: {era_token}で絞り込み {len(kept)}/{len(placemarks)}件 -> {dst}"
    )


if __name__ == "__main__":
    # 第3引数で西暦年を指定可能(省略時は今年)。過去年のファイル化に使う。
    target_year = int(sys.argv[3]) if len(sys.argv) > 3 else None
    main(sys.argv[1], sys.argv[2], target_year)
