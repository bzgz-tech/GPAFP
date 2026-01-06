import uuid
import time
from typing import Dict, Tuple
from captcha.image import ImageCaptcha
import random
import string

# In-memory storage for captcha codes: {uuid: (code, expire_time)}
# Note: In a production environment with multiple workers, use Redis instead.
CAPTCHA_STORE: Dict[str, Tuple[str, float]] = {}
CAPTCHA_EXPIRE_SECONDS = 300  # 5 minutes

class CaptchaService:
    def __init__(self):
        self.image_generator = ImageCaptcha(width=120, height=40)

    def generate_captcha(self) -> Tuple[str, bytes]:
        """
        Generate a new captcha.
        Returns:
            Tuple[str, bytes]: (captcha_id, image_bytes)
        """
        # Clean up expired captchas occasionally (simple lazy cleanup)
        self._cleanup()

        # Generate code
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        
        # Generate image
        image_data = self.image_generator.generate(code)
        image_bytes = image_data.read()

        # Store in memory
        captcha_id = str(uuid.uuid4())
        expire_time = time.time() + CAPTCHA_EXPIRE_SECONDS
        CAPTCHA_STORE[captcha_id] = (code.lower(), expire_time)

        return captcha_id, image_bytes

    def verify_captcha(self, captcha_id: str, captcha_code: str) -> bool:
        """
        Verify the captcha code.
        """
        if not captcha_id or not captcha_code:
            return False
            
        stored = CAPTCHA_STORE.get(captcha_id)
        if not stored:
            return False
            
        stored_code, expire_time = stored
        
        # Check expiration
        if time.time() > expire_time:
            del CAPTCHA_STORE[captcha_id]
            return False
            
        # Check match (case-insensitive)
        if stored_code == captcha_code.lower():
            # Invalidate after successful use (single use)
            del CAPTCHA_STORE[captcha_id]
            return True
            
        return False

    def _cleanup(self):
        """Remove expired items"""
        now = time.time()
        # Create list of keys to remove to avoid runtime error during iteration
        to_remove = [k for k, v in CAPTCHA_STORE.items() if v[1] < now]
        for k in to_remove:
            del CAPTCHA_STORE[k]

captcha_service = CaptchaService()
