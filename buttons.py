from telegram import KeyboardButton, ReplyKeyboardMarkup


class Buttons:

    # Button Names
    get_oracle_info_name = "Info ℹ️"

    # Buttons
    get_oracle_info_btn = KeyboardButton(get_oracle_info_name)

    # Button Markups
    basic_markup = ReplyKeyboardMarkup([[get_oracle_info_btn]])

