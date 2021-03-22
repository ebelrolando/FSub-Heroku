import time
import logging
from config import Config
from pyrogram import Client, filters
from sql_helpers import forceSubscribe_sql as sql
from pyrogram.types import ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant, UsernameNotOccupied, ChatAdminRequired, PeerIdInvalid

logging.basicConfig(level=logging.INFO)

static_data_filter = filters.create(lambda _, __, query: query.data == "onUnMuteRequest")
@Client.on_callback_query(static_data_filter)
def _onUnMuteRequest(client, cb):
  user_id = cb.from_user.id
  chat_id = cb.message.chat.id
  chat_db = sql.fs_settings(chat_id)
  if chat_db:
    channel = chat_db.channel
    chat_member = client.get_chat_member(chat_id, user_id)
    if chat_member.restricted_by:
      if chat_member.restricted_by.id == (client.get_me()).id:
          try:
            client.get_chat_member(channel, user_id)
            client.unban_chat_member(chat_id, user_id)
            if cb.message.reply_to_message.from_user.id == user_id:
              cb.message.delete()
          except UserNotParticipant:
            client.answer_callback_query(cb.id, text="❗ Únase al 'canal @Anuncios_cu y presione el botón nuevamente.", show_alert=True)
      else:
        client.answer_callback_query(cb.id, text="❗ Estás silenciado por otras  razones.", show_alert=True)
    else:
      if not client.get_chat_member(chat_id, (client.get_me()).id).status == 'administrator':
        client.send_message(chat_id, f"❗ **{cb.from_user.mention} está tratando de desactivar el silencio a sí mismo, pero no puedo hacerlo porque no soy un administrador en este chat, agrégueme como administrador de nuevo.**\n__#Leaving this chat...__")
        client.leave_chat(chat_id)
      else:
        client.answer_callback_query(cb.id, text="❗ Advertencia: no haga clic en el botón si puede hablar libremente.", show_alert=True)



@Client.on_message(filters.text & ~filters.private & ~filters.edited, group=1)
def _check_member(client, message):
  chat_id = message.chat.id
  chat_db = sql.fs_settings(chat_id)
  if chat_db:
    user_id = message.from_user.id
    if not client.get_chat_member(chat_id, user_id).status in ("administrator", "creator") and not user_id in Config.SUDO_USERS:
      channel = chat_db.channel
      try:
        client.get_chat_member(channel, user_id)
      except UserNotParticipant:
        try:
          sent_message = message.reply_text(
              "Hola {}, **espera**, No estás suscrito a nuestro **Canal Directorio de\n [📣🍔 𝗔𝗻𝘂𝗻𝗰𝗶𝗼𝘀: 𝗡𝗲𝗴𝗼𝗰𝗶𝗼𝘀 𝘆 𝗩𝗲𝗻𝘁𝗮𝘀 🍹📣](https://t.me/Anuncios_cu)**.\n\n  •➤@Anuncios_cu\n    •➤@Anuncios_cu\n      •➤@Anuncios_cu\n\n**Si vives en Cuba éste es tu canal, te será de mucha ayuda.**\n︾ Luego pulsa el botón de abajo ︾.".format(message.from_user.mention, channel, channel),
              disable_web_page_preview=True,
              reply_markup=InlineKeyboardMarkup(
                  [[InlineKeyboardButton("🔔 Ya estoy en el canal ✅", callback_data="onUnMuteRequest")]]
              )
          )
          client.restrict_chat_member(chat_id, user_id, ChatPermissions(can_send_messages=False))
        except ChatAdminRequired:
          sent_message.edit("❗ **No soy admin aquí.**\n__Hazme admin y añádeme de nuevo.\n#Dejando...__")
          client.leave_chat(chat_id)
      except ChatAdminRequired:
        client.send_message(chat_id, text=f"❗ **No soy admin en @{channel}**\n__Hazme admin con todos los permisos.\n#Dejando...__")
        client.leave_chat(chat_id)


@Client.on_message(filters.command(["forzar", "f"]) & ~filters.private)
def fsub(client, message):
  user = client.get_chat_member(message.chat.id, message.from_user.id)
  if user.status is "creator" or user.user.id in Config.SUDO_USERS:
    chat_id = message.chat.id
    if len(message.command) > 1:
      input_str = message.command[1]
      input_str = input_str.replace("@", "")
      if input_str.lower() in ("off", "no", "disable"):
        sql.disapprove(chat_id)
        message.reply_text("❌ **Desactivado correctamente.**")
      elif input_str.lower() in ('clear'):
        sent_message = message.reply_text('**Actualizando...**')
        try:
          for chat_member in client.get_chat_members(message.chat.id, filter="restricted"):
            if chat_member.restricted_by.id == (client.get_me()).id:
                client.unban_chat_member(chat_id, chat_member.user.id)
                time.sleep(1)
          sent_message.edit('✅ **Ya pueden escribir todos los miembros que he silenciado.**')
        except ChatAdminRequired:
          sent_message.edit('❗ **No soy administrador en este grupo.**\n__No puedo silenciar a los miembros si no me otorgas todos los permisos.__')
      else:
        try:
          client.get_chat_member(input_str, "me")
          sql.add_channel(chat_id, input_str)
          message.reply_text(f"✅ **El bot está habilitado**\n__Todos los mimbros del grupo tendrán que estar suscrito a [Anuncios_cu](https://t.me/{input_str}) para poder enviar mensajes al grupo.__", disable_web_page_preview=True)
        except UserNotParticipant:
          message.reply_text(f"❗ **No soy administrador en el canal.**\n__Añádeme a [channel](https://t.me/{input_str}). Y otórgame todos los permisos.__", disable_web_page_preview=True)
        except (UsernameNotOccupied, PeerIdInvalid):
          message.reply_text(f"❗ **Username del canal inválido.**")
        except Exception as err:
          message.reply_text(f"❗ **ERROR:** ```{err}```")
    else:
      if sql.fs_settings(chat_id):
        message.reply_text(f"✅ **Está activo en este grupo.**\n__Para el Canal [Channel](https://t.me/{sql.fs_settings(chat_id).channel})__", disable_web_page_preview=True)
      else:
        message.reply_text("❌ **No está activado en este grupo.**")
  else:
      message.reply_text("❗ **Creador del grupo requerido.**\n__Tienes que ser el creador del grupo para usar el bot acá.__")
