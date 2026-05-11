"""
بوت تليجرام لتوليد الصور بالذكاء الاصطناعي
"""

import logging
import requests
import os
from urllib.parse import quote
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")

logging.basicConfig(
      format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
      level=logging.INFO
)
logger = logging.getLogger(__name__)


def generate_image(prompt: str, width: int = 1024, height: int = 1024) -> bytes:
      encoded_prompt = quote(prompt)
      url = (
          f"https://image.pollinations.ai/prompt/{encoded_prompt}"
          f"?width={width}&height={height}"
          f"&nologo=true&enhance=true"
      )
      response = requests.get(url, timeout=120)
      response.raise_for_status()
      return response.content


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
      welcome_message = (
                "🎨 أهلاً بك في بوت توليد الصور!\n\n"
                "✨ ابعتلي وصف لأي صورة عايزها وأنا هولدها لك\n\n"
                "📝 أمثلة:\n"
                "• قطة تشرب قهوة في باريس\n"
                "• منظر طبيعي لجبال وقت الغروب\n\n"
                "💡 كل ما الوصف يكون مفصل أكتر، الصورة تطلع أحلى"
      )
      await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
      help_text = (
                "📚 كيفية الاستخدام:\n\n"
                "اكتب وصف الصورة وانتظر 10-30 ثانية\n\n"
                "🎯 نصائح:\n"
                "• استخدم وصف تفصيلي\n"
                "• اذكر النمط والألوان\n"
                "• الإنجليزية أحياناً تعطي نتائج أفضل"
      )
      await update.message.reply_text(help_text)


  async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
            prompt = update.message.text

    logger.info(f"طلب من {user.username or user.first_name}: {prompt}")

      waiting_message = await update.message.reply_text(
          "🎨 جاري توليد الصورة...\n⏳ الرجاء الانتظار 10-30 ثانية"
)

        try:
        image_bytes = generate_image(prompt)
        temp_path = f"temp_{user.id}.png"

        with open(temp_path, 'wb') as f:
            f.write(image_bytes)

        with open(temp_path, 'rb') as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=f"✨ تم توليد الصورة\n📝 {prompt[:100]}"
)

        os.remove(temp_path)
        await waiting_message.delete()

except requests.exceptions.Timeout:
        await waiting_message.edit_text("⚠️ انتهت مهلة الانتظار. حاول مرة أخرى.")
except Exception as e:
        logger.error(f"خطأ: {e}")
        await waiting_message.edit_text("❌ حدث خطأ. حاول مرة أخرى.")


def main() -> None:
      application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(
              MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    logger.info("🚀 البوت يعمل الآن...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
      main()
