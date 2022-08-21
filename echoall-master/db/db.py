from peewee import *
from aiogram.utils.exceptions import RetryAfter,BotBlocked,ChatNotFound
from aiogram.types import InlineKeyboardButton,InlineKeyboardMarkup
from datetime import datetime,timedelta
from asyncio import sleep
import logging

import toml


with open("config.toml") as file:
    config = toml.load(file)["AIOGRAM"]

logging.basicConfig(filename='logs.log')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


db = SqliteDatabase('db/users.sqlite')

class Users(Model):
    id = PrimaryKeyField()
    ban = BooleanField(default=False)
    timer = DateTimeField()
    warns = IntegerField(default=0)

    class Meta:
        database = db

class Admins(Model):
    id = PrimaryKeyField()

    class Meta:
        database = db

class sadms(Model):
    id = IntegerField()

    class Meta:
        database = db

class Messages(Model):
    primary_id = PrimaryKeyField()
    all_id = TextField()

    class Meta:
        database = db

with db:
    db.create_tables([Users,Messages])

def creat(_id):
    if not Users.select().where(Users.id == _id).exists():
        logger.info(f'new user in db {_id}')
        Users.create(id=_id,timer = datetime.now()-timedelta(days=7))


def stata():
    return len(Users.select(Users.id))


def unload_all():
    Users.update(timer=datetime.now()-timedelta(seconds=1000))


async def ban_user(_id,whats,bot):
    logger.info(f'ban - {_id} {whats}')
    await bot.send_message(_id,f'<b>Вы забанены по причине: {whats}</b>')
    print(Users.update(ban=True).where(Users.id == _id).execute())

async def unban_user(_id,whats,bot):
    logger.info(f'unban - {_id} {whats}')
    await bot.send_message(_id,f'<b>Вы разбанены по причине: {whats}</b>')
    Users.update(ban=False).where(Users.id == _id).execute()

async def get_warn(_id,bot):
    def update_time(_id,sec):
        logger.info(f'new warn to {_id}')
        Users.update(timer=Users.get(Users.id==_id).timer + timedelta(seconds=sec)).where(Users.id == _id).execute()

    to_warn = Users.get(Users.id==_id).warns + 1
    Users.update(warns=to_warn).where(Users.id==_id).execute()

    if to_warn == 1:
        update_time(_id,120)
        await bot.send_message(_id,f'<b>Вы получили 1 предупреждение и замучены на 120 секунд</b>')

    if to_warn == 2:
        update_time(_id,3600)
        await bot.send_message(_id,f'<b>Вы получили 2 предупреждение и замучены на 3600 секунд</b>')

    if to_warn == 3:
        Users.update(ban=True).where(Users.id == _id).execute()
        await bot.send_message(_id,f'<b>Вы получили 3 предупреждение и забанены навсегда</b>')
    
    return to_warn
    

async def al(message,bot,_iid=None):
    send = Users.select(Users.id)
    try:
        wadmincheck = Admins.get_or_none(id=message.from_user.id)
        if datetime.now()<Users.get(Users.id==message.from_user.id).timer + timedelta(seconds=10) and wadmincheck is None:
            data = ((Users.get(Users.id==message.from_user.id).timer + timedelta(seconds=10))-datetime.now())
            await message.answer(f'<b>Ты сможешь отправить следущее сообщение через {data.seconds} секунд</b>')
            return
        else:
            Users.update(timer=datetime.now()).where(Users.id==message.from_user.id).execute()
    except:
        logger.info('new usre in db with send')
        creat(message.from_user.id)
        Users.update(timer=datetime.now()).where(Users.id==message.from_user.id).execute()
    if Users.get(Users.id==message.from_user.id).ban == True:
        await message.answer('<b>Вы забанены. По вопросам писать @m1Ifa</b>')
        return
    to = await message.answer(f'<b>Ваше сообщение будет отправлено {len(send)} юзерам</b>')
    try:
        text = len(message.text)
        if text > 2001:
            logger.warning('text > 2001 err')
            await to.edit_text('<b>Слишком большой текст</b>')
            return
    except TypeError:
        pass
    num=0
    for user in send:
        try:
            admincheck = Admins.get_or_none(id=int(user.id))
            if admincheck is not None:  
                if _iid:
                    await bot.send_message(user.id,f'>> {_iid}\n\n{message.text}',reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text=f'{message.from_user.id}',url='tg://settings'),InlineKeyboardButton(text=f'Предупреждение',callback_data=f'warn|{message.from_user.id}')))
                else:
                    await message.copy_to(user.id,reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text=f'{message.from_user.id}',url='tg://settings'),InlineKeyboardButton(text=f'Предупреждение',callback_data=f'warn|{message.from_user.id}')))
            
            qadmincheck = Admins.get_or_none(id=message.from_user.id)
            elif qadmincheck is not None:
                if _iid:
                    data = f'>> {_iid}\n\n'+message.text
                    await bot.send_message(user.id,data,reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text='ADMIN',url=f'tg://user?id={message.from_user.id}')))
                else:
                    await message.copy_to(user,reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text='ADMIN',url=f'tg://user?id={message.from_user.id}')))
            else:
                if _iid:
                    await bot.send_message(user.id,f'>> {_iid}\n\n{message.text}')
                else:
                    await message.copy_to(user)
            num+=1
        except RetryAfter:
            await logger.warning('flood wait 3 sec')
            await sleep(3)
        except (BotBlocked,ChatNotFound):
            Users.delete().where(Users.id == user).execute()
        except Exception as g:
            logger.exception(g)
    await to.edit_text(f'<b>Отправил ваше сообщение {num} юзерам</b><br>(это сообщение будет удалено через 5 сек)')
    await sleep(5)
    await to.delete()

async def Adminspromote(event, user, sender):
    admincheck = sadms.get_or_none(id=sender)
    if admincheck is None:  
        await event.reply("Ты не админ!")
    else:
        textObj, admincheckmsg = Admins.get_or_create(id=user)
        if admincheckmsg is True:
            await event.reply("Назначен новый админ!")
        else:
            await event.reply("Он уже админ!")

async def sadmpromote(event, user, sender):
    admincheck = sadms.get_or_none(id=sender)
    if admincheck is None:  
        await event.reply("Ты не админ!")
    else:
        textObj, admincheckmsg = sadms.get_or_create(id=user)
        if admincheckmsg is True:
            await event.reply("Назначен новый <strong>супер</strong> админ!")
        else:
            await event.reply("Он уже <strong>супер</strong> админ!")

async def Adminsdemote(event, user, sender):
    admincheck = sadms.get_or_none(id=sender)
    if admincheck is None:  
        return await event.reply("Ты не админ!")
    
    Admins.delete().where(Admins.id == user).execute()
    await event.reply("Снят админ!")

async def sadmdemote(event, user, sender):
    admincheck = sadms.get_or_none(id=sender)
    if admincheck is None:  
        return await event.reply("Ты не админ!")
    
    sadms.delete().where(sadms.id == user).execute()
    await event.reply("Снят <strong>супер</strong> админ!")
