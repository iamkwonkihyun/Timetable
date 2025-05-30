from dotenv import load_dotenv
from timetable.functions import get_api_func, today_variable
import os

load_dotenv()

key = os.getenv("NEIS_API_KEY")


ymd, _, _, _, = today_variable()

get_api_func(key, ymd)