import argparse
import os
import sys
from typing import Dict, List
import concurrent.futures

from log_parser import process_file
from reports import HandlersReport


def aggregate_results(results: List[Dict[str, Dict[str, int]]]) -> Dict[str, Dict[str, int]]:
    """
    Объединяет результаты обработки нескольких файлов.
    Каждый результат – это словарь: {handler: {level: count, ...}}.
    """
    aggregated: Dict[str, Dict[str, int]] = {}
    for file_result in results:
        for handler, counts in file_result.items():
            if handler not in aggregated:
                aggregated[handler] = counts.copy()
            else:
                for level, count in counts.items():
                    aggregated[handler][level] = aggregated[handler].get(level, 0) + count
    return aggregated


def main() -> None:
    parser = argparse.ArgumentParser(description="Анализатор логов Django и формирователь отчётов")
    parser.add_argument("files", nargs="+", help="Пути к файлам логов")
    parser.add_argument("--report", required=True, choices=["handlers"], help="Название отчёта для формирования")
    args = parser.parse_args()

    # Проверка существования файлов
    for file_path in args.files:
        if not os.path.isfile(file_path):
            print(f"Ошибка: Файл не найден: {file_path}", file=sys.stderr)
            sys.exit(1)

    # Обработка файлов в параллельном режиме
    results: List[Dict[str, Dict[str, int]]] = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        future_to_file = {executor.submit(process_file, file_path): file_path for file_path in args.files}
        for future in concurrent.futures.as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                print(f'При обработке файла {file_path} возникло исключение: {exc}', file=sys.stderr)
    print(results)
    aggregated_data = aggregate_results(results)

    # Генерация отчёта, в данный момент доступен только "handlers"
    if args.report == "handlers":
        report = HandlersReport().generate(aggregated_data)
        print(report)


if __name__ == "__main__":
    main()
