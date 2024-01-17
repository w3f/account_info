import sys
import time

import json
import requests

# Constants

# Headers needed for receiving content
HEADERS = {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY,
}


# Arguments:
# 1: Network - Accepts "kusama" or "polkadot"
# 1: Address - Address of account to research
# 3: API Key - Your subscan API key. See https://support.subscan.io/#introductionb


# Check if account is verified - returns string "Yes" or "No"
def account_verified(address):
    endpoint = "https://" + NETWORK.lower() + ".api.subscan.io/api/v2/scan/accounts"
    json_data = {
        'row': 10,
        'page': 0,
        'address': [address],
    }
    r = requests.post(endpoint, headers=HEADERS, json=json_data)
    rj = json.loads(r.text)

    try:
        verified = rj['data']['list'][0]['account_display']['identity']
        return verified
    except:
        return "No"

# Get account identity information.
# This has to be done via the  api/v2/scan/search endpoint
# Return string with any identity information
def get_account_identity_info(address):
    return "meow"

# Get earliest identity set date (i.e. earliest date a
# an identity.IdentitySet event occurred). Note that you need to check
# for events, not extrinsics, because the extrinsic won't show up
# if a proxy was used.
def get_identity_set_date(address):
    return "1 Jan 1970"

# Get earliest identity verified date (i.e. earliest date a
# an identity.JudgementGiven event occurred). Note that you need to check
# for events, not extrinsics, because the extrinsic won't show up
# if a proxy was used.
def get_identity_verified_date(address):
    return "1 Jan 1970"

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
    print("Verified Information: " + str(verified_info))
    print("Identity first set: " + str(identity_set_date))
    print("Identity first verified: " + str(identity_verified_date))
    print("Other treasury proposals: " + str(other_treasury_proposals))

# EXECUTION STARTS HERE


# Read in args from command line

ARGS_LEN = len(sys.argv) - 1
if ARGS_LEN != 3:
    print("Usage: python info.py NETWORK ACCOUNT API_KEY")
    print("NETWORK - either 'kusama' or 'polkadot' (without quotes)")
    print("ADDRESS - account to research")
    print("API Key - Your subscan API key. See https://support.subscan.io/")
    sys.exit(1)
else:
    
    NETWORK = sys.argv[1].lower()
    ADDRESS = sys.argv[2]
    API_KEY = sys.argv[3]



# Check if you should connect to Polkadot or Kusama API endpoints
if NETWORK == 'kusama' or NETWORK == 'polkadot':
    print("Connecting to ' + str(NETWORK) + ' Subscan API endpoint.")
else:
    print("Accepted networks are KUSAMA or POLKADOT (case-insensitive)")
    sys.exit(1)

print("Connecting to " + str(NETWORK) + " Subscan API endpoint.")



verified = account_verified(ADDRESS)
identity_info = get_account_identity_info(ADDRESS)
identity_set_date = get_identity_set_date(ADDRESS)
identity_verified_date = get_identity_verified_date(ADDRESS)
other_tps = get_other_tps(ADDRESS)

print_out_final(ADDRESS, verified, identity_info, identity_set_date,
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
