import asyncio
import random
import sys
from playwright.async_api import async_playwright

if len(sys.argv) < 2:
    sys.exit(1)

GAME_URL = sys.argv[1]

async def play_game():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--use-gl=swiftshader", "--enable-unsafe-swiftshader"]
        )
        context = await browser.new_context(viewport={"width": 1280, "height": 720})
        page = await context.new_page()
        
        # Ловим ошибки из консоли браузера (например, если игра упала)
        page.on("console", lambda msg: print(f"[BROWSER CONSOLE] {msg.type}: {msg.text}"))
        
        print(f"Открываем игру: {GAME_URL}")
        try:
            await page.goto(GAME_URL, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(10)
            
            # 📸 СКРИНШОТ 1: Сразу после загрузки
            await page.screenshot(path="screenshot_1_loaded.png")
            print("Скриншот 1 сделан.")

            await page.mouse.click(640, 360) 
            await page.keyboard.press("Space")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            await browser.close()
            return
        
        target_seconds = random.randint(900, 1200)
        end_time = asyncio.get_event_loop().time() + target_seconds
        last_ad_check = asyncio.get_event_loop().time()
        
        try:
            loop_count = 0
            while asyncio.get_event_loop().time() < end_time:
                loop_count += 1
                
                # 📸 СКРИНШОТ 2: Через минуту после начала "игры"
                if loop_count == 20:
                    await page.screenshot(path="screenshot_2_midgame.png")
                    print("Скриншот 2 сделан (середина сессии).")

                if len(context.pages) > 1:
                    for extra_page in context.pages[1:]:
                        await extra_page.close()
                    await page.bring_to_front()
                
                if asyncio.get_event_loop().time() - last_ad_check > 45:
                    try:
                        close_btn = page.locator("text=Close").first
                        if await close_btn.is_visible(timeout=1000):
                            await asyncio.sleep(6.5)
                            await close_btn.click()
                    except:
                        pass
                    last_ad_check = asyncio.get_event_loop().time()

                action = random.random()
                if action > 0.95:
                    await asyncio.sleep(random.uniform(5.0, 12.0))
                    continue
                
                x = random.randint(100, 1000)
                y = random.randint(150, 680)
                await page.mouse.move(x, y, steps=10)
                if action > 0.4:
                    await page.mouse.click(x, y)
                
                if random.random() > 0.5:
                    m_key = random.choice(["KeyW", "KeyA", "KeyS", "KeyD"])
                    await page.keyboard.down(m_key)
                    await asyncio.sleep(random.uniform(0.5, 1.5))
                    await page.keyboard.up(m_key)
                    
                await asyncio.sleep(random.uniform(1.0, 3.0))
                
            print("Сессия завершена успешно.")
        except Exception as e:
            print(f"Критическая ошибка: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(play_game())
