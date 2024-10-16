import logging
from datetime import datetime, timedelta
import asyncio
from .tokens import get_refresh_tokens, get_tokens_from_credentials

class GroheClient:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.access_token = None
        self.refresh_token = None
        self.access_token_expiring_date = None

    async def _initialize_tokens(self):
        """
        Get the initial access and refresh tokens.
        """
        try:
            tokens = await get_tokens_from_credentials(self.email, self.password)
            self.access_token = tokens['access_token']
            self.access_token_expiring_date = datetime.now() + timedelta(seconds=tokens['access_token_expires_in'] - 60)
            self.refresh_token = tokens['refresh_token']
        except Exception as e:
            logging.error(f"Could not get initial tokens: {e}")
            exit(1)

    async def refresh_tokens(self):
        """
        Refresh the access and refresh tokens.
        """
        logging.info("Refreshing tokens")
        tokens = await get_refresh_tokens(self.refresh_token)
        self.access_token = tokens['access_token']
        self.refresh_token = tokens['refresh_token']
        self.access_token_expiring_date = datetime.now() + timedelta(seconds=tokens['access_token_expires_in'] - 60)

    async def get_access_token(self) -> str:
        """
        Get the access token. Refresh the tokens if they are expired.
        Returns: The access token.
        """
        # Refresh the tokens if they are expired
        if datetime.now() > self.access_token_expiring_date:
            await self.refresh_tokens()
        return self.access_token
