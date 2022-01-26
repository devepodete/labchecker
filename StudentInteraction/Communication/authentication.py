def get_credentials(filename) -> (str, str):
    with open(filename, 'r') as f:
        login, password = f.readline().replace('\n', '').split(' ')

    return login, password
