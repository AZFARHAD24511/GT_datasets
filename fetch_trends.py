from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime
import time
import random
import os

# نگاشت فارسی به پینگلیش
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

# بازه زمانی
start_date = "2025-07-31"
end_date = datetime.now().strftime("%Y-%m-%d")

# تقسیم کلیدواژه‌ها به گروه‌های 5تایی
def chunk_keywords(lst, size=5):
    for i in range(0, len(lst), size):
        yield lst[i:i+size]

# ساخت مسیر پوشه خروجی
output_folder = "data"
os.makedirs(output_folder, exist_ok=True)
output_path = os.path.join(output_folder, "google_trends_long_daily.csv")

# اتصال به گوگل ترندز
pytrends = TrendReq(hl='fa', tz=270)  # تهران +4:30

all_data = []

for chunk in chunk_keywords(keywords, size=5):
    try:
        pytrends.build_payload(chunk, timeframe=f'{start_date} {end_date}', geo='')
        data = pytrends.interest_over_time()
        if data.empty:
            continue

        # حذف ستون isPartial
        data = data.drop(columns='isPartial', errors='ignore')

        # تبدیل به فرمت طولانی (long)
        df_long = data.reset_index().melt(id_vars='date', var_name='keyword_fa', value_name='hits')

        # افزودن نام پینگلیش
        df_long['keyword'] = df_long['keyword_fa'].map(keyword_map)

        # انتخاب ستون‌های نهایی
        df_long = df_long[['date', 'keyword', 'hits']]

        all_data.append(df_long)
        
        # توقف تصادفی بین درخواست‌ها برای جلوگیری از بلاک شدن
        time.sleep(random.uniform(2, 5))

    except Exception as e:
        print(f"❌ خطا هنگام دریافت داده برای {chunk}: {e}")

if all_data:
    final_df = pd.concat(all_data, ignore_index=True)
    final_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"✅ دریافت داده‌ها تمام شد و فایل ذخیره شد: {output_path}")
else:
    print("⚠️ هیچ داده‌ای دریافت نشد.")
