# bot.py
import asyncio
import random
import sys
from playwright.async_api import async_playwright

# Проверяем, передан ли URL в аргументах
if len(sys.argv) < 2:
    print("Ошибка: укажи URL игры (например, python bot.py https://... )")
    sys.exit(1)

GAME_URL = sys.argv[1]

async def play_game():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        page = await context.new_page()
        
        print(f"Открываем игру: {GAME_URL}")
        try:
            await page.goto(GAME_URL, wait_until="networkidle", timeout=60000)
        except Exception as e:
            print(f"Ошибка загрузки страницы: {e}")
            await browser.close()
            return
        
        # Ждем инициализации игры
        await asyncio.sleep(10)
        
        print("Начинаем имитацию игры (7 минут)...")
        # Играем 7 минут (420 секунд)
        end_time = asyncio.get_event_loop().time() + 420
        
        while asyncio.get_event_loop().time() < end_time:
            x = random.randint(50, 1200)
            y = random.randint(50, 700)
            await page.mouse.move(x, y)
            
            if random.random() > 0.3:
                await page.mouse.click(x, y)
            
            # Имитация нажатия пробела (часто используется в играх)
            if random.random() > 0.8:
                await page.keyboard.press("Space")
                
            await asyncio.sleep(random.uniform(1.5, 3.5))
            
        print("Сессия завершена.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(play_game())
