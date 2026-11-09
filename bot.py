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
    """Функция для поиска и закрытия рекламы"""
    try:
        # Ищем элемент, содержащий текст "Close" (он виден на твоем скрине)
        # Используем .first, так как Playwright может найти несколько совпадений
        close_btn = page.locator("text=Close").first
        
        # Если кнопка видима на экране
        if await close_btn.is_visible(timeout=1000):
            print("Обнаружена реклама! Ждем 6.5 секунд...")
            await asyncio.sleep(6.5)
            
            # Пробуем кликнуть по кнопке
            await close_btn.click()
            print("Реклама закрыта кликом по кнопке.")
            await asyncio.sleep(1)
            return True
    except Exception:
        pass

    # Если кнопку не нашли (или она в iframe), кликаем по жестким координатам правого верхнего угла
    # Координаты X: 1260, Y: 40 (судя по твоему скрину)
    try:
        # Проверяем, не перекрыт ли экран (например, если мы уже в игре)
        # Если мы сделаем клик в пустоту, ничего страшного не случится
        await page.mouse.click(1260, 40)
        await page.mouse.click(1260, 40) # Двойной клик на всякий случай
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
        
        # Ждем загрузки интерфейса
        await asyncio.sleep(10)
        
        # Рандомное время игры: от 6.5 минут (390 сек) до 8 минут (480 сек)
        target_seconds = random.randint(390, 480)
        print(f"Начинаем имитацию игры ({target_seconds} секунд)...")
        
        end_time = asyncio.get_event_loop().time() + target_seconds
        last_ad_check = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() < end_time:
            # 1. Закрываем новые вкладки, если они открылись
            if len(context.pages) > 1:
                for extra_page in context.pages[1:]:
                    await extra_page.close()
                await page.bring_to_front()
            
            # 2. Раз в 30 секунд проверяем наличие рекламы
            current_time = asyncio.get_event_loop().time()
            if current_time - last_ad_check > 30:
                print("Проверка на наличие рекламы...")
                await handle_ads(page)
                last_ad_check = asyncio.get_event_loop().time()

            # 3. Имитация игры (клики ТОЛЬКО в безопасной зоне)
            # Зона игры: X от 100 до 1000, Y от 150 до 680 (чтобы не нажать на меню и сайдбар)
            action = random.random()
            
            if action > 0.85:
                # Иногда кликаем в правый верхний угол (вдруг там крестик от мини-баннера)
                await page.mouse.click(1000, 150)
            else:
                x = random.randint(100, 1000)
                y = random.randint(150, 680)
                await page.mouse.move(x, y)
                await page.mouse.click(x, y)
            
            # 4. Имитация нажатия пробела
            if random.random() > 0.7:
                await page.keyboard.press("Space")
                
            await asyncio.sleep(random.uniform(1.5, 3.5))
            
        print("Сессия завершена.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(play_game())
