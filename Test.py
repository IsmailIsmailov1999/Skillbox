import os
import logging
import configparser
import time
import requests
from datetime import datetime


class CloudStorage:
    def __init__(self, token, cloud_folder_path):
        self.token = token
        self.cloud_folder_path = cloud_folder_path

    def load(self, path):
        """Загружает файл в облачное хранилище"""
        try:
            with open(path, 'rb') as file:
                response = requests.post(
                    f'https://cloudstorage.example.com/upload/{self.cloud_folder_path}',
                    files={'file': file},
                    headers={'Authorization': f'Bearer {self.token}'}
                )
            if response.status_code == 200:
                logging.info(f'Файл {path} успешно загружен в облачное хранилище.')
            else:
                logging.error(f'Ошибка загрузки файла {path}: {response.text}')
        except Exception as e:
            logging.error(f'Ошибка при загрузке файла {path}: {str(e)}')

    def reload(self, path):
        """Перезаписывает файл в облачном хранилище"""
        self.load(path)

    def delete(self, filename):
        """Удаляет файл из облачного хранилища"""
        try:
            response = requests.delete(
                f'https://cloudstorage.example.com/delete/{self.cloud_folder_path}/{filename}',
                headers={'Authorization': f'Bearer {self.token}'}
            )
            if response.status_code == 200:
                logging.info(f'Файл {filename} удалён из облачного хранилища.')
            else:
                logging.error(f'Ошибка при удалении файла {filename}: {response.text}')
        except Exception as e:
            logging.error(f'Ошибка при удалении файла {filename}: {str(e)}')

    def get_info(self):
        """Получает информацию о файлах в облачном хранилище"""
        try:
            response = requests.get(
                f'https://cloudstorage.example.com/list/{self.cloud_folder_path}',
                headers={'Authorization': f'Bearer {self.token}'}
            )
            if response.status_code == 200:
                return response.json()  # Возвращает список файлов
            else:
                logging.error(f'Ошибка получения информации: {response.text}')
        except Exception as e:
            logging.error(f'Ошибка при получении информации о файлах: {str(e)}')


def sync_folder(local_folder, cloud_storage):
    """Синхронизирует локальную папку с облачным хранилищем"""
    try:
        cloud_files = cloud_storage.get_info()

        # Обрабатываем локальные файлы
        for filename in os.listdir(local_folder):
            local_file = os.path.join(local_folder, filename)

            if os.path.isfile(local_file):
                # Проверка на наличие файла в облаке
                cloud_file = next((f for f in cloud_files if f['name'] == filename), None)
                if cloud_file is None:
                    cloud_storage.load(local_file)
                else:
                    # Проверка на изменение файла
                    if os.path.getmtime(local_file) > cloud_file['last_modified']:
                        cloud_storage.reload(local_file)

        # Удаление файлов, которых нет в локальной папке
        for cloud_file in cloud_files:
            if cloud_file['name'] not in os.listdir(local_folder):
                cloud_storage.delete(cloud_file['name'])

    except Exception as e:
        logging.error(f'Ошибка при синхронизации папки {local_folder}: {str(e)}')


def read_config(config_file):
    """Читает параметры из конфигурационного файла"""
    config = configparser.ConfigParser()
    config.read(config_file)

    local_folder = config.get('Settings', 'local_folder')
    cloud_folder = config.get('Settings', 'cloud_folder')
    token = config.get('Settings', 'token')
    sync_interval = config.getint('Settings', 'sync_interval')
    log_file = config.get('Settings', 'log_file')

    return local_folder, cloud_folder, token, sync_interval, log_file


def setup_logging(log_file):
    """Настроить логирование"""
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def main():
    config_file = 'config.ini'

    # Чтение конфигурации
    local_folder, cloud_folder, token, sync_interval, log_file = read_config(config_file)

    # Настройка логирования
    setup_logging(log_file)

    # Логирование начала работы
    logging.info(f'Запуск синхронизации для папки: {local_folder}')

    # Создание экземпляра облачного хранилища
    cloud_storage = CloudStorage(token, cloud_folder)

    # Первичная синхронизация
    sync_folder(local_folder, cloud_storage)

    while True:
        time.sleep(sync_interval)
        sync_folder(local_folder, cloud_storage)


if __name__ == '__main__':
    main()
