import logging
from pathlib import Path
from project_summary.config import DirectoryConfig
from project_summary.core import create_project_summary

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Тестовая конфигурация
config = {
    'path': '.',
    'extensions': ['.py', '.md', '.toml', '.yaml', '.yml'],
    'exclude_dirs': ['__pycache__', '.git', 'venv', '.venv'],
    'exclude_files': [],
    'max_file_size': 1048576  # 1MB
}

# Создаем директорию для выходных файлов
output_dir = Path('test_output')
output_dir.mkdir(exist_ok=True)

# Создаем и запускаем
dir_config = DirectoryConfig(config)
create_project_summary(dir_config, output_dir)