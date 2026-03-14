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

Optional tuning for polling when running as a long-lived container:

- `POLL_INTERVAL_SEC` - base polling interval in seconds during working hours (default: `60`)
- `SLEEP_OUTSIDE_WORKING_HOURS_SEC` - sleep time in seconds outside working hours (default: `1800`, i.e. 30 minutes)
- `WORKING_HOURS_START` - start of working hours (hour of day, 0-23, default: `8`)
- `WORKING_HOURS_END` - end of working hours (hour of day, 0-23, default: `24`)
- `MAX_POLL_INTERVAL_SEC` - maximum backoff interval when there are no new messages (default: `600`)

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

Alternatively, you can pull a pre-built image from GitHub Container Registry (GHCR):

```shell
docker pull ghcr.io/aseevlx/pesula-notifications-bot:latest
```

Secrets (API credentials, Telegram tokens) are **not** baked into the image and must be provided via environment variables (for example using a `.env` file and `docker compose` as shown below).

- Run:
```shell
docker compose up -d
```

- If the code is changed - just restart the container
```
docker compose restart
```

