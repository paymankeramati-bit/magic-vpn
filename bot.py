import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    ContextTypes, filters
)

# ================== تنظیمات ==================
BOT_TOKEN = "8814983168:AAGJm3N60oZgLlHAakqnC3IFou-N6tKiI9Q"
ADMIN_ID = 7554584580
CARD_NUMBER = "5047-0616-7071-3144"
CARD_NAME = "پیمان کرامتی"

# ================== پلن‌ها ==================

V2RAY_PLANS = {
    "v2_1m_20g":  {"name": "یک‌ماهه - ۲۰ گیگ",  "price": "۱۰۰,۰۰۰ تومان", "days": 30, "traffic": "20GB"},
    "v2_1m_50g":  {"name": "یک‌ماهه - ۵۰ گیگ",  "price": "۲۵۰,۰۰۰ تومان", "days": 30, "traffic": "50GB"},
    "v2_1m_100g": {"name": "یک‌ماهه - ۱۰۰ گیگ", "price": "۵۰۰,۰۰۰ تومان", "days": 30, "traffic": "100GB"},
    "v2_2m_50g":  {"name": "دوماهه - ۵۰ گیگ",  "price": "۳۰۰,۰۰۰ تومان", "days": 60, "traffic": "50GB"},
    "v2_2m_100g": {"name": "دوماهه - ۱۰۰ گیگ", "price": "۶۰۰,۰۰۰ تومان", "days": 60, "traffic": "100GB"},
}

WIREGUARD_PLANS = {
    "wg_1m_20g":  {"name": "۱ ماهه - ۲۰ گیگ",  "price": "۱۶۰,۰۰۰ تومان", "days": 30,  "traffic": "20GB"},
    "wg_1m_36g":  {"name": "۱ ماهه - ۳۶ گیگ",  "price": "۲۰۰,۰۰۰ تومان", "days": 30,  "traffic": "36GB"},
    "wg_2m_78g":  {"name": "۲ ماهه - ۷۸ گیگ",  "price": "۴۲۰,۰۰۰ تومان", "days": 60,  "traffic": "78GB"},
    "wg_3m_127g": {"name": "۳ ماهه - ۱۲۷ گیگ", "price": "۶۵۰,۰۰۰ تومان", "days": 90,  "traffic": "127GB"},
    "wg_6m_300g": {"name": "۶ ماهه - ۳۰۰ گیگ", "price": "۱,۱۰۰,۰۰۰ تومان", "days": 180, "traffic": "300GB"},
}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data.clear()

    text = f"""سلام {user.first_name} 👋

به ربات فروش فیلترشکن خوش اومدی.

از دکمه‌های زیر یکی رو انتخاب کن:"""

    keyboard = [
        [InlineKeyboardButton("🚀 خرید V2Ray", callback_data="protocol_v2ray")],
        [InlineKeyboardButton("🔒 خرید WireGuard", callback_data="protocol_wireguard")],
        [InlineKeyboardButton("📞 پشتیبانی", callback_data="support")],
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "support":
        await query.edit_message_text("برای پشتیبانی به آیدی زیر پیام بده:\n@magicvpn3")
        return

    if data == "back_main":
        keyboard = [
            [InlineKeyboardButton("🚀 خرید V2Ray", callback_data="protocol_v2ray")],
            [InlineKeyboardButton("🔒 خرید WireGuard", callback_data="protocol_wireguard")],
            [InlineKeyboardButton("📞 پشتیبانی", callback_data="support")],
        ]
        await query.edit_message_text("منوی اصلی:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data == "protocol_v2ray":
        context.user_data["protocol"] = "V2Ray"
        plans = V2RAY_PLANS
        title = "پلن‌های V2Ray"
    elif data == "protocol_wireguard":
        context.user_data["protocol"] = "WireGuard"
        plans = WIREGUARD_PLANS
        title = "پلن‌های WireGuard"
    else:
        plans = None
        title = None

    if plans:
        keyboard = []
        for key, plan in plans.items():
            btn_text = f"{plan['name']} | {plan['price']}"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"plan_{key}")])
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")])

        await query.edit_message_text(
            f"🔹 {title}\n\nیکی از پلن‌ها رو انتخاب کن:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if data.startswith("plan_"):
        plan_key = data.replace("plan_", "")
        protocol = context.user_data.get("protocol")

        if protocol == "V2Ray":
            plan = V2RAY_PLANS.get(plan_key)
        else:
            plan = WIREGUARD_PLANS.get(plan_key)

        if not plan:
            await query.edit_message_text("پلن پیدا نشد. دوباره /start بزن.")
            return

        context.user_data["selected_plan"] = plan
        context.user_data["waiting_receipt"] = True

        text = f"""✅ پلن انتخاب شده:

🔹 پروتکل: {protocol}
📦 پلن: {plan['name']}
💰 قیمت: {plan['price']}
📅 مدت: {plan['days']} روز
📊 ترافیک: {plan['traffic']}

━━━━━━━━━━━━━━
💳 لطفاً مبلغ رو به کارت زیر واریز کن:

`{CARD_NUMBER}`
به نام: {CARD_NAME}

بعد از واریز، **عکس فیش** رو همینجا بفرست."""

        await query.edit_message_text(text, parse_mode="Markdown")
        return

    if data.startswith("approve_"):
        user_id = int(data.replace("approve_", ""))
        try:
            await query.edit_message_caption(
                caption=(query.message.caption or "") + "\n\n✅ توسط ادمین تأیید شد.\nحالا کانفیگ رو برای کاربر بفرست.",
                reply_markup=None
            )
        except:
            await query.edit_message_text(
                text=(query.message.text or "") + "\n\n✅ توسط ادمین تأیید شد.",
                reply_markup=None
            )
        await context.bot.send_message(
            chat_id=user_id,
            text="✅ پرداخت شما تأیید شد!\n\nکانفیگ به زودی برات ارسال می‌شه. لطفاً چند لحظه صبر کن."
        )
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"حالا کانفیگ مربوط به کاربر `{user_id}` رو براش فوروارد یا کپی کن.",
            parse_mode="Markdown"
        )
        return

    if data.startswith("reject_"):
        user_id = int(data.replace("reject_", ""))
        try:
            await query.edit_message_caption(
                caption=(query.message.caption or "") + "\n\n❌ توسط ادمین رد شد.",
                reply_markup=None
            )
        except:
            await query.edit_message_text(
                text=(query.message.text or "") + "\n\n❌ توسط ادمین رد شد.",
                reply_markup=None
            )
        await context.bot.send_message(
            chat_id=user_id,
            text="❌ متأسفانه فیش شما تأیید نشد.\n\nلطفاً دوباره فیش صحیح رو ارسال کن یا با پشتیبانی در ارتباط باش."
        )
        return

async def receipt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_receipt"):
        return

    user = update.effective_user
    plan = context.user_data.get("selected_plan")
    protocol = context.user_data.get("protocol")

    if not plan:
        await update.message.reply_text("خطا! دوباره از اول شروع کن با /start")
        return

    context.user_data["waiting_receipt"] = False

    await update.message.reply_text(
        "✅ فیش دریافت شد.\n\nدر حال بررسی توسط ادمین هستی...\nبعد از تأیید، کانفیگ برات ارسال می‌شه."
    )

    caption = f"""🧾 فیش جدید دریافت شد

👤 کاربر: {user.first_name} (@{user.username or 'ندارد'})
🆔 آیدی: `{user.id}`
🔹 پروتکل: {protocol}
📦 پلن: {plan['name']}
💰 قیمت: {plan['price']}

برای تأیید یا رد از دکمه‌های زیر استفاده کن:"""

    keyboard = [
        [
            InlineKeyboardButton("✅ تأیید و ارسال کانفیگ", callback_data=f"approve_{user.id}"),
            InlineKeyboardButton("❌ رد کردن", callback_data=f"reject_{user.id}")
        ]
    ]

    if update.message.photo:
        photo = update.message.photo[-1].file_id
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=caption + "\n\n(فیش به صورت متن ارسال شده)",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO | (filters.TEXT & ~filters.COMMAND), receipt_handler))

    print("ربات روشن شد...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()