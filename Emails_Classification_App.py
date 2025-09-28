import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QPushButton, QLabel, QComboBox
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from Translator import Translate_txt
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

# === PyQt6 App ===
class BertSentimentApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BERT Text Classification App")
        self.setGeometry(100, 100, 600, 400)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Text input
        self.text_input = QTextEdit(self)
        self.text_input.setPlaceholderText("Enter your text here...")
        layout.addWidget(self.text_input)

        # Example dropdown
        self.example_combo = QComboBox(self)
        self.example_combo.addItems([name for name, _ in example_reviews])
        self.example_combo.currentTextChanged.connect(self.load_example)
        layout.addWidget(self.example_combo)

        # Translate button
        self.translate_button = QPushButton("Translate Text", self)
        self.translate_button.clicked.connect(self.translate_text)
        layout.addWidget(self.translate_button)

        # Analyze button
        self.analyze_button = QPushButton("Classify Text", self)
        self.analyze_button.clicked.connect(self.analyze_text)
        layout.addWidget(self.analyze_button)

        # Result label
        self.result_label = QLabel("Result will appear here", self)
        layout.addWidget(self.result_label)

    def load_example(self, example_name):
        for name, text in example_reviews:
            if name == example_name:
                self.text_input.setText(text)
                break

    def translate_text(self):
        input_text = self.text_input.toPlainText().strip()
        text = Translate_txt(input_text)
        self.text_input.setText(text)

    def analyze_text(self):
        input_text = self.text_input.toPlainText().strip()
        if input_text:
            label, confidence = predict_with_bert(input_text)
            self.result_label.setText(f"Prediction: {label} (confidence {confidence:.2f})")
        else:
            self.result_label.setText("Please enter some text to analyze!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BertSentimentApp()
    window.show()
    sys.exit(app.exec())
