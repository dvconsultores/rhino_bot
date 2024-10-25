#!/bin/bash


# Compile translations
msgfmt telegram_bot/locales/es/LC_MESSAGES/messages.po -o telegram_bot/locales/es/LC_MESSAGES/messages.mo
msgfmt telegram_bot/locales/en/LC_MESSAGES/messages.po -o telegram_bot/locales/en/LC_MESSAGES/messages.mo

echo "Setup completed successfully."