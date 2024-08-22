import requests
import time
import subprocess
import re
import os
import json

# Define the wallet address to watch
wallet_address = "BPJmf3DMBQ2vrWsn27LyckxQ5NSPH7M9k4"

def wait_for_tx_confirmation(address):
    api_url = f"https://bells.quark.blue/api/address/{address}"
    while True:
        try:
            time.sleep(120)
            response = requests.get(api_url)
            response.raise_for_status()  # Raises an error for HTTP codes 4xx/5xx
            try:
                response_data = response.json()  # Parse JSON response
            except json.JSONDecodeError:
                print(f"Failed to decode JSON from API response: {response.text}")
                time.sleep(30)
                continue

            # Check if mempool_stats tx_count is zero
            tx_count = response_data.get("mempool_stats", {}).get("tx_count", -1)
            if tx_count == 0:
                print(f"All transactions for address {address} have been confirmed.")
                break
            else:
                print(f"Waiting for transactions to be confirmed. Current mempool tx_count: {tx_count}. Retrying in 150 seconds...")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching address data {address}: {e}")
        
        time.sleep(30)

def handle_post_action(address):
    while True:
        wait_for_tx_confirmation(address)
        result_sync = subprocess.run("node . wallet sync", shell=True, capture_output=True, text=True)
        print("Output from wallet sync command:")
        print(result_sync.stdout)

        txid_search = re.search(r"txid: (\w+)", result_sync.stdout)
        if txid_search:
            txid_to_confirm = txid_search.group(1)
            print(f"New TXID to confirm: {txid_to_confirm}")

        if "too long mempool reached" not in result_sync.stdout:
            break

def process_mint(directory, file_extension, start_number, details_list):
    for i in range(start_number, len(details_list) + start_number):
        actual_index = i - start_number
        if actual_index >= len(details_list):
            print(f"Index {i} exceeds the length of details_list {len(details_list)}")
            break
        details = details_list[actual_index]
        image_path = os.path.join(directory, f"{i}.{file_extension}")
        print(f"Processing file: {image_path} for address: {details['dogecoin_address']}")
        if not os.path.exists(image_path):
            print(f"File not found: {image_path}")
            continue
        
        # Minting process
        mint_command = f"node . mint {details['dogecoin_address']} {image_path}"
        result_mint = subprocess.run(mint_command, shell=True, capture_output=True, text=True)
        print("Output from mint command:")
        print(result_mint.stdout)
        if result_mint.stderr:
            print("Error in mint command:")
            print(result_mint.stderr)
        
        # Extract TXID and update JSON
        txid_search = re.search(r"txid: (\w+)", result_mint.stdout)
        if txid_search:
            last_txid = txid_search.group(1)
            modified_txid = f"{last_txid}i0"
            print(f"Successful mint, TXID: {modified_txid}")
            update_json_file(image_path, modified_txid, details)
        else:
            print("No TXID found, skipping file update.")
            continue

        # Check for specific console messages
        if "too long mempool reached, wait for TXID to confirm before wallet sync command" in result_mint.stdout or \
           "inscription complete continue to next file" in result_mint.stdout:
            handle_post_action(wallet_address)

def update_json_file(image_path, txid, details):
    json_file_name = "airDropOutput.json"
    try:
        data = {}
        if os.path.exists(json_file_name):
            with open(json_file_name, 'r') as file:
                data = json.load(file)
        key = os.path.basename(image_path)
        data[key] = {"txid": txid, "address": details['dogecoin_address']}
        with open(json_file_name, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Updated {json_file_name} with {key}: {txid}, {details['dogecoin_address']}")
    except Exception as e:
        print(f"Error updating {json_file_name}: {e}")

def extract_details(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            details = json.load(file).get('airDropList', [])
            print(f"Extracted {len(details)} details from {file_name}")
            return details
    except Exception as e:
        print(f"An error occurred while reading {file_name}: {e}")
        return []

def read_last_output(json_file_name):
    if os.path.exists(json_file_name):
        try:
            with open(json_file_name, 'r') as file:
                data = json.load(file)
                return len(data)
        except json.JSONDecodeError as e:
            print(f"JSON decode error in {json_file_name}: {e}")
    return 0

def continuous_minting_process(directory, file_extension, start_number):
    last_count = read_last_output('airDropOutput.json')
    print(f"Starting minting process from last count: {last_count}")
    details_list = extract_details('airDropList.json')
    details_list = details_list[last_count:]
    process_mint(directory, file_extension, start_number, details_list)

# Initialize main variables and start process
directory = r'<file dir>'
file_extension = 'webp'
start_number = 1

continuous_minting_process(directory, file_extension, start_number)
