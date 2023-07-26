# import requests
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import NamedTuple, List


class Anime(NamedTuple):
    """ Структура хранения аниме"""
    link: str
    name: str 
    total_episodes: int 
    released_episodes: int 
    next_episode_date: str


async def parse_anime(url: str) -> Anime:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            soup = BeautifulSoup(await response.text(), 'lxml')

            name = soup.find('h1').text.strip()
            try:
                date = soup.find('dl').find_all('dd')[0].find('span').text.strip()
                episodes = soup.find('dl').find_all('dd')[3].text.strip()
                episodes = [ep.strip() for ep in episodes.split('/')]
                released_episodes = int(episodes[0]) if episodes[0].isdigit() else 99999
                total_episodes = int(episodes[1]) if episodes[1].isdigit() else 99999
            except:
                date = "Аниме вышло полностью!"
                released_episodes = int(soup.find('dl').find_all('dd')[1].text.strip())
                total_episodes = released_episodes
            

    return Anime(link=url,
                name=name,
                total_episodes=total_episodes,
                released_episodes=released_episodes,
                next_episode_date=date)


if __name__ == '__main__':
    print(asyncio.run(parse_anime('https://animego.org/anime/van-pis-65')))

# async def parse_anime(link: str) -> Anime:
#     response = requests.get(link).text
#     soup = BeautifulSoup(response, 'lxml')

#     name = soup.find('h1').text.strip()
#     episodes = soup.find('dl').find_all('dd')[3].text.strip()
#     released_episodes, total_episodes = [ep.strip() for ep in episodes.split('/')]
#     date = soup.find('dl').find_all('dd')[0].find('span').text.strip()

#     return Anime(link=link,
#                  name=name,
#                  total_episodes=total_episodes,
#                  released_episodes=released_episodes,
#                  next_episode_date=date)
