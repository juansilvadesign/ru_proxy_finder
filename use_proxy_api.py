import aiohttp
import asyncio
import json
import os
from datetime import datetime
import re
import sys
from rich.console import Console
from rich.table import Table
from bs4 import BeautifulSoup
import random
import requests

console = Console()

# Конфигурация
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

class RussianProxyFinder:
    def __init__(self):
        self.proxies = []
        self.session = None
        self.russian_proxies = []
    
    async def initialize(self):
        self.session = aiohttp.ClientSession()
    
    async def close(self):
        if self.session:
            await self.session.close()
    
    async def get_proxies_from_api(self):
        # Собираем прокси из разных API источников
        tasks = [
            self.get_proxies_from_proxylist_download(),
            self.get_proxies_from_freeproxy_world(),
            self.get_proxies_from_proxy_list_ru(),
            self.get_proxies_from_hidemy_name(),
            self.get_proxies_from_geonode(),
            self.get_proxies_from_free_proxy_list(),
            self.get_proxies_from_proxy_list_download(),
            self.get_proxies_from_proxy_list_org(),
            # Специализированные российские источники
            self.get_proxies_from_proxyscrape_ru(),
            self.get_proxies_from_proxyservers_ru(),
            self.get_proxies_from_2ip_ru(),
            self.get_proxies_from_proxy24_net_ru(),
            # Новые источники прокси
            self.get_proxies_from_htmlweb_api(),
            self.get_proxies_from_proxy5_net(),
            self.get_proxies_from_fineproxy_org(),
            self.get_proxies_from_proxyfreeonly(),
            self.get_proxies_from_good_proxies_ru(),
            self.get_proxies_from_iproyal_ru(),
        ]
        
        await asyncio.gather(*tasks)
        console.print(f"[bold green]Найдено {len(self.proxies)} прокси из API источников")

    async def get_proxies_from_proxylist_download(self):
        try:
            url = "https://www.proxy-list.download/api/v1/get?type=http"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    text = await response.text()
                    proxy_list = text.strip().split('\r\n')
                    self.proxies.extend(proxy_list)
                    console.print(f"Получено {len(proxy_list)} прокси от proxy-list.download")
        except Exception as e:
            console.print(f"[red]Ошибка при получении прокси от proxy-list.download: {e}")
    
    async def get_proxies_from_freeproxy_world(self):
        try:
            url = "https://www.freeproxy.world/"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    text = await response.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    rows = soup.select('.table-striped tbody tr')
                    proxy_list = []
                    for row in rows:
                        columns = row.select('td')
                        if len(columns) >= 2:
                            ip = columns[0].text.strip()
                            port = columns[1].text.strip()
                            country = columns[6].text.strip() if len(columns) > 6 else ""
                            if country and "Russia" in country or "RU" in country:
                                proxy_list.append(f"{ip}:{port}")
                    self.proxies.extend(proxy_list)
                    console.print(f"Получено {len(proxy_list)} прокси от freeproxy.world")
        except Exception as e:
            console.print(f"[red]Ошибка при получении прокси от freeproxy.world: {e}")

    async def get_proxies_from_proxy_list_ru(self):
        try:
            url = "https://proxy-list.ru/russian-proxy-list"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    text = await response.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    rows = soup.select('.proxy-list-table tr')
                    proxy_list = []
                    for row in rows[1:]:  # Пропускаем заголовок
                        columns = row.select('td')
                        if len(columns) >= 2:
                            ip = columns[0].text.strip()
                            port = columns[1].text.strip()
                            proxy_list.append(f"{ip}:{port}")
                    self.proxies.extend(proxy_list)
                    console.print(f"Получено {len(proxy_list)} прокси от proxy-list.ru")
        except Exception as e:
            console.print(f"[red]Ошибка при получении прокси от proxy-list.ru: {e}")
    
    async def get_proxies_from_hidemy_name(self):
        try:
            url = "https://hidemy.name/ru/proxy-list/?country=RU"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
            async with self.session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    text = await response.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    rows = soup.select('.table_block tbody tr')
                    proxy_list = []
                    for row in rows:
                        columns = row.select('td')
                        if len(columns) >= 2:
                            ip = columns[0].text.strip()
                            port = columns[1].text.strip()
                            proxy_list.append(f"{ip}:{port}")
                    self.proxies.extend(proxy_list)
                    console.print(f"Получено {len(proxy_list)} прокси от hidemy.name")
        except Exception as e:
            console.print(f"[red]Ошибка при получении прокси от hidemy.name: {e}")
    
    async def get_proxies_from_geonode(self):
        try:
            url = "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&country=RU&speed=fast&protocols=http,https,socks4,socks5"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    proxy_list = []
                    for proxy in data.get('data', []):
                        ip = proxy.get('ip')
                        port = proxy.get('port')
                        if ip and port:
                            proxy_list.append(f"{ip}:{port}")
                    self.proxies.extend(proxy_list)
                    self.russian_proxies.extend(proxy_list)
                    console.print(f"Получено {len(proxy_list)} российских прокси от geonode.com")
        except Exception as e:
            console.print(f"[red]Ошибка при получении прокси от geonode.com: {e}")
    
    async def get_proxies_from_free_proxy_list(self):
        try:
            url = "https://free-proxy-list.net/"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    text = await response.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    rows = soup.select('#list tbody tr')
                    proxy_list = []
                    for row in rows:
                        columns = row.select('td')
                        if len(columns) >= 8:
                            ip = columns[0].text.strip()
                            port = columns[1].text.strip()
                            country_code = columns[2].text.strip()
                            if country_code == "RU":
                                proxy_list.append(f"{ip}:{port}")
                    self.proxies.extend(proxy_list)
                    self.russian_proxies.extend(proxy_list)
                    console.print(f"Получено {len(proxy_list)} российских прокси от free-proxy-list.net")
        except Exception as e:
            console.print(f"[red]Ошибка при получении прокси от free-proxy-list.net: {e}")

    async def get_proxies_from_proxy_list_download(self):
        try:
            url = "https://www.proxy-list.download/api/v2/get?l=en&t=http&c=Russian+Federation"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    text = await response.text()
                    try:
                        data = json.loads(text)
                        proxy_list = []
                        for proxy in data.get('LISTA', []):
                            ip = proxy.get('IP')
                            port = proxy.get('PORT')
                            if ip and port:
                                proxy_list.append(f"{ip}:{port}")
                        self.proxies.extend(proxy_list)
                        self.russian_proxies.extend(proxy_list)
                        console.print(f"Получено {len(proxy_list)} российских прокси от proxy-list.download v2")
                    except json.JSONDecodeError:
                        pass
        except Exception as e:
            console.print(f"[red]Ошибка при получении прокси от proxy-list.download v2: {e}")
    
    async def get_proxies_from_proxy_list_org(self):
        try:
            url = "https://proxy-list.org/russian/index.php"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    text = await response.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    proxy_blocks = soup.select('.table ul li')
                    proxy_list = []
                    for block in proxy_blocks:
                        proxy_text = block.text.strip()
                        match = re.search(r'(\d+\.\d+\.\d+\.\d+):(\d+)', proxy_text)
                        if match:
                            ip, port = match.groups()
                            proxy_list.append(f"{ip}:{port}")
                    self.proxies.extend(proxy_list)
                    console.print(f"Получено {len(proxy_list)} прокси от proxy-list.org")
        except Exception as e:
            console.print(f"[red]Ошибка при получении прокси от proxy-list.org: {e}")

    # Новые специализированные источники российских прокси
    async def get_proxies_from_proxyscrape_ru(self):
        try:
            url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=RU&ssl=all&anonymity=all"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    text = await response.text()
                    proxy_list = text.strip().split('\n')
                    self.proxies.extend(proxy_list)
                    self.russian_proxies.extend(proxy_list)
                    console.print(f"Получено {len(proxy_list)} прокси от proxyscrape.com (RU)")
        except Exception as e:
            console.print(f"[red]Ошибка при получении прокси от proxyscrape.com: {e}")

    async def get_proxies_from_proxyservers_ru(self):
        try:
            url = "https://ru.proxyservers.pro/proxy/list?country=RU&type=http"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
            }
            async with self.session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    text = await response.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    rows = soup.select('table.proxy-list tbody tr')
                    proxy_list = []
                    for row in rows:
                        columns = row.select('td')
                        if len(columns) >= 2:
                            ip = columns[1].text.strip()
                            port = columns[2].text.strip()
                            proxy_list.append(f"{ip}:{port}")
                    self.proxies.extend(proxy_list)
                    console.print(f"Получено {len(proxy_list)} прокси от proxyservers.pro (RU)")
        except Exception as e:
            console.print(f"[red]Ошибка при получении прокси от proxyservers.pro: {e}")

    async def get_proxies_from_2ip_ru(self):
        try:
            url = "https://2ip.ru/proxy/?filter_country=RU&filter_port=&filter_type=any&filter_anon=any"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
            }
            async with self.session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    text = await response.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    proxy_table = soup.select_one('.proxy__table')
                    if proxy_table:
                        rows = proxy_table.select('tbody tr')
                        proxy_list = []
                        for row in rows:
                            columns = row.select('td')
                            if len(columns) >= 2:
                                ip = columns[0].text.strip()
                                port = columns[1].text.strip()
                                proxy_list.append(f"{ip}:{port}")
                        self.proxies.extend(proxy_list)
                        console.print(f"Получено {len(proxy_list)} прокси от 2ip.ru (RU)")
        except Exception as e:
            console.print(f"[red]Ошибка при получении прокси от 2ip.ru: {e}")

    async def get_proxies_from_proxy24_net_ru(self):
        try:
            url = "https://proxy24.net/ru-proxy"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
            }
            async with self.session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    text = await response.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    rows = soup.select('table.table-striped tbody tr')
                    proxy_list = []
                    for row in rows:
                        columns = row.select('td')
                        if len(columns) >= 2:
                            ip = columns[0].text.strip()
                            port = columns[1].text.strip()
                            country = columns[3].text.strip() if len(columns) > 3 else ""
                            if "RU" in country:
                                proxy_list.append(f"{ip}:{port}")
                    self.proxies.extend(proxy_list)
                    console.print(f"Получено {len(proxy_list)} прокси от proxy24.net (RU)")
        except Exception as e:
            console.print(f"[red]Ошибка при получении прокси от proxy24.net: {e}")

    async def verify_russian_proxies(self):
        """Проверка, что прокси действительно из России"""
        proxies_to_check = set(self.proxies) - set(self.russian_proxies)
        console.print(f"[yellow]Проверка еще {len(proxies_to_check)} прокси на принадлежность к России...")
        
        tasks = []
        for proxy in proxies_to_check:  # Проверяем только те прокси, которые еще не были добавлены в russian_proxies
            tasks.append(self.check_proxy_country(proxy))
        
        if tasks:  # Проверяем только если есть прокси для проверки
            await asyncio.gather(*tasks)
            
        console.print(f"[bold green]Найдено {len(self.russian_proxies)} российских прокси")

    async def check_proxy_country(self, proxy):
        """Проверка страны прокси через ipinfo.io и другие сервисы"""
        ip = proxy.split(':')[0]
        try:
            # Проверяем страну через ipinfo.io (без токена - лимит 1000 запросов/день)
            url = f"https://ipinfo.io/{ip}/json"
            async with self.session.get(url, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    country = data.get('country')
                    if country == "RU":
                        self.russian_proxies.append(proxy)
                        console.print(f"[green]Прокси {proxy} подтверждён как российский")
        except Exception:
            # Запасной вариант - проверка через ip-api.com
            try:
                url = f"http://ip-api.com/json/{ip}"
                async with self.session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        country_code = data.get('countryCode')
                        if country_code == "RU":
                            self.russian_proxies.append(proxy)
                            console.print(f"[green]Прокси {proxy} подтверждён как российский (резервный метод)")
            except Exception as e:
                pass  # Игнорируем ошибки

    async def save_proxies(self):
        """
        Сохраняем найденные российские прокси в файл
        """
        output_file = os.path.join(DATA_DIR, "russian_proxies.txt")
        with open(output_file, "w") as f:
            for proxy in self.russian_proxies:
                f.write(f"{proxy}\n")
        console.print(f"[bold]Сохранено {len(self.russian_proxies)} российских прокси в {output_file}")

    async def check_vats_access(self):
        """Проверка доступа к VATS через найденные российские прокси"""
        console.print("[bold]Проверка доступа к VATS через российские прокси...")
        
        working_proxies = []
        vats_url = "http://vats290368.megapbx.ru/"
        
        # Будем использовать семафор для ограничения количества одновременных запросов
        max_concurrent = 20  # Максимальное количество одновременных запросов
        semaphore = asyncio.Semaphore(max_concurrent)
        
        # Характерные признаки формы входа
        login_indicators = [
            'input[name="login"]', 'input[name="username"]', 
            'input[type="password"]', 'form', '<form',
            'Логин', 'Пароль', 'Вход', 'Авторизация',
            'Личный кабинет', 'Виртуальной АТС'
        ]
        
        async def check_single_proxy(proxy):
            """Асинхронная проверка одного прокси"""
            try:
                async with semaphore:
                    # Используем aiohttp вместо requests для асинхронных запросов
                    proxy_url = f"http://{proxy}"
                    timeout = aiohttp.ClientTimeout(total=5)  # Снижаем таймаут для ускорения проверки
                    
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        try:
                            async with session.get(vats_url, proxy=proxy_url, ssl=False) as response:
                                if response.status == 200:
                                    text = await response.text()
                                    html_content = text.lower()
                                    
                                    # Проверяем наличие диагностических данных (информация о запросе), значит это не настоящий интерфейс
                                    if "remote_addr" in html_content or "request_method" in html_content:
                                        console.print(f"[yellow]⚠️ Прокси {proxy} возвращает только диагностические данные")
                                        return None
                                    
                                    # Проверяем наличие признаков формы входа
                                    for indicator in login_indicators:
                                        if indicator.lower() in html_content:
                                            console.print(f"[bold green]✅ Прокси {proxy} успешно открывает форму входа VATS!")
                                            return proxy
                                    
                                    console.print(f"[yellow]⚠️ Прокси {proxy} открывает страницу, но форма входа не найдена")
                                else:
                                    console.print(f"[red]❌ Прокси {proxy} вернул код {response.status}")
                        except aiohttp.ClientError as e:
                            console.print(f"[red]❌ Ошибка при проверке {proxy}: {str(e)[:50]}...")
            except Exception as e:
                console.print(f"[red]❌ Ошибка при проверке {proxy}: {str(e)[:50]}...")
            return None
        
        # Запускаем проверку всех прокси
        console.print(f"[blue]Параллельная проверка {len(self.russian_proxies)} прокси (максимально {max_concurrent} одновременно)...")
        tasks = [check_single_proxy(proxy) for proxy in self.russian_proxies]
        results = await asyncio.gather(*tasks)
        
        # Фильтруем результаты, удаляя None значения (неработающие прокси)
        working_proxies = [proxy for proxy in results if proxy is not None]
        
        # Сохраняем рабочие прокси в отдельный файл
        if working_proxies:
            output_file = os.path.join(DATA_DIR, "vats_working_proxies.txt")
            with open(output_file, "w") as f:
                for proxy in working_proxies:
                    f.write(f"{proxy}\n")
            console.print(f"[bold green]Сохранено {len(working_proxies)} рабочих прокси для VATS в {output_file}")
        else:
            console.print("[bold red]Не найдено ни одного прокси, который может открыть VATS с формой входа")

        return working_proxies

    # Новые методы для получения прокси
    async def get_proxies_from_htmlweb_api(self):
        try:
            url = "https://htmlweb.ru/analiz/api_proxy.php?country=ru&format=json"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    proxy_list = []
                    if isinstance(data, dict) and 'list' in data:
                        for proxy_data in data['list']:
                            ip = proxy_data.get('ip')
                            port = proxy_data.get('port')
                            if ip and port:
                                proxy_list.append(f"{ip}:{port}")
                    self.proxies.extend(proxy_list)
                    console.print(f"Получено {len(proxy_list)} прокси от htmlweb.ru API")
        except Exception as e:
            console.print(f"[red]Ошибка при получении прокси от htmlweb.ru API: {e}")

    async def get_proxies_from_proxy5_net(self):
        try:
            url = "https://proxy5.net/ru/free-proxy/russia"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
            }
            async with self.session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    text = await response.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    proxy_list = []
                    
                    # Поиск таблицы с прокси
                    proxy_table = soup.select_one('table.proxy-table')
                    if proxy_table:
                        rows = proxy_table.select('tbody tr')
                        for row in rows:
                            columns = row.select('td')
                            if len(columns) >= 2:
                                ip = columns[0].text.strip()
                                port = columns[1].text.strip()
                                proxy_list.append(f"{ip}:{port}")
                    self.proxies.extend(proxy_list)
                    console.print(f"Получено {len(proxy_list)} прокси от proxy5.net")
        except Exception as e:
            console.print(f"[red]Ошибка при получении прокси от proxy5.net: {e}")

    async def get_proxies_from_fineproxy_org(self):
        try:
            url = "https://fineproxy.org/ru/free-proxies/europe/russia/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
            }
            async with self.session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    text = await response.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    proxy_list = []
                    
                    # Поиск таблицы с прокси
                    proxy_table = soup.select_one('table.proxy__list')
                    if proxy_table:
                        rows = proxy_table.select('tbody tr')
                        for row in rows:
                            columns = row.select('td')
                            if len(columns) >= 2:
                                ip = columns[0].text.strip()
                                port = columns[1].text.strip()
                                proxy_list.append(f"{ip}:{port}")
                    self.proxies.extend(proxy_list)
                    console.print(f"Получено {len(proxy_list)} прокси от fineproxy.org")
        except Exception as e:
            console.print(f"[red]Ошибка при получении прокси от fineproxy.org: {e}")

    async def get_proxies_from_proxyfreeonly(self):
        try:
            url = "https://proxyfreeonly.com/ru/free-proxy-list/russia"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
            }
            async with self.session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    text = await response.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    proxy_list = []
                    
                    # Поиск таблицы с прокси
                    proxy_table = soup.select_one('table.proxy-table')
                    if proxy_table:
                        rows = proxy_table.select('tbody tr')
                        for row in rows:
                            columns = row.select('td')
                            if len(columns) >= 2:
                                ip = columns[0].text.strip()
                                port = columns[1].text.strip()
                                proxy_list.append(f"{ip}:{port}")
                    self.proxies.extend(proxy_list)
                    console.print(f"Получено {len(proxy_list)} прокси от proxyfreeonly.com")
        except Exception as e:
            console.print(f"[red]Ошибка при получении прокси от proxyfreeonly.com: {e}")

    async def get_proxies_from_good_proxies_ru(self):
        try:
            url = "https://www.good-proxies.ru/free-proxy"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
            }
            async with self.session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    text = await response.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    proxy_list = []
                    
                    # Поиск таблицы с прокси
                    proxy_table = soup.select('table.proxy-list')
                    for table in proxy_table:
                        rows = table.select('tbody tr')
                        for row in rows:
                            columns = row.select('td')
                            if len(columns) >= 2:
                                ip = columns[0].text.strip()
                                port = columns[1].text.strip()
                                country = columns[2].text.strip() if len(columns) > 2 else ""
                                if "RU" in country or "Россия" in country:
                                    proxy_list.append(f"{ip}:{port}")
                    self.proxies.extend(proxy_list)
                    console.print(f"Получено {len(proxy_list)} прокси от good-proxies.ru")
        except Exception as e:
            console.print(f"[red]Ошибка при получении прокси от good-proxies.ru: {e}")

    async def get_proxies_from_iproyal_ru(self):
        try:
            url = "https://iproyal.com/ru/free-proxies/russia-ru/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
            }
            async with self.session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    text = await response.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    proxy_list = []
                    
                    # Поиск таблицы с прокси
                    proxy_table = soup.select_one('table.proxies-table')
                    if proxy_table:
                        rows = proxy_table.select('tbody tr')
                        for row in rows:
                            columns = row.select('td')
                            if len(columns) >= 2:
                                ip = columns[0].text.strip()
                                port = columns[1].text.strip()
                                proxy_list.append(f"{ip}:{port}")
                    self.proxies.extend(proxy_list)
                    console.print(f"Получено {len(proxy_list)} прокси от iproyal.com")
        except Exception as e:
            console.print(f"[red]Ошибка при получении прокси от iproyal.com: {e}")

async def main():
    finder = RussianProxyFinder()
    try:
        await finder.initialize()
        console.print("[bold]Поиск российских прокси...")
        await finder.get_proxies_from_api()
        await finder.verify_russian_proxies()
        await finder.save_proxies()
        
        if finder.russian_proxies:
            working_proxies = await finder.check_vats_access()
            if working_proxies:
                console.print("\n[bold]Рабочие прокси для доступа к VATS:")
                table = Table(show_header=True, header_style="bold")
                table.add_column("№", style="dim")
                table.add_column("Прокси")
                
                for i, proxy in enumerate(working_proxies, 1):
                    table.add_row(str(i), proxy)
                
                console.print(table)
                console.print("\n[bold]Используйте эти прокси для доступа к VATS через браузер.")
            else:
                console.print("\n[bold yellow]Российские прокси найдены, но ни один не может открыть VATS с полным интерфейсом")
        else:
            console.print("[bold red]Не найдено ни одного российского прокси")
            
    except Exception as e:
        console.print(f"[bold red]Ошибка: {e}")
    finally:
        await finder.close()

# Запуск программы
if __name__ == "__main__":
    print("\n🔍 Поиск российских прокси для доступа к VATS...\n")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())