from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime
import time
import random
import os

# کلیدواژه‌ها
keywords = [
    'خرید دلار','فروش دلار','دلار فردا','نرخ ارز','سکه طلا',
    'صرافی آنلاین','تورم','انتخابات','اعتراضات','تحریم',
    'برجام','انفجار','ترور','حمله','جنگ'
]

# تقسیم به گروه‌های ۵تایی
def chunk_keywords(lst, size=5):
    for i in range(0, len(lst), size):
        yield lst[i:i+size]

# ایجاد session پایدار
pytrends = TrendReq(hl='fa', tz=330)

# زمان و مسیر فایل
today_str = datetime.today().strftime('%Y-%m-%d')
output_folder = "data"
os.makedirs(output_folder, exist_ok=True)
output_path = os.path.join(output_folder, f"trends_{today_str}.csv")

# جمع‌آوری داده‌ها
all_data = []

for group in chunk_keywords(keywords, 5):
    print(f"دریافت داده برای: {group}")
    pytrends.build_payload(group, timeframe='now 4-H')  # فقط ۴ ساعت اخیر
    data = pytrends.interest_over_time()
    if not data.empty:
        data = data.drop(columns='isPartial')
        all_data.append(data)
    sleep_time = random.uniform(5, 10)
    time.sleep(sleep_time)  # جلوگیری از بلاک شدن

# ادغام داده‌ها و ذخیره
if all_data:
    result_df = pd.concat(all_data, axis=1)
    result_df.to_csv(output_path)
    print(f"✅ داده‌ها ذخیره شدند: {output_path}")
else:
    print("⚠️ داده‌ای یافت نشد.")

