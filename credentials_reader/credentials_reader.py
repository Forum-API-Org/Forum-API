def credentials_reader():
    path = r'C:\Users\alexa\Desktop\credentials.txt'  # <- Тук вкарайте пътя към вашия credentials.txt!!!
    credentials = {'user': None, 'password': None, 'host': None, 'port': None, 'database': None}
    keys = list(credentials.keys())

    with open(path, 'r') as file:
        content = file.readlines()

        for n, line in enumerate(content):
            line = line.strip()
            if n < len(keys):
                if keys[n] == 'port':
                    credentials[keys[n]] = int(line)
                else:
                    credentials[keys[n]] = line

    return credentials


print(credentials_reader())

