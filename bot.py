# bot.py
import asyncio
import random
import sys
from playwright.async_api import async_playwright

if len(sys.argv) < 2:
    print("Ошибка: укажи URL игры")
    sys.exit(1)

GAME_URL = sys.argv[1]

async def handle_ads(page):
    try:
        # Ищем кнопку Close (с учетом iframe)
        close_btn = page.locator("text=Close").first
        if await close_btn.is_visible(timeout=1000):
            print("Найдена кнопка Close. Ждем 6.5 сек...")
            await asyncio.sleep(6.5)
            await close_btn.click()
            return True
    except:
        pass

    # Если не нашли кнопку, кликаем по всем 4 углам (там часто прячут крестики)
    try:
        corners = [(1260, 40), (20, 40), (1260, 680), (20, 680)]
        for x, y in corners:
            await page.mouse.move(x, y, steps=5)
            await page.mouse.click(x, y)
            await asyncio.sleep(0.5)
    except:
        pass

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
            await asyncio.sleep(10)
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            await page.screenshot(path="error_load.png") # Скриншот при ошибке загрузки
            await browser.close()
            return
        
        target_seconds = random.randint(900, 1200)
        print(f"Начинаем имитацию игры ({target_seconds} секунд)...")
        
        end_time = asyncio.get_event_loop().time() + target_seconds
        last_ad_check = asyncio.get_event_loop().time()
        
        # Разнообразие клавиш для нажатия
        keys = ["Space", "ArrowUp", "ArrowRight", "ArrowDown", "Enter", "KeyW", "KeyA"]

        try:
            while asyncio.get_event_loop().time() < end_time:
                # Закрываем новые вкладки
                if len(context.pages) > 1:
                    for extra_page in context.pages[1:]:
                        await extra_page.close()
                    await page.bring_to_front()
                
                current_time = asyncio.get_event_loop().time()
                if current_time - last_ad_check > 45:
                    print("Проверка на наличие рекламы...")
                    await handle_ads(page)
                    last_ad_check = asyncio.get_event_loop().time()

                # Имитация поведения
                action = random.random()
                
                if action > 0.95:
                    # 5% шанс: Бот "залипает" на 5-12 секунд (смотрит в экран)
                    print("Бот отвлекся (залипание)...")
                    await asyncio.sleep(random.uniform(5.0, 12.0))
                    continue
                
                # Плавное движение мыши (steps=15 делает движение человеческим)
                x = random.randint(100, 1000)
                y = random.randint(150, 680)
                await page.mouse.move(x, y, steps=15)
                
                if action > 0.3:
                    await page.mouse.click(x, y)
                
                # Нажимаем случайную клавишу
                if random.random() > 0.6:
                    key = random.choice(keys)
                    await page.keyboard.press(key)
                    
                await asyncio.sleep(random.uniform(1.0, 3.0))
                
            print("Сессия завершена успешно.")
        except Exception as e:
            print(f"Критическая ошибка во время игры: {e}")
            # Делаем скриншот, чтобы понять, на чем застряли
            await page.screenshot(path="error_play.png")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(play_game())
