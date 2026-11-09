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
        close_btn = page.locator("text=Close").first
        if await close_btn.is_visible(timeout=1000):
            print("Обнаружена реклама! Ждем 6.5 секунд...")
            await asyncio.sleep(6.5)
            await close_btn.click()
            print("Реклама закрыта.")
            await asyncio.sleep(1)
            return True
    except Exception:
        pass

    # Жесткий клик по координатам крестика, если он в iframe
    try:
        await page.mouse.click(1260, 40)
        await page.mouse.click(1260, 40)
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
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            await browser.close()
            return
        
        await asyncio.sleep(10)
        
        # УВЕЛИЧИВАЕМ ВРЕМЯ: от 15 минут (900 сек) до 20 минут (1200 сек)
        target_seconds = random.randint(900, 1200)
        print(f"Начинаем имитацию игры ({target_seconds} секунд)...")
        
        end_time = asyncio.get_event_loop().time() + target_seconds
        last_ad_check = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() < end_time:
            # Закрываем новые вкладки
            if len(context.pages) > 1:
                for extra_page in context.pages[1:]:
                    await extra_page.close()
                await page.bring_to_front()
            
            # Проверяем рекламу раз в 45 секунд
            current_time = asyncio.get_event_loop().time()
            if current_time - last_ad_check > 45:
                print("Проверка на наличие рекламы...")
                await handle_ads(page)
                last_ad_check = asyncio.get_event_loop().time()

            # Клики в безопасной зоне (безопасно для 15-20 минут)
            action = random.random()
            
            if action > 0.85:
                await page.mouse.click(1000, 150)
            else:
                x = random.randint(100, 1000)
                y = random.randint(150, 680)
                await page.mouse.move(x, y)
                await page.mouse.click(x, y)
            
            # Иногда нажимаем пробел
            if random.random() > 0.7:
                await page.keyboard.press("Space")
                
            await asyncio.sleep(random.uniform(1.5, 3.5))
            
        print("Сессия завершена.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(play_game())
