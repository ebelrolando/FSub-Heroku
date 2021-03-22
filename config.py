import os

class Config(object):
	BOT_TOKEN = os.environ.get("BOT_TOKEN")
	APP_ID = int(os.environ.get("APP_ID"))
	API_HASH = os.environ.get("API_HASH")
	DATABASE_URL = os.environ.get("DATABASE_URL")
	SUDO_USERS = list(set(int(x) for x in ''.split()))
	SUDO_USERS.append(853393439)
	SUDO_USERS = list(set(SUDO_USERS))

class Messages():

	START_MSG = "**Hola! [👋](https://t.me/joinchat/pbY-xTXjcrozMGFh) [{}](tg://user?id={})**\n\n● 📣🍔 𝗔𝗻𝘂𝗻𝗰𝗶𝗼𝘀: 𝗡𝗲𝗴𝗼𝗰𝗶𝗼𝘀 𝘆 𝗩𝗲𝗻𝘁𝗮𝘀 🍹📣**\n\n ¿Ya te uniste al directorio más completo de Anuncios de Negocios,**Ventas y Servicios?."
