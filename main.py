from icecream import ic
from bs4 import BeautifulSoup
import requests
import snoop


def main():
    ret = []
    response = requests.get("https://news.ycombinator.com")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    title_and_links = soup.find_all("span", class_="titleline")
    for item in title_and_links:
        element = {}
        element["title"] = item.text
        element["link"] = item.find("a").get("href")
        # position, points
        ret.append(element)
    ranks = soup.find_all("span", class_="rank")
    assert len(ranks) == 30, len(ranks)
    for i, rank in enumerate(ranks):
        rank = rank.text
        rank = rank.replace(".", "")
        element = ret[i]
        element["position"] = int(rank)

    subtexts = soup.find_all("td", class_="subtext")
    assert len(subtexts) == 30, len(subtexts)
    for i, subtext in enumerate(subtexts):
        score = subtext.find("span", class_="score")
        if not score:
            continue
        score = score.text
        score = score.replace(" points", "")
        element = ret[i]
        element["points"] = int(score)
    ic(ret)
    for item in ret:
        if "points" not in item:
            ic(item)


if __name__ == "__main__":
    main()
