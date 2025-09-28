import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QTextEdit, QPushButton, QLabel, QComboBox, 
                            QSpinBox, QLineEdit, QTabWidget, QProgressBar, 
                            QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
import torch
import pandas as pd
from transformers import BertTokenizer, BertForSequenceClassification
from Translator import Translate_txt
from email_crawler import EmailCrawler 

# === Init model BERT ===
MODEL_PATH = "./results/checkpoint-380"  
LABEL_NAMES = ['advertising', 'entertainment', 'friends', 'spam', 'study', 'work']

# Load model + tokenizer
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = BertForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()

# Example reviews
example_reviews = [
    ("Spam", """
    Subject: You Won a $1000 Gift Card!
    Body:
    Congratulations!
    You have been selected to receive a $1000 gift card. Click the link below to claim your prize now. Hurry, this offer expires in 24 hours!"""),
    ("Advertising", """
    Subject: Weekend Mega Sale - 50% Off!
    Body:
    Dear customer,
    Don't miss our huge weekend sale! Enjoy up to 50% off on all electronics and home appliances. Visit our store today to grab the best deals before they're gone!"""),
    ("Entertainment", """
    Subject: New Action Movie Premiere
    Body:
    Hi there,
    The most anticipated action movie of the year is releasing this Friday! Book your tickets now and enjoy thrilling stunts and breathtaking visuals on the big screen."""),
    ("Friends", """
    Subject: Coffee Catch-Up This Weekend
    Body:
    Hey buddy,
    It's been a while! Want to grab coffee this weekend and catch up? Let me know which day works best for you. Looking forward to it!"""),
    ("Study", """
    Subject: Final Exam Schedule Posted
    Body:
    Dear students,
    The final exam timetable has been published on the school portal. Please review your exam dates carefully and prepare accordingly. Good luck!"""),
    ("Work", """
    Subject: Project Meeting Tomorrow at 9 AM
    Body:
    Hello team,
    This is a reminder that our project meeting will take place tomorrow at 9 AM in the main conference room. Please be ready to present your progress and next steps."""),
]

# Hàm dự đoán sentiment bằng BERT
def predict_with_bert(text: str):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=-1)
        pred_id = torch.argmax(probs, dim=-1).item()
    return LABEL_NAMES[pred_id], probs[0][pred_id].item()

# Email Crawler Worker Thread
class EmailCrawlerWorker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(pd.DataFrame)
    error = pyqtSignal(str)
    
    def __init__(self, num_emails, translate, credentials_file="credentials.json"):
        super().__init__()
        self.num_emails = num_emails
        self.translate = translate
        self.credentials_file = credentials_file
    
    def run(self):
        try:
            self.progress.emit("Initializing email crawler...")
            crawler = EmailCrawler(credentials_file=self.credentials_file)
            
            self.progress.emit("Authenticating with Gmail...")
            crawler.authenticate()
            
            self.progress.emit(f"Crawling {self.num_emails} emails...")
            df = crawler.crawl_emails(max_results=self.num_emails, translate=self.translate)
            
            if not df.empty:
                self.progress.emit(f"Successfully crawled {len(df)} emails")
                self.finished.emit(df)
            else:
                self.error.emit("No emails found or error occurred during crawling")
                
        except Exception as e:
            self.error.emit(f"Error during email crawling: {str(e)}")

# === PyQt6 App ===
class BertSentimentApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Email Classification App with BERT")
        self.setGeometry(100, 100, 1000, 700)
        
        self.crawler_worker = None
        self.crawled_data = None

        # Create main widget and tabs
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Tab 1: Single Text Classification
        self.create_single_text_tab()
        
        # Tab 2: Email Crawler
        self.create_email_crawler_tab()
        
        # Tab 3: Batch Results
        self.create_results_tab()

    def create_single_text_tab(self):
        """Tab for single text classification"""
        tab1 = QWidget()
        self.tabs.addTab(tab1, "Single Text Classification")
        layout = QVBoxLayout(tab1)

        # Text input
        self.text_input = QTextEdit(self)
        self.text_input.setPlaceholderText("Enter your email text here...")
        layout.addWidget(self.text_input)

        # Example dropdown
        example_label = QLabel("Load Example:")
        layout.addWidget(example_label)
        
        self.example_combo = QComboBox(self)
        self.example_combo.addItems([name for name, _ in example_reviews])
        self.example_combo.currentTextChanged.connect(self.load_example)
        layout.addWidget(self.example_combo)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Translate button
        self.translate_button = QPushButton("Translate to English", self)
        self.translate_button.clicked.connect(self.translate_text)
        buttons_layout.addWidget(self.translate_button)

        # Analyze button
        self.analyze_button = QPushButton("Classify Text", self)
        self.analyze_button.clicked.connect(self.analyze_text)
        buttons_layout.addWidget(self.analyze_button)
        
        layout.addLayout(buttons_layout)

        # Result label
        self.result_label = QLabel("Result will appear here", self)
        self.result_label.setStyleSheet("QLabel { padding: 10px; border: 1px solid gray; }")
        layout.addWidget(self.result_label)

    def create_email_crawler_tab(self):
        """Tab for email crawling functionality"""
        tab2 = QWidget()
        self.tabs.addTab(tab2, "Email Crawler")
        layout = QVBoxLayout(tab2)

        # Credentials section
        cred_label = QLabel("Gmail API Setup:")
        cred_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(cred_label)
        
        # Credentials file path
        cred_layout = QHBoxLayout()
        self.cred_path_input = QLineEdit("credentials.json")
        self.cred_browse_button = QPushButton("Browse")
        self.cred_browse_button.clicked.connect(self.browse_credentials)
        cred_layout.addWidget(QLabel("Credentials File:"))
        cred_layout.addWidget(self.cred_path_input)
        cred_layout.addWidget(self.cred_browse_button)
        layout.addLayout(cred_layout)

        # Number of emails
        email_count_layout = QHBoxLayout()
        email_count_layout.addWidget(QLabel("Number of emails to crawl:"))
        self.email_count_spinbox = QSpinBox()
        self.email_count_spinbox.setMinimum(1)
        self.email_count_spinbox.setMaximum(100)
        self.email_count_spinbox.setValue(30)
        email_count_layout.addWidget(self.email_count_spinbox)
        email_count_layout.addStretch()
        layout.addLayout(email_count_layout)

        # Translation option
        self.translate_checkbox = QComboBox()
        self.translate_checkbox.addItems(["Translate to English", "Keep Original Language"])
        translate_layout = QHBoxLayout()
        translate_layout.addWidget(QLabel("Translation:"))
        translate_layout.addWidget(self.translate_checkbox)
        translate_layout.addStretch()
        layout.addLayout(translate_layout)

        # Crawl button
        self.crawl_button = QPushButton("Start Crawling Emails")
        self.crawl_button.clicked.connect(self.start_email_crawling)
        layout.addWidget(self.crawl_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Ready to crawl emails")
        layout.addWidget(self.status_label)

        # Export buttons
        export_layout = QHBoxLayout()
        self.export_csv_button = QPushButton("Export to CSV")
        self.export_csv_button.clicked.connect(self.export_to_csv)
        self.export_csv_button.setEnabled(False)
        
        self.classify_all_button = QPushButton("Classify All Emails")
        self.classify_all_button.clicked.connect(self.classify_all_emails)
        self.classify_all_button.setEnabled(False)
        
        export_layout.addWidget(self.export_csv_button)
        export_layout.addWidget(self.classify_all_button)
        layout.addLayout(export_layout)

    def create_results_tab(self):
        """Tab for displaying batch results"""
        tab3 = QWidget()
        self.tabs.addTab(tab3, "Results")
        layout = QVBoxLayout(tab3)

        # Results table
        self.results_table = QTableWidget()
        layout.addWidget(self.results_table)

        # Summary label
        self.summary_label = QLabel("No data to display")
        layout.addWidget(self.summary_label)

    def load_example(self, example_name):
        """Load example text"""
        for name, text in example_reviews:
            if name == example_name:
                self.text_input.setText(text)
                break

    def browse_credentials(self):
        """Browse for credentials file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Credentials File", "", "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            self.cred_path_input.setText(file_path)

    def start_email_crawling(self):
        """Start the email crawling process"""
        num_emails = self.email_count_spinbox.value()
        translate = self.translate_checkbox.currentText() == "Translate to English"
        credentials_file = self.cred_path_input.text()
        
        if not os.path.exists(credentials_file):
            QMessageBox.warning(self, "Warning", f"Credentials file not found: {credentials_file}")
            return
        
        self.crawl_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Start worker thread
        self.crawler_worker = EmailCrawlerWorker(num_emails, translate, credentials_file)
        self.crawler_worker.progress.connect(self.update_crawling_status)
        self.crawler_worker.finished.connect(self.on_crawling_finished)
        self.crawler_worker.error.connect(self.on_crawling_error)
        self.crawler_worker.start()

    def update_crawling_status(self, message):
        """Update crawling status"""
        self.status_label.setText(message)

    def on_crawling_finished(self, df):
        """Handle successful crawling completion"""
        self.crawled_data = df
        self.crawl_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.export_csv_button.setEnabled(True)
        self.classify_all_button.setEnabled(True)
        
        self.status_label.setText(f"Successfully crawled {len(df)} emails")
        self.update_results_table()
        self.tabs.setCurrentIndex(2)  # Switch to results tab

    def on_crawling_error(self, error_message):
        """Handle crawling errors"""
        self.crawl_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Crawling failed")
        QMessageBox.critical(self, "Error", error_message)

    def update_results_table(self):
        """Update the results table with crawled data"""
        if self.crawled_data is None or self.crawled_data.empty:
            return
        
        df = self.crawled_data
        self.results_table.setRowCount(len(df))
        self.results_table.setColumnCount(len(df.columns))
        self.results_table.setHorizontalHeaderLabels(df.columns.tolist())
        
        for i in range(len(df)):
            for j in range(len(df.columns)):
                item = QTableWidgetItem(str(df.iloc[i, j]))
                self.results_table.setItem(i, j, item)
        
        self.results_table.resizeColumnsToContents()
        self.summary_label.setText(f"Displaying {len(df)} emails")

    def classify_all_emails(self):
        """Classify all crawled emails"""
        if self.crawled_data is None or self.crawled_data.empty:
            QMessageBox.warning(self, "Warning", "No crawled data to classify")
            return
        
        self.classify_all_button.setEnabled(False)
        self.status_label.setText("Classifying emails...")
        
        # Use translated content if available, otherwise original content
        text_column = 'content_en' if 'content_en' in self.crawled_data.columns else 'content'
        
        predictions = []
        confidences = []
        
        for i, row in self.crawled_data.iterrows():
            text = str(row[text_column])
            if text and text.strip():
                label, confidence = predict_with_bert(text)
                predictions.append(label)
                confidences.append(confidence)
            else:
                predictions.append('unknown')
                confidences.append(0.0)
        
        self.crawled_data['predicted_label'] = predictions
        self.crawled_data['confidence'] = confidences
        
        self.update_results_table()
        self.classify_all_button.setEnabled(True)
        self.status_label.setText(f"Classification completed for {len(predictions)} emails")

    def export_to_csv(self):
        """Export crawled data to CSV"""
        if self.crawled_data is None or self.crawled_data.empty:
            QMessageBox.warning(self, "Warning", "No data to export")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save CSV File", "crawled_emails.csv", "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            try:
                self.crawled_data.to_csv(file_path, index=False, encoding='utf-8')
                QMessageBox.information(self, "Success", f"Data exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export data: {str(e)}")

    def translate_text(self):
        """Translate text in the input field"""
        input_text = self.text_input.toPlainText().strip()
        if not input_text:
            QMessageBox.warning(self, "Warning", "Please enter some text to translate")
            return
        
        try:
            self.translate_button.setEnabled(False)
            self.translate_button.setText("Translating...")
            
            translated_text = Translate_txt(input_text)
            self.text_input.setText(translated_text)
            
        except Exception as e:
            QMessageBox.critical(self, "Translation Error", f"Failed to translate text: {str(e)}")
        finally:
            self.translate_button.setEnabled(True)
            self.translate_button.setText("Translate to English")

    def analyze_text(self):
        """Analyze single text"""
        input_text = self.text_input.toPlainText().strip()
        if input_text:
            try:
                label, confidence = predict_with_bert(input_text)
                result_text = f"<b>Prediction:</b> {label}<br><b>Confidence:</b> {confidence:.3f}"
                self.result_label.setText(result_text)
            except Exception as e:
                QMessageBox.critical(self, "Classification Error", f"Failed to classify text: {str(e)}")
        else:
            self.result_label.setText("Please enter some text to analyze!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BertSentimentApp()
    window.show()
    sys.exit(app.exec())
