from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime
import time
import random
import os

# نگاشت فارسی → پینگلیش برای نام ستون‌ها
keyword_map = {
    'خرید دلار': 'kharid_dollar',
    'فروش دلار': 'foroosh_dollar',
    'دلار فردا': 'dollar_farda',
    'نرخ ارز': 'nerkh_arz',
    'سکه طلا': 'sekke_tala',
    'صرافی آنلاین': 'sarafi_online',
    'تورم': 'tavvarom',
    'انتخابات': 'entekhabat',
    'اعتراضات': 'eeteraaz',
    'تحریم': 'tahrim',
    'برجام': 'barjam',
    'انفجار': 'enfejar',
    'ترور': 'teror',
    'حمله': 'hamle',
    'جنگ': 'jang'
}

# لیست کلیدواژه‌ها
keywords = list(keyword_map.keys())

# تقسیم کلیدواژه‌ها به گروه‌های ۵تایی
def chunk_keywords(lst, size=5):
    for i in range(0, len(lst), size):
        yield lst[i:i+size]

# ساخت session پایدار با Pytrends
pytrends = TrendReq(hl='fa', tz=330)

# تنظیم مسیر فایل خروجی در فولدر data
today_str = datetime.today().strftime('%Y-%m-%d')
output_folder = "data"
os.makedirs(output_folder, exist_ok=True)
output_path = os.path.join(output_folder, f"GT_{today_str}.csv")

# دریافت داده‌ها و ذخیره‌سازی موقت
all_data = []

for group in chunk_keywords(keywords, 5):
    print(f"📡 دریافت داده برای: {group}")
    try:
        pytrends.build_payload(group, timeframe='now 4-H')
        data = pytrends.interest_over_time()
        if not data.empty:
            data = data.drop(columns='isPartial', errors='ignore')
            # تغییر نام ستون‌ها به پینگلیش
            data.rename(columns=keyword_map, inplace=True)
            all_data.append(data)
    except Exception as e:
        print(f"❌ خطا هنگام دریافت داده برای {group}: {e}")
    time.sleep(random.uniform(5, 10))  # تاخیر برای جلوگیری از بلاک شدن

if all_data:
    # ادغام داده‌ها
    result_df = pd.concat(all_data, axis=1)
    # حذف ستون‌های تکراری
    result_df = result_df.loc[:, ~result_df.columns.duplicated()]

    # تبدیل به فرمت طولانی (long)
    result_long = result_df.reset_index().melt(id_vars=['date'], var_name='keyword', value_name='hits')

    # فرمت دلخواه برای ستون تاریخ (مناسب ویندوز)
    result_long['date'] = result_long['date'].dt.strftime('%#m/%#d/%Y')

    # ذخیره خروجی به صورت long format بدون ایندکس
    result_long.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"✅ ذخیره انجام شد: {output_path}")
else:
    print("⚠️ هیچ داده‌ای دریافت نشد.")
