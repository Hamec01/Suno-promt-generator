# Suno Prompt Generator

Локальное desktop-приложение на Python + PySide6 для генерации музыкальных промтов под Suno AI.

## Возможности

- Выбор параметров музыки через категории и чекбоксы
- Автоматическая сборка полного промта на английском
- Короткая версия промта до 120 символов
- Подсчёт символов
- Копирование полного и короткого промта в буфер
- Случайная генерация набора тегов
- Очистка выбора
- Загрузка и сохранение пресетов в JSON
- Импорт JSON с объединением без затирания старых данных
- Экспорт токенов, пресетов, промтов и всей базы
- Добавление новых слов в любую категорию (включая новые категории)
- Сохранение и управление пользовательскими промтами
- Автосоздание JSON-файлов по умолчанию, если они отсутствуют

## Требования

- Python 3.11+
- PySide6

## Установка

```bash
pip install PySide6
```

## Запуск

```bash
python main.py
```

Запускать из папки проекта:

```bash
cd suno_prompt_generator
python main.py
```

## Структура

- main.py
- data/prompt_data.json
- data/presets.json
- data/user_prompts.json
- data/prompt_data_fantasy_ambient.json
- exports/
- app/main_window.py
- app/prompt_builder.py
- app/storage.py
- app/import_export.py
- app/styles.py
