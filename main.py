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
# QUICK ACTION BUTTONS/ANSWERS
TRAVEL = "travel" #"VIAJAR COM OS CARONERS"
PAY_TRAVELS = "pay" #"PAGAR SERASA DAS CARONAS"

# BOT ID
TOKEN: Final = '6756594900:AAFOTbGjr8e77T5phlNKn68P2ul8WIRdeP0'
BOT_USERNAME: Final = '@caroner_manager_bot'


# COMMANDS    
async def credentials_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'{update.message.from_user.first_name} {update.message.from_user.last_name}\n'+
                        f'chat {update.message.chat.id}\n'+
                        f'user {update.message.from_user.id}'
                        ) 
    
async def total_travels_command(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    last_name = update.message.from_user.last_name
    date = update.message.date
    connection = database.connect(database.CARONAS)
    cursor = conn.cursor()
    travels_sum = 0
    for travel in database.get_carona_by_user(connection, cursor, chat_id, user_id, status=database.pending_status):
        travels_sum += travel[5]
    await update.message.reply_text(f'{first_name} {last_name}\n'+
                                    f'total de viagens: {travels_sum}')
 
    
async def travel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    last_name = update.message.from_user.last_name
    date = update.message.date
    connection = database.connect(database.CARONAS)
    cursor = conn.cursor()
    database.add_carona(connection, cursor, chat_id, user_id, first_name, last_name, date, status=database.pending_status)
    await total_travels_command(update, context)

     
async def pay_travels_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    last_name = update.message.from_user.last_name
    connection = database.connect(database.CARONAS)
    cursor = conn.cursor()
    database.update_user_caronas_status(connection, cursor, chat_id, user_id)
    await update.message.reply_text(f'{first_name} {last_name} tirou o nome do serasa')
    

# async def all_users_pending_payments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    

async def quick_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [[KeyboardButton("/"+TRAVEL)], [KeyboardButton("/"+PAY_TRAVELS)]]
    await context.bot.send_message(
                            chat_id=update.effective_chat.id, 
                            text="Carona?", 
                            reply_markup=ReplyKeyboardMarkup(buttons)
                            )

# async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text("")


# # NEEDS FIXING
# async def poll_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     chat_id = update.message.chat_id
#     question = "usuario do caroners: IDA"
#     options = ['vou', 'nao vou']
    
#     message = await context.bot.send_poll(
#         update.effective_chat.id,
#         options=options,
#         question=question,
#         is_anonymous=False,
#         allows_multiple_answers=False,
#     )
    
# Responses
def handle_response(text: str, update: Update) -> str:
    # text = text.lower()
    chat_id = update.message.chat.id
    user_id = update.message.from_user.id
    date = update.message.date
    
    if 'data' in text:
        return f'{update.message.date}'
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
    conn = database.connect(database.CARONAS)
    c = conn.cursor()
    
    # COMMANDS
    # app.add_handler(CommandHandler('help', help_command))
    # app.add_handler(CommandHandler('ask', ask_command))
    # app.add_handler(CommandHandler('poll', poll_command))
    # app.add_handler(CommandHandler(TRAVEL, travel_command))
    app.add_handler(CommandHandler('quickactions', quick_actions))
    app.add_handler(CommandHandler('credentials', credentials_command))
    app.add_handler(CommandHandler('pending', total_travels_command))
    app.add_handler(CommandHandler(TRAVEL, travel_command))
    app.add_handler(CommandHandler(PAY_TRAVELS, pay_travels_command))

    
    # schedule.run_pending()  

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    # Errors
    app.add_error_handler(error)
    
    # Polling
    print('polling...')
    app.run_polling(poll_interval=3)