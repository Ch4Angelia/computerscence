import pandas as pd
import json
import os
# 移除 deep_translator 避免呼叫問題
# from deep_translator import GoogleTranslator 
# 移除 requests 避免不必要的依賴
# import requests 
# import io 

# =================================================================
# ⚠️ 1. 設定檔案名稱與關鍵欄位名稱 (請確保欄位名稱與您的 CSV 檔案一致)
# =================================================================
# 您的 CSV 檔案名稱 (必須與您上傳到GitHub的名稱一模一樣)
csv_file_name = '食品營養成分資料庫2024UPDATE2.xlsx - 工作表1.csv'

# 您的 CSV 中，中文食物名稱的欄位名稱
FOOD_NAME_COLUMN = '樣品名稱' 

# 您的 CSV 中，熱量的欄位名稱
CALORIE_COLUMN = '熱量(kcal)'

# 您的 CSV 中，英文品名的欄位名稱 (請在 CSV 中建立此欄位)
ENGLISH_NAME_COLUMN = 'English Name' 
# =================================================================


# 存檔路徑設定
target_folder = 'Sedentary_Lifestyle_Management'
filename = os.path.join(target_folder, 'food_database.json')
backup_filename = os.path.join(target_folder, 'food_database.backup.json')

# 確保資料夾存在
if not os.path.exists(target_folder):
    os.makedirs(target_folder, exist_ok=True)
    
print(f"正在讀取預先翻譯好的本地數據: {csv_file_name}...")

try:
    # 1. 讀取本機 CSV 檔案 (跳過第一行非標題行)
    # 這裡的 skiprows=1 是根據您提供的 CSV 內容調整的
    df = pd.read_csv(csv_file_name, encoding='utf-8-sig', skiprows=1)
    
    new_database_list = []
    
    # 2. 遍歷 CSV 數據，生成新的 JSON 列表
    for index, row in df.iterrows():
        # === 讀取中英雙欄位 ===
        zh_name = str(row.get(FOOD_NAME_COLUMN, '')).strip()
        # 讀取新增的英文欄位
        en_name = str(row.get(ENGLISH_NAME_COLUMN, '')).strip()
        new_cal = str(row.get(CALORIE_COLUMN, '0')).strip()
        # =======================

        if pd.isna(zh_name) or zh_name == '': continue
        if new_cal == 'nan': new_cal = '0'
        
        new_database_list.append({
            "zh": zh_name,
            # 直接使用 CSV 中的英文名稱
            "en": en_name, 
            "cal": new_cal
        })

    # 3. 存檔與備份機制 (保持不變)
    if os.path.exists(filename):
        if not os.path.exists(target_folder):
             os.makedirs(target_folder, exist_ok=True)
             
        if os.path.exists(filename):
            if os.path.exists(backup_filename):
                os.remove(backup_filename)
            os.rename(filename, backup_filename)
            print(f"已備份舊資料為 {backup_filename}")

    # 寫入最新的資料
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(new_database_list, f, ensure_ascii=False, indent=4)

    print(f"處理完成！資料已寫入: {filename}")
    print(f"總共處理了 {len(new_database_list)} 筆中英對照食物數據。")

except Exception as e:
    print(f"發生錯誤: {e}")
    # 為了方便日後除錯，保留錯誤提示
    # if 'English Name' or '樣品名稱' is missing, the code will likely fail here