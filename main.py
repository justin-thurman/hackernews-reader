import json
from typing import TypedDict
from bs4 import BeautifulSoup
import requests


class HackerNewsSite(TypedDict):
    link: str
    title: str
    points: int | None  # job postings have no points
    position: int


def main():
    response = requests.get("https://news.ycombinator.com")
    response.raise_for_status()

    list_of_sites: list[HackerNewsSite] = []

    soup = BeautifulSoup(response.text, "html.parser")

    # HackerNews has a top-level `table` with two sub-`table` elements
    # The second subtable has the data we need. There are no CSS classes we
    # can use to grab the right table, so we must iterate.
    top_level_table = soup.find("table")
    assert top_level_table, "Top level table element not found"
    subtables = top_level_table.find_all("table", limit=2)
    assert len(subtables) == 2, f"Expected two subtables; got {len(subtables)}"
    subtable = subtables[1]

    # Within the subtable, each item is comprised of three `tr` elements:
    # 1. The title and link (CSS class: `athing`)
    # 2. The points and other metadata (No CSS class)
    # 3. A spacer
    # These elements do not have a parent `tr` element, so we must iterate through all of them.
    rows = subtable.find_all(
        "tr", class_=lambda el: el == "athing" or el is None, limit=60
    )
    assert len(rows) == 60, f"Expected 60 rows; got {len(rows)}"

    # iterate `i` by 2 to facilitate grabbing two items from the subtable on every loop
    for i in range(0, 60, 2):
        site: HackerNewsSite = {}

        primary_row = rows[i]
        points_row = rows[i + 1]

        rank = primary_row.find("span", class_="rank")
        assert rank, "Rank not found"
        rank = int(rank.text.replace(".", ""))
        site["position"] = rank

        titleline = primary_row.find("span", class_="titleline")
        assert titleline, "Titleline not found"
        site["title"] = titleline.text
        link = titleline.find("a")
        assert link, "Link not found"
        site["link"] = link.get("href")

        points = points_row.find("span", class_="score")
        if not points:
            site["points"] = None
            list_of_sites.append(site)
            continue
        points = int(points.text.replace(" points", ""))
        site["points"] = points

        list_of_sites.append(site)

    formatted_output = json.dumps(list_of_sites, indent=2)
    print(formatted_output)


if __name__ == "__main__":
    main()
