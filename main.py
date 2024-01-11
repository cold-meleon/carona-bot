from typing import Final
from telegram import (
    KeyboardButton,
    KeyboardButtonPollType,
    Poll,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
# from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PollAnswerHandler,
    PollHandler,
    filters,
)
# from datetime import datetime
import schedule
import time
import database

# timezone utc-3

# BOT ID
TOKEN: Final = '6756594900:AAFOTbGjr8e77T5phlNKn68P2ul8WIRdeP0'
BOT_USERNAME: Final = '@caroner_manager_bot'
# bot = Bot(token=TOKEN)


# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('manager started')
    
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('manager help')
    
async def pagar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'carona paga {update.message.from_user.first_name}')
    # database.remove_user_caronas(connection, update.message.chat.id, update.message.from_user.id)
    
async def credentials_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'{update.message.from_user.first_name} {update.message.from_user.last_name}\n'+
                        f'chat {update.message.chat.id}\n'+
                        f'user {update.message.from_user.id}'
                        ) 
    
async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [[KeyboardButton("SIM")], [KeyboardButton("NAO")]]
    await context.bot.send_message(
                            chat_id=update.effective_chat.id, 
                            text="Carona?", 
                            reply_markup=ReplyKeyboardMarkup(buttons)
                            )
    
# NEEDS FIXING
async def poll_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    question = "usuario do caroners: IDA"
    options = ['vou', 'nao vou']
    
    message = await context.bot.send_poll(
        update.effective_chat.id,
        options=options,
        question=question,
        is_anonymous=False,
        allows_multiple_answers=False,
    )
    
# Responses
def handle_response(text: str, update: Update) -> str:
    text = text.lower()
    chat_id = update.message.chat.id
    date = update.message.date
    user_id = update.message.from_user.id
    
    if 'sim' in text:
        database.add_carona(connection, chat_id, user_id, date, num_caronas=1)
        # return f'carona {chat_id} addicionada'
        return 'carona adicionada'
    if 'nao' in text:
        pass
    else:
        return 'not a command'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text
    
    print(f'User ({update.message.from_user.id}) in {message_type} {update.message.chat.id}: "{text}"')
    
    if message_type == 'group':
        if BOT_USERNAME in text:
            actual_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(actual_text, update)
        else:
            return
    else:
        response: str = handle_response(text, update)
        
    print('Bot: ', response)
    await update.message.reply_text(response)
    
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

# Main 
if __name__ == '__main__':
    print('starting...')
    app = Application.builder().token(TOKEN).build()
    connection = database.connect()
    # database.create_tables(connection)
    
    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('ask', ask_command))
    app.add_handler(CommandHandler('poll', poll_command))
    app.add_handler(CommandHandler('pagar', pagar_command))
    app.add_handler(CommandHandler('credentials', credentials_command))
    
    schedule.run_pending()  

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    # Errors
    app.add_error_handler(error)
    
    # Polling
    print('polling...')
    app.run_polling(poll_interval=3)