def credentials_reader():
    with open('credentials.txt', 'r') as file:
        content = file.readlines()
        credentials = {'user': None, 'password': None, 'host': None, 'port': None, 'database': None}
        keys = list(credentials.keys())
        for n in range(len(content)):
            line = content[n]
            if line.endswith('\n'):
                if keys[n] == 'port':
                    credentials[keys[n]] = int(line[0:-1])
                else:
                    credentials[keys[n]] = line[0:-1]
            else:
                credentials[keys[n]] = line
        return credentials

credentials = credentials_reader()
