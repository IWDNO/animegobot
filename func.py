import asyncio
from aiogram import types
from typing import NamedTuple

import db
import parse
from parse import Anime


class AnimeList(NamedTuple):
    message: str
    markup: types.InlineKeyboardMarkup

#TODO: может проверочку получше?
async def verify_url(url: str) -> Anime | None:
    """ return `Anime` object if valid url else None """
    try:
        data = await parse.parse_anime(url)
        return data
    except:
        return
    

def add_anime_to_db(data: Anime, user) -> bool:
    """ Returns `True` if inserted and `Fasle` if already exists"""
    cursor = db.get_cursor()
    cursor.execute("SELECT id FROM watching_list WHERE user = ? AND anime_link = ?", (user, data.link))
    if cursor.fetchall():
        return False
    column_values = {
        'anime_link': data.link,
        'anime_name': data.name,
        'user': str(user),
        'watched': '0',
        'released_episodes': data.released_episodes,
        'total_episodes': data.total_episodes
    }
    db.insert('watching_list', column_values)
    return True


def update_user_episodes(id, action, message: str) -> str:
    cursor = db.get_cursor()
    cursor.execute("SELECT watched, released_episodes FROM watching_list WHERE id = ?", (id,))
    old_watched, released_episodes = cursor.fetchone()
    new_watched = max(0, min(eval(str(old_watched) + action), released_episodes))
    # update DB
    db.update('watching_list', id, 'watched', new_watched)
    # update message
    message = message.replace(f'Просмотрено: {old_watched}', f'Просмотрено: {new_watched}')
    return message


async def get_anime_list(user) -> AnimeList:
    """ Fetchall animes related to user id """
    user = str(user)
    anime_list = db.fetchall(table='watching_list', columns=['id', 'anime_link', 'watched'], column='user', column_id=user)

    tasks = []
    for anime in anime_list:
        tasks.append(asyncio.create_task(parse.parse_anime(anime['anime_link'])))
    parsed_anime = await asyncio.gather(*tasks)

    markup = types.InlineKeyboardMarkup()
    reply_message = []
    for new, old in zip(parsed_anime, anime_list):
        # update DB 
        db.update('watching_list', old['id'], 'released_episodes', new.released_episodes)
        db.update('watching_list', old['id'], 'total_episodes', new.total_episodes)
        db.update('watching_list', old['id'], 'next_episode_date', new.next_episode_date)
        # add button
        button = types.InlineKeyboardButton(text=new.name, callback_data=old['id'])
        markup.add(button)
        # check for updates
        if new.released_episodes > old['watched']:
            reply_message.append(f"{new.name} | *{new.released_episodes - old['watched']} Новых эпизодов* ({new.released_episodes} / {new.total_episodes})\n\n")
    # Кнопка для обновления
    markup.add( types.InlineKeyboardButton('🔄', callback_data='.update') )
    
    reply_message = ''.join(reply_message) if reply_message else 'Нет обновлений'
    return AnimeList(message=reply_message,
                     markup=markup)

    
def get_anime_info_message(id: str):
    """ get info about singe anime """
    id = str(id)
    columns = ['id', 'anime_name', 'anime_link', 'user', 'watched', 'released_episodes', 'total_episodes', 'next_episode_date']
    data = db.fetchall(table='watching_list', columns=columns, column='id', column_id=id)[0]

    keyboard = [
        [types.InlineKeyboardButton('⬅️1', callback_data=f'.-1/{id}'), types.InlineKeyboardButton('1➡️', callback_data=f'.+1/{id}')],
        [types.InlineKeyboardButton('⬅️10', callback_data=f'.-10/{id}'), types.InlineKeyboardButton('10➡️', callback_data=f'.+10/{id}')],
        [types.InlineKeyboardButton('Перейти', url=data['anime_link'])],
        [types.InlineKeyboardButton('Назад', callback_data='.back'), types.InlineKeyboardButton('Удалить', callback_data=f'.del/{id}')],
    ]
    markup = types.InlineKeyboardMarkup(inline_keyboard=keyboard)

    reply_message = (
        f'<b>{data["anime_name"]}</b>\n'
        f'{data["released_episodes"]} / {data["total_episodes"]}\n\n'
        f'Следующий эпизод:\n{data["next_episode_date"]}\n\n'
        f'Просмотрено: {data["watched"]} / {data["released_episodes"]}'
    )
    return AnimeList(message=str(reply_message),
                     markup=markup) 


def delete_anime(id):
    """ delete anime from DB """
    db.delete('watching_list', id)


if __name__ == '__main__':
    print(asyncio.run(verify_url('asd')))