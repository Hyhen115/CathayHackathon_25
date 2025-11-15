import pyautogui

class ScreenshotTaker:
    def __init__(self, save_path="screenshot.png"):
        """Initialize the ScreenshotTaker with a default save path."""
        self.save_path = save_path

    def take_screenshot(self):
        """Take a screenshot of the entire screen and save it to the specified path."""
        screenshot = pyautogui.screenshot()
        screenshot.save(self.save_path)
        print(f"Screenshot saved to {self.save_path}")