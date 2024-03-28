import requests
import json
import time

nodenum = input("Node ID: ").strip()  # Removing extra spaces if any
url = input("URL: ")
apikey = input("API Key (Application): ")

try:
    # Converting the entered node ID to int if the API expects a number
    nodenum = int(nodenum)
except ValueError:
    # API expects a string, don't convert to int
    pass

yes_or_no = input("Delete servers on the node? (y/n): ")
if yes_or_no.lower() != 'y':
    exit()

base_url = f'{url}/api/application/servers'
headers = {
    "Authorization": f"Bearer {apikey}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

servers_on_node = []
page = 1

while True:
    params = {'page': page}
    response = requests.get(base_url, headers=headers, params=params)

    if response.status_code == 200 and 'application/json' in response.headers['Content-Type']:
        try:
            data = response.json()
            data_servers = data.get('data', [])
            if data_servers:
                for server in data_servers:
                    # Checking if the node ID matches considering possible data type differences
                    if str(server['attributes']['node']) == str(nodenum):
                        servers_on_node.append(server)
                page += 1
            else:
                break
        except json.JSONDecodeError:
            print(f"Response is not valid JSON: {response.text}")
            break
    else:
        print(f"Inappropriate status code {response.status_code} or Content-Type: {response.headers['Content-Type']}")
        break

server_count = len(servers_on_node)
print("Number of servers on the node:", server_count)

identifiers = [server['attributes']['id'] for server in servers_on_node]
with open('server_identifiers.json', 'w') as file:
    json.dump(identifiers, file)

time.sleep(1)

# Confirmation of user action before deletion
confirm_delete = input("Are you sure you want to proceed with deletion? All servers on the node will be deleted. (y/n): ")
if confirm_delete.lower() != 'y':
    exit()

print("Deleting servers...")

for identifier in identifiers:
    request_url = f'{base_url}/{identifier}/force'  # Fixed to correctly form the URL
    response = requests.delete(request_url, headers=headers)
    if response.status_code in [200, 204]:
        print(f"Server with identifier {identifier} deleted.")
    else:
        print(f"Failed to delete server with identifier {identifier}: {response.status_code} {response.text}")

print("Deletion operation completed.")
