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
    Job,
    JobQueue,
    Updater,
)
# from datetime import datetime
import datetime
import database

# timezone utc-3
# QUICK ACTION BUTTONS/ANSWERS AND OTHER CONSTANTS
TRAVEL = "travel" #"VIAJAR COM OS CARONERS"
PAY_TRAVELS = "pay" #"PAGAR SERASA DAS CARONAS"
CARONA_COST = 5

# BOT ID
TOKEN: Final = '6756594900:AAFOTbGjr8e77T5phlNKn68P2ul8WIRdeP0'
BOT_USERNAME: Final = '@caroner_manager_bot'


# COMMANDS        
async def reply_privately(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id, text_message: str):
    await context.bot.send_message(chat_id=user_id, 
                                   text=text_message)
    
    
def total_travels(chat_id, user_id): 
    connection = database.connect(database.CARONAS)
    cursor = connection.cursor()
    
    # position of data in tuple
    num_travels_pos = 5
    
    travels_sum = 0
    for travel in database.get_carona_by_user(connection, cursor, chat_id, user_id, status=database.pending_status):
        travels_sum += travel[num_travels_pos]
        
    return travels_sum
 
 
async def credentials_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = text_message=(f'{update.message.from_user.first_name} {update.message.from_user.last_name}\n'+
                        f'chat {update.message.chat.id}\n'+
                        f'user {update.message.from_user.id}'
                        )
    await reply_privately(update, context, update.message.from_user.id, msg)
    

async def quick_actions(update: Update, context: ContextTypes.DEFAULT_TYPE, button1=("/"+TRAVEL), button2=("/"+PAY_TRAVELS),text_message="Quem vem carona?"):
    buttons = [[KeyboardButton(button1)], [KeyboardButton(button2)]]
    await context.bot.send_message(
                            chat_id=update.effective_chat.id, 
                            text=text_message, 
                            reply_markup=ReplyKeyboardMarkup(buttons)
                            )
 
 
async def travel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    last_name = update.message.from_user.last_name
    date = update.message.date
    connection = database.connect(database.CARONAS)
    cursor = connection.cursor()
    database.add_carona(connection, cursor, chat_id, user_id, first_name, last_name, date, status=database.pending_status)
    
    total = total_travels(chat_id, user_id)
    msg = f'in: {update.message.chat.title}\n'+f'caronas: {total}'
    
    await reply_privately(update, context, user_id, msg)

     
async def pay_travels_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    last_name = update.message.from_user.last_name
    connection = database.connect(database.CARONAS)
    cursor = connection.cursor()
    database.update_user_caronas_status(connection, cursor, chat_id, user_id)
    await update.message.reply_text(f'{first_name} {last_name} tirou o nome do serasa')
    

async def all_users_pending_payments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    connection = database.connect(database.CARONAS)
    cursor = connection.cursor()
    chat_id = update.message.chat.id
    
    # position of data in tuple
    first_name_pos = 0
    last_name_pos = 1
    
    all_users = database.get_carona_users(connection, cursor, chat_id)
    user_msg = []
    final_msg = 'Lista do SERASA\n'

    for user_id in all_users.keys():
        user_total = total_travels(chat_id, user_id)
        user_msg = f'{all_users[user_id][first_name_pos]} {all_users[user_id][last_name_pos]} : {user_total} viagens (R$ {CARONA_COST*user_total},00)\n'
        
        final_msg = ''.join([final_msg,user_msg])
            
    await update.message.reply_text(final_msg)


# async def ask_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     admins = update.message.chat
#     for admin in admins:
#         if admin.status == 'owner':
#             owner_id = admin.user.id
#             print(owner_id)        
    
#     msg = "Vai viajar hoje?"
#     await reply_privately(update, context, owner_id, msg)
    

# NEEDS TO BE FINISHED, ONLY WHEN ALL FUNCTION HAVE BEEN CREATE
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("COMMANDS | DESCRIPTION\n"+
                                        "-quickactions | creates buttons\n"+
                                        "-credentials | user credentials\n"+
                                        "-pending | user pending travels\n"+
                                        "-travel | adds user travel\n"+
                                        "-pay | resets pending travels\n\t\t\t(from current group)")




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
    
# RESPONSES
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

# MAIN 
if __name__ == '__main__':
    print('starting...')
    
    app = Application.builder().token(TOKEN).build()
    # conn = database.connect(database.CARONAS)
    # c = conn.cursor() 
    
    # if not database.check_db(database.CARONAS):
    #     database.create_tables(conn, c, database.CREATE_TABLE_SCHEDULE)
    
    
    
    # COMMANDS
    app.add_handler(CommandHandler('help', help_command))
    # app.add_handler(CommandHandler('poll', poll_command))
    app.add_handler(CommandHandler('quickactions', quick_actions))
    app.add_handler(CommandHandler('credentials', credentials_command))
    app.add_handler(CommandHandler('pending', total_travels))
    app.add_handler(CommandHandler('pending_users', all_users_pending_payments))
    app.add_handler(CommandHandler(TRAVEL, travel_command))
    app.add_handler(CommandHandler(PAY_TRAVELS, pay_travels_command))
    # app.add_handler(CommandHandler('ask', ask_owner))    

    # MESSAGES
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    # ERRORS
    app.add_error_handler(error)
    
    # POLLING
    print('polling...')
    app.run_polling(poll_interval=3)
    