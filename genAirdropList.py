import json

# Addresses
address_1 = "BMsrDGdiMeKpDREnmeu4mka7KqG8ZbaNec"
address_2 = "BMsWxK97VWBfY1J5dLSRC4pQ29D4zS62Nx"
address_3 = "BT7KGQjVLBJCsz4BZpWc7g4vhGUTvukwUc"
address_4 = "BMVF7j8iJLUDT5s1cS1S67JSij2Z6j3xit"

# Create the airdrop list
airdrop_list = [{"dogecoin_address": address_1} for _ in range(1250)] + \
               [{"dogecoin_address": address_2} for _ in range(1250)]+ \
               [{"dogecoin_address": address_3} for _ in range(1250)]+ \
               [{"dogecoin_address": address_4} for _ in range(1250)]

# Create the final JSON structure
airdrop_data = {
    "airDropList": airdrop_list
}

# Save to a JSON file
with open("airDropList.json", "w") as json_file:
    json.dump(airdrop_data, json_file, indent=4)

print("JSON file created with 5000 entries.")