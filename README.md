# Mail-Sender Console-Based App

A simple TUI script used for sending emails through MailGun API. The authentication protocol is insecure, and email validation is not yet implemented.
The mailgun module also includes a simple CLI argument parser that for now supports only loading the CSV file data.

![TUI Image](https://github.com/YoloTheBEst/Mailgun-Mail-Sender/blob/main/images/TUI.png)

## TUI Usage

    Linux:
    pip install -r requirements.txt
    python3 /path/to/folder/source/tui.py

    Windows:
    pip install -r requirements.txt
    python3 path\to\folder\source\tui.py

## CLI Usage

`tui.py [-h] --csv [CSV] [-c] [-n [NAME]] [-e [EMAILS]] [-s [SUBJECT]] [-t [TEXT]]`

## Synopsis

This command line tool is used to perform certain operations on a CSV file. It requires the `--csv` argument followed by the path to the CSV file. Additionally, you can use the following optional arguments:

**Arguments:**

- `-h, --help`: Show the help message and exit.

- `--csv [CSV]`: Path to the CSV file (required argument).

- `-c`: Enables the CLI mode for the script. ()

- `-n [NAME]`: Specify a name for the operation.

- `-e [EMAILS]`: Provide one or more email addresses.

- `-s [SUBJECT]`: Set a subject for sending a mail.

- `-t [TEXT]`: Enter custom text for sending a mail.
