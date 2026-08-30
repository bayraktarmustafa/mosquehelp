import sys
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QComboBox, QLineEdit, QTextEdit, 
                             QMessageBox, QFileDialog, QStackedWidget, QHeaderView, QTableWidget, QTableWidgetItem, QDateEdit, QTabWidget, QMenu, QDialog, QFormLayout, QAbstractItemView)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QPixmap
import db_manager
import pandas as pd
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mudanya Müftülüğü - Cami Yardım Takip")
        self.resize(950, 650)
        
        db_manager.init_db()
        # Varsayılan camileri bir kereye mahsus ekleyelim
        db_manager.insert_default_mosques()
        self.mosques = {}
        
        # Ana widget ve layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QVBoxLayout(main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.stacked_widget_main = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget_main)
        
        # Uygulama Sayfası
        self.page_app = QWidget()
        self.setup_app_page()
        
        self.stacked_widget_main.addWidget(self.page_app)
        self.stacked_widget_main.setCurrentWidget(self.page_app)
        
        # Başlangıçta verileri çek ve kayıt sayfasını aç
        self.refresh_mosques()
        self.show_kayit()

    def setup_app_page(self):
        layout = QHBoxLayout(self.page_app)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # --- Sol Menü ---
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("background-color: #2c3e50; color: white;")
        sidebar_layout = QVBoxLayout(sidebar)
        
        logo_text = QLabel("Mudanya İlçe Müftülüğü")
        logo_text.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px; margin-top: 20px;")
        logo_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(logo_text)
        
        btn_kayit = QPushButton("Yardım Kaydet")
        btn_kayit.setStyleSheet("padding: 10px; font-size: 14px; text-align: left; margin: 5px 10px; background-color: #34495e; border-radius: 5px;")
        btn_kayit.clicked.connect(self.show_kayit)
        sidebar_layout.addWidget(btn_kayit)
        
        btn_liste = QPushButton("Yardım Listesi")
        btn_liste.setStyleSheet("padding: 10px; font-size: 14px; text-align: left; margin: 5px 10px; background-color: #34495e; border-radius: 5px;")
        btn_liste.clicked.connect(self.show_liste)
        sidebar_layout.addWidget(btn_liste)
        
        btn_ayarlar = QPushButton("Cami Ayarları")
        btn_ayarlar.setStyleSheet("padding: 10px; font-size: 14px; text-align: left; margin: 5px 10px; background-color: #34495e; border-radius: 5px;")
        btn_ayarlar.clicked.connect(self.show_ayarlar)
        sidebar_layout.addWidget(btn_ayarlar)
        
        sidebar_layout.addStretch()
        
        lbl_dev = QLabel("development by Mustafa Bayraktar")
        lbl_dev.setStyleSheet("font-size: 10px; color: #95a5a6; margin-bottom: 10px;")
        lbl_dev.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(lbl_dev)
        
        # --- Sağ İçerik (Stacked Widget) ---
        self.stacked_widget_app = QStackedWidget()
        self.stacked_widget_app.setStyleSheet("background-color: #ecf0f1;")
        
        self.page_kayit = QWidget()
        self.page_liste = QWidget()
        self.page_ayarlar = QWidget()
        
        self.setup_kayit_page()
        self.setup_liste_page()
        self.setup_ayarlar_page()
        
        self.stacked_widget_app.addWidget(self.page_kayit)
        self.stacked_widget_app.addWidget(self.page_liste)
        self.stacked_widget_app.addWidget(self.page_ayarlar)
        
        layout.addWidget(sidebar)
        layout.addWidget(self.stacked_widget_app)

    def show_kayit(self):
        self.refresh_mosques()
        self.stacked_widget_app.setCurrentWidget(self.page_kayit)

    def show_liste(self):
        self.refresh_liste()
        self.stacked_widget_app.setCurrentWidget(self.page_liste)

    def show_ayarlar(self):
        self.refresh_mosques()
        self.stacked_widget_app.setCurrentWidget(self.page_ayarlar)

    # --- KAYIT SAYFASI ---
    def setup_kayit_page(self):
        layout = QVBoxLayout(self.page_kayit)
        layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("Yeni Yardım Kaydı")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)
        
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        self.cmb_cami = QComboBox()
        self.cmb_cami.setStyleSheet("padding: 5px; font-size: 14px; background-color: white;")
        form_layout.addWidget(QLabel("Cami Seçiniz:"))
        form_layout.addWidget(self.cmb_cami)
        
        self.ent_tarih = QLineEdit(datetime.now().strftime("%d-%m-%Y"))
        self.ent_tarih.setStyleSheet("padding: 5px; font-size: 14px; background-color: white;")
        form_layout.addWidget(QLabel("Tarih (GG-AA-YYYY):"))
        form_layout.addWidget(self.ent_tarih)
        
        self.ent_miktar = QLineEdit()
        self.ent_miktar.setPlaceholderText("Örn: 1500.50")
        self.ent_miktar.setStyleSheet("padding: 5px; font-size: 14px; background-color: white;")
        form_layout.addWidget(QLabel("Miktar (TL):"))
        form_layout.addWidget(self.ent_miktar)

        self.ent_purpose = QLineEdit()
        self.ent_purpose.setPlaceholderText("Örn: Filistin, Kur'an Kursu, Depremzedeler")
        self.ent_purpose.setStyleSheet("padding: 5px; font-size: 14px; background-color: white;")
        form_layout.addWidget(QLabel("Toplanma Yeri / Amacı:"))
        form_layout.addWidget(self.ent_purpose)
        
        self.ent_aciklama = QLineEdit()
        self.ent_aciklama.setPlaceholderText("Cuma yardımı, vb. (İsteğe Bağlı)")
        self.ent_aciklama.setStyleSheet("padding: 5px; font-size: 14px; background-color: white;")
        form_layout.addWidget(QLabel("Açıklama (İsteğe Bağlı):"))
        form_layout.addWidget(self.ent_aciklama)
        
        layout.addLayout(form_layout)
        
        btn_kaydet = QPushButton("Yardımı Kaydet")
        btn_kaydet.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; font-size: 16px; font-weight: bold; margin-top: 20px; border-radius: 5px;")
        btn_kaydet.clicked.connect(self.save_donation)
        layout.addWidget(btn_kaydet)
        
        layout.addStretch()

    def save_donation(self):
        cami_adi = self.cmb_cami.currentText()
        tarih = self.ent_tarih.text().strip()
        miktar_str = self.ent_miktar.text().strip()
        purpose = self.ent_purpose.text().strip()
        aciklama = self.ent_aciklama.text().strip()

        if not cami_adi or cami_adi == "Cami Bulunamadı":
            QMessageBox.warning(self, "Uyarı", "Lütfen bir cami seçiniz!")
            return
        if not tarih:
            QMessageBox.warning(self, "Uyarı", "Lütfen tarih giriniz!")
            return
        if not purpose:
            QMessageBox.warning(self, "Uyarı", "Lütfen yardımın toplanma yerini / amacını giriniz!")
            return
            
        try:
            # Tarih formatı kontrolü
            datetime.strptime(tarih, "%d-%m-%Y")
        except ValueError:
            QMessageBox.warning(self, "Uyarı", "Lütfen tarihi GG-AA-YYYY formatında giriniz (Örn: 26-08-2026)")
            return

        try:
            miktar = float(miktar_str.replace(",", "."))
        except ValueError:
            QMessageBox.warning(self, "Uyarı", "Geçerli bir miktar giriniz (Örn: 1500 veya 1500.50)")
            return

        mosque_id = self.mosques.get(cami_adi)
        if mosque_id:
            db_manager.add_donation(mosque_id, tarih, miktar, aciklama, purpose)
            QMessageBox.information(self, "Başarılı", "Yardım başarıyla kaydedildi.")
            self.ent_miktar.clear()
            self.ent_purpose.clear()
            self.ent_aciklama.clear()
        else:
            QMessageBox.critical(self, "Hata", "Seçilen cami bulunamadı.")

    # --- LİSTE SAYFASI ---
    def setup_liste_page(self):
        layout = QVBoxLayout(self.page_liste)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header_layout = QHBoxLayout()
        title = QLabel("Yardım Kayıtları")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Filtreleme (Tab Widget)
        self.filter_tabs = QTabWidget()
        self.filter_tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #bdc3c7; border-radius: 4px; }
            QTabBar::tab { background: #ecf0f1; padding: 6px 15px; margin-right: 2px; border-radius: 4px 4px 0 0; }
            QTabBar::tab:selected { background: #2980b9; color: white; font-weight: bold; }
            QCalendarWidget QWidget { color: black; }
            QCalendarWidget QToolButton { color: black; background-color: white; border-radius: 4px; }
            QCalendarWidget QMenu { color: black; }
            QCalendarWidget QSpinBox { color: black; }
            QCalendarWidget QAbstractItemView:enabled { color: black; background-color: white; selection-background-color: #2980b9; selection-color: white; }
            QCalendarWidget QAbstractItemView:disabled { color: gray; }
        """)
        
        # Hızlı Filtre Tab
        tab_hizli = QWidget()
        layout_hizli = QHBoxLayout(tab_hizli)
        layout_hizli.setContentsMargins(10, 10, 10, 10)
        layout_hizli.addWidget(QLabel("Hazır Filtreler:"))
        self.cmb_filtre = QComboBox()
        self.cmb_filtre.addItems(["Tümü", "Son 1 Hafta", "Son 1 Ay", "Son 3 Ay", "Son 1 Yıl"])
        self.cmb_filtre.setStyleSheet("padding: 5px; background-color: white; color: black;")
        layout_hizli.addWidget(self.cmb_filtre)
        layout_hizli.addStretch()
        
        btn_uygula_hizli = QPushButton("Filtrele")
        btn_uygula_hizli.setStyleSheet("background-color: #27ae60; color: white; padding: 6px 15px; font-weight: bold; border-radius: 4px;")
        btn_uygula_hizli.clicked.connect(self.refresh_liste)
        layout_hizli.addWidget(btn_uygula_hizli)
        
        # Özel Tarih Tab
        tab_ozel = QWidget()
        layout_ozel = QHBoxLayout(tab_ozel)
        layout_ozel.setContentsMargins(10, 10, 10, 10)
        
        layout_ozel.addWidget(QLabel("Başlangıç:"))
        self.date_baslangic = QDateEdit(calendarPopup=True)
        self.date_baslangic.setDisplayFormat("dd-MM-yyyy")
        self.date_baslangic.setDate(QDate.currentDate().addDays(-7))
        self.date_baslangic.setStyleSheet("padding: 5px; background-color: white; color: black;")
        layout_ozel.addWidget(self.date_baslangic)
        
        layout_ozel.addWidget(QLabel("Bitiş:"))
        self.date_bitis = QDateEdit(calendarPopup=True)
        self.date_bitis.setDisplayFormat("dd-MM-yyyy")
        self.date_bitis.setDate(QDate.currentDate())
        self.date_bitis.setStyleSheet("padding: 5px; background-color: white; color: black;")
        layout_ozel.addWidget(self.date_bitis)
        layout_ozel.addStretch()
        
        btn_uygula_ozel = QPushButton("Uygula")
        btn_uygula_ozel.setStyleSheet("background-color: #27ae60; color: white; padding: 6px 15px; font-weight: bold; border-radius: 4px;")
        btn_uygula_ozel.clicked.connect(self.refresh_liste)
        layout_ozel.addWidget(btn_uygula_ozel)
        
        self.filter_tabs.addTab(tab_hizli, "Hızlı Filtre")
        self.filter_tabs.addTab(tab_ozel, "Özel Tarih Aralığı")
        
        header_layout.addWidget(self.filter_tabs)
        
        btn_excel = QPushButton("Excel'e Aktar")
        btn_excel.setStyleSheet("background-color: #2980b9; color: white; padding: 8px 15px; font-weight: bold; border-radius: 4px; margin-left: 10px;")
        btn_excel.clicked.connect(self.export_excel)
        header_layout.addWidget(btn_excel)
        
        btn_temizle = QPushButton("Tümünü Temizle")
        btn_temizle.setStyleSheet("background-color: #c0392b; color: white; padding: 8px 15px; font-weight: bold; border-radius: 4px; margin-left: 10px;")
        btn_temizle.clicked.connect(self.clear_all_donations)
        header_layout.addWidget(btn_temizle)
        
        layout.addLayout(header_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Cami Adı", "Tarih", "Miktar (TL)", "Toplanma Yeri", "Açıklama", "İşlem"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("background-color: white;")
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)
        
        self.lbl_toplam = QLabel("TOPLAM YARDIM MİKTARI: 0.00 TL")
        self.lbl_toplam.setStyleSheet("font-size: 16px; font-weight: bold; color: #27ae60; margin-top: 5px; margin-bottom: 15px;")
        layout.addWidget(self.lbl_toplam)
        
        # --- Toplamayanlar Tablosu ---
        self.lbl_toplamayanlar = QLabel("Seçili Dönemde Yardım Toplamayan Camiler")
        self.lbl_toplamayanlar.setStyleSheet("font-size: 18px; font-weight: bold; color: #c0392b;")
        layout.addWidget(self.lbl_toplamayanlar)
        
        self.table_toplamayan = QTableWidget()
        self.table_toplamayan.setColumnCount(1)
        self.table_toplamayan.setHorizontalHeaderLabels(["Cami Adı"])
        self.table_toplamayan.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_toplamayan.setStyleSheet("background-color: #fdf2f0;")
        layout.addWidget(self.table_toplamayan)
        
        self.filtered_donations = []
        self.toplamayanlar_listesi = []

    def refresh_liste(self):
        donations = db_manager.get_donations_with_names()
        all_mosques = db_manager.get_all_mosques() # [(id, name), ...]
        
        active_tab = self.filter_tabs.currentIndex()
        if active_tab == 0:
            filtre = self.cmb_filtre.currentText()
        else:
            filtre = "Özel Tarih Aralığı"
            
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 1. Seçili filtreye göre yardımları filtrele
        filtered = []
        toplayan_camiler = set()
        toplam = 0.0

        for d in donations:
            cami_adi = d[1]
            tarih_str = d[2]
            miktar = d[3]
            try:
                d_date = datetime.strptime(tarih_str, "%d-%m-%Y")
                days_diff = (today - d_date).days
                
                if filtre == "Son 1 Hafta" and days_diff > 7:
                    continue
                elif filtre == "Son 1 Ay" and days_diff > 30:
                    continue
                elif filtre == "Son 3 Ay" and days_diff > 90:
                    continue
                elif filtre == "Son 1 Yıl" and days_diff > 365:
                    continue
                elif filtre == "Özel Tarih Aralığı":
                    # PyQt QDate objesini Python datetime objesine çevirelim
                    start_qdate = self.date_baslangic.date()
                    end_qdate = self.date_bitis.date()
                    
                    start_date = datetime(start_qdate.year(), start_qdate.month(), start_qdate.day())
                    end_date = datetime(end_qdate.year(), end_qdate.month(), end_qdate.day())
                    
                    # Eğer bağış tarihi başlangıç ve bitiş arasında değilse atla
                    if not (start_date <= d_date <= end_date):
                        continue
                
                filtered.append(d)
                toplayan_camiler.add(cami_adi)
                toplam += miktar
            except ValueError:
                # Tarih formatı bozuksa listeye dahil et
                filtered.append(d)
                toplayan_camiler.add(cami_adi)
                toplam += miktar
                
        self.filtered_donations = filtered
        
        # 2. Tablo 1'i Doldur (Yardım Kayıtları)
        self.table.setRowCount(len(filtered))
        for row_idx, d in enumerate(filtered):
            d_id, cami, tarih, miktar, aciklama, purpose = d
            
            # İşlem Butonları (Düzenle ve Sil)
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)
            btn_layout.setSpacing(5)
            
            btn_edit = QPushButton("✏️")
            btn_edit.setToolTip("Düzenle")
            btn_edit.setFixedSize(24, 24)
            btn_edit.setStyleSheet("background-color: #f39c12; color: white; border-radius: 3px; font-size: 12px;")
            btn_edit.clicked.connect(lambda checked, r=row_idx: self.edit_record(r))
            
            btn_delete = QPushButton("🗑️")
            btn_delete.setToolTip("Sil")
            btn_delete.setFixedSize(24, 24)
            btn_delete.setStyleSheet("background-color: #e74c3c; color: white; border-radius: 3px; font-size: 12px;")
            btn_delete.clicked.connect(lambda checked, r=row_idx: self.delete_record(r))
            
            btn_layout.addWidget(btn_edit)
            btn_layout.addWidget(btn_delete)
            btn_layout.addStretch()
            
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(d_id)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(cami))
            self.table.setItem(row_idx, 2, QTableWidgetItem(tarih))
            self.table.setItem(row_idx, 3, QTableWidgetItem(f"{miktar:.2f}"))
            self.table.setItem(row_idx, 4, QTableWidgetItem(purpose if purpose else ""))
            self.table.setItem(row_idx, 5, QTableWidgetItem(aciklama if aciklama else ""))
            
            self.table.setCellWidget(row_idx, 6, btn_widget)
            
        self.table.resizeColumnToContents(6)
            
        self.lbl_toplam.setText(f"TOPLAM YARDIM MİKTARI: {toplam:.2f} TL")
        
        # 3. Tablo 2'yi Doldur (Toplamayan Camiler)
        self.toplamayanlar_listesi = []
        for m_id, m_name in all_mosques:
            if m_name not in toplayan_camiler:
                self.toplamayanlar_listesi.append(m_name)
                
        self.table_toplamayan.setRowCount(len(self.toplamayanlar_listesi))
        for row_idx, m_name in enumerate(self.toplamayanlar_listesi):
            self.table_toplamayan.setItem(row_idx, 0, QTableWidgetItem(m_name))

    def delete_record(self, row_idx):
        if row_idx < 0 or row_idx >= self.table.rowCount():
            return
            
        record_id = int(self.table.item(row_idx, 0).text())
        cami_adi = self.table.item(row_idx, 1).text()
        miktar = self.table.item(row_idx, 3).text()
        
        cevap = QMessageBox.question(self, "Onay", f"{cami_adi} için eklenen {miktar} TL tutarındaki kaydı silmek istediğinize emin misiniz?", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if cevap == QMessageBox.StandardButton.Yes:
            db_manager.delete_donation(record_id)
            QMessageBox.information(self, "Başarılı", "Kayıt silindi.")
            self.refresh_liste()

    def clear_all_donations(self):
        if not self.filtered_donations:
            QMessageBox.information(self, "Bilgi", "Zaten silinecek bir kayıt yok.")
            return
            
        cevap = QMessageBox.question(self, "Onay", "Tüm yardım kayıtlarını (tüm yılları) tamamen silmek istediğinize emin misiniz?\nBu işlem geri alınamaz!",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if cevap == QMessageBox.StandardButton.Yes:
            db_manager.delete_all_donations()
            QMessageBox.information(self, "Başarılı", "Tüm kayıtlar silindi.")
            self.refresh_liste()

    def edit_record(self, row_idx):
        if row_idx < 0 or row_idx >= self.table.rowCount():
            return
            
        record_id = int(self.table.item(row_idx, 0).text())
        cami_adi = self.table.item(row_idx, 1).text()
        tarih_str = self.table.item(row_idx, 2).text()
        miktar = self.table.item(row_idx, 3).text()
        purpose = self.table.item(row_idx, 4).text()
        aciklama = self.table.item(row_idx, 5).text()
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Kaydı Düzenle")
        dialog.resize(400, 300)
        
        layout = QFormLayout(dialog)
        
        cmb_cami = QComboBox()
        cmb_cami.addItems(self.mosques.keys())
        cmb_cami.setCurrentText(cami_adi)
        layout.addRow("Cami Adı:", cmb_cami)
        
        date_edit = QDateEdit(calendarPopup=True)
        date_edit.setDisplayFormat("dd-MM-yyyy")
        date_edit.setDate(QDate.fromString(tarih_str, "dd-MM-yyyy"))
        layout.addRow("Tarih:", date_edit)
        
        ent_miktar = QLineEdit(miktar)
        layout.addRow("Miktar (TL):", ent_miktar)
        
        ent_purpose = QLineEdit(purpose)
        layout.addRow("Toplanma Yeri/Amacı:", ent_purpose)
        
        ent_aciklama = QTextEdit()
        ent_aciklama.setText(aciklama)
        ent_aciklama.setFixedHeight(60)
        layout.addRow("Açıklama:", ent_aciklama)
        
        btn_layout = QHBoxLayout()
        btn_kaydet = QPushButton("Kaydet")
        btn_iptal = QPushButton("İptal")
        btn_layout.addWidget(btn_kaydet)
        btn_layout.addWidget(btn_iptal)
        
        layout.addRow(btn_layout)
        
        def save_changes():
            yeni_cami = cmb_cami.currentText()
            yeni_tarih = date_edit.date().toString("dd-MM-yyyy")
            try:
                yeni_miktar = float(ent_miktar.text().replace(',', '.'))
            except ValueError:
                QMessageBox.critical(dialog, "Hata", "Geçerli bir miktar giriniz!")
                return
            yeni_aciklama = ent_aciklama.toPlainText()
            yeni_purpose = ent_purpose.text()
            
            cami_id = self.mosques[yeni_cami]
            db_manager.update_donation(record_id, cami_id, yeni_tarih, yeni_miktar, yeni_aciklama, yeni_purpose)
            QMessageBox.information(dialog, "Başarılı", "Kayıt güncellendi.")
            dialog.accept()
            self.refresh_liste()
            
        btn_kaydet.clicked.connect(save_changes)
        btn_iptal.clicked.connect(dialog.reject)
        
        dialog.exec()

    def export_excel(self):
        if not self.filtered_donations and not self.toplamayanlar_listesi:
            QMessageBox.information(self, "Bilgi", "Dışa aktarılacak kayıt yok.")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Excel Olarak Kaydet", 
            f"Yardimlar_{datetime.now().strftime('%Y%m%d')}.xlsx", 
            "Excel Files (*.xlsx)"
        )
        
        if filepath:
            try:
                # Toplayanlar (filtered_donations)
                df_data = []
                for d in self.filtered_donations:
                    df_data.append({
                        "Cami Adı": d[1],
                        "Tarih": d[2],
                        "Miktar (TL)": d[3],
                        "Toplanma Yeri / Amacı": d[5],
                        "Açıklama": d[4]
                    })
                df_toplayan = pd.DataFrame(df_data)
                
                # Toplamayanlar
                df_toplamayan_data = []
                for m_name in self.toplamayanlar_listesi:
                    df_toplamayan_data.append({
                        "Cami Adı": m_name
                    })
                df_toplamayan = pd.DataFrame(df_toplamayan_data)
                
                # Excel'e iki sayfa olarak yaz
                with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                    df_toplayan.to_excel(writer, sheet_name='Toplanan Yardımlar', index=False)
                    df_toplamayan.to_excel(writer, sheet_name='Toplamayan Camiler', index=False)
                    
                    from openpyxl.styles import Border, Side
                    thin_border = Border(left=Side(style='thin', color='000000'), 
                                         right=Side(style='thin', color='000000'), 
                                         top=Side(style='thin', color='000000'), 
                                         bottom=Side(style='thin', color='000000'))
                    
                    for sheet_name in ['Toplanan Yardımlar', 'Toplamayan Camiler']:
                        worksheet = writer.sheets[sheet_name]
                        for row in worksheet.iter_rows():
                            for cell in row:
                                cell.border = thin_border
                                
                        # Sütun genişliklerini ayarla
                        for col in worksheet.columns:
                            max_length = 0
                            column = col[0].column_letter
                            for cell in col:
                                try:
                                    if len(str(cell.value)) > max_length:
                                        max_length = len(str(cell.value))
                                except:
                                    pass
                            adjusted_width = (max_length + 2)
                            worksheet.column_dimensions[column].width = adjusted_width
                            
                QMessageBox.information(self, "Başarılı", f"Kayıtlar başarıyla kaydedildi:\n{filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Excel'e kaydedilirken hata oluştu:\n{e}")

    # --- AYARLAR SAYFASI ---
    def setup_ayarlar_page(self):
        layout = QVBoxLayout(self.page_ayarlar)
        layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("Cami Ekleme / Silme")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)
        
        add_layout = QHBoxLayout()
        add_layout.addWidget(QLabel("Yeni Cami Adı:"))
        self.ent_yeni_cami = QLineEdit()
        self.ent_yeni_cami.setStyleSheet("padding: 5px; background-color: white;")
        add_layout.addWidget(self.ent_yeni_cami)
        
        btn_ekle = QPushButton("Ekle")
        btn_ekle.setStyleSheet("background-color: #2980b9; color: white; padding: 5px 15px; border-radius: 4px;")
        btn_ekle.clicked.connect(self.add_mosque)
        add_layout.addWidget(btn_ekle)
        layout.addLayout(add_layout)
        
        layout.addSpacing(40)
        
        layout.addWidget(QLabel("Mevcut Camiler (Silmek için seçin):"))
        self.cmb_sil_cami = QComboBox()
        self.cmb_sil_cami.setStyleSheet("padding: 5px; background-color: white;")
        layout.addWidget(self.cmb_sil_cami)
        
        btn_sil = QPushButton("Seçili Camiyi Sil")
        btn_sil.setStyleSheet("background-color: #e74c3c; color: white; padding: 10px; margin-top: 10px; border-radius: 4px;")
        btn_sil.clicked.connect(self.delete_mosque)
        layout.addWidget(btn_sil)
        
        layout.addSpacing(20)
        
        lbl_toplu = QLabel("Toplu Cami Yükleme")
        lbl_toplu.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(lbl_toplu)
        
        toplu_layout = QHBoxLayout()
        btn_sablon = QPushButton("Şablon İndir")
        btn_sablon.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; border-radius: 4px;")
        btn_sablon.clicked.connect(self.download_template)
        
        btn_yukle = QPushButton("Excel'den Yükle")
        btn_yukle.setStyleSheet("background-color: #8e44ad; color: white; padding: 10px; border-radius: 4px;")
        btn_yukle.clicked.connect(self.upload_mosques)
        
        toplu_layout.addWidget(btn_sablon)
        toplu_layout.addWidget(btn_yukle)
        layout.addLayout(toplu_layout)
        
        layout.addStretch()

    def download_template(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Şablonu Kaydet", "Cami_Sablon.xlsx", "Excel Files (*.xlsx)")
        if filepath:
            try:
                df = pd.DataFrame({"Cami Adı": ["ÖRNEK CAMİ MH.C.", "BAŞKA BİR CAMİ MH.C."]})
                with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                    from openpyxl.styles import Border, Side
                    thin_border = Border(left=Side(style='thin', color='000000'), right=Side(style='thin', color='000000'), top=Side(style='thin', color='000000'), bottom=Side(style='thin', color='000000'))
                    ws = writer.sheets['Sheet1']
                    for row in ws.iter_rows():
                        for cell in row:
                            cell.border = thin_border
                    ws.column_dimensions['A'].width = 40
                QMessageBox.information(self, "Başarılı", "Şablon başarıyla kaydedildi.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Şablon kaydedilirken hata oluştu:\n{e}")

    def upload_mosques(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Excel Seç", "", "Excel Files (*.xlsx *.xls)")
        if filepath:
            try:
                df = pd.read_excel(filepath)
                if "Cami Adı" not in df.columns:
                    QMessageBox.warning(self, "Hata", "Excel dosyasında 'Cami Adı' sütunu bulunamadı!")
                    return
                
                added_count = 0
                for cami in df["Cami Adı"].dropna():
                    if db_manager.add_mosque(str(cami).strip()):
                        added_count += 1
                
                self.load_mosques()
                QMessageBox.information(self, "Başarılı", f"{added_count} adet cami eklendi.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Camiler yüklenirken hata oluştu:\n{e}")

    def add_mosque(self):
        cami_adi = self.ent_yeni_cami.text().strip()
        if not cami_adi:
            QMessageBox.warning(self, "Uyarı", "Cami adını giriniz.")
            return
        
        if db_manager.add_mosque(cami_adi):
            QMessageBox.information(self, "Başarılı", f"'{cami_adi}' eklendi.")
            self.ent_yeni_cami.clear()
            self.refresh_mosques()
        else:
            QMessageBox.critical(self, "Hata", "Bu isimde bir cami zaten mevcut.")

    def delete_mosque(self):
        cami_adi = self.cmb_sil_cami.currentText()
        if not cami_adi or cami_adi == "Cami Yok":
            return
        
        reply = QMessageBox.question(self, 'Onay', f"'{cami_adi}' silinsin mi?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            db_manager.delete_mosque(cami_adi)
            QMessageBox.information(self, "Silindi", "Cami silindi.")
            self.refresh_mosques()

    # --- YARDIMCI METOTLAR ---
    def refresh_mosques(self):
        mosques_db = db_manager.get_all_mosques()
        self.mosques = {name: m_id for m_id, name in mosques_db}
        
        names = list(self.mosques.keys())
        
        self.cmb_cami.clear()
        self.cmb_sil_cami.clear()
        
        if names:
            self.cmb_cami.addItems(names)
            self.cmb_sil_cami.addItems(names)
        else:
            self.cmb_cami.addItem("Cami Bulunamadı")
            self.cmb_sil_cami.addItem("Cami Yok")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
