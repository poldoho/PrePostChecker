#!/usr/bin/python3

from getpass import getpass
from datetime import datetime
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException, NetMikoAuthenticationException
import os


def read_file(filename):
    '''
    Read a file then return a list containing all lines from the file.

    Args:
        filename (str): name of file to be converted to python list

    Returns:
        lines: text file converted to python list
    '''
    with open(filename) as file:
        lines = file.read().splitlines()
        return lines


def get_inputs():
    '''
    Get username and password from user.

    Returns:
        username: login username
        password: login password
        port: ssh port (default=22)
    '''

    username = input("Username: ")
    password = getpass()

    # Get SSH port
    while True:
        port = input("SSH port (leave blank for default): ")
        try:
            int(port)
            if port == "":
                port = "22"
                break
            else:
                break
        except ValueError:
            print("Invalid input! Enter a valid port number.")

    # Get Pre or Post
    while True:
        prepost = input("Pre or Post: ").title()
        if prepost.lower() == "pre" or prepost.lower() == "post":
            break
        else:
            print("Invalid input!")

    print("")

    return username, password, port, prepost


def prepostchecks(devices, commands, username, password, prepost, port="22"):
    '''
    Connect to network devices using netmiko module and capture different show commands.

    Args:
        devices (list): python list containing network devices
        commands (list): python list containing show commands
        username (str): login username
        password (str): login password
        port (str): (optional) port used by SSH

    Raises:
        NetMikoAuthenticationException: Invalid/incorrect auth credentials
        NetMikoTimeoutException: Device is unreachable
    '''

    for device in devices:
        ios_xe = {
            'device_type': 'cisco_xe',
            'host': device,
            'username': username,
            'password': password,
            'port': port  # optional parameter
        }

        print("#" * 100)
        print(f"Connecting to {ios_xe['host']}..")
        print("#" * 100)

        try:
            net_connect = ConnectHandler(**ios_xe)

            hostname = net_connect.find_prompt().replace("#", "")
            print(f"Logged in to {hostname}.")
            print(f"Getting logs now.")

            # Filename for Pre/Post Checks, BackupConfig, Output Directories
            show_filename = f"{hostname}_{prepost}CheckLogs-{datetime.now().strftime('%m%d%Y-%H%M')}.txt"

            show_fullpath = os.path.join(
                os.getcwd(), f"Logs/{prepost}", show_filename)

            print(f"Outdir: {os.getcwd()}/Logs/{prepost}/")
            print(f"Logs Filename: {show_filename}")

            output = ""
            for command in commands:
                output += "\n" + ("*" * 20) + str(command) + \
                    ("*" * (80 - len(command))) + "\n\n"
                output += net_connect.send_command(command)
                # For troubleshooting only
                # print(output)

            with open(show_fullpath, "w") as logs:
                logs.writelines(output)

            print("")
            print("Backing up config.")

            backup_filename = f"{hostname}_BackupConfig-{datetime.now().strftime('%m%d%Y-%H%M')}.cfg"
            backup_fullpath = os.path.join(
                os.getcwd(), f"Logs/{prepost}", backup_filename)
            print(f"Backup Filename: {backup_filename}")

            with open(backup_fullpath, "w") as backup:
                backup.write(net_connect.send_command("show running"))

            print(f"Completed! Disconnecting now from {hostname}.")
            print("#" * 100)
            print("")

        except NetMikoAuthenticationException:
            print("Authentication failed.\nSkipping..")
            print("#" * 100)
            print("")

        except NetMikoTimeoutException:
            print("Device unreachable.\nSkipping..")
            print("#" * 100)
            print("")


if __name__ == "__main__":

    # Banner
    print("*" * 100)
    print("  _ \            _ \            |    ___| |               |")
    print(" |   |  __| _ \ |   | _ \   __| __| |     __ \   _ \  __| |  /  _ \  __|")
    print(" ___/  |    __/ ___/ (   |\__ \ |   |     | | |  __/ (      <   __/ |")
    print("_|    _|  \___|_|   \___/ ____/\__|\____|_| |_|\___|\___|_|\_\\___|_|")
    print("*" * 100)

    # Get inputs from user
    username, password, port, prepost = get_inputs()

    # Get list of devices from devices.txt
    devices = read_file("devices.txt")

    # Get list of commands from commands.txt
    commands = read_file("commands.txt")

    # Create directories needed

    if not os.path.exists("./Logs/Pre"):
        os.makedirs("./Logs/Pre")
    elif not os.path.exists("./Logs/Post"):
        os.makedirs("./Logs/Post")

    # Call program
    prepostchecks(devices, commands, username, password, prepost, port=port)
