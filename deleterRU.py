import requests
import json
import time

nodenum = input("ID узла: ").strip()  # Удаление лишних пробелов, если они есть
url = input("URL: ")
apikey = input("Ключ API (Приложение): ")

try:
    # Преобразование введённого ID узла в int, если API ожидает число
    nodenum = int(nodenum)
except ValueError:
    # API ожидает строку, не преобразуем в int
    pass

yes_or_no = input("Удалить серверы на узле? (y/n): ")
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
                    # Проверка соответствия ID узла с учётом возможного различия в типах данных
                    if str(server['attributes']['node']) == str(nodenum):
                        servers_on_node.append(server)
                page += 1
            else:
                break
        except json.JSONDecodeError:
            print(f"Ответ не является допустимым JSON: {response.text}")
            break
    else:
        print(f"Неподходящий код состояния {response.status_code} или Content-Type: {response.headers['Content-Type']}")
        break

server_count = len(servers_on_node)
print("Количество серверов на узле:", server_count)

identifiers = [server['attributes']['id'] for server in servers_on_node]
with open('server_identifiers.json', 'w') as file:
    json.dump(identifiers, file)

time.sleep(1)

# Перед выполнением удаления - подтверждение действия пользователя
confirm_delete = input("Вы уверены, что хотите продолжить удаление? Все серверы на узле будут удалены. (y/n): ")
if confirm_delete.lower() != 'y':
    exit()

print("Удаление серверов...")

for identifier in identifiers:
    request_url = f'{base_url}/{identifier}/force'  # Исправлено на правильное формирование URL
    response = requests.delete(request_url, headers=headers)
    if response.status_code in [200, 204]:
        print(f"Сервер с идентификатором {identifier} удален.")
    else:
        print(f"Не удалось удалить сервер с идентификатором {identifier}: {response.status_code} {response.text}")

print("Операция удаления завершена.")
