from traceback import format_exc
from httpx import AsyncClient

from src.config import get_settings

# Sends an error message to the configured Discord Webhook URL
async def error_webhook(scraper: str, error: Exception, client: AsyncClient):
  await client.post(get_settings().discord_webhook_url, json={
    "username": "PriceComp Errors",
    "content": f"**{scraper}** scraper failed due to the following exception: "
      + f"```{format_exc()}```"
  })