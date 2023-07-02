#!/usr/bin/python3
"""
Fail2Ban Blacklist
Author: @siccl (github.com/siccl)
Description: Save Banned IP into file and send to an API with JWT
"""
import sys
import os

# Fail2Ban variables
BAN_IP = sys.argv[1]
BLACKLIST_FILE = os.environ['BLACKLIST_FILE']
File="/var/lib/misc/fail2banBlackList"

# JWT variables
JWT_TOKEN = os.environ['JWT_TOKEN']
JWT_HEADER = os.environ['JWT_HEADER']
JWT_PAYLOAD = os.environ['JWT_PAYLOAD']

# API variables
API_URL = os.environ['API_URL']
ContentType="Content-Type: application/json"
# Save banned IP into file
