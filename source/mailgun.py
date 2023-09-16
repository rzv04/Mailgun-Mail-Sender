"""
Simple mail-sending driving code using MailGun.
The authentication is insecure, and email validation (SPF,DKIM,DMARC) is not yet implemented.
"""

# TODO:
# -Authentication from CSV file- complete
# Linux-like command-line launch(with argument parsing)
import os
import argparse
from abc import abstractclassmethod, abstractmethod
import requests
from sys import exit
import csv
from typing import List


class MailGun:

    """
    Parent MailGun Class. Contains methods for obtaining the API Key, mail address,etc.

    """

    def __init__(
        self,
        api_key="",
        domain_name="",
        api_url="",
        domain_country="",
        csv_path="api.csv",
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
                self.api_url = (
                    "https://api.mailgun.net/v3/{domain_name}/messages".format(
                        domain_name=self.domain_name
                    )
                )
            case "EU":
                self.api_url = (
                    "https://api.eu.mailgun.net/v3/{domain_name}/messages".format(
                        domain_name=self.domain_name
                    )
                )
            case _:
                self.api_url = (
                    "https://api.mailgun.net/v3/{domain_name}/messages".format(
                        domain_name=self.domain_name
                    )
                )

        return self

    # Experimental - credential authentication - slow, should be used for first setup only
    ##################################################
    def validate_credentials(self, api_key, domain_name, domain_country):
        # Validate API key
        response = requests.get(
            "https://api.mailgun.net/v3/domains", auth=("api", self.api_key)
        )
        if response.status_code != 200:
            return False, "Invalid API key"

        # Validate domain name
        response = requests.get(
            f"https://api.mailgun.net/v3/domains/{self.domain_name}",
            auth=("api", self.api_key),
        )
        if response.status_code != 200:
            return False, "Invalid domain name"

        # Validate domain country - Not implemented
        # response = requests.get(
        #     f"https://api.mailgun.net/v3/domains/{self.domain_name}",
        #     auth=("api", self.api_key),
        # )
        # if response.status_code == 200:
        #     data = response.json()
        #     if data["region"] != domain_country:
        #         return False, "Domain country does not match"
        # else:
        #     return False, "Failed to validate domain country"

        # All validations passed
        return True, "Valid credentials"

    ####################################################

    # Not implemented correctly
    @abstractclassmethod
    def check_api_key(cls, api_key, api_url):
        authenticate = requests.post(api_url, auth=("api", api_key))
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
                    self.api_url = (
                        "https://api.mailgun.net/v3/{domain_name}/messages".format(
                            domain_name=self.domain_name
                        )
                    )
                case "EU":
                    self.api_url = (
                        "https://api.eu.mailgun.net/v3/{domain_name}/messages".format(
                            domain_name=self.domain_name
                        )
                    )
                case _:
                    self.api_url = (
                        "https://api.mailgun.net/v3/{domain_name}/messages".format(
                            domain_name=self.domain_name
                        )
                    )

        # Getters

    def get_api_key(self) -> str:
        return self.api_key

    def get_csv_path(self) -> str:
        return self.csv_path

        # Particular Setter for Parser - experimental

    def set_csv_path(self, csv_path):
        if os.path.exists(csv_path):
            self.csv_path = csv_path
        else:
            raise FileNotFoundError("Incorrect CSV file path.")


class Mail(MailGun):

    """
    Primary Mail class. Contains methods for setting MailGun API key, domain name, country, and for sending an email.
    """

    def set_mail_contents(self):
        self.from_name = input("Input your name: ")
        self.to_emails = input("Input emails to send to: ").split()
        self.subject = input("Enter email Title/Subject: ")
        self.content = input("Enter email content:\n")

        return self

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

    def check_mails(self):
        pass

    def get_to_emails(self) -> List[str]:
        return self.to_emails


def Parser(mail):
    # parser=None
    def init_parser(mail):
        parser = argparse.ArgumentParser(description="Send emails using MailGun API.")

        # parser.add_argument(
        #     "--api-key",
        #     required=False,
        #     nargs="?",
        #     help="Set MailGun API key",
        #     type=str,
        #     action="store",
        #     const=mail.set_api_key,
        # )

        parser.add_argument(
            "--csv",
            required=True,
            nargs="?",
            help="""Path to CSV file with the following:
            api_key,domain_country,domain_name""",
            action="store",
        )

        args = parser.parse_args()
        mail.set_csv_path(args.csv)
        mail.set_params_from_csv()

    return init_parser


# Example flow
def main():
    mail = Mail()

    mail.set_params_from_csv()
    response, message = mail.validate_credentials(
        mail.api_key, mail.domain_name, mail.domain_country
    )

    print(message)
    # mail.set_mail_contents()
    # mail.send_email()

    # parse_init = Parser(mail)  # Closure
    # parser = parse_init(mail)


if __name__ == "__main__":
    main()
