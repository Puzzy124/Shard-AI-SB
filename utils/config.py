import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv('./.env')

def none_if_none(value):
    return value if value != "None" else None

PROXY: Optional[str] = none_if_none(os.getenv('PROXY'))
PROVIDER: Optional[str] = none_if_none(os.getenv('PROVIDER'))
MODEL: Optional[str] = none_if_none(os.getenv('MODEL'))
API_KEY: Optional[str] = none_if_none(os.getenv('API_KEY'))
WPM: Optional[int] = float(none_if_none(os.getenv('WPM')))
PROMPT: Optional[str] = none_if_none(os.getenv('PROMPT'))
TRIGGER: Optional[str] = none_if_none(os.getenv('TRIGGER'))

if API_KEY is None and PROVIDER:
    raise ValueError("API_KEY is empty, must be filled out to use a custom provider")

if MODEL and PROVIDER is None:
    raise ValueError("Must use a custom provider to use custom models!")