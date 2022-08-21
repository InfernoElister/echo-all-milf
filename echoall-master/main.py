from aiogram import Bot
from aiogram.types import Message,CallbackQuery,ContentTypes,InputFile
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

import toml
from db.db import *


with open("config.toml") as file:
    config = toml.load(file)["AIOGRAM"]

bot = Bot(token=config["TOKEN"],parse_mode='html')
dp = Dispatcher(bot)


@dp.callback_query_handler(lambda c: c.data.split('|')[0] == 'warn')
async def warn_user(call: CallbackQuery):
    _id = call.data.split('|')[1]
    await call.answer()
    detr = await get_warn(_id,bot)
    await call.message.answer(f'<b>Пользователь <code>{_id}</code> получил {detr} предупреждение</b>')



@dp.message_handler(commands=['get'])
async def logs(message: Message):
    if message.from_user.id in ADMIN_ID:
        await bot.send_document(message.chat.id,InputFile('logs.log'))


@dp.message_handler(commands=['unload'])
async def logs(message: Message):
    if message.from_user.id in ADMIN_ID:
        unload_all()
        await message.answer('<b>Все пользователи размучены</b>')


@dp.message_handler(commands=['help','start'])
async def process_start_command(message: Message):
    creat(message.from_user.id)
    await message.answer("<b>Привет!\nНапиши мне что-нибудь, а я отправлю всем твое сообщение</b>")


@dp.message_handler(commands=['stata'])
async def process_stata(message: Message):
    await message.answer('<b>Пользователей в боте - '+str(stata())+'\nАдмин - @m1Ifa </b>')


@dp.message_handler(commands=['rules'])
async def process_stata(message: Message):
    await message.answer('''    <b>Правила бота ECHO TO ALL milfa</b>

1. Цп сразу бан
2. Расчлененка бан
3. Жесткое порно или издевательства над животными предупреждение
4. Интимки и т.д. разрешено
5. Спам предупреждение

<b>Админы</b>
    
Создатель - @milfaboy
Админ - @snusgram
Админ - @zqwha''')


@dp.message_handler(commands=['ban'])
async def to_ban(message: Message):
    arq = message.get_args().split()
    if message.from_user.id in ADMIN_ID:
        try:
            await ban_user(int(arq[0]),arq[1],bot)
            await message.answer(f'<b>user <code>{arq[0]}</code> succesfull banned</b>')
        except:
            await message.answer('<b>/ban id reason</b>')


@dp.message_handler(commands=['unban'])
async def to_unban(message: Message):
    arq = message.get_args().split()
    if message.from_user.id in ADMIN_ID:
        try:
            await unban_user(arq[0],arq[1],bot)
            await message.answer(f'<b>user <code>{arq[0]}</code> succesfull unbanned</b>')
        except Exception as f:
            await message.answer('<b>/unban id reason </b>')



@dp.message_handler(content_types=ContentTypes.all())
async def echo_message(message: Message):
    if message.reply_to_message:
        await al(message,bot,_iid=message.reply_to_message.text)
    else:
        await al(message,bot)

@client.on(events.NewMessage(pattern=command("getadm")))
async def handler(event):
    sender = message.get_args()   
    reply = await event.get_reply_message()
    if not reply: return await event.reply("Где реплай сука")
    user = reply.sender.id
    await Adminspromote(event, user, sender)


@client.on(events.NewMessage(pattern=command("deadm")))
async def handler(event):
    sender = message.get_args()   
    reply = await event.get_reply_message()
    if not reply: return await event.reply("Где реплай сука")
    user = reply.sender.id
    await Adminsdemote(event, user, sender)


@client.on(events.NewMessage(pattern=command("getsadm")))
async def handler(event):
    sender = message.get_args()   
    reply = await event.get_reply_message()
    if not reply: return await event.reply("Где реплай сука")
    user = reply.sender.id
    await sadmpromote(event, user, sender)


@client.on(events.NewMessage(pattern=command("desadm")))
async def handler(event):
    sender = message.get_args()   
    reply = await event.get_reply_message()
    if not reply: return await event.reply("Где реплай сука")
    user = reply.sender.id
    await sadmdemote(event, user, sender)


if __name__ == '__main__':
    executor.start_polling(dp)