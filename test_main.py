import os
import tempfile
from typing import Dict
import pytest

from log_parser import process_file
from reports import HandlersReport

# Пример логов для тестов
LOG_SAMPLE = '''2021-09-01 12:00:00,000 DEBUG django.request: "GET /admin/dashboard/ HTTP/1.1" Дополнительная информация
2021-09-01 12:00:01,000 INFO django.request: "POST /api/v1/auth/login/ HTTP/1.1" Детали запроса
2021-09-01 12:00:02,000 WARNING django.request: "GET /api/v1/orders/ HTTP/1.1" Предупреждение
2021-09-01 12:00:03,000 ERROR django.request: "PUT /api/v1/products/ HTTP/1.1" Ошибка
2021-09-01 12:00:04,000 CRITICAL django.request: "DELETE /api/v1/shipping/ HTTP/1.1" Критическая ошибка
2021-09-01 12:00:05,000 DEBUG django.request: "GET /admin/dashboard/ HTTP/1.1" Ещё информация
'''

def create_temp_log_file(contents: str) -> str:
    fd, path = tempfile.mkstemp(text=True)
    with os.fdopen(fd, 'w', encoding="utf-8") as tmp:
        tmp.write(contents)
    return path

def test_process_file() -> None:
    file_path = create_temp_log_file(LOG_SAMPLE)
    try:
        result = process_file(file_path)
        # Проверяем, что ручки корректно извлеклись
        assert "/admin/dashboard/" in result
        assert result["/admin/dashboard/"]["DEBUG"] == 2
        assert "/api/v1/auth/login/" in result
        assert result["/api/v1/auth/login/"]["INFO"] == 1
        assert "/api/v1/orders/" in result
        assert result["/api/v1/orders/"]["WARNING"] == 1
        assert "/api/v1/products/" in result
        assert result["/api/v1/products/"]["ERROR"] == 1
        assert "/api/v1/shipping/" in result
        assert result["/api/v1/shipping/"]["CRITICAL"] == 1
    finally:
        os.remove(file_path)

def test_handlers_report() -> None:
    # Подготавливаем тестовые данные
    data: Dict[str, Dict[str, int]] = {
        "/admin/dashboard/": {"DEBUG": 20, "INFO": 72, "WARNING": 19, "ERROR": 14, "CRITICAL": 18},
        "/api/v1/auth/login/": {"DEBUG": 23, "INFO": 78, "WARNING": 14, "ERROR": 15, "CRITICAL": 18},
    }
    report = HandlersReport().generate(data)
    # Проверяем, что в заголовке отчёта указано общее количество запросов
    # (20+72+19+14+18) + (23+78+14+15+18) = 291

    assert "Total requests: 291" in report
    # Проверяем, что ручки выведены в алфавитном порядке
    index_admin = report.find("/admin/dashboard/")
    index_auth = report.find("/api/v1/auth/login/")
    assert index_admin < index_auth
