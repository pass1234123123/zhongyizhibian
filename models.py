import sqlite3
import json
import hashlib
from datetime import datetime

from config import DATABASE


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA foreign_keys=ON')
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()
    c.executescript('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT UNIQUE NOT NULL,
        username TEXT NOT NULL DEFAULT '',
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        avatar TEXT DEFAULT '',
        balance REAL DEFAULT 0.0,
        points INTEGER DEFAULT 0,
        total_earnings REAL DEFAULT 0.0,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS points_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount INTEGER NOT NULL,
        balance_after INTEGER DEFAULT 0,
        source_type TEXT NOT NULL,
        source_id INTEGER DEFAULT 0,
        note TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
    );

    -- AI settings for DeepSeek integration
    CREATE TABLE IF NOT EXISTS ai_settings (
        id INTEGER PRIMARY KEY DEFAULT 1,
        provider TEXT DEFAULT 'deepseek',
        api_key TEXT DEFAULT '',
        model TEXT DEFAULT 'deepseek-chat',
        api_url TEXT DEFAULT 'https://api.deepseek.com/v1/chat/completions',
        auto_approve INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Member settings (global, singleton row)
    CREATE TABLE IF NOT EXISTS member_settings (
        id INTEGER PRIMARY KEY DEFAULT 1,
        annual_fee REAL DEFAULT 199.00,
        free_duration_days INTEGER DEFAULT 365,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Members
    CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL UNIQUE,
        type TEXT NOT NULL DEFAULT 'regular',
        status TEXT NOT NULL DEFAULT 'active',
        start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_date TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    -- Member renewal applications
    CREATE TABLE IF NOT EXISTS member_applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        type TEXT NOT NULL DEFAULT 'contributor_renewal',
        status TEXT NOT NULL DEFAULT 'pending',
        review_note TEXT DEFAULT '',
        reviewer_id INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        reviewed_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    -- View log for non-member tracking
    CREATE TABLE IF NOT EXISTS view_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        treatment_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS disease_categories (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        icon TEXT DEFAULT '',
        color TEXT DEFAULT '#FEE4E2'
    );

    CREATE TABLE IF NOT EXISTS diseases (
        id INTEGER PRIMARY KEY,
        category_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        icon TEXT DEFAULT '',
        treatment_count INTEGER DEFAULT 0,
        FOREIGN KEY (category_id) REFERENCES disease_categories(id)
    );

    CREATE TABLE IF NOT EXISTS treatment_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS treatments (
        id INTEGER PRIMARY KEY,
        disease_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        price REAL DEFAULT 0.0,
        rating REAL DEFAULT 0.0,
        feedback_count INTEGER DEFAULT 0,
        effective_rate INTEGER DEFAULT 0,
        preview TEXT DEFAULT '',
        full_content TEXT DEFAULT '',
        is_special INTEGER DEFAULT 0,
        status TEXT DEFAULT 'published',
        uploader_id INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (disease_id) REFERENCES diseases(id)
    );

    CREATE TABLE IF NOT EXISTS treatment_type_relations (
        treatment_id INTEGER NOT NULL,
        type_name TEXT NOT NULL,
        PRIMARY KEY (treatment_id, type_name),
        FOREIGN KEY (treatment_id) REFERENCES treatments(id)
    );

    CREATE TABLE IF NOT EXISTS treatment_formulas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        treatment_id INTEGER NOT NULL,
        formula_name TEXT DEFAULT '',
        ingredients TEXT DEFAULT '',
        usage_text TEXT DEFAULT '',
        note TEXT DEFAULT '',
        FOREIGN KEY (treatment_id) REFERENCES treatments(id)
    );

    CREATE TABLE IF NOT EXISTS treatment_acupoints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        treatment_id INTEGER NOT NULL,
        points TEXT DEFAULT '',
        method TEXT DEFAULT '',
        course TEXT DEFAULT '',
        FOREIGN KEY (treatment_id) REFERENCES treatments(id)
    );

    CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        treatment_id INTEGER NOT NULL,
        amount REAL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, treatment_id),
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (treatment_id) REFERENCES treatments(id)
    );

    CREATE TABLE IF NOT EXISTS feedbacks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        treatment_id INTEGER NOT NULL,
        rating INTEGER NOT NULL CHECK(rating>=1 AND rating<=5),
        efficacy TEXT DEFAULT '',
        description TEXT DEFAULT '',
        course_days INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (treatment_id) REFERENCES treatments(id)
    );

    CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        treatment_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, treatment_id),
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (treatment_id) REFERENCES treatments(id)
    );

    CREATE TABLE IF NOT EXISTS uploads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        content TEXT DEFAULT '',
        file_names TEXT DEFAULT '',
        ai_result TEXT DEFAULT '',
        status TEXT DEFAULT 'pending',
        review_note TEXT DEFAULT '',
        reviewer_id INTEGER DEFAULT 0,
        reviewed_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    ''')
    conn.commit()
    conn.close()


def seed_data():
    conn = get_db()
    c = conn.cursor()
    # Check if data already exists
    existing = c.execute('SELECT COUNT(*) FROM disease_categories').fetchone()[0]
    if existing > 0:
        conn.close()
        return
    
    # Seed categories
    categories = [
        (1, '内科', '\U0001fa81', '#FEE4E2'),
        (2, '外科', '\U0001f3e5', '#FFF3E0'),
        (3, '妇科', '\U0001f469', '#FCE4EC'),
        (4, '儿科', '\U0001f476', '#E8F5E9'),
        (5, '骨伤科', '\U0001f9b4', '#E3F2FD'),
        (6, '皮肤科', '\U0001f9f4', '#F3E5F5'),
        (7, '肿瘤科', '\U0001f397', '#FBE9E7'),
        (8, '五官科', '\U0001f441', '#E0F7FA'),
        (9, '男科', '\U0001f468', '#E8EAF6'),
        (10, '神经科', '\U0001f9e0', '#F1F8E9'),
        (11, '风湿免疫科', '\U0001f9b5', '#FFF8E1'),
        (12, '肛肠科', '\U0001fa79', '#FBE9E7'),
        (13, '眼科', '\U0001f440', '#E0F2F1'),
    ]
    c.executemany('INSERT OR IGNORE INTO disease_categories (id, name, icon, color) VALUES (?,?,?,?)', categories)
    
    # Seed diseases
    diseases = [
        (101, 1, '胃痛', '\U0001f525', 12), (102, 1, '糖尿病', '\U0001f36c', 8),
        (103, 1, '高血压', '\U0001f489', 7), (104, 1, '感冒', '\U0001f927', 15),
        (105, 1, '失眠', '\U0001f634', 9), (106, 1, '便秘', '\U0001f6bd', 6),
        (107, 1, '咳嗽', '\U0001f912', 10), (108, 1, '哮喘', '\U0001f32c', 5),
        (109, 1, '慢性胃炎', '\U0001f525', 8), (110, 1, '冠心病', '\u2764', 6),
        (111, 1, '中风后遗症', '\u26a1', 7), (112, 1, '肾炎', '\U0001fa78', 4),
        (201, 2, '痔疮', '\U0001fa79', 5), (202, 2, '痈疽', '\U0001f534', 3),
        (203, 2, '跌打损伤', '\U0001f915', 8), (204, 2, '乳腺增生', '\U0001f380', 6),
        (205, 2, '甲状腺结节', '\U0001f534', 5),
        (301, 3, '月经不调', '\U0001f4c5', 10), (302, 3, '痛经', '\U0001f4a2', 7),
        (303, 3, '产后调理', '\U0001f476', 8), (304, 3, '更年期综合征', '\U0001f30a', 6),
        (305, 3, '不孕症', '\U0001f930', 6),
        (401, 4, '小儿积食', '\U0001f37c', 5), (402, 4, '小儿感冒', '\U0001f912', 8),
        (403, 4, '小儿腹泻', '\U0001f4a9', 6), (404, 4, '小儿咳嗽', '\U0001f927', 6),
        (501, 5, '颈椎病', '\U0001f992', 8), (502, 5, '腰椎间盘突出', '\U0001f519', 7),
        (503, 5, '肩周炎', '\U0001f4aa', 6), (504, 5, '关节炎', '\U0001f9b5', 8),
        (601, 6, '湿疹', '\U0001f534', 8), (602, 6, '荨麻疹', '\U0001f4a8', 6),
        (603, 6, '痤疮', '\U0001f637', 7), (604, 6, '银屑病', '\U0001f504', 5),
        (605, 6, '带状疱疹', '\U0001f525', 6), (606, 6, '脱发', '\U0001f487', 5),
        (701, 7, '肺癌辅助', '\U0001fac1', 6), (702, 7, '胃癌辅助', '\U0001fac4', 5),
        (703, 7, '乳腺癌辅助', '\U0001f380', 6), (704, 7, '放化疗后调理', '\U0001f48a', 7),
        (801, 8, '鼻炎', '\U0001f443', 8), (802, 8, '咽炎', '\U0001f5e3', 7),
        (803, 8, '耳鸣耳聋', '\U0001f442', 6), (804, 8, '牙痛', '\U0001f9b7', 6),
        (805, 8, '口腔溃疡', '\U0001f48b', 5),
        (901, 9, '前列腺炎', '\U0001f534', 6), (902, 9, '阳痿', '\U0001f6ab', 5),
        (903, 9, '早泄', '\u26a1', 5),
        (1001, 10, '偏头痛', '\U0001f915', 7), (1002, 10, '面瘫', '\U0001f610', 6),
        (1003, 10, '三叉神经痛', '\u26a1', 5), (1004, 10, '坐骨神经痛', '\U0001f9b5', 5),
        (1101, 11, '类风湿关节炎', '\U0001f9b4', 6), (1102, 11, '痛风', '\U0001f9b6', 7),
        (1103, 11, '干燥综合征', '\U0001f3dc', 3),
        (1201, 12, '痔疮(肛肠)', '\U0001fa79', 5), (1202, 12, '肛裂', '\U0001f494', 4),
        (1203, 12, '肛瘘', '\U0001f534', 3),
        (1301, 13, '近视', '\U0001f453', 5), (1302, 13, '干眼症', '\U0001f3dc', 6),
        (1303, 13, '白内障', '\U0001f32b', 4),
    ]
    c.executemany('INSERT OR IGNORE INTO diseases (id, category_id, name, icon, treatment_count) VALUES (?,?,?,?,?)', diseases)
    
    # Seed treatments data from the embedded JSON in demo.html
    treatments_data = {
        "101": [
            {"id": 10101, "t": "胃痛温中健脾方", "ty": ["方剂内服"], "pr": 9.9, "ra": 4.2, "fb": 23, "ef": 78, "pv": "理中汤化裁，专治脾胃虚寒型胃痛", "fu": "【方名】温中健胃汤\n【组成】党参15g、白术12g、干姜6g、炙甘草6g、茯苓12g、木香6g、砂仁6g(后下)\n【用法】每日1剂水煎2次", "fo": [{"fn": "温中健胃汤", "ing": "党参15g、白术12g、干姜6g、炙甘草6g、茯苓12g、木香6g、砂仁6g(后下)", "us": "每日1剂，水煎2次", "nt": "7天为一疗程"}]},
            {"id": 10102, "t": "胃痛针灸止痛方", "ty": ["针灸"], "pr": 6.9, "ra": 4.5, "fb": 18, "ef": 85, "pv": "选取任脉及足阳明胃经穴位", "fu": "【主穴】中脘、足三里、内关、公孙\n【操作】中脘直刺1-1.5寸，提插捻转法，留针30分钟", "ac": [{"pt": "中脘、足三里、内关、公孙", "me": "直刺1-1.5寸，提插捻转法", "co": "每日1次，7次一疗程"}]},
            {"id": 10103, "t": "胃痛推拿调理法", "ty": ["推拿手法"], "pr": 5.9, "ra": 4.0, "fb": 10, "ef": 72, "pv": "按揉胃脘部及背部俞穴，调理脾胃气机", "fu": "【手法】一指禅推法、揉法、按法、摩法\n【取穴】中脘、天枢、气海、足三里、脾俞、胃俞"},
            {"id": 10104, "t": "胃痛食疗药膳方", "ty": ["食疗药膳"], "pr": 3.9, "ra": 4.3, "fb": 15, "ef": 80, "pv": "药食同源，通过日常饮食调理脾胃", "fu": "【药膳】山药茯苓粥：山药30g、茯苓15g、粳米100g、红枣5枚"},
            {"id": 10105, "t": "胃痛拔罐疗法", "ty": ["拔罐"], "pr": 4.9, "ra": 3.9, "fb": 8, "ef": 68, "pv": "背部膀胱经拔罐，疏通经络", "fu": "【取穴】脾俞、胃俞、中脘、天枢\n【操作】4号火罐闪火法，留罐10-15分钟"},
        ],
        "102": [
            {"id": 10201, "t": "糖尿病益气养阴方", "ty": ["方剂内服"], "pr": 12.9, "ra": 4.3, "fb": 15, "ef": 76, "pv": "益气养阴，对II型糖尿病有良好辅助治疗作用", "fu": "【方名】益气养阴降糖方\n【组成】生黄芪30g、生地15g、山药15g、天花粉12g、葛根12g、五味子6g、麦冬12g", "fo": [{"fn": "益气养阴降糖方", "ing": "生黄芪30g、生地15g、山药15g、天花粉12g、葛根12g、五味子6g、麦冬12g", "us": "每日1剂，水煎分2次温服", "nt": "配合低糖饮食"}]},
            {"id": 10202, "t": "糖尿病足浴方", "ty": ["方剂外用"], "pr": 8.9, "ra": 4.0, "fb": 9, "ef": 70, "pv": "中药足浴改善下肢血液循环", "fu": "【方名】活血通络足浴方\n【组成】川芎15g、红花10g、桂枝12g、透骨草15g、艾叶12g、花椒6g"},
            {"id": 10203, "t": "糖尿病针灸调理", "ty": ["针灸"], "pr": 7.9, "ra": 4.1, "fb": 11, "ef": 73, "pv": "针刺特定穴位调节胰岛素分泌", "fu": "【主穴】胰俞、脾俞、足三里、三阴交、太溪\n【操作】背俞穴斜刺，平补平泻法", "ac": [{"pt": "胰俞、脾俞、足三里、三阴交、太溪", "me": "背俞斜刺，平补平泻", "co": "隔日1次，10次一疗程"}]},
            {"id": 10204, "t": "糖尿病食疗功法", "ty": ["食疗药膳", "导引气功"], "pr": 4.9, "ra": 3.8, "fb": 7, "ef": 65, "pv": "饮食控制配合八段锦锻炼", "fu": "【药膳】苦瓜炒山药\n【茶饮】玉米须枸杞茶\n【功法】八段锦每日早晚各1遍"},
        ],
        "103": [
            {"id": 10301, "t": "高血压平肝潜阳方", "ty": ["方剂内服"], "pr": 11.9, "ra": 4.1, "fb": 12, "ef": 74, "pv": "天麻钩藤饮化裁，平肝潜阳", "fu": "【方名】平肝降压方\n【组成】天麻12g、钩藤15g(后下)、石决明30g(先煎)、黄芩10g、牛膝12g"},
            {"id": 10302, "t": "高血压耳尖放血", "ty": ["放血"], "pr": 5.9, "ra": 4.2, "fb": 14, "ef": 78, "pv": "耳尖放血是中医急救降压的有效手段", "fu": "【部位】耳尖穴\n【操作】三棱针快速刺入1-2mm，挤出5-10滴血\n【注意】需专业人员操作", "sp": True},
            {"id": 10303, "t": "高血压足浴降压法", "ty": ["方剂外用"], "pr": 7.9, "ra": 3.9, "fb": 9, "ef": 71, "pv": "中药足浴辅助降压", "fu": "【方名】降压足浴方\n【组成】钩藤30g、夏枯草30g、桑叶20g、菊花20g、牛膝20g"},
        ],
        "104": [
            {"id": 10401, "t": "感冒风寒方", "ty": ["方剂内服"], "pr": 5.9, "ra": 4.4, "fb": 25, "ef": 82, "pv": "麻黄汤加减，发汗解表", "fu": "【方名】加减麻黄汤\n【组成】麻黄9g、桂枝6g、杏仁10g、甘草6g、荆芥10g、防风10g"},
            {"id": 10402, "t": "感冒风热方", "ty": ["方剂内服"], "pr": 5.9, "ra": 4.3, "fb": 22, "ef": 80, "pv": "银翘散加减，疏风清热", "fu": "【方名】银翘散加减\n【组成】金银花15g、连翘12g、薄荷6g(后下)、牛蒡子10g、桔梗6g、甘草6g"},
            {"id": 10403, "t": "感冒推拿疗法", "ty": ["推拿手法"], "pr": 3.9, "ra": 4.1, "fb": 16, "ef": 75, "pv": "按揉特定穴位缓解感冒症状", "fu": "【取穴】风池、太阳、迎香、合谷\n【操作】按揉风池3分钟，推抹太阳2分钟"},
            {"id": 10404, "t": "感冒拔罐疗法", "ty": ["拔罐"], "pr": 3.9, "ra": 3.8, "fb": 12, "ef": 70, "pv": "大椎穴拔罐对风寒感冒初起有良效", "fu": "【取穴】大椎、风门、肺俞\n【操作】3号罐闪火法，留罐10分钟"},
            {"id": 10405, "t": "感冒食疗方", "ty": ["食疗药膳"], "pr": 2.9, "ra": 4.5, "fb": 20, "ef": 85, "pv": "生姜红糖水是经典感冒食疗方", "fu": "【食疗】生姜红糖水：生姜5片、红糖30g\n【茶饮】葱白豆豉汤"},
        ],
        "105": [
            {"id": 10501, "t": "失眠安神方", "ty": ["方剂内服"], "pr": 10.9, "ra": 4.2, "fb": 18, "ef": 76, "pv": "酸枣仁汤化裁，养心安神", "fu": "【方名】安神助眠汤\n【组成】酸枣仁30g(打碎先煎)、知母10g、茯苓15g、川芎6g、甘草6g、夜交藤30g"},
            {"id": 10502, "t": "失眠针灸方", "ty": ["针灸"], "pr": 7.9, "ra": 4.4, "fb": 14, "ef": 80, "pv": "调理心脾肾三脏，安神定志", "fu": "【主穴】神门、内关、百会、三阴交、安眠\n【操作】神门直刺0.3-0.5寸，捻转补法", "ac": [{"pt": "神门、内关、百会、三阴交、安眠", "me": "直刺，捻转补法", "co": "下午或睡前治疗，隔日1次"}]},
            {"id": 10503, "t": "失眠足浴安神法", "ty": ["方剂外用"], "pr": 5.9, "ra": 4.1, "fb": 12, "ef": 74, "pv": "中药足浴引火归元，助眠安神", "fu": "【方名】安神足浴方\n【组成】夜交藤30g、合欢皮30g、艾叶20g、肉桂10g"},
        ],
        "106": [
            {"id": 10601, "t": "便秘润肠通下方", "ty": ["方剂内服"], "pr": 8.9, "ra": 4.0, "fb": 14, "ef": 71, "pv": "增液承气汤化裁，增水行舟", "fu": "【方名】润肠通便方\n【组成】玄参15g、麦冬12g、生地15g、火麻仁15g、郁李仁12g、枳壳10g"},
            {"id": 10602, "t": "便秘腹部推拿", "ty": ["推拿手法"], "pr": 3.9, "ra": 4.3, "fb": 16, "ef": 82, "pv": "顺时针摩腹是中医最经典的便秘自我调理法", "fu": "【手法】顺时针摩腹5分钟，点按天枢3分钟\n【取穴】天枢、大横、支沟、上巨虚", "sp": True},
        ],
        "107": [
            {"id": 10701, "t": "咳嗽化痰方", "ty": ["方剂内服"], "pr": 7.9, "ra": 4.1, "fb": 16, "ef": 74, "pv": "止嗽散合三拗汤加减，宣肺止咳", "fu": "【方名】宣肺止咳方\n【组成】桔梗10g、荆芥10g、紫菀12g、百部10g、白前10g、杏仁10g、甘草6g"},
            {"id": 10702, "t": "咳嗽灸法", "ty": ["针灸"], "pr": 5.9, "ra": 4.3, "fb": 10, "ef": 78, "pv": "艾灸背部俞穴温肺化痰", "fu": "【取穴】肺俞、膏肓、大椎\n【操作】温和灸15分钟，以皮肤潮红为度", "ac": [{"pt": "肺俞、膏肓、大椎", "me": "温和灸15分钟", "co": "每日1次"}]},
        ],
        "108": [
            {"id": 10801, "t": "哮喘固本平喘方", "ty": ["方剂内服"], "pr": 12.9, "ra": 4.1, "fb": 8, "ef": 72, "pv": "金匮肾气丸合三子养亲汤化裁", "fu": "【方名】固本平喘方\n【组成】熟地15g、山药15g、山萸肉10g、茯苓12g、苏子10g、白芥子6g、莱菔子10g"},
            {"id": 10802, "t": "哮喘三伏贴", "ty": ["针灸", "方剂外用"], "pr": 8.9, "ra": 4.5, "fb": 12, "ef": 82, "pv": "冬病夏治经典疗法，连续3年效果好", "fu": "【穴位】肺俞、心俞、膈俞、大椎\n【药物】白芥子30g、细辛15g、甘遂15g、延胡索30g\n【用法】三伏天贴敷4-6小时", "sp": True},
        ],
        "110": [
            {"id": 11001, "t": "冠心病活血通脉方", "ty": ["方剂内服"], "pr": 14.9, "ra": 4.0, "fb": 9, "ef": 72, "pv": "血府逐瘀汤加减，活血化瘀，通脉止痛", "fu": "【方名】活血通脉方\n【组成】丹参15g、赤芍12g、川芎10g、红花6g、降香6g、瓜蒌15g、薤白10g"},
        ],
        "302": [
            {"id": 30201, "t": "痛经温经散寒方", "ty": ["方剂内服"], "pr": 8.9, "ra": 4.4, "fb": 16, "ef": 82, "pv": "温经汤化裁，温经散寒，祛瘀止痛", "fu": "【方名】温经止痛方\n【组成】当归15g、川芎10g、白芍12g、桂枝10g、吴茱萸6g、延胡索12g", "sp": True},
            {"id": 30202, "t": "痛经温灸疗法", "ty": ["针灸"], "pr": 6.9, "ra": 4.6, "fb": 18, "ef": 88, "pv": "艾灸关元、神阙，痛经外治最有效", "fu": "【取穴】关元、神阙、三阴交、次髎\n【操作】艾条悬灸关元15分钟，隔姜灸神阙5壮", "sp": True, "ac": [{"pt": "关元、神阙、三阴交、次髎", "me": "艾条悬灸+隔姜灸", "co": "经前3天开始，每日1次"}]},
        ],
        "301": [
            {"id": 30101, "t": "月经不调养血方", "ty": ["方剂内服"], "pr": 9.9, "ra": 4.3, "fb": 14, "ef": 77, "pv": "四物汤加减，补血调经", "fu": "【方名】调经养血方\n【组成】当归15g、熟地15g、白芍12g、川芎10g、香附10g、益母草15g"},
            {"id": 30102, "t": "月经不调针灸方", "ty": ["针灸"], "pr": 7.9, "ra": 4.4, "fb": 12, "ef": 80, "pv": "调理冲任二脉，调节月经周期", "fu": "【主穴】关元、三阴交、血海、归来\n【操作】关元直刺1-1.5寸，平补平泻", "ac": [{"pt": "关元、三阴交、血海、归来", "me": "直刺，平补平泻", "co": "经前1周开始，每日1次"}]},
        ],
        "401": [
            {"id": 40101, "t": "小儿积食推拿法", "ty": ["推拿手法", "食疗药膳"], "pr": 4.9, "ra": 4.4, "fb": 10, "ef": 84, "pv": "纯手法治疗，宝宝容易接受", "fu": "【推拿】运内八卦100次、摩腹5分钟、捏脊3-5遍\n【食疗】山楂麦芽水", "sp": True},
        ],
        "501": [
            {"id": 50101, "t": "颈椎病针灸推拿", "ty": ["针灸", "推拿手法"], "pr": 9.9, "ra": 4.4, "fb": 20, "ef": 82, "pv": "针灸配合推拿是颈椎病黄金组合", "fu": "【主穴】颈夹脊、风池、肩髃、手三里\n【操作】斜刺1寸配合电针，颈肩部推拿牵引", "sp": True, "ac": [{"pt": "颈夹脊、风池、肩髃、手三里", "me": "斜刺+电针，配合推拿", "co": "每日1次，10次一疗程"}]},
        ],
        "601": [
            {"id": 60101, "t": "湿疹清热祛湿方", "ty": ["方剂内服", "方剂外用"], "pr": 8.9, "ra": 3.9, "fb": 12, "ef": 71, "pv": "萆薢渗湿汤加减，清热利湿", "fu": "【方名】清热祛湿方\n【组成】萆薢15g、薏苡仁30g、黄柏10g、赤茯苓15g、丹皮10g、泽泻12g"},
            {"id": 60102, "t": "湿疹外洗方", "ty": ["方剂外用"], "pr": 6.9, "ra": 4.0, "fb": 10, "ef": 74, "pv": "中药外洗直接作用于皮损", "fu": "【方名】祛湿止痒外洗方\n【组成】苦参30g、黄柏20g、蛇床子20g、地肤子20g、白鲜皮20g"},
        ],
        "701": [
            {"id": 70101, "t": "肺癌扶正固本方", "ty": ["方剂内服"], "pr": 15.9, "ra": 3.9, "fb": 8, "ef": 65, "pv": "益气养阴，辅助放化疗", "fu": "【方名】扶正抗癌方\n【组成】黄芪30g、沙参15g、麦冬12g、半枝莲30g、白花蛇舌草30g"},
            {"id": 70102, "t": "放化疗后调理膳", "ty": ["食疗药膳"], "pr": 9.9, "ra": 4.1, "fb": 10, "ef": 72, "pv": "药膳调理减轻放化疗副作用", "fu": "【药膳】黄芪山药粥、枸杞银耳羹\n【茶饮】参须麦冬茶"},
        ],
        "801": [
            {"id": 80101, "t": "鼻炎通窍方", "ty": ["方剂内服", "方剂外用"], "pr": 7.9, "ra": 4.0, "fb": 14, "ef": 74, "pv": "苍耳子散加减，疏风通窍", "fu": "【方名】通窍鼻炎方\n【组成】辛夷10g(包煎)、苍耳子6g、白芷10g、薄荷6g(后下)、黄芩10g"},
            {"id": 80102, "t": "鼻炎针灸疗法", "ty": ["针灸"], "pr": 7.9, "ra": 4.2, "fb": 12, "ef": 78, "pv": "针刺迎香、鼻通，快速缓解鼻塞", "fu": "【主穴】迎香、鼻通、印堂、合谷\n【疗程】隔日1次，10次一疗程", "ac": [{"pt": "迎香、鼻通、印堂、合谷", "me": "斜刺0.3-0.5寸", "co": "隔日1次，10次一疗程"}]},
        ],
        "1001": [
            {"id": 100101, "t": "偏头痛川芎茶调方", "ty": ["方剂内服"], "pr": 7.9, "ra": 4.1, "fb": 12, "ef": 75, "pv": "川芎茶调散加减，疏风止痛", "fu": "【方名】疏风止痛方\n【组成】川芎15g、白芷10g、羌活10g、防风10g、薄荷6g(后下)、甘草6g"},
            {"id": 100102, "t": "偏头痛放血疗法", "ty": ["放血"], "pr": 5.9, "ra": 4.3, "fb": 11, "ef": 82, "pv": "太阳穴刺血对偏头痛急性发作快速止痛", "fu": "【部位】太阳穴(患侧)、耳尖\n【操作】三棱针点刺太阳穴出血3-5滴", "sp": True},
        ],
        "1102": [
            {"id": 110201, "t": "痛风清热利湿方", "ty": ["方剂内服", "方剂外用"], "pr": 10.9, "ra": 4.1, "fb": 13, "ef": 74, "pv": "四妙散加减，清热利湿", "fu": "【方名】清热利湿痛风方\n【组成】苍术12g、黄柏10g、薏苡仁30g、牛膝12g、忍冬藤30g"},
            {"id": 110202, "t": "痛风放血疗法", "ty": ["放血"], "pr": 6.9, "ra": 4.2, "fb": 10, "ef": 79, "pv": "刺络放血快速缓解急性痛风", "fu": "【部位】红肿最明显处\n【操作】三棱针点刺3-5针，加拔火罐出血5-10ml", "sp": True},
        ],
    }
    
    for disease_key, treats in treatments_data.items():
        disease_id = int(disease_key)
        for t in treats:
            c.execute('''INSERT OR IGNORE INTO treatments 
                (id, disease_id, title, price, rating, feedback_count, effective_rate, preview, full_content, is_special)
                VALUES (?,?,?,?,?,?,?,?,?,?)''',
                (t['id'], disease_id, t['t'], t['pr'], t['ra'], t['fb'], t['ef'], t['pv'], t['fu'], 1 if t.get('sp') else 0))
            
            for typ in t['ty']:
                c.execute('INSERT OR IGNORE INTO treatment_types (name) VALUES (?)', (typ,))
                c.execute('INSERT OR IGNORE INTO treatment_type_relations (treatment_id, type_name) VALUES (?,?)', (t['id'], typ))
            
            for fo in t.get('fo', []):
                c.execute('INSERT INTO treatment_formulas (treatment_id, formula_name, ingredients, usage_text, note) VALUES (?,?,?,?,?)',
                    (t['id'], fo['fn'], fo['ing'], fo['us'], fo.get('nt', '')))
            
            for ac in t.get('ac', []):
                c.execute('INSERT INTO treatment_acupoints (treatment_id, points, method, course) VALUES (?,?,?,?)',
                    (t['id'], ac['pt'], ac['me'], ac['co']))
    
    # Create default admin user
    password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
    c.execute('INSERT OR IGNORE INTO users (id, phone, username, password_hash, role, points) VALUES (1, "13800000000", "管理员", ?, "admin", 9999)', (password_hash,))

    # Seed default member settings
    c.execute('INSERT OR IGNORE INTO member_settings (id, annual_fee, free_duration_days) VALUES (1, 199.00, 365)')
    c.execute('INSERT OR IGNORE INTO ai_settings (id, provider, api_key, model, auto_approve) VALUES (1, "deepseek", "", "deepseek-chat", 1)')
    
    conn.commit()
    conn.close()
    print('数据库初始化完成！')
    print('管理员账号: 13800000000 / admin123')
