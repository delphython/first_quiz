import logging
import os

from dotenv import load_dotenv
from vkbottle.bot import Bot, Message
from vkbottle import BaseStateGroup, Keyboard, Text, VKAPIError
from vkbottle import CtxStorage
from vkbottle.modules import logger

load_dotenv()

token = os.environ["TOKEN"]

bot = Bot(token)
ctx = CtxStorage()
logging.basicConfig(level=logging.INFO)


class RegData(BaseStateGroup):
    NAME = 0
    AGE = 1
    WEIGHT = 2
    HEIGHT = 3
    TOWN = 4
    CORRECT_WEIGHT = 5
    INFO_METHOD = 6
    VK_PAGE = 7


@bot.on.message(lev="/reg")
async def reg_handler(message: Message):
    await bot.state_dispenser.set(message.peer_id, RegData.NAME)
    return "Введите ваше имя"


@bot.on.message(state=RegData.NAME)
async def name_handler(message: Message):
    ctx.set("name", message.text)
    await bot.state_dispenser.set(message.peer_id, RegData.AGE)
    return "Введите ваш возраст"


@bot.on.message(state=RegData.AGE)
async def age_handler(message: Message):
    ctx.set("age", message.text)
    await bot.state_dispenser.set(message.peer_id, RegData.WEIGHT)
    return "Введите ваш вес"


@bot.on.message(state=RegData.WEIGHT)
async def weight_handler(message: Message):
    ctx.set("weight", message.text)
    await bot.state_dispenser.set(message.peer_id, RegData.HEIGHT)
    return "Введите ваш рост"


@bot.on.message(state=RegData.HEIGHT)
async def height_handler(message: Message):
    ctx.set("height", message.text)
    await bot.state_dispenser.set(message.peer_id, RegData.TOWN)
    return "Город проживания"


@bot.on.message(state=RegData.TOWN)
async def town_handler(message: Message):
    ctx.set("town", message.text)
    await bot.state_dispenser.set(message.peer_id, RegData.CORRECT_WEIGHT)
    return "На какое колиичество кг хотите скорректировать вес?"


@bot.on.message(state=RegData.CORRECT_WEIGHT)
async def correct_weight_handler(message: Message):
    ctx.set("correct_weight", message.text)
    await message.answer(
        "Способ получения информации",
        keyboard=(
            Keyboard(one_time=True)
            .add(Text("WhatsApp"))
            .add(Text("Telegram"))
            .get_json()
        ),
    )
    await bot.state_dispenser.set(message.peer_id, RegData.INFO_METHOD)
    # return "Способ получения информации"


@bot.on.message(state=RegData.INFO_METHOD)
async def info_method_handler(message: Message):
    ctx.set("info_method", message.text)
    await bot.state_dispenser.set(message.peer_id, RegData.VK_PAGE)
    return "Ссылка на вашу страничку вконтакте (желательно)"


@bot.on.message(state=RegData.VK_PAGE)
async def vk_page_handler(message: Message):
    name = ctx.get("name")
    age = ctx.get("age")
    weight = ctx.get("weight")
    height = ctx.get("height")
    town = ctx.get("town")
    correct_weight = ctx.get("correct_weight")
    info_method = ctx.get("info_method")
    vk_page = message.text

    nessage_text = f"""
        Имя: {name}
        Возраст: {age}
        Вес: {weight}
        Рост: {height}
        Город: {town}
        Коррекция веса: {correct_weight}
        Способ получения информации: {info_method}
        Страницв ВКонтакте: {vk_page}
        """

    await message.answer(nessage_text)

    try:
        await bot.api.messages.send(
            peer_id=19266191,
            message=nessage_text,
            random_id=0,
        )
    except VKAPIError[901]:
        logger.error("Can't send message to user with id {}", event.object.user_id)

    return "Регистрация прошла успешно"


bot.run_forever()
