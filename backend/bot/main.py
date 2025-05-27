import io, logging
from uuid import uuid4

import httpx

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,           # <-- new
    filters
)

from common.settings import Credentials, S3, Microservices
from common.connectors.db import SessionLocal
from common.models.user import User
from common.models.storage import TelegramUserMapping, Entry, SourceType
from common.connectors.s3 import get_s3_client
from common.utils.s3 import check_bucket
from common.utils.jwt import create_jwt


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_user_id = update.effective_user.id
    db = SessionLocal()
    try:
        mapping = (
            db.query(TelegramUserMapping)
              .filter_by(telegram_user_id=telegram_user_id)
              .first()
        )

        if not mapping:
            # create internal user
            internal_user = User(username=str(telegram_user_id), password_hash="")
            db.add(internal_user)
            db.commit()
            db.refresh(internal_user)

            # link to Telegram user
            mapping = TelegramUserMapping(
                telegram_user_id=telegram_user_id,
                internal_user_id=internal_user.id
            )
            db.add(mapping)
            db.commit()

        await update.message.reply_text(
            'Привет! Я помогу тебе в удалении облаков со спутниковых фотографий. '
            'Отправь мне фотографию.'
        )
    finally:
        db.close()


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Загружайте снимки без сжатия (в виде файлов)"
    )


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_user_id = update.effective_user.id
    doc = update.message.document

    # only accept PNG documents
    if not doc or doc.mime_type != "image/png":
        await update.message.reply_text(
            "Пожалуйста, отправьте изображение в формате PNG (в виде документа)."
        )
        return

    # fetch Telegram file
    tg_file = await doc.get_file()
    file_bytes = await tg_file.download_as_bytearray()

    db = SessionLocal()
    try:
        mapping = (
            db.query(TelegramUserMapping)
              .filter_by(telegram_user_id=telegram_user_id)
              .first()
        )
        if not mapping:
            await update.message.reply_text(
                "Пользователь не найден, пожалуйста введите /start сначала."
            )
            return

        # record new entry
        user = db.query(User).get(mapping.internal_user_id)
        entry = Entry.create(db, user, SourceType.user)

        # upload original to S3
        s3 = get_s3_client()

        if not check_bucket(s3, S3.bucket):
            await update.message.reply_text("Извините, произошла ошибка.")

        key = f"{uuid4()}.png"
        s3.put_object(
            Bucket=S3.bucket,
            Key=key,
            Body=file_bytes,
            ContentType="image/png"
        )

        # save the S3 key on the DB entry
        entry.file.source_key = key
        db.commit()
        db.refresh(entry)

        await update.message.reply_text("Работаю над фотографией...")

        # Creating a JWT token for authenticating with the the ML service
        token = create_jwt({"user_id": user.id, "type": "user"}, 60)

        ml_url = f"http://{Microservices.ml_service}/cloud-remove"
        async with httpx.AsyncClient() as client:
            response = await client.get(
                ml_url,
                headers={"Authorization": f"Bearer {token}"},
                params={"entry_id": str(entry.uuid)}
            )

        if response.status_code == 200:
            entry = Entry.from_uuid(db, entry.uuid)
            if entry and entry.file.result_key:
                processed = s3.get_object(
                    Bucket=S3.bucket,
                    Key=entry.file.result_key
                )
                img_data = processed["Body"].read()
                await update.message.reply_document(
                    document=io.BytesIO(img_data),
                    filename=f"{str(entry.uuid)}.png"
                )
            else:
                await update.message.reply_text(
                    "Обработанное изображение недоступно."
                )
        else:
            await update.message.reply_text(
                f"Ошибка обработки изображения сервисом ML. {response.text}"
            )
    finally:
        db.close()


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(
        "Exception while handling an update:",
        exc_info=context.error
    )


def main() -> None:
    application = (
        Application
        .builder()
        .token(Credentials.Telegram.api_key)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(
        MessageHandler(filters.Document.ALL, handle_file)
    )
    application.add_error_handler(error_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
