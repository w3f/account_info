import sys
import time

import json
import requests

from dotenv import load_dotenv
from datetime import datetime

import os

# load the .env file
load_dotenv()

# get the key from the .env file
api_key = os.getenv('API_KEY')

# Constants

# Headers needed for receiving content
HEADERS = {
    'Content-Type': 'application/json',
    'X-API-Key': api_key,
}


# Arguments:
# 1: Network - Accepts "kusama" or "polkadot"
# 1: Address - Address of account to research

# the following was changed in favor of a .env file.
# 3: API Key - Your subscan API key. See https://support.subscan.io/#introductionb


# Once gather the events related to the account
def fetch_events(address):
    # The endpoint for events
    endpoint = "/api/v2/scan/events"

    # Full URL
    url = f"{BASE_URL}{endpoint}"

    # Parameters for the request, adjust if necessary
    params = json.dumps({
        "address": address,
        "page": 0,
        "row": 100
    })

    # Send the GET request to the API
    response = requests.request("POST", url, headers=HEADERS, data=params)
    
    # Check if the request was successful
    if response.status_code != 200:
        print("fetching events failed with status code: " + response.status_code)
        sys.exit(1)
    else:
        # Convert the response to JSON
        data = response.json()
        return data

# Once gather the events related to the account
def fetch_account_data(address):
    endpoint = "/api/v2/scan/accounts"
    json_data = {
        'address': [address],
        'row': 10,
        'page': 0,
    }
    url = f"{BASE_URL}{endpoint}"
    r = requests.post(url, headers=HEADERS, json=json_data)
    result = json.loads(r.text)
    return result

# Check if account is verified - returns string "Yes" or "No"
def account_verified(address):
    
    verified = ACCOUNT_DATA['data']['list'][0]['registrar_info']

    if verified == None:
        verified = "NOT VERIFIED"
    else:
        verified = "VERIFIED"

    return verified


# Get account identity information.
# This has to be done via the  api/v2/scan/search endpoint
# Return string with any identity information
def print_account_identity_info():
    identity_info = ACCOUNT_DATA['data']['list'][0]['account_display']
    # check for most identity items

    # List of items you want to check in the dictionary
    items_to_check = ["display", "legal", "web", "riot", "email", "twitter"]
    
    # Check if the identity_info is a dictionary and has content
    if isinstance(identity_info, dict) and identity_info:
        for item in items_to_check:
            # Check if the item is in the dictionary and has a non-empty value
            if item in identity_info and identity_info[item]:
                print(f"{item}: {identity_info[item]}  {verified}")
    else:
        print("No identity information available.")
    

# Get earliest identity set date (i.e. earliest date a
# an identity.IdentitySet event occurred). Note that you need to check
# for events, not extrinsics, because the extrinsic won't show up
# if a proxy was used.
def get_identity_set_date(address):  
    # search for first event that sets the on-chain identity
    first_identity_event = None
    for event in EVENTS['data']['events']:
        # Check if the event concerns setting the identity
        if event['event_id'] == 'IdentitySet':
            first_identity_event = event

    if first_identity_event == None:
        return "no record found"
    if  'block_timestamp' in first_identity_event:
        block_timestamp = int(first_identity_event['block_timestamp'])    
        timestamp = datetime.utcfromtimestamp(block_timestamp).strftime('%Y-%m-%d %H:%M:%S')
        return timestamp 

# Get earliest identity verified date (i.e. earliest date a
# an identity.JudgementGiven event occurred). Note that you need to check
# for events, not extrinsics, because the extrinsic won't show up
# if a proxy was used.
def get_identity_verified_date(address):
    # search for first event that sets the on-chain identity
    first_identity_verified_event = None
    for event in EVENTS['data']['events']:
        # Check if the event concerns setting the identity
        if event['event_id'] == 'JudgementGiven':
            first_identity_verified_event = event
    
    if first_identity_verified_event == None:
        return "no record found"
    if 'block_timestamp' in first_identity_verified_event:
        block_timestamp = int(first_identity_verified_event['block_timestamp'])    
        timestamp = datetime.utcfromtimestamp(block_timestamp).strftime('%Y-%m-%d %H:%M:%S')
        return timestamp 

# Get any other treasury proposals made by this account
# OpenGov TPs: Generally you can check for referenda.DecisionDepositPlaced
# or SubmissionDepositPlaced (99% of the time both are initial submitter)
# for a Treasury Proposal.
# It may be better to check for Treasury.Rewarded events, but these would
# have to be double-checked as the proposal_index won't line up exactly
# with the Referendum.
def get_other_tps(address):
    return "None"


# Print out final results.
# They should look like this: https://polkadot.polkassembly.io/referenda/410#3PXzrYA5O16lenAy6wcP
def print_out_final(address,
                    verified,
                    verified_info,
                    identity_set_date,
                    identity_verified_date,
                    other_treasury_proposals):
    print("Address: " + str(address))
    print("Verified?: " + str(verified))
    print("Identity Information: ")
    print_account_identity_info()
    print("Identity first set: " + str(identity_set_date))
    print("Identity first verified: " + str(identity_verified_date))
    print("Other treasury proposals: " + str(other_treasury_proposals))

# EXECUTION STARTS HERE


# Read in args from command line

ARGS_LEN = len(sys.argv) - 1
if ARGS_LEN != 2:
    print("Usage: python info.py NETWORK ACCOUNT API_KEY")
    print("NETWORK - either 'kusama' or 'polkadot' (without quotes)")
    print("ADDRESS - account to research")
    sys.exit(1)
else:
    
    NETWORK = sys.argv[1].lower()
    BASE_URL = "https://" + NETWORK + ".api.subscan.io"
    ADDRESS = sys.argv[2]



# Check if you should connect to Polkadot or Kusama API endpoints
if NETWORK == 'kusama' or NETWORK == 'polkadot':
    print("Connecting to " + str(NETWORK) + " Subscan API endpoint.")
else:
    print("Accepted networks are KUSAMA or POLKADOT (case-insensitive)")
    sys.exit(1)
ACCOUNT_DATA = fetch_account_data(ADDRESS)
EVENTS = fetch_events(ADDRESS)
verified = account_verified(ADDRESS)
#identity_info = get_account_identity_info(ACCOUNT_DATA)
identity_set_date = get_identity_set_date(ADDRESS)
identity_verified_date = get_identity_verified_date(ADDRESS)
other_tps = get_other_tps(ADDRESS)

print_out_final(ADDRESS, verified, print_account_identity_info, identity_set_date,
                identity_verified_date, other_tps)

sys.exit(0)



# Helper code for reading in multiple pages (never executed right now)

for j in range(0, MAX_PAGES):
 
    json_data = {
        'row': NUM_ITEMS_PER_PAGE,
        'page': j,
        'module': 'Identity',
    }
    r = requests.post(URL, headers=HEADERS, json=json_data)
    rj = json.loads(r.text)

    for j in range(0, NUM_ITEMS_PER_PAGE):
        rj2 = json.loads(rj['data']['extrinsics'][j]['params'])
        raw_vote = (rj2[0]['value'])
        addr = rj['data']['extrinsics'][j]['account_display']['address']
        extr = rj['data']['extrinsics'][j]['extrinsic_index']
        


        # This sleeps for 400 ms, to ensure that we don't overwhelm our free tier of
        # API services from Subscan
        time.sleep(0.4)
