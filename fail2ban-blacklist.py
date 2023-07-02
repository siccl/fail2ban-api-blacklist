#!/usr/bin/python3
"""
Fail2Ban Blacklist
Author: @siccl (github.com/siccl)
Description: Save Banned IP into file and send to an API with JWT
"""
import sys
import os
import ipaddress
import datetime
import jwt
import requests

# Fail2Ban variables
BAN_IP = sys.argv[1]
BLACKLIST_FILE = os.environ['BLACKLIST_FILE']

# API variables
API_URL = os.environ['API_URL']
CONTENT_TYPE="Content-Type: application/json"

# Save banned IP into file function
def save_banned_ip():
    with open(BLACKLIST_FILE, 'a') as file:
        file.write(BAN_IP + '\n')

# Remove banned IP from file function
def remove_banned_ip():
    with open(BLACKLIST_FILE, 'r+') as file:
        lines = file.readlines()
        file.seek(0)
        for line in lines:
            if line != BAN_IP + '\n':
                file.write(line)
        file.truncate()

# Check if BAN_IP is valid function
def is_valid_ip():
    # Check if IP is valid
    try:
        ipaddress.ip_address(BAN_IP)
        # Check if IP is local or private
        if ipaddress.ip_address(BAN_IP).is_private:
            return False
        if ipaddress.ip_address(BAN_IP).is_loopback:
            return False
        if ipaddress.ip_address(BAN_IP).is_link_local:
            return False
    except ValueError:
        return False
    return True

# Check if IP is banned function
def is_banned_ip():
    # Check if IP is banned in file
    with open(BLACKLIST_FILE, 'r') as file:
        for line in file:
            if BAN_IP in line:
                return True
            else:
                return False

# Generate JWT token function
def generate_jwt_token():
    # Generate JWT token
    SECRET_KEY=os.environ['SECRET_KEY']
    NOW = datetime.datetime.utcnow()
    EXP = NOW + datetime.timedelta(seconds=30)
    payload = {
        "iss": "fail2ban-blacklist",
        "iat": NOW,
        "exp": EXP,
        "nbf": NOW,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

# Send banned IP to API function
def send_banned_ip():
    headers = {
        'Authorization': 'Bearer ' + generate_jwt_token(),
        'Content-Type': 'application/json',
    }
    data = '{"ip": "' + BAN_IP + '"}'
    response = requests.post(API_URL, headers=headers, data=data)
    if response.status_code == 200:
        return True
    else:
        return False

# Display help function
def display_help():
    # Display help message, if no arguments are passed
    # ban IP, unban IP
    print("Usage: fail2ban-blacklist.py [ban|unban|check] [IP]")

# check dependencies
def check_dependencies():
    # Check if dependencies are installed
    try:
        import jwt
        import requests
    except ImportError:
        print("Error: Please install dependencies")
        print("pip3 install -r requirements.txt")
        sys.exit(1)

# Main function
def main():
    if len(sys.argv) == 1:
        display_help()
    elif sys.argv[1] == 'ban':
        if is_valid_ip() and not is_banned_ip():
            save_banned_ip()
            return send_banned_ip()
    elif sys.argv[1] == 'unban':
        remove_banned_ip()
    else:
        display_help()