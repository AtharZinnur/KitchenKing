#!/usr/bin/env python3
"""Test the Pic2Kitchen upload form using Playwright"""

import asyncio
from playwright.async_api import async_playwright
import os

async def test_upload_form():
    async with async_playwright() as p:
        # Launch browser in headed mode to see what's happening
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print("1. Navigating to homepage...")
        await page.goto("http://127.0.0.1:8000")
        
        # Take screenshot of initial page
        await page.screenshot(path="screenshots/01_homepage.png")
        print("   ✓ Screenshot saved: 01_homepage.png")
        
        # Wait for page to load and find the upload form
        print("\n2. Looking for file upload form...")
        
        # The form is on the second section, need to scroll to it
        await page.evaluate("document.querySelector('.cachu__sections').scrollTo(0, window.innerHeight)")
        await page.wait_for_timeout(1000)  # Wait for scroll animation
        
        await page.screenshot(path="screenshots/02_form_section.png")
        print("   ✓ Screenshot saved: 02_form_section.png")
        
        # Find the file input
        file_input = page.locator('input[type="file"]')
        
        # Check if file input exists
        if await file_input.count() > 0:
            print("   ✓ Found file input")
            
            # Create a test image if it doesn't exist
            test_image_path = "/home/athar/Pic2kitchen-master/test_image.jpg"
            if not os.path.exists(test_image_path):
                print("\n3. Creating test image...")
                # Use an existing image from the project
                import shutil
                existing_image = "/home/athar/Pic2kitchen-master/app/static/images/w1-1.png"
                if os.path.exists(existing_image):
                    shutil.copy(existing_image, test_image_path)
                    print("   ✓ Test image created")
            
            # Upload the file
            print("\n4. Uploading test image...")
            await file_input.set_input_files(test_image_path)
            await page.wait_for_timeout(1000)  # Wait for preview to load
            
            await page.screenshot(path="screenshots/03_file_selected.png")
            print("   ✓ Screenshot saved: 03_file_selected.png")
            
            # Check if preview is displayed
            preview_div = page.locator('#imagePreview')
            is_preview_visible = await preview_div.is_visible()
            print(f"   ✓ Image preview visible: {is_preview_visible}")
            
            # Find the submit button
            print("\n5. Looking for submit button...")
            submit_button = page.locator('button[type="submit"]:has-text("Submit form")')
            
            if await submit_button.count() > 0:
                print("   ✓ Found submit button")
                
                # Check if button is visible and enabled
                is_visible = await submit_button.is_visible()
                is_enabled = await submit_button.is_enabled()
                print(f"   - Button visible: {is_visible}")
                print(f"   - Button enabled: {is_enabled}")
                
                # Get button location and size
                box = await submit_button.bounding_box()
                if box:
                    print(f"   - Button location: x={box['x']}, y={box['y']}")
                    print(f"   - Button size: {box['width']}x{box['height']}")
                
                # Highlight the button
                await page.evaluate("""
                    const button = document.querySelector('button[type="submit"]');
                    if (button) {
                        button.style.border = '3px solid red';
                        button.style.boxShadow = '0 0 10px red';
                    }
                """)
                
                await page.screenshot(path="screenshots/04_submit_button_highlighted.png")
                print("   ✓ Screenshot saved: 04_submit_button_highlighted.png")
                
                # Try clicking the button
                print("\n6. Attempting to submit form...")
                await submit_button.click()
                
                # Wait for navigation or response
                await page.wait_for_timeout(3000)
                
                await page.screenshot(path="screenshots/05_after_submit.png")
                print("   ✓ Screenshot saved: 05_after_submit.png")
                
                # Check current URL
                current_url = page.url
                print(f"   - Current URL: {current_url}")
                
            else:
                print("   ✗ Submit button not found!")
                
                # Try to find any submit buttons
                all_buttons = await page.locator('button').all()
                print(f"\n   Found {len(all_buttons)} buttons on page:")
                for i, btn in enumerate(all_buttons):
                    text = await btn.text_content()
                    print(f"   - Button {i+1}: '{text}'")
        
        else:
            print("   ✗ File input not found!")
        
        # Keep browser open for inspection
        print("\n\nTest completed. Browser will stay open for 10 seconds...")
        await page.wait_for_timeout(10000)
        
        await browser.close()

# Create screenshots directory
os.makedirs("screenshots", exist_ok=True)

# Run the test
asyncio.run(test_upload_form())