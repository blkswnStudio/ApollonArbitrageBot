from telegram import KeyboardButton, ReplyKeyboardMarkup


class Buttons:

    # Button Names
    get_current_data_name = "Current Data ℹ️"

    # Buttons
    get_current_data_btn = KeyboardButton(get_current_data_name)

    # Button Markups
    basic_markup = ReplyKeyboardMarkup([[get_current_data_btn]])

