import email
import imaplib
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, Updater

# Set the email address and password
EMAIL_ADDRESS = "CHANGE HERE WITH YOUR EMAIL ADDRESS"
EMAIL_PASSWORD = "CHANGE HERE WITH YOUR PASSWORD THAT GOOGLE GENERATED FOR YOU"

# Set the chat ID of the Telegram chat you want to receive notifications in
CHAT_ID = 'CHANGE HERE WITH YOUR CHAT ID'

# Set the frequency (in seconds) at which to check for new emails
CHECK_FREQUENCY = 1800

# Set the bot token
BOT_TOKEN = "CHANGE HERE WITH YOUR TOKEN BOT"

# Set up the updater and dispatcher
updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher
job_queue = updater.job_queue


def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if chat_id == CHAT_ID:
        message = "Benvenuto! Inizio subito a cercare nuove email"
        context.bot.send_message(chat_id=chat_id, text=message)
        job_queue.run_repeating(check_for_new_emails, interval=CHECK_FREQUENCY, first=10, name=str(chat_id))
    else:
        message = "Non abilitato ad usare questo bot!"
        context.bot.send_message(chat_id=chat_id, text=message)


def stop(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if chat_id == CHAT_ID:
        message = "Addio!"
        context.bot.send_message(chat_id=chat_id, text=message)
        current_jobs = job_queue.get_jobs_by_name(str(chat_id))
        for job in current_jobs:
            job.schedule_removal()
    else:
        message = "Non abilitato ad usare questo bot!"
        context.bot.send_message(chat_id=chat_id, text=message)



def check_for_new_emails(context):
    # Connect to the IMAP server
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    imap.select("inbox")

    # Search for all unread messages
    status, messages = imap.search(None, "UNSEEN")

    if messages[0]:
        for num in messages[0].split():
            typ, data = imap.fetch(num, "(RFC822)")
            message = email.message_from_bytes(data[0][1])

            # Extract email details
            from_address = email.utils.parseaddr(message["From"])
            date = message["Date"]
            subject = message["Subject"]

            # Compose and send the notification message
            notification_message = (
                f"Received from: {from_address}\n"
                f"On: {date}\n"
                f"Subject: {subject}\n"
                "--------\n"
            )
            context.bot.send_message(chat_id=CHAT_ID, text=notification_message)

            # Mark the email as seen
            imap.store(num, "+FLAGS", "\\Seen")

    # Close the connection
        imap.close()
        imap.logout()
    else:
        context.bot.send_message(chat_id=5488706734, text="Non ci sono nuove emails!")


dispatcher.add_handler(CommandHandler('stop', stop))
dispatcher.add_handler(CommandHandler('start', start))
updater.start_polling()
updater.idle()
