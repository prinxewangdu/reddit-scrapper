import asyncpraw
import pandas as pd
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import nest_asyncio

# Function to scrape the best captions from a specific subreddit
async def scrape_subreddit(reddit, subreddit_name, limit=10):
    try:
        subreddit = await reddit.subreddit(subreddit_name)  # Await the subreddit call
        if subreddit is None or not subreddit.display_name:
            return None

        captions = []
        async for submission in subreddit.top(limit=limit, time_filter='week'):  # Get top submissions of the week
            captions.append(submission.title)
        
        return captions
    except Exception as e:
        print(f"Error accessing subreddit: {e}")
        return None

# Function to start the bot and ask for subreddit name
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome! Send me the name of a subreddit (e.g., AskReddit) and I'll send you the top captions.\n"
        "You can also request up to 50 or 100 captions by typing /top50 or /top100 after the subreddit name."
    )

# Function to handle messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE, reddit) -> None:
    user_input = update.message.text.strip()
    
    # Determine the limit based on user input
    if user_input.lower().startswith("/top50"):
        limit = 50
        subreddit_name = user_input[6:].strip()
    elif user_input.lower().startswith("/top100"):
        limit = 100
        subreddit_name = user_input[7:].strip()
    else:
        limit = 10
        subreddit_name = user_input
    
    try:
        captions = await scrape_subreddit(reddit, subreddit_name, limit=limit)  # Await the scrape_subreddit call
        if captions:
            response = f"🔝 Top {limit} of the week 🔝\nhttps://www.reddit.com/r/{subreddit_name}/top/?t=week\n\n"
            response += "\n\n".join(f"{index + 1}. <code>{caption}</code>" for index, caption in enumerate(captions))
            response += "\n\nAny questions? Feel free to contact developer @lazywongsy"
            await update.message.reply_text(response, parse_mode='HTML')  # Use HTML parsing
        else:
            await update.message.reply_text("No captions found or the subreddit does not exist. Please check the subreddit name.")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def main():
    # Initialize Async PRAW with your credentials
    async with asyncpraw.Reddit(client_id='52ZwB-fsX5E8sSRSn-Uoug',
                                 client_secret='1tmcSGPRaZ-2rIyfsAbPqlPlxc0e6g',
                                 user_agent='MyRedditScraper/0.1 by Prinxe') as reddit:

        # Set up the bot using ApplicationBuilder
        application = ApplicationBuilder().token("7539099624:AAHUUyDoLN7_ejyiBhFI9Rw07vHhJE5aI-o").build()

        # Command handlers
        application.add_handler(CommandHandler("start", start))
        
        # Message handler for subreddit names
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lambda update, context: handle_message(update, context, reddit)))

        # Start polling
        await application.run_polling()

if __name__ == "__main__":
    nest_asyncio.apply()  # Apply nest_asyncio to allow running in an existing event loop
    asyncio.run(main())
