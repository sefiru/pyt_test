from typing import Dict, List

LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

class Report:
    def generate(self, data: Dict[str, Dict[str, int]]) -> str:
        raise NotImplementedError

class HandlersReport(Report):
    def generate(self, data: Dict[str, Dict[str, int]]) -> str:
        """
        Формирует отчёт о запросах к ручкам API.
        Ручки сортируются в алфавитном порядке.
        Последняя строка содержит общее количество запросов по каждому уровню.
        """
        # Подсчет итогов по всем уровням
        total = {lvl: 0 for lvl in LOG_LEVELS}
        lines: List[str] = []
        # Сортировка по названиям ручек
        for handler in sorted(data.keys()):
            counts = data[handler]
            # Форматируем строку отчёта: имя ручки + количество по каждому уровню
            line = f"{handler:<22}"
            for lvl in LOG_LEVELS:
                count = counts.get(lvl, 0)
                line += f"\t{count:<7}"
                total[lvl] += count
            lines.append(line)
        # Строка с итоговыми данными
        total_line = " " * 22
        for lvl in LOG_LEVELS:
            total_line += f"\t{total[lvl]:<7}"
        # Общее количество запросов
        total_requests = sum(total.values())
        header = f"Total requests: {total_requests}\n\n"
        header += f"{'HANDLER':<22}" + "".join([f"\t{lvl:<7}" for lvl in LOG_LEVELS])
        report_str = header + "\n" + "\n".join(lines) + "\n" + total_line
        return report_str
