import logging
import time
import httpx
import asyncio

import requests

from ..settings import get_setting as _

DEVICE_LOCATION_ID = _("DEVICE/LOCATION_ID")
DEVICE_APPLIANCE_ID = _("DEVICE/APPLIANCE_ID")
DEVICE_ROOM_ID = _("DEVICE/ROOM_ID")

APPLIANCE_COMMAND_URL = f'https://idp2-apigw.cloud.grohe.com/v3/iot' \
                        f'/locations/{DEVICE_LOCATION_ID}' \
                        f'/rooms/{DEVICE_ROOM_ID}' \
                        f'/appliances/{DEVICE_APPLIANCE_ID}' \
                        f'/command'


def get_auth_header(access_token: str) -> str:
    """
    Returns the authorization header for the given access token.
    Args:
        access_token: The access token to use.

    Returns: The authorization header.

    """
    return f'Bearer {access_token}'


async def execute_tap_command(tap_type: int, amount: int, access_token, tries=0) -> bool:
    """
    Executes the command for the given tap type and amount.

    Args:
        tap_type: The type of tap. 1 for still, 2 for medium, 3 for sparkling.
        amount: The amount of water to be dispensed in ml.
        tries: The number of tries to execute the command.

    Returns: True if the command was executed successfully, False otherwise.
    """
    check_tap_params(tap_type, amount)

    async def send_command():
        headers = {
            "Content-Type": "application/json",
            "Authorization": get_auth_header(access_token),
        }
        data = {
            "type": None,
            "appliance_id": DEVICE_APPLIANCE_ID,
            "command": get_command(tap_type, amount),
            "commandb64": None,
            "timestamp": None,
        }

        async with httpx.AsyncClient() as client:
            for attempt in range(3):
                try:
                    response = await client.post(APPLIANCE_COMMAND_URL, headers=headers, json=data)
                    response.raise_for_status()

                    if ((response.status_code-200) >= 0 and (response.status_code-200) < 100):
                        return True

                    logging.error(f'Failed to execute tap command. Response: {response.text}')

                    # Check for a server error and retry
                    if response.status_code >= 500 and attempt < 2:
                        logging.info("Server error, retrying after 5 seconds...")
                        await asyncio.sleep(5)
                    elif response.status_code == 401:
                        logging.info('Refreshing tokens and trying again.')
                        refresh_tokens()

                except httpx.RequestError as e:
                    logging.error(f"Request failed: {e}")

                await asyncio.sleep(5)  # Delay before retrying

        return False

    return await send_command()


def check_tap_params(tap_type: int, amount: int) -> None:
    """
    Checks the given tap parameters.
    Args:
        tap_type: The type of tap. 1 for still, 2 for medium, 3 for sparkling.
        amount: The amount of water to be dispensed in ml.

    Raises: ValueError if the parameters are invalid.

    """
    # check if the tap type is valid
    if tap_type not in [1, 2, 3]:
        raise ValueError(f'Invalid tap type: {tap_type}. Valid values are 1, 2 and 3.')
    # check if the amount is valid
    if amount % 50 != 0 or amount <= 0 or amount > 2000:
        raise ValueError('The amount must be a multiple of 50, greater than 0 and less or equal to 2000.')


def get_command(tap_type: int, amount: int) -> dict:
    """
    Returns the command to execute for the given tap type and amount.
    Args:
        tap_type: The type of tap. 1 for still, 2 for medium, 3 for sparkling.
        amount: The amount of water to be dispensed in ml.

    Returns: The command to execute.

    """
    return {
        "co2_status_reset"         : False,
        "tap_type"                 : tap_type,
        "cleaning_mode"            : False,
        "filter_status_reset"      : False,
        "get_current_measurement"  : False,
        "tap_amount"               : amount,
        "factory_reset"            : False,
        "revoke_flush_confirmation": False,
        "exec_auto_flush"          : False
    }


async def get_dashboard_data(access_token) -> dict:
    """
    Retrieves information about the appliance from the Grohe API.

    Returns:
        A dictionary containing the appliance information if successful,
        or an empty dictionary if the request fails.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": get_auth_header(access_token),  # Ensure these functions are defined elsewhere
    }

    appliance_info_url = 'https://idp2-apigw.cloud.grohe.com/v3/iot/dashboard'

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(appliance_info_url, headers=headers)
            response.raise_for_status()
            logging.info("Appliance information retrieved successfully.")
            return response.json()

    except httpx.HTTPStatusError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
    except httpx.RequestError as err:
        logging.error(f"Request error occurred: {err}")

    return {}