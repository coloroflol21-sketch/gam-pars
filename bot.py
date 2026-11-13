import asyncio
import random
import sys
from playwright.async_api import async_playwright

if len(sys.argv) < 2:
    print("Ошибка: укажи URL игры")
    sys.exit(1)

GAME_URL = sys.argv[1]

# 🎭 Списки для рандомизации отпечатков браузера
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
]

VIEWPORTS = [
    {"width": 1920, "height": 1080},
    {"width": 1536, "height": 864},
    {"width": 1440, "height": 900},
    {"width": 1366, "height": 768},
    {"width": 1280, "height": 720}
]

LOCALES = ["en-US", "en-GB", "ru-RU", "de-DE"]

async def handle_ads(page):
    try:
        close_btn = page.locator("text=Close").first
        if await close_btn.is_visible(timeout=1000):
            print("Обнаружена реклама! Ждем 6.5 секунд...")
            await asyncio.sleep(6.5)
            await close_btn.click()
            return True
    except:
        pass
    try:
        await page.mouse.click(1260, 40)
    except:
        pass

async def play_game():
    # 🛡️ РАНДОМНАЯ ЗАДЕРЖКА СТАРТА (чтобы параллельные боты не стартовали одновременно)
    start_delay = random.randint(0, 240)
    print(f"Ожидание перед стартом: {start_delay} секунд...")
    await asyncio.sleep(start_delay)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--no-sandbox", 
                "--disable-dev-shm-usage",
                "--use-gl=swiftshader",
                "--enable-unsafe-swiftshader"
            ]
        )
        
        # 🎲 ВЫБИРАЕМ СЛУЧАЙНЫЕ ПАРАМЕТРЫ
        selected_ua = random.choice(USER_AGENTS)
        selected_viewport = random.choice(VIEWPORTS)
        selected_locale = random.choice(LOCALES)
        
        print(f"Отпечаток: {selected_ua[:30]}... | Экран: {selected_viewport['width']}x{selected_viewport['height']} | Язык: {selected_locale}")

        context = await browser.new_context(
            user_agent=selected_ua,
            viewport=selected_viewport,
            locale=selected_locale
        )
        page = await context.new_page()
        
        # ВОЗВРАЩАЕМ ЛОГИ КОНСОЛИ (для отладки)
        page.on("console", lambda msg: print(f"[BROWSER CONSOLE] {msg.type}: {msg.text}"))
        
        print(f"Открываем игру: {GAME_URL}")
        try:
            await page.goto(GAME_URL, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(10)
            
            # 📸 СКРИНШОТ 1
            await page.screenshot(path="screenshot_1_loaded.png")
            print("Скриншот 1 сделан.")

            # Клик в центр на основе выбранного разрешения
            center_x = selected_viewport["width"] // 2
            center_y = selected_viewport["height"] // 2
            await page.mouse.click(center_x, center_y)
            await page.keyboard.press("Space")
            await asyncio.sleep(2)
            
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            await browser.close()
            return
        
        target_seconds = random.randint(900, 1200) # 15-20 минут
        print(f"Начинаем имитацию игры ({target_seconds} секунд)...")
        
        end_time = asyncio.get_event_loop().time() + target_seconds
        last_ad_check = asyncio.get_event_loop().time()
        keys = ["Space", "ArrowUp", "Enter"]
        move_keys = ["KeyW", "KeyA", "KeyS", "KeyD"]

        try:
            loop_count = 0
            while asyncio.get_event_loop().time() < end_time:
                loop_count += 1
                
                # 📸 СКРИНШОТ 2 (через минуту)
                if loop_count == 20:
                    await page.screenshot(path="screenshot_2_midgame.png")
                    print("Скриншот 2 сделан (середина сессии).")

                # Закрываем новые вкладки
                if len(context.pages) > 1:
                    for extra_page in context.pages[1:]:
                        await extra_page.close()
                    await page.bring_to_front()
                
                # Проверка рекламы
                if asyncio.get_event_loop().time() - last_ad_check > 45:
                    print("Проверка на наличие рекламы...")
                    await handle_ads(page)
                    last_ad_check = asyncio.get_event_loop().time()

                action = random.random()
                
                if action > 0.95:
                    print("Бот отвлекся (залипание)...")
                    await asyncio.sleep(random.uniform(5.0, 12.0))
                    continue
                
                # Безопасная зона кликов зависит от размера экрана
                x = random.randint(100, selected_viewport["width"] - 300)
                y = random.randint(150, selected_viewport["height"] - 100)
                
                await page.mouse.move(x, y, steps=15)
                
                # Обычный клик или УДЕРЖАНИЕ (для рыбалочной шкалы)
                if action >= 0.7:
                    # Имитация удержания кнопки мыши
                    await page.mouse.down() 
                    await asyncio.sleep(random.uniform(2.0, 5.0)) 
                    await page.mouse.up()
                    await asyncio.sleep(1)
                elif action > 0.4:
                    await page.mouse.click(x, y)
                
                # Нажатия клавиш
                if random.random() > 0.5:
                    m_key = random.choice(move_keys)
                    await page.keyboard.down(m_key)
                    await asyncio.sleep(random.uniform(0.5, 1.5))
                    await page.keyboard.up(m_key)
                elif random.random() > 0.7:
                    await page.keyboard.press(random.choice(keys))
                    
                await asyncio.sleep(random.uniform(1.0, 3.0))
                
            print("Сессия завершена успешно.")
        except Exception as e:
            print(f"Критическая ошибка: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(play_game())
