import os
import datetime
import pandas as pd
from TODOIST_API.api import TodoistAPI

# ---------------- 配置区域 ----------------
# 你的 CSV 链接 (确保是发布为 CSV 的链接)
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRKGGAzH4TH8kL-868ITJn-oJ5TubHVJasslgxXabdyDvCksIYeo92FtMchhBYggloM5r7SqH5BDgN4/pubhtml"
TODOIST_TOKEN = os.environ.get("TODOIST_API")

COL_DATE = 'DATE'
COL_BREAKFAST = 'BREAKFAST'  
COL_LUNCH = 'LUNCH'        
COL_DINNER = 'DINNER'
COL_SUPPORT = 'SUPPORT'
COL_TRAINING = 'TRAINING'
COL_CALORIES = 'KAL_GAP'
# ----------------------------------------

def sync_fitness_plan():
    print("🚀 开始同步健身计划...")
    
    try:
        # 读取 CSV
        df = pd.read_csv(CSV_URL)
        
        # 将表头所有的空格去掉，防止误判
        df.columns = df.columns.str.strip()
        
        # 确保包含日期列
        if COL_DATE not in df.columns:
            print(f"❌ 错误：表格里找不到叫 '{COL_DATE}' 的列。")
            print(f"   当前读取到的表头是: {list(df.columns)}")
            return
            
        # 强制将日期列转为字符串，并处理可能的空值
        df[COL_DATE] = df[COL_DATE].astype(str).fillna('')
        
    except Exception as e:
        print(f"❌ 读取 Google Sheet 失败: {e}")
        return

    # --- 核心：处理中文日期匹配 ---
    # 获取今天的时间对象
    now = datetime.datetime.now()
    
    # 构造匹配关键词：例如今天是 1月5日，我们就找包含 "1月5日" 的单元格
    # 这样可以忽略后面的 "（周三）"
    date_keyword = f"{now.month}月{now.day}日"
    
    print(f"📅 今天的匹配关键词是: '{date_keyword}'")

    # 在日期列中查找包含该关键词的行
    # str.contains 是模糊匹配
    today_data = df.loc[df[COL_DATE].str.contains(date_keyword, na=False)]

    if today_data.empty:
        print(f"😴 今天 ({date_keyword}) 表格里没写计划，或者格式不匹配，休息一天！")
        return
    
    # 取出这一行数据
    plan = today_data.iloc[0]

    # --- 连接 Todoist ---
    api = TodoistAPI(TODOIST_TOKEN)
    tasks = []

    # --- 组装任务 ---
    # 1. 早餐
    if COL_BREAKFAST in plan and pd.notna(plan[COL_BREAKFAST]):
        tasks.append(f"🥣 早餐: {plan[COL_BREAKFAST]}")
        
    # 2. 午餐
    if COL_LUNCH in plan and pd.notna(plan[COL_LUNCH]):
        tasks.append(f"🍱 午餐: {plan[COL_LUNCH]}")
        
    # 3. 晚餐
    if COL_DINNER in plan and pd.notna(plan[COL_DINNER]):
        tasks.append(f"🍽️ 晚餐: {plan[COL_DINNER]}")

    # 4. 补给/支持
    if COL_SUPPORT in plan and pd.notna(plan[COL_SUPPORT]):
        tasks.append(f"💊 补给: {plan[COL_SUPPORT]}")
        
    # 5. 训练
    if COL_TRAINING in plan and pd.notna(plan[COL_TRAINING]):
        tasks.append(f"💪 训练: {plan[COL_TRAINING]}")
    
    # 6. 热量缺口
    if COL_CALORIES in plan and pd.notna(plan[COL_CALORIES]):
        tasks.append(f"🔥 热量缺口: {plan[COL_CALORIES]}")

    # --- 推送 ---
    if not tasks:
        print("今天虽然有日期，但各列内容都是空的。")
        return

    print(f"准备推送 {len(tasks)} 个任务...")
    
    for t in tasks:
        try:
            # priority=4 是最高优先级(红色)，due_string="today" 设为今天截止
            api.add_task(content=t, due_string="today", priority=4)
            print(f"✅ 已添加任务: {t}")
        except Exception as e:
            print(f"❌ 添加失败: {e}")

if __name__ == "__main__":
    if TODOIST_TOKEN:
        sync_fitness_plan()
    else:
        print("❌ 请在 GitHub Secrets 里配置 TODOIST_API")
