import os

def credentials_reader():
    # Get the current script's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))


    containing_dir = os.path.abspath(os.path.join(current_dir))
    path = os.path.join(containing_dir, 'credentials.txt')

    # Default credentials
    credentials = {'user': 'root',
                   'password': 'root',
                   'host': 'localhost',
                   'port': 3306,
                   'database': 'forum_3'}

    # Credentials pull
    if os.path.exists(path):
        with open(path, 'r') as file:
            content = file.readlines()

            keys = list(credentials.keys())
            for n, line in enumerate(content):
                line = line.strip()
                if n < len(keys):
                    if keys[n] == 'port':
                        credentials[keys[n]] = int(line)
                    else:
                        credentials[keys[n]] = line
    else:
        print(f"Warning: File at {path} not found. Using default credentials.")

    return credentials


print(credentials_reader())

