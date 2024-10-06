import sys
from bot import bot

if __name__ == '__main__':
    try:
        bot.process()
    except KeyboardInterrupt:
        print("Bot stopped by user...")
        sys.exit(2)