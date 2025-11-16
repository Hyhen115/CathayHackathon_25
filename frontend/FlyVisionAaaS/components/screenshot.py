import pyscreenshot as ImageGrab
from datetime import datetime
import uuid
import os

class ScreenCapturer:
    def __init__(self, save_dir="screenshots"):
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)

    def screenshot_full(self, filename=None):
        """Take a full-screen screenshot."""
        if filename is None:
            filename = self._generate_filename()

        path = os.path.join(self.save_dir, filename)
        img = ImageGrab.grab()  # full screen
        img.save(path)
        return path

    def screenshot_object(self, bbox, filename=None):
        """
        Take a screenshot of the object.
        bbox = (x1, y1, x2, y2)
        """
        if filename is None:
            filename = self._generate_filename()

        path = os.path.join(self.save_dir, filename)
        img = ImageGrab.grab(bbox=bbox)
        img.save(path)
        return path

    def _generate_filename(self):
        unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.png"
        return unique_filename
