#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
from requests.exceptions import HTTPError
import base64
import re
import os

headers = {"X-Vault-Token": os.environ["VAULT_TOKEN"]}
api_host = os.environ["VAULT_HOST"]

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text("""
    This is a Telegram Bot that use Encryption as a Service (provided by the Transit Secrets Engine of Hashicorp Vault)\n
    Usage:
    For encrypt a messagge c:<your_key>:<your message>
    For Decrypt a messagge d:<your_key>:<your_message>
    """)


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    #update.message.reply_text(update.message.text)
    logger.info(f"Received this message from Telegram: {update.message.text}")
    
    logger.info(f"{len(update.message.text.split(':'))}")

    if len(update.message.text.split(':')) > 2:
        if re.match(r"^e:.*", update.message.text):
            logger.info(f"[Encrypt] Starting request to Vault")

            key = update.message.text.split(':', 2)[1]

            logger.info(f"[Encrypt] Checking if the key ({key}) is a correct format")

            if re.match(r"[a-z0-9]*$", key):
                update.message.reply_text(f"Encrypting your message using Vault key {key} with 2048-bit RSA key")
                myobj = {"type": "rsa-2048"}

                try:
                    logger.info(f"[Encrypt] Creating key {key} for transit engine")
                    r = requests.post(f"{api_host}/v1/transit/keys/{key}", json=myobj, verify=False, headers=headers, allow_redirects=True) 
                except HTTPError as http_err:
                    logger.info(f'[Encrypt] HTTP error occurred: {http_err}')
                except Exception as err:
                    logger.info(f'[Encrypt] Other error occurred: {err}')

                logger.info(f"[Encrypt] Status code of key creation: {r.status_code}")
                logger.info(f"[Encrypt] Key creation result: {r.text}")

                message = re.match(r"^e:(.*):(.*)", update.message.text)[2]
                if len(message) > 1:
                    logger.info(f"[Encrypt] Full message received: {message}")
                    message_bytes = message.encode('UTF8')
                    base64_bytes = base64.b64encode(message_bytes)
                    base64_message = base64_bytes.decode('UTF8')
                    logger.info(f"[Encrypt] base64_message {base64_message}")

                    myobj = {"plaintext": base64_message}
                    logger.info(myobj)
                    r = requests.Request
                    try:
                        r = requests.post(f"{api_host}/v1/transit/encrypt/{key}", json=myobj, verify=False, headers=headers, allow_redirects=True) 
                    except HTTPError as http_err:
                        logger.info(f'Encrypt] HTTP error occurred: {http_err}')
                    except Exception as err:
                        logger.info(f'Encrypt] Other error occurred: {err}')

                    payload = r.json()
                    update.message.reply_text(payload["data"]["ciphertext"])
                else:
                    update.message.reply_text("""
                    Message not valid! 
                    Usage:
                    For Encrypt a messagge c:<your_key>:<your_message>
                    For Decrypt a messagge d:<your_key>:<your_message>
                    """)
            else:
                update.message.reply_text("Key name is not valid. Use only numbers or lowercase letters")

        elif re.match(r"^d:.*", update.message.text):
            logger.info("[Decrypt] Starting request to Vault")
            logger.info(f"[Decrypt] Full message received {update.message.text}")

            key = update.message.text.split(':', 2)[1]

            logger.info(f"[Decrypt] Using key {key}")
            update.message.reply_text(f"Decrypting your message using Vault key {key}")

            ciphertext = update.message.text.split(':', 2)[2]

            logger.info(f"[Decrypt] Received message. ciphertext: {ciphertext}")

            myobj = {"ciphertext": ciphertext}

            try:
                r = requests.post(f"{api_host}/v1/transit/decrypt/{key}", json=myobj, verify=False, headers=headers, allow_redirects=True) 
            except HTTPError as http_err:
                logger.info(f'[Decrypt] HTTP error occurred: {http_err}')
                update.message.reply_text("Error in decrypting message...")

            except Exception as err:
                logger.info(f'[Decrypt] Other error occurred: {err}')
                update.message.reply_text("Error in decrypting message...")


            logger.info(f"[Decrypt] Response status code: {r.status_code}")
            logger.info(f"[Decrypt] Response payload: {r.text}")

            if r.status_code != "200":
                update.message.reply_text("Error in decrypting message...")

            payload = r.json()
            base64_message = payload["data"]["plaintext"]
            logger.info(base64_message)

            base64_bytes = base64_message.encode('UTF8')
            message_bytes = base64.b64decode(base64_bytes)
            message = message_bytes.decode('UTF8')
            logger.info(f"[Decrypt] Lenght final message: {len(message)}")

            if len(message) > 0:
                update.message.reply_text(message)
            else:
                update.message.reply_text("Error in decrypting message...")
        else:
            update.message.reply_text("""
            Usage:
            For Encrypt a messagge c:<your_key>:<your_message>
            For Decrypt a messagge d:<your_key>:<your_message>
            """)
    else:
        update.message.reply_text("""
        Usage:
        For Encrypt a messagge c:<your_key>:<your_message>
        For Decrypt a messagge d:<your_key>:<your_message>
        """)


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(os.environ["TELEGRAM_TOKEN"])

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    logger.info("Starting Vault Bot")
    main()
