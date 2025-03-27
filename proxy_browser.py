#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Прокси-сервер для доступа к VATS через найденные прокси
"""

import asyncio
import json
import os
import random
import webbrowser
import requests
import aiohttp
import urllib3
from rich.console import Console
from rich.table import Table
import time

console = Console()

# Отключаем предупреждения о незащищенных HTTPS запросах
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Конфигурация
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PROXY_FILE = os.path.join(DATA_DIR, "async_ru_proxies.json")
VATS_URL = "https://vats290368.megapbx.ru/#/"

# Порт для локального прокси-сервера
LOCAL_PORT = 8080

class ProxyBrowser:
    def __init__(self):
        self.proxies = self.load_proxies()
        self.current_proxy = None
    
    def load_proxies(self):
        """Загрузка найденных прокси из файла"""
        if not os.path.exists(PROXY_FILE):
            console.print("[red]Ошибка: Файл с прокси не найден. Сначала запустите use_proxy_api.py для поиска прокси.")
            return []
        
        with open(PROXY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Фильтруем только прокси с доступом к VATS
            return [p for p in data.get("proxies", []) if p.get("vats_access")]

    def select_proxy(self, proxy_idx=None):
        """Выбор прокси по индексу или случайным образом"""
        if not self.proxies:
            console.print("[red]Нет доступных прокси!")
            return None
        
        if proxy_idx is not None and 0 <= proxy_idx < len(self.proxies):
            self.current_proxy = self.proxies[proxy_idx]
        else:
            self.current_proxy = random.choice(self.proxies)
        
        console.print(f"[green]Выбран прокси: {self.current_proxy['proxy']} ({self.current_proxy['protocol']})")
        return self.current_proxy
    
    def show_proxies(self):
        """Отображение списка доступных прокси"""
        if not self.proxies:
            console.print("[red]Нет доступных прокси!")
            return
        
        table = Table(title="Доступные прокси с доступом к VATS")
        table.add_column("№", justify="right")
        table.add_column("Прокси", justify="left")
        table.add_column("Протокол", justify="left")
        table.add_column("Задержка", justify="right")
        
        for i, proxy in enumerate(self.proxies):
            table.add_row(
                str(i+1),
                proxy["proxy"],
                proxy["protocol"],
                f"{proxy['latency']}с"
            )
        
        console.print(table)

    def open_in_browser(self, proxy_idx=None):
        """Открытие браузера с прокси"""
        if not self.select_proxy(proxy_idx):
            return

        # Настройка прокси
        proxy_info = self.current_proxy
        proxy_url = f"{proxy_info['protocol']}://{proxy_info['proxy']}"
        
        # Проверяем работоспособность прокси
        try:
            console.print(f"[yellow]Проверяем прокси {proxy_url}...")
            proxies = {
                "http": proxy_url,
                "https": proxy_url
            }
            response = requests.get("https://www.yandex.ru", proxies=proxies, timeout=5, verify=False)
            if response.status_code == 200:
                console.print(f"[green]Прокси {proxy_url} работает!")
            else:
                console.print(f"[red]Прокси {proxy_url} вернул код {response.status_code}")
                return
        except Exception as e:
            console.print(f"[red]Ошибка при проверке прокси: {str(e)}")
            return

        # Выводим инструкцию по настройке прокси в браузере
        console.print("\n[bold green]Для использования этого прокси в браузере:")
        console.print(f"1. Настройте свой браузер для использования прокси: [bold blue]{proxy_url}[/bold blue]")
        
        if proxy_info['protocol'] == 'http':
            console.print("2. Для Chrome: Настройки -> Дополнительные -> Система -> Открыть настройки прокси")
            console.print("   Для Firefox: Настройки -> Общие -> Параметры сети -> Настроить")
        else:  # SOCKS4/SOCKS5
            console.print("2. Для SOCKS-прокси может потребоваться расширение (например, FoxyProxy для Firefox)")
        
        # Открываем сайт VATS
        console.print(f"\n[yellow]Открываем сайт {VATS_URL} в браузере...")
        webbrowser.open(VATS_URL)
        
        # Выводим список доступных прокси
        console.print("\n[bold]Список всех доступных прокси с доступом к VATS:")
        for i, proxy in enumerate(self.proxies):
            console.print(f"{i+1}. {proxy['protocol']}://{proxy['proxy']} - Задержка: {proxy['latency']}с")

    def test_all_proxies_sequentially(self):
        """Последовательно проверить все прокси, пока не найдется рабочий"""
        if not self.proxies:
            console.print("[red]Нет доступных прокси!")
            return False
        
        console.print("[bold yellow]Последовательно проверяем все прокси, пока не найдем рабочий...")
        
        for idx, proxy in enumerate(self.proxies):
            proxy_url = f"{proxy['protocol']}://{proxy['proxy']}"
            console.print(f"[yellow]Проверка прокси #{idx+1}: {proxy_url}...")
            
            try:
                proxies = {
                    "http": proxy_url,
                    "https": proxy_url
                }
                response = requests.get("https://vats290368.megapbx.ru/#/", proxies=proxies, timeout=10, verify=False)
                if response.status_code in [200, 301, 302]:
                    console.print(f"[bold green]✅ Прокси {proxy_url} работает для доступа к VATS!")
                    self.current_proxy = proxy
                    return True
                else:
                    console.print(f"[red]❌ Прокси вернул код {response.status_code}")
            except Exception as e:
                console.print(f"[red]❌ Ошибка: {str(e)}")
            
            # Небольшая пауза между запросами
            time.sleep(1)
        
        console.print("[bold red]❌ Не найдено рабочих прокси для доступа к VATS!")
        return False

def main():
    proxy_browser = ProxyBrowser()
    if not proxy_browser.proxies:
        return
    
    proxy_browser.show_proxies()
    
    # Выбор действия
    console.print("\n[bold]Выберите действие:")
    console.print("1. Открыть VATS через случайный прокси")
    console.print("2. Выбрать конкретный прокси")
    console.print("3. Последовательно проверить все прокси до первого рабочего")
    
    choice = input("\nВаш выбор (1, 2 или 3): ")
    
    if choice == "1":
        proxy_browser.open_in_browser()
    elif choice == "2":
        proxy_idx = int(input(f"\nВведите номер прокси (1-{len(proxy_browser.proxies)}): ")) - 1
        proxy_browser.open_in_browser(proxy_idx)
    elif choice == "3":
        # Автоматически перебираем все прокси
        if proxy_browser.test_all_proxies_sequentially():
            # Если нашли рабочий прокси, открываем VATS
            proxy_browser.open_in_browser(None) # Используем текущий прокси
    else:
        console.print("[red]Неверный выбор!")

if __name__ == "__main__":
    main()
