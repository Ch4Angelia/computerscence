import pandas as pd
from deep_translator import GoogleTranslator
import json
import time
import requests
import io
import os

# =================================================================
# ⚠️ 1. 設定檔案名稱與關鍵欄位名稱 (已使用您提供的名稱)
# =================================================================
# 您的 CSV 檔案名稱 (必須與您上傳到GitHub的名稱一模一樣)
csv_file_name = '食品營養成分資料庫2024UPDATE2.xlsx - 工作表1.csv'

# 您的 CSV 中，食物名稱的欄位名稱
FOOD_NAME_COLUMN = '樣品名稱' 

# 您的 CSV 中，熱量的欄位名稱
CALORIE_COLUMN = '熱量(kcal)'
# =================================================================


# 存檔路徑設定
target_folder = 'Sedentary_Lifestyle_Management'
filename = os.path.join(target_folder, 'food_database.json')
backup_filename = os.path.join(target_folder, 'food_database.backup.json')

# 確保資料夾存在
if not os.path.exists(target_folder):
    os.makedirs(target_folder, exist_ok=True)
    
print(f"正在讀取本機數據: {csv_file_name}...")

try:
    # 1. 讀取本機 CSV 檔案 (從 GitHub Actions 的環境中讀取)
    # 這裡假設 CSV 在根目錄
    # 嘗試解決編碼問題 (utf-8-sig 通常適用於 Excel 導出的 CSV)
    df = pd.read_csv(csv_file_name, encoding='utf-8-sig')
    
    # 2. 讀取「舊的」JSON 資料 (如果存在)
    old_data_map = {} 
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            old_list = json.load(f)
            for item in old_list:
                old_data_map[item['zh']] = item
    
    print(f"舊資料庫共有 {len(old_data_map)} 筆資料")

    def get_english_name(text):
        try:
            if not text or str(text).isascii(): return text
            # 由於這是大量數據，使用 GoogleTranslator 會有頻率限制，但測試時可用
            return GoogleTranslator(source='zh-TW', target='en').translate(text) 
        except:
            return text

    new_database_list = []
    updated_count = 0
    new_count = 0
    skipped_count = 0

    # 3. 比對邏輯
    for index, row in df.iterrows():
        # === 使用新的欄位名稱 ===
        zh_name = row.get(FOOD_NAME_COLUMN, '').strip()
        if pd.isna(zh_name) or zh_name == '': continue
        
        # 確保數值是字串或數字，處理 NaN
        new_cal = str(row.get(CALORIE_COLUMN, '0')).strip()
        # =======================

        if new_cal == 'nan': new_cal = '0'

        # 檢查是否已存在
        if zh_name in old_data_map:
            old_entry = old_data_map[zh_name]
            old_cal = str(old_entry.get('cal', '0')).strip()

            # A. 名稱相同，數值也相同 -> 直接沿用舊翻譯
            if old_cal == new_cal:
                new_database_list.append(old_entry)
                skipped_count += 1
            
            # B. 名稱相同，但數值變了 -> 更新數值
            else:
                old_entry['cal'] = new_cal
                new_database_list.append(old_entry)
                updated_count += 1
        
        # C. 完全的新品項 -> 呼叫翻譯 API
        else:
            en_name = get_english_name(zh_name)
            new_database_list.append({
                "zh": zh_name,
                "en": en_name,
                "cal": new_cal
            })
            new_count += 1
            # 建議保留 sleep，避免翻譯 API 頻率過高被阻擋
            time.sleep(0.5) 

    # 4. 存檔與備份機制
    if os.path.exists(filename):
        if os.path.exists(backup_filename):
            os.remove(backup_filename)
        os.rename(filename, backup_filename)
        print(f"已備份舊資料為 {backup_filename}")

    # 寫入最新的資料
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(new_database_list, f, ensure_ascii=False, indent=4)

    print(f"處理完成！資料已寫入: {filename}")
    print(f"- 無變動: {skipped_count}")
    print(f"- 數值更新: {updated_count}")
    print(f"- 新增翻譯: {new_count}")

except Exception as e:
    print(f"發生錯誤: {e}")