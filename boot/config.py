# Cyberspace bot

##This source serves as a base for Cyberspace store bots.
##It aims to be as modular as possible, allowing adding new features with minor effort.

## Example config file
#6203838763:AAFKHxOaQilei4GnWtvyJ6NPXI03qwhuFI8
##```python
# Your Telegram bot token.
BOT_TOKEN = "7449536264:AAEnQmgx6Q0X7rE6ExQPykoSqhlN_1QC6Xc"

# Telegram API ID and Hash. This is NOT your bot token and shouldn't be changed.
API_ID = 9641313
API_HASH = "baefb797b70643121704c7f344b92870"

# Chat used for logging errors.
LOG_CHAT = 476727347

# Chat used for logging user actions (like buy, gift, etc).
ADMIN_CHAT = 476727347
GRUPO_PUB = 4212604276


# How many updates can be handled in parallel.
# Don't use high values for low-end servers.
WORKERS = 20

# Admins can access panel and add new materials to the bot.
ADMINS = [476727347, 6840540201]

# Sudoers have full access to the server and can execute commands.
SUDOERS = [476727347, 6840540201]

# All sudoers should be admins too
ADMINS.extend(SUDOERS)

GIFTERS = [476727347, 6840540201]

# Bote o Username do bot sem o @
# Exemplo: default
BOT_LINK = "LojinhaBetano_Bot"



# Bote o Username do suporte sem o @
# Exemplo: suporte
BOT_LINK_SUPORTE = "Lonsepo"
##```
