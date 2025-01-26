import logging
import requests


class CloudStorage:
    """Класс для взаимодействия с облачным хранилищем."""

    def __init__(self, token, cloud_folder_path):
        self.token = token
        self.cloud_folder_path = cloud_folder_path

    def load(self, path):
        """Загружает файл в облачное хранилище."""
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
        """Перезаписывает файл в облачном хранилище."""
        self.load(path)

    def delete(self, filename):
        """Удаляет файл из облачного хранилища."""
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
        """Получает информацию о файлах в облачном хранилище."""
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
