from aiogram import Bot, Dispatcher, executor, types
import re

import func


API_TOKEN = '5457465685:AAH06wsBGJZZ8BHm0Ee457Y8zh8oA31MpJI'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['help', 'start'])
async def help(message: types.Message):
    """ Say Hello """
    await message.answer(
        "Для добавления аниме в список нужно отправить сообщение с ссылкой на это аниме с сайта animego.org"
        "\n\nСписок команд:"
        "\n/list - Посмотреть добавленные аниме"
        "\n/help | /start - Если потеряется это сообщение"
        "\n\nP.S. Подтверждений для действий (например удаления) нигде нет"
        "\nP.P.S. Пожалуйста пишите мне при обнаружении ошибок (только не по поводу моего говно-хостинга и большого времени ожидания)" 
    )


@dp.message_handler(lambda message: message.text.startswith('https://'))
async def add(message: types.Message):
    """ Verifies url and adds to DB """
    data = await func.verify_url(message.text)
    if not data:
        await message.answer("Неверная ссылка")
        return
    result = func.add_anime_to_db(data, message.from_user.id)
    if not result:
        await message.answer("Уже добавлено")
        return
    await message.answer(
        f'{data.name}  -  {data.released_episodes} / {data.total_episodes}\n'
        f'{data.next_episode_date}\n\n'
        '*Добавлено!!!*\n'
        'Полный список - /list',
        parse_mode='markdown'
    )


@dp.message_handler(commands=['list'])
async def view(message: types.Message):
    """ view the list of added anime """
    reply_data = await func.get_anime_list(message.from_user.id)
    await message.answer(text=reply_data.message,
                        reply_markup=reply_data.markup,
                        parse_mode='markdown')


@dp.callback_query_handler(lambda call: str(call.data).isdigit())
async def cb(call: types.CallbackQuery):
    reply_data = func.get_anime_info_message(str(call.data))
    await call.message.edit_text(reply_data.message, reply_markup=reply_data.markup, parse_mode='html')


@dp.callback_query_handler(lambda call: str(call.data).startswith('.'))
async def cb1(call: types.CallbackQuery):
    task = str(call.data)[1:]
    if re.match(r'^[+-]\d+.*$', task):
        try:
            new_message = func.update_user_episodes(task.split('/')[1], task.split('/')[0], call.message.text)
            await call.message.edit_text(new_message, reply_markup=call.message.reply_markup)
        except:
            await call.answer('Нельзя :)')
    elif task == 'back':
        new_message_data = await func.get_anime_list(call['from']['id'])
        await call.message.edit_text(new_message_data.message, reply_markup=new_message_data.markup, parse_mode='markdown')
    elif task.startswith('del'):
        func.delete_anime(task.split('/')[1])
        new_message_data = await func.get_anime_list(call['from']['id'])
        await call.message.edit_text(new_message_data.message, reply_markup=new_message_data.markup, parse_mode='markdown')
    elif task == 'update':
        try:
            new_message_data = await func.get_anime_list(call['from']['id'])
            await call.message.edit_text(new_message_data.message, reply_markup=new_message_data.markup, parse_mode='markdown')
        except:
            await call.answer('Всё гуд')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)