from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import logging

from settings import Microservices, Credentials


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Send the image you want to remove clouds from.')


async def handle_image(update: Update, context: CallbackContext) -> None:
    file = await update.message.photo[-1].get_file()
    await file.download_to_drive('user_image.jpg')
    await update.message.reply_photo(photo=open('user_image.jpg', 'rb'))


async def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f'Update {update} caused error {context.error}')


def main() -> None:
    application = Application.builder().token(Credentials.api_key).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    application.add_error_handler(error)
    application.run_polling()


if __name__ == '__main__':
    main()
