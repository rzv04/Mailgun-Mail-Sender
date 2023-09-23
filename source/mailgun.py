"""
Simple mail-sending driving code using MailGun.
The authentication is insecure, and email validation (SPF,DKIM,DMARC) is not yet implemented.
"""

# TODO:
# -Authentication from CSV file- complete
# Linux-like command-line launch(with argument parsing) - in progress
import os


import argparse
from abc import abstractclassmethod, abstractmethod
import requests
from sys import exit
import csv
from typing import List
import hashlib
import json


class MailGun:

    """
    Parent MailGun Class. Contains methods for obtaining the API Key, mail address,etc.

    """

    MAILGUN_API_URL = "https://api.mailgun.net/v3/{domain_name}/messages"
    EU_MAILGUN_API_URL = "https://api.eu.mailgun.net/v3/{domain_name}/messages"

    def __init__(
        self,
        api_key="",
        domain_name="",
        api_url="",
        domain_country="",
        csv_path="api.csv",  # default values
    ) -> None:
        self.api_key = api_key
        self.domain_name = domain_name
        self.api_url = api_url
        self.domain_country = domain_country
        self.csv_path = csv_path

    def set_params(self):
        self.api_key = input("Enter API key:\n")
        self.domain_country = input("Enter domain country:\n").strip().upper()
        self.domain_name = input("Enter domain name:\n")

        match self.domain_country:
            case "US":
                self.api_url = self.MAILGUN_API_URL.format(domain_name=self.domain_name)
            case "EU":
                self.api_url = self.EU_MAILGUN_API_URL.format(
                    domain_name=self.domain_name
                )
            case _:
                self.api_url = self.MAILGUN_API_URL.format(domain_name=self.domain_name)

        return self

        # Getters

    def get_api_key(self) -> str:
        return self.api_key

    def get_csv_path(self) -> str:
        return self.csv_path

        # Particular Setter for Parser - experimental

    def set_csv_path(self, csv_path):
        if csv_path == None:
            raise ValueError("CSV file path not specified.")
        if os.path.exists(csv_path):
            self.csv_path = csv_path
        else:
            raise FileNotFoundError("Incorrect CSV file path.")

    # Credential authentication - slow, should be used for first setup only (checked through config and hash)
    ##################################################
    def validate_credentials(self):
        # Validate API key

        response = requests.get("https://api.mailgun.net/", auth=("api", self.api_key))
        if response.status_code != 200:
            return False, "Invalid API key"

        # Validate domain name
        response = requests.get(
            f"https://api.mailgun.net/v3/domains/{self.domain_name}",
            auth=("api", self.api_key),
        )
        if response.status_code != 200:
            return False, "Invalid domain name"

        return True, "Valid credentials"

    # Not implemented correctly
    @abstractmethod
    def check_api_key(self):
        authenticate = requests.post(self.api_url, auth=("api", self.api_key))
        if authenticate.status_code == 200:
            print("Authentication successful")

        else:
            print("Error:", authenticate.text)
            exit(1)

    @abstractmethod
    def send_email(cls):
        ...

    def set_params_from_csv(self) -> None:
        """
        Reads and sets the necessary parameters using a CSV file.
        Reads and sets the necessary parameters using a CSV file.
        The CSV file should be named "api.csv" and formatted thusly:
        api_key,domain_country,domain_name
        """

        def set_params():
            self.set_csv_path(self.csv_path)

            with open(self.csv_path, "r") as read_file:
                reader = csv.DictReader(read_file)

                for i in reader:
                    try:
                        self.api_key = i["api_key"]
                        self.domain_country = i["domain_country"].upper()
                        self.domain_name = i["domain_name"]

                    except KeyError:
                        print("CSV File is incorrectly formatted.")
                        exit(1)

                match self.domain_country:
                    case "US":
                        self.api_url = self.MAILGUN_API_URL.format(
                            domain_name=self.domain_name
                        )
                    case "EU":
                        self.api_url = self.EU_MAILGUN_API_URL.format(
                            domain_name=self.domain_name
                        )
                    case _:
                        self.api_url = self.MAILGUN_API_URL.format(
                            domain_name=self.domain_name
                        )

        if Config.check_for_config() == True and os.path.getsize(
            Config.config_path
        ):  # If config exists and is not empty
            already_loaded = Config.load_config()
            Config.update_config(already_loaded)

        else:
            Config.create_config()
            already_loaded = False
            Config.update_config(already_loaded)

        if already_loaded:
            hash_check = Hasher.hash_csv()
            with open(Config.config_path, "r") as reader:
                json_data = json.load(reader)
                if hash_check == json_data["hash"] and json_data["Valid"] == "True":
                    return
                else:
                    set_params()
                    valid, _ = self.validate_credentials()
                    Config.update_config(valid)
        else:
            set_params()
            valid, _ = self.validate_credentials()
            Config.update_config(valid)


class Mail(MailGun):

    """
    Primary Mail class. Contains methods for setting MailGun API key, domain name, country, and for sending an email.
    """

    def set_mail_contents_interactive(self):
        self.from_name = input("Input your name: ")
        self.to_emails = input("Input emails to send to: ").split()
        self.subject = input("Enter email Title/Subject: ")
        self.content = input("Enter email content:\n")

        return self

    def set_mail_contents_cli(self, args):
        self.from_name = args.name
        self.to_emails = args.emails
        self.subject = args.subject
        self.content = args.text

    def send_email(self) -> "Mail":
        try:
            request = requests.post(
                self.api_url,
                auth=("api", self.api_key),
                data={
                    "from": f"{self.from_name} <mailgun@{self.domain_name}>",
                    "to": self.to_emails,
                    "subject": self.subject,
                    "text": self.content,
                },
            )
        except Exception:
            print("Incorrect request format.")
            exit(1)

        if request.status_code == 200:
            print("Mail sent successfully!")

        else:
            print("Error:", request.text)
            exit(1)

        return self

    def get_to_emails(self) -> List[str]:
        return self.to_emails

    def init_parser(self):
        parser = argparse.ArgumentParser(description="Send emails using MailGun API.")

        parser.add_argument(
            "--csv",
            required=True,
            nargs="?",
            help="""Path to CSV file with the following:
            api_key,domain_country,domain_name""",
            action="store",
        )

        parser.add_argument(
            "-c",
            "--cli",
            required=False,
            help="""Use CLI mode of the script.Required to use the other arguments.
            All of the other arguments become mandatory to use when this argument is used.
            """,
            action="store_true",
        )
        parser.add_argument(
            "-n",
            "--name",
            required=False,
            nargs="?",
            help="""Input your name""",
            action="store",
        )
        parser.add_argument(
            "-e",
            "--emails",
            required=False,
            nargs="?",
            help="""Input emails to send to""",
            action="store",
        )
        parser.add_argument(
            "-s",
            "--subject",
            required=False,
            nargs="?",
            help="""Enter email Title/Subject""",
            action="store",
        )
        parser.add_argument(
            "-t",
            "--text",
            required=False,
            nargs="?",
            help="""Enter email content""",
            action="store",
        )
        return parser

    def parse_args(self, parser):
        args = parser.parse_args()

        self.set_csv_path(
            args.csv
        )  # args is a Namespace object containing the csv attribute
        if args.cli:
            self.set_params_from_csv()
            self.set_mail_contents_cli(args)
            self.send_email()
        else:
            raise ValueError("Incorrect arguments passed.")

    # Not implemented yet
    @abstractmethod
    def check_mails(self):
        pass


mail = Mail()  # TODO propose a fix to make this local


class Hasher:
    """
    Simple MD5 Checksum hashing method.
    Might break the program if the CSV file is intentionally too large.
    """

    csv_path = mail.get_csv_path()

    # This code opens a file and reads it in binary mode.
    # It then uses hashlib to compute the md5 hash of the file and stores it in a variable. It then returns the hash.
    @classmethod
    def hash_csv(cls):
        md5_hash = hashlib.md5()
        with open(cls.csv_path, "rb") as reader:
            md5_bytes = reader.read()
            md5_hash.update(md5_bytes)
            file_hash = md5_hash.hexdigest()
        cls.file_hash = file_hash
        return cls.file_hash


class Config:
    """
    Class for handling a JSON config file.
    By default, the config file is/will be created in the same location as the
    Python script.
    """

    system_type = os.name
    config_path = (
        os.getcwd() + "/" + "config.json"
        if system_type == "posix"
        else (os.getcwd() + "\\" + "config.json")
    )

    @classmethod
    def check_for_config(cls) -> bool:
        """
        Checks for the existence of a JSON config file in the same path
        as the Python script.
        """
        if os.path.isfile(cls.config_path):
            return True
        return False

    @classmethod
    def create_config(cls):  # Creates config and configures the setting
        # Compute current CSV file hash
        csv_hash = Hasher.hash_csv()
        json_data = json.dumps({"Valid": None, "hash": csv_hash}, indent=4)  # TODO
        with open(cls.config_path, "w") as reader:
            reader.seek(0)
            reader.write(json_data)
            reader.truncate()

    @classmethod
    def load_config(
        cls,
    ) -> (
        bool
    ):  # If config exists, load config and check for valid credentials, returns bool if CSV file is already loaded
        with open(cls.config_path, "r") as reader:
            json_data = json.load(reader)
            if json_data["Valid"] == "True":
                return True
            return False

    @classmethod
    def update_config(
        cls, value: bool
    ) -> (
        None
    ):  # Update the Valid setting with the given value.Takes 1 positional argument
        with open(cls.config_path, "r+") as reader:
            json_data = json.load(reader)
            json_data["Valid"] = str(value)
            json_data = json.dumps(json_data)
            reader.seek(0)
            reader.write(json_data)
            reader.truncate()


# Example flow
def main():
    mail.parse_args(mail.init_parser())


if __name__ == "__main__":
    main()
