import os
import time
import logging
import configparser
from cloud_storage import CloudStorage


def setup_logging(log_file):
    """Настраивает логирование."""
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def read_config(config_file):
    """Читает параметры из конфигурационного файла."""
    config = configparser.ConfigParser()
    config.read(config_file)

    local_folder = config.get('Settings', 'local_folder')
    cloud_folder = config.get('Settings', 'cloud_folder')
    token = config.get('Settings', 'token')
    sync_interval = config.getint('Settings', 'sync_interval')
    log_file = config.get('Settings', 'log_file')

    return local_folder, cloud_folder, token, sync_interval, log_file


def sync_folder(local_folder, cloud_storage):
    """Синхронизирует локальную папку с облачным хранилищем."""
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
