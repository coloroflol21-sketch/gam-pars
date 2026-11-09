# bot.py
import asyncio
import random
import sys
from playwright.async_api import async_playwright

# URL твоей игры (лучше передавать через аргумент)
GAME_URL = "https://твой_url_игры"

async def play_game():
    async with async_playwright() as p:
        # Запускаем в видимом режиме (xvfb сделает так, чтобы это работало в GHA)
        browser = await p.chromium.launch(headless=False)
        
        # Создаем контекст с рандомным User-Agent
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        page = await context.new_page()
        
        print("Открываем игру...")
        await page.goto(GAME_URL, wait_until="networkidle")
        
        # Ждем загрузки игры
        await asyncio.sleep(5)
        
        # Имитация игры: двигаем мышь и кликаем каждые 2-4 секунды
        print("Начинаем имитацию игры...")
        # Играем 6.5 минут (390 секунд), чтобы точно перекрыть порог в 6:00
        end_time = asyncio.get_event_loop().time() + 390
        
        while asyncio.get_event_loop().time() < end_time:
            # Рандомное движение мыши
            x = random.randint(100, 1000)
            y = random.randint(100, 600)
            await page.mouse.move(x, y)
            
            # Случайный клик (иногда)
            if random.random() > 0.5:
                await page.mouse.click(x, y)
            
            # Пауза между действиями (от 1 до 4 секунд)
            await asyncio.sleep(random.uniform(1.0, 4.0))
            
        print("Сессия завершена. Закрываем браузер.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(play_game())
