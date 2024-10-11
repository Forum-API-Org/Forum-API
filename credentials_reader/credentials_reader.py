# def credentials_reader():
#     path = r'C:\Users\alexa\Desktop\credentials.txt'  # <- Тук вкарайте пътя към вашия credentials.txt!!!
#     credentials = {'user': None, 'password': None, 'host': None, 'port': None, 'database': None}
#     keys = list(credentials.keys())
#
#     with open(path, 'r') as file:
#         content = file.readlines()
#
#         for n, line in enumerate(content):
#             line = line.strip()
#             if n < len(keys):
#                 if keys[n] == 'port':
#                     credentials[keys[n]] = int(line)
#                 else:
#                     credentials[keys[n]] = line
#
#     return credentials
#
#
# print(credentials_reader())

import os

def credentials_reader():
    # Get the current script's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Go two directories up from 'forum-api' to find 'credentials.txt'
    grandparent_dir = os.path.abspath(os.path.join(current_dir))  # Go up two levels
    path = os.path.join(grandparent_dir, 'credentials.txt')

    # Default credentials
    credentials = {'user': 'root',
                   'password': 'root',
                   'host': 'localhost',
                   'port': 3306,
                   'database': 'forum_3'}


    # Check if the file exists two directories up
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

