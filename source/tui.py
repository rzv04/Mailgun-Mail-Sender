"""
Simple TUI for Mailgun API.Checking mails not yet implemented.Also has a CLI interface that can be accessed by typing -c or --cli in the command line.
"""


import consolemenu
import consolemenu.items
from colorama.ansi import Fore
import pyfiglet
from sys import exit, argv
from os.path import exists
from mailgun import Mail
import time


class FeedbackHandler:
    def __init__(self):
        pass

        # Fore is Font Foreground color

    def data_loaded_successfully(self):
        consolemenu.Screen().println(Fore.GREEN + "Data loaded successfully")

    def data_load_failed(self):
        consolemenu.Screen().println(Fore.RED + "Data load failed")

    def data_updated_successfully(self):
        consolemenu.Screen().println(Fore.GREEN + "Data updated successfully")

    def data_update_failed(self):
        consolemenu.Screen().println(Fore.RED + "Data update failed")


class MainMenu:
    mail = Mail()

    def load_contents_and_send_email(self) -> None:
        self.mail.set_mail_contents_interactive()
        self.mail.send_email()

        FeedbackHandler().data_loaded_successfully()
        time.sleep(1)

    def set_params_interactive_feedback(self) -> None:
        self.mail.set_params()

        FeedbackHandler().data_loaded_successfully()
        time.sleep(1)

    def set_params_csv_feedback(self) -> None:
        self.mail.set_params_from_csv()

        FeedbackHandler().data_loaded_successfully()
        time.sleep(1)

    def __init__(self) -> None:
        self.hero_title = pyfiglet.figlet_format("Mail-Sender", "small")

        self.hero_subtitle = "Send emails using the Mailgun API"

        self.menu = consolemenu.ConsoleMenu(
            Fore.GREEN + self.hero_title,
            subtitle=Fore.BLUE + self.hero_subtitle,
            show_exit_option=False,
        )

        self.enter_api_key_interactive = consolemenu.items.FunctionItem(
            Fore.GREEN + "Input API credentials",
            self.set_params_interactive_feedback,
        )

        self.enter_api_key_csv = consolemenu.items.FunctionItem(
            Fore.GREEN + "Input API credentials from api.csv",
            self.set_params_csv_feedback,
        )

        self.send_email_prompt = consolemenu.items.FunctionItem(
            Fore.GREEN + "Send An Email", self.load_contents_and_send_email
        )

        self.check_mail_prompt = consolemenu.items.FunctionItem(
            Fore.GREEN + "Check Recieved Messages (Not Implemented)",
            self.mail.check_mails,
        )  # TODO

        self.exit_menu = consolemenu.items.ExitItem(Fore.RED + "Exit")

        self.menu.append_item(self.enter_api_key_interactive)
        self.menu.append_item(self.enter_api_key_csv)
        self.menu.append_item(self.send_email_prompt)
        self.menu.append_item(self.check_mail_prompt)
        self.menu.append_item(self.exit_menu)

    def show(self) -> None:
        self.menu.show()


def main():
    if len(argv) == 1:
        console = MainMenu()
        console.show()
    else:
        mail = Mail()
        mail.parse_args(mail.init_parser())


if __name__ == "__main__":
    main()
