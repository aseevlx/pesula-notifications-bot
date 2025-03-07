# Pesula / Laundry notifications bot

This is a script that uses Telegram bot for notify you when your laundry is done.  
It is intended to be used with the [Nortec](https://vuoronvaraus.fi) laundry reservation system.

## Pre-requisites
- Prepare your email and password from the Nortec website
- Create a tg bot with [BotFather](https://t.me/botfather) and get the bot token.
- Add the bot to your group chat (or use your own id)
- Get chat id with [What's my Telegram ID?](https://t.me/my_id_bot)


## Env variables
- `API_USERNAME` - your api username
- `API_PASSWORD` - your api password
- `TG_BOT_TOKEN` - telegram bot token, get it from BotFather
- `TG_CHAT_ID` - telegram chat id
- `TG_ERROR_CHAT_ID` - telegram chat id for error messages (might be your own id if you activated your bot with /start command in TG)

##  Usage
- Create and update .env file with your data:
```shell
cp env .env
nano .env
```

- Build the image:
```shell
docker compose build
```

- Run:
```shell
docker compose up -d
```

- If the code is changed - just restart the container
```
docker compose restart
```

