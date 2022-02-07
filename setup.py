import json
import os.path

CONFIG_FILE_PATH = 'config.json'


def safe_mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def create_checker_folders():
    print('Creating checker folders...')
    with open(CONFIG_FILE_PATH, 'r') as configFile:
        cfg = json.load(configFile)
        file_structure = cfg['FileStructure']

        checker_data = file_structure['CheckerData']
        checker_data_path = checker_data['value']
        safe_mkdir(checker_data_path)

        generated_paths_file = os.path.join(checker_data_path, checker_data['GeneratedPaths']['value'])

        with open(generated_paths_file, 'w') as out:
            data = dict()
            data['public_keys'] = os.path.join(checker_data_path, checker_data['GPGKeys']['value'])
            safe_mkdir(data['public_keys'])

            credentials_file_path = os.path.join(checker_data_path, checker_data['AdminCredentials']['value'])
            data['admin_credentials'] = credentials_file_path
            print(f'Please place credentials file to {credentials_file_path}')

            testing_area = file_structure['TestingArea']
            testing_area_path = testing_area['value']
            data['testing_area'] = testing_area_path
            safe_mkdir(data['testing_area'])

            submits_path = os.path.join(testing_area_path, testing_area['Submits']['value'])
            data['submits'] = submits_path
            safe_mkdir(submits_path)

            labs_path = os.path.join(testing_area_path, testing_area['Labs']['value'])
            data['labs'] = labs_path
            safe_mkdir(data['labs'])

            json.dump(data, out, indent='  ')


def main():
    create_checker_folders()


if __name__ == '__main__':
    main()
