import random
import string
import secrets
from utils.logger import logger


def random_string(length=8):
    logger.info(f"random_string: length = {length}")
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def hex_token(number_of_bytes=8):
    '''
    If number_of_bytes = 6, it will output 12 characters
    Hexadecimal encoding represents 1 byte using 2 characters
    example output: a3f9c21d8b44
    '''
    logger.info(f"token: number_of_bytes = {number_of_bytes}")
    return secrets.token_hex(number_of_bytes)
