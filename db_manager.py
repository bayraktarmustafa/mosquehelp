import sqlite3
import pandas as pd
import os
import sys

# Taşınabilir (Portable) Veritabanı Yolu:
# Çalıştırılan .exe dosyasının (veya Python scriptinin) bulunduğu klasörü bul.
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

DB_FILE = os.path.join(application_path, "yardim_takip.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Camiler tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mosques (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    
    # Yardımlar tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mosque_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            purpose TEXT,
            FOREIGN KEY (mosque_id) REFERENCES mosques(id)
        )
    ''')
    
    # Eğer tablo önceden oluşturulmuşsa ve purpose sütunu yoksa ekleyelim
    try:
        cursor.execute("ALTER TABLE donations ADD COLUMN purpose TEXT")
    except sqlite3.OperationalError:
        pass # Sütun zaten var
        
    conn.commit()
    conn.close()

def add_mosque(name):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO mosques (name) VALUES (?)", (name,))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False # Zaten var
    conn.close()
    return success

def delete_mosque(name):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM mosques WHERE name=?", (name,))
    conn.commit()
    conn.close()

def tr_sort_key(s):
    # s is a tuple (id, name), we sort by name
    name = s[1].upper()
    order = {'A':1, 'B':2, 'C':3, 'Ç':4, 'D':5, 'E':6, 'F':7, 'G':8, 'Ğ':9, 'H':10, 'I':11, 'İ':12, 'J':13, 'K':14, 'L':15, 'M':16, 'N':17, 'O':18, 'Ö':19, 'P':20, 'R':21, 'S':22, 'Ş':23, 'T':24, 'U':25, 'Ü':26, 'V':27, 'Y':28, 'Z':29}
    return [order.get(c, ord(c)) for c in name]

def get_all_mosques():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM mosques")
    mosques = cursor.fetchall()
    conn.close()
    
    # Sort alphabetically using Turkish characters
    mosques.sort(key=tr_sort_key)
    return mosques

def add_donation(mosque_id, date, amount, description, purpose):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO donations (mosque_id, date, amount, description, purpose) 
        VALUES (?, ?, ?, ?, ?)
    ''', (mosque_id, date, amount, description, purpose))
    conn.commit()
    conn.close()

def delete_donation(donation_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM donations WHERE id=?", (donation_id,))
    conn.commit()
    conn.close()

def delete_all_donations():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM donations")
    conn.commit()
    conn.close()

def update_donation(donation_id, mosque_id, date, amount, description, purpose):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE donations 
        SET mosque_id=?, date=?, amount=?, description=?, purpose=?
        WHERE id=?
    ''', (mosque_id, date, amount, description, purpose, donation_id))
    conn.commit()
    conn.close()

def get_donations_with_names():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT d.id, m.name, d.date, d.amount, d.description, d.purpose
        FROM donations d
        JOIN mosques m ON d.mosque_id = m.id
        ORDER BY d.id DESC
    ''')
    donations = cursor.fetchall()
    conn.close()
    
    # Sort by mosque name using Turkish sort key, preserving d.id DESC for same mosque
    # We can rely on Python's stable sort. First we have them ordered by id DESC from DB.
    # Then we sort by name.
    def tr_sort_donations(d):
        name = d[1].upper()
        order = {'A':1, 'B':2, 'C':3, 'Ç':4, 'D':5, 'E':6, 'F':7, 'G':8, 'Ğ':9, 'H':10, 'I':11, 'İ':12, 'J':13, 'K':14, 'L':15, 'M':16, 'N':17, 'O':18, 'Ö':19, 'P':20, 'R':21, 'S':22, 'Ş':23, 'T':24, 'U':25, 'Ü':26, 'V':27, 'Y':28, 'Z':29}
        return [order.get(c, ord(c)) for c in name]
        
    donations.sort(key=tr_sort_donations)
    return donations

def export_to_excel(filepath):
    conn = sqlite3.connect(DB_FILE)
    query = '''
        SELECT m.name AS "Cami Adı", d.date AS "Tarih", d.amount AS "Miktar (TL)", d.purpose AS "Toplanma Yeri/Amacı", d.description AS "Açıklama"
        FROM donations d
        JOIN mosques m ON d.mosque_id = m.id
        ORDER BY d.date DESC, d.id DESC
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Excel'e yaz
    df.to_excel(filepath, index=False, engine='openpyxl')

def insert_default_mosques():
    mudanya_camileri = [
        "AKKÖY MH.C.", "ALTINKUM GÖNÜL DOSTLARI C.", "ALTINTAŞ MH.C.",
        "ALTINTAŞ MH.ÇAMLIBEL C.", "ALTINTAŞ MH.SAHİL C.", "AYDINPINAR MH.C.",
        "AYDINPINAR MH.HACI SULTAN KANBEROĞLU C.", "BADEMLİ MH.C.", "BALABANCIK MH.C.",
        "BAYRAK C.", "BURGAZ AKŞEMSEDDİN C.", "ÇAĞRIŞAN MH.C.", "ÇAMLIK MH.C.",
        "ÇAYÖNÜ MH.C.", "ÇEKRİCE MH.C.", "ÇEPNİ MH.C.", "ÇINARLI MH.C.",
        "DEDEKÖY MH.C.", "DEREKÖY MH.C.", "EĞERCE MH.C.", "EĞERCE MH.SAHİL C.",
        "EMİRLERYENİCESİ MH.C.", "ESENCE MH.C.", "ESENCE MH.KUBA C.", "ESENCE MH.SAHİL C.",
        "ESKİ C.", "EVCİLER MH.C.", "GÖYNÜKLÜ MH.C.", "GÖYNÜKLÜ MH.ÜÇER C.",
        "GÖYNÜKLÜ MH.YENİ C.", "GÜZELYALI MH.ÇAYIRBAŞI C.", "GÜZELYALI MH.DURAN C.",
        "GÜZELYALI MH.ESKİ C.", "GÜZELYALI MH.SİTELER C.", "GÜZELYALI MH.YENİ C.",
        "HACI EMİNE GÜLSEÇEN C.", "HACIBABA C.", "HANÇERLİ MH.C.", "HASANBEY C.",
        "HASKÖY MH.C.", "IŞIKLI MH.C.", "İPEKYAYLA MH.C.", "KAYMAKOBA MH.C.",
        "KUMYAKA MH.C.", "KÜÇÜKYENİCE MH.C.", "LOKMAN HEKİM C.", "MEHMET AKİF ERSOY C.",
        "MESUDİYE MH.ALİ FATMA GÜN C.", "MESUDİYE MH.C.", "MESUDİYE MH.HACI AVNİ DERYA C.",
        "MESUDİYE MH.SAHİL ÜSKÜP C.", "MİRZAOBA MH.C.", "MUDANYA ÜNİVERSİTESİ MESCİDİ",
        "MÜFTÜLÜK C.", "MÜRSEL MH.C.", "ORHANİYE MH.C.", "ÖMERBEY C.",
        "SÖĞÜTPINAR MH.C.", "TEKKE-İ ATİK C.", "TEKKE-İ CEDİT C.", "TİRİLYE MH.FATİH C.",
        "TİRİLYE MH.TALATBEY C.", "ÜLKÜKÖY MH.C.", "YALIÇİFTLİK MH.C.", "YAMAN MH.C.",
        "YAYLACIK MH.C.", "YENİ C.", "YÖRÜKALİ MH.C.", "YÖRÜKYENİCESİ MH.C."
    ]
    for cami in mudanya_camileri:
        add_mosque(cami)

if __name__ == "__main__":
    init_db()
    insert_default_mosques()
