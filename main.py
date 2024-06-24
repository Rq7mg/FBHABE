import feedparser
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bs4 import BeautifulSoup
import re
from datetime import datetime
BOT_TOKEN = '6888677441:AAEQMucVBX-V1cNxUFOZO0iEcjzEV7fuoi0'
CHANNEL_ID = '@Fenerbahce1907haber'
RSS_FEED_URLS = [
    'https://www.fotomac.com.tr/fenerbahce#_articles.rss',
    'https://www.fotomac.com.tr/rss/fenerbahce.xml',
]
last_titles = {}
def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext
def get_first_sentence(text):
    sentences = text.split('. ')
    return sentences[0] + '.' if sentences else text
async def fetch_news(bot):
    global last_titles
    first_news = True
    for rss_url in RSS_FEED_URLS:
        feed = feedparser.parse(rss_url)
        if feed.entries:
            new_title = feed.entries[0].title
            if rss_url not in last_titles or new_title != last_titles[rss_url]:
                last_titles[rss_url] = new_title
                entry = feed.entries[0]
                title = entry.title
                description = BeautifulSoup(entry.summary, features="html.parser").text
                description = clean_html(description)
                description = get_first_sentence(description)
                link = entry.link
                source = rss_url.split('/')[2] 
                publish_date = entry.published_parsed if hasattr(entry, 'published_parsed') else None
                date_str = datetime(*publish_date[:6]).strftime('%Y-%m-%d %H:%M:%S') if publish_date else 'Yayınlanma tarihi bilinmiyor'
                message_text = f"<b>{title}</b>\n\n{description}\n\n<a href='{link}'>Haberin Devamı</a>\n{date_str}"
                
                image_url = entry.media_content[0]['url'] if 'media_content' in entry and len(entry.media_content) > 0 else None
                
                if not first_news:
                    await bot.send_message(chat_id=CHANNEL_ID, text="꧁꧂𝐊𝐈𝐘𝐈𝐂𝐈꧁꧂", parse_mode='HTML')

                if image_url:
                    await bot.send_photo(chat_id=CHANNEL_ID, photo=image_url, caption=message_text, parse_mode='HTML')
                else:
                    await bot.send_message(chat_id=CHANNEL_ID, text=message_text, parse_mode='HTML')

                first_news = False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Merhaba! Haber botu başlatıldı.')
    await fetch_news(context.bot)

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    
    scheduler = AsyncIOScheduler()
    scheduler.add_job(fetch_news, 'interval', minutes=10, args=(application.bot,))
    scheduler.start()
    
    application.run_polling()

if __name__ == '__main__':
    main()
