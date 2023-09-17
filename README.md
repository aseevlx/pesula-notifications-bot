# Pesula / Laundry notifications bot

This is a script that uses Telegram bot for notify you when your laundry is done.  
It is intended to be used with the [Nortec](https://vuoronvaraus.fi) laundry reservation system.

## Pre-requisites
- Setup sending notifications to your email. Gmail can't be used because it doesn't support IMAP with only password auth
- Get your IMAP server address and port
- Get your email and password from your email provider
- Create a tg bot with [BotFather](https://t.me/botfather) and get the bot token.
- Add the bot to your group chat (or use your own id)
- Get chat id with [What's my Telegram ID?](https://t.me/my_id_bot)

## Env variables
- `EMAIL_USERNAME` - your email address
- `EMAIL_PASSWORD` - your email password
- `IMAP_SERVER` - imap server address
- `TG_BOT_TOKEN` - telegram bot token, get it from BotFather
- `TG_CHAT_ID` - telegram chat id
- `TG_ERROR_CHAT_ID` - telegram chat id for error messages from bot (you can use your own id)

##  Usage
- Build the image:
```shell
docker build -t pesula-bot .
```

- Run:
```shell
docker run -it --restart unless-stopped --name pesula-bot -d \
    -e EMAIL_USERNAME=<your email> \
    -e EMAIL_PASSWORD=<your password> \
    -e IMAP_SERVER=<your imap server> \
    -e TG_BOT_TOKEN=<your bot token> \
    -e TG_CHAT_ID=<your chat id> \
    -e TG_ERROR_CHAT_ID=<your error chat id> \
    pesula-bot
```


## Possible improvements
- Add notification when laundry shift is starting