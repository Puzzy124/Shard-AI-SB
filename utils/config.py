import os
from typing import Optional

from dotenv import load_dotenv


load_dotenv('./.env')

PROXY: Optional[str] = os.getenv('PROXY')
PROVIDER: Optional[str] = os.getenv('PROVIDER')
MODEL: Optional[str] = os.getenv('MODEL')
API_KEY: Optional[str] = str(os.getenv('API_KEY'))
WPM: Optional[int] = float(os.getenv('WPM'))
PROMPT: Optional[str] = str(os.getenv('PROMPT'))
TRIGGER: Optional[str] = str(os.getenv('TRIGGER'))

if API_KEY is None and PROVIDER:
    raise ValueError("API_KEY is empty, must be filled out to use a custom provider")

if MODEL and PROVIDER is None:
    raise ValueError("Must use a custom provider to use custom models!")