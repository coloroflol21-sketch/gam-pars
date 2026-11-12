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
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--no-sandbox", 
                "--disable-dev-shm-usage",
                "--use-gl=swiftshader", # Софтверный WebGL
                "--enable-unsafe-swiftshader"
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        page = await context.new_page()
        
        print(f"Открываем игру: {GAME_URL}")
        try:
            await page.goto(GAME_URL, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(10)
            
            # Принудительный клик и нажатие для фокуса
            await page.mouse.click(640, 360) 
            await page.keyboard.press("Space")
            await asyncio.sleep(2)
            
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            await browser.close()
            return
        
        target_seconds = random.randint(900, 1200)
        print(f"Начинаем имитацию игры ({target_seconds} секунд)...")
        
        end_time = asyncio.get_event_loop().time() + target_seconds
        last_ad_check = asyncio.get_event_loop().time()
        keys = ["Space", "ArrowUp", "Enter"]
        move_keys = ["KeyW", "KeyA", "KeyS", "KeyD"]

        try:
            while asyncio.get_event_loop().time() < end_time:
                if len(context.pages) > 1:
                    for extra_page in context.pages[1:]:
                        await extra_page.close()
                    await page.bring_to_front()
                
                if asyncio.get_event_loop().time() - last_ad_check > 45:
                    print("Проверка на наличие рекламы...")
                    await handle_ads(page)
                    last_ad_check = asyncio.get_event_loop().time()

                action = random.random()
                
                if action > 0.95:
                    await asyncio.sleep(random.uniform(5.0, 12.0))
                    continue
                
                # Клик и движение мыши
                x = random.randint(100, 1000)
                y = random.randint(150, 680)
                await page.mouse.move(x, y, steps=15)
                if action > 0.4:
                    await page.mouse.click(x, y)
                
                # Имитация зажатия клавиш движения (Anti-Idle)
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
