import re
from typing import Dict

# Поддерживаемые уровни логирования
LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# Новое регулярное выражение для поиска URL-ручки в записях django.request.
# Оно учитывает, что после "django.request:" может идти HTTP-метод или сразу текст "Internal Server Error:".

LOG_PATTERN = re.compile(
    r'\b(' + '|'.join(LOG_LEVELS) + r')\b.*\s(/[^ ]*)'
)

def process_file(file_path: str) -> Dict[str, Dict[str, int]]:
    """
    Обрабатывает файл логов и возвращает словарь, где ключ — URL обработчика (handler),
    а значение — словарь с количеством записей по уровням логирования.
    """
    result: Dict[str, Dict[str, int]] = {}
    with open(file_path, 'r', encoding="utf-8") as f:
        for line in f:
            # Обрабатываем только записи, относящиеся к django.request
            if "django.request" not in line:
                continue

            # Определяем уровень логирования из строки (ищем первое вхождение из списка)
            level_found = None
            for lvl in LOG_LEVELS:
                if lvl in line:
                    level_found = lvl
                    break
            if level_found is None:
                continue

            # Поиск handler'а с помощью регулярного выражения
            match = LOG_PATTERN.search(line)
            if not match:
                continue

            # Группа 2 всегда содержит URL
            handler = match.group(2)
            if handler not in result:
                # Инициализируем словарь для всех уровней, чтобы потом можно было суммировать
                result[handler] = {lvl: 0 for lvl in LOG_LEVELS}
            result[handler][level_found] += 1
    return result
