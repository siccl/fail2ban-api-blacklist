#!/usr/bin/python3
import sys
import os
import ipaddress
import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

# Set environment variables
BLACKLIST_FILE = os.getenv('BLACKLIST_FILE')

# Save banned IP into file function
def save_banned_ip(BAN_IP):
    with open(BLACKLIST_FILE, 'a') as file:
        file.write(BAN_IP + '\n')

# Remove banned IP from file function
def remove_banned_ip(BAN_IP):
    with open(BLACKLIST_FILE, 'r+') as file:
        lines = file.readlines()
        file.seek(0)
        for line in lines:
            if line != BAN_IP + '\n':
                file.write(line)
        file.truncate()

# Check if BAN_IP is valid function
def is_valid_ip(BAN_IP):
    # Check if IP is valid
    TEST_IP = False
    try:
        TEST_IP = ipaddress.ip_address(BAN_IP)
        # Check if IP is local or private
        if ipaddress.ip_address(BAN_IP).is_private:
            TEST_IP = False
        if ipaddress.ip_address(BAN_IP).is_loopback:
            TEST_IP = False
        if ipaddress.ip_address(BAN_IP).is_link_local:
            TEST_IP = False
    except ValueError:
        TEST_IP = False
    return TEST_IP

# Check if IP is banned function
def is_banned_ip(BAN_IP):
    # Check if IP is banned in file
    with open(BLACKLIST_FILE, 'r') as file:
        for line in file:
            if BAN_IP in line:
                return True
            else:
                return False

# Generate JWT token function
def generate_jwt_token():
    import jwt
    # Generate JWT token
    SECRET_KEY=os.getenv('JWT_SECRET_KEY')
    ALGORITHM=os.getenv('JWT_ALGORITHM')
    NOW = datetime.datetime.utcnow()
    EXP_TIME = int(os.getenv('JWT_EXP_TIME'))
    EXP = NOW + datetime.timedelta(seconds=EXP_TIME)
    payload = {
        "iss": os.getenv('JWT_ISSUER'),
        "iat": NOW,
        "exp": EXP,
        "nbf": NOW,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Send banned IP to API function
def send_banned_ip(BAN_IP):
    API_URL = os.getenv('API_URL')
    headers = {
        'Authorization': 'Bearer ' + generate_jwt_token(),
        'Content-Type': 'application/json',
    }
    data = '{"IP": "' + BAN_IP + '"}'
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
def check_dependencies(test=True):
    global BLACKLIST_FILE
    # Check if dependencies are installed
    # Check run script as root or sudo
    if not os.geteuid() == 0:
        print("Error: Please run script as root or sudo")
        sys.exit(1)
    CHECK_ERROR = False
    # Check if dependencies are installed
    try:
        import jwt
        import requests
        import ipaddress
        import datetime
    except ImportError:
        print("Error: Please install dependencies")
        print("pip3 install -r requirements.txt")
        CHECK_ERROR = True
    if CHECK_ERROR:
        sys.exit(1)
    else:
        # Check if environment variables are set
        # Validate folder BLACKLIST_FILE if exists
        if not os.path.exists(os.path.dirname(BLACKLIST_FILE)):
            print("Error: BLACKLIST_FILE folder does not exist")
            CHECK_ERROR = True
    if CHECK_ERROR:
        sys.exit(1)
    else:
        if test:
            print("Dependencies are installed and valid")

# Main function
def main():
    # Check if arguments are passed
    try:
        sys.argv[1]
        BAN_IP = sys.argv[2]
    except IndexError:
        display_help()
        sys.exit(0)
    if len(sys.argv) == 1:
        display_help()
    elif sys.argv[1] == 'ban':
        check_dependencies(False)
        if is_valid_ip(BAN_IP) and not is_banned_ip(BAN_IP):
            save_banned_ip(BAN_IP)
            return send_banned_ip(BAN_IP)
        else:
            if not is_valid_ip(BAN_IP):
                print("Error: " + BAN_IP + "is not valid")
            elif is_banned_ip(BAN_IP):
                print("Error: IP is already banned")
            sys.exit(1)
    elif sys.argv[1] == 'unban':
        check_dependencies(False)
        remove_banned_ip(BAN_IP)
    elif sys.argv[1] == 'check':
        check_dependencies()
    else:
        display_help()
    sys.exit(0)
# Run main function
if __name__ == "__main__":
    main()