#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RU Proxy Finder - скрипт для поиска и проверки российских прокси для доступа к VATS.

Этот инструмент собирает прокси из множества источников, проверяет их работоспособность
и выявляет прокси, которые могут успешно открывать VATS с формой входа.

Автор: SergD
Лицензия: MIT
"""

import asyncio
import argparse
import os
import sys
from rich.console import Console
from rich.table import Table
from use_proxy_api import RussianProxyFinder

console = Console()


async def find_proxies(check_vats=True, max_concurrent=20, timeout=5):
    """Полный процесс поиска и проверки прокси."""
    finder = RussianProxyFinder()
    await finder.initialize()

    try:
        # Собираем прокси из разных источников
        await finder.get_proxies_from_api()
        # Проверяем принадлежность стран (замена устаревшего check_country)
        await finder.verify_russian_proxies()

        # Сохраняем найденные российские прокси
        await finder.save_proxies()

        # Если нужно проверить доступность VATS
        if check_vats:
            working_proxies = await finder.check_vats_access()
            if working_proxies:
                show_working_proxies(working_proxies)
                return working_proxies
            else:
                console.print("[bold red]Не найдено прокси, которые могут открыть VATS с формой входа!")

        return finder.russian_proxies
    finally:
        await finder.close()


def show_working_proxies(proxies):
    """Отображение списка рабочих прокси в виде таблицы."""
    if not proxies:
        console.print("[bold red]Нет рабочих прокси для отображения.")
        return

    table = Table(title="Рабочие прокси для доступа к VATS")
    table.add_column("№", style="cyan")
    table.add_column("Прокси", style="green")

    for idx, proxy in enumerate(proxies, 1):
        table.add_row(str(idx), proxy)

    console.print(table)
    console.print("\nИспользуйте эти прокси для доступа к VATS через браузер.")


async def main():
    """Главная функция программы с обработкой аргументов командной строки."""
    parser = argparse.ArgumentParser(description="Поиск и проверка российских прокси для доступа к VATS")
    parser.add_argument("-n", "--novats", action="store_true", help="Не проверять доступность VATS")
    parser.add_argument("-c", "--concurrent", type=int, default=20, help="Количество одновременных запросов")
    parser.add_argument("-t", "--timeout", type=int, default=5, help="Таймаут соединения в секундах")
    args = parser.parse_args()

    console.print("\n🔍 Поиск российских прокси для доступа к VATS...\n")

    try:
        await find_proxies(check_vats=not args.novats, max_concurrent=args.concurrent, timeout=args.timeout)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Работа программы прервана пользователем.")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]Ошибка при выполнении: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
