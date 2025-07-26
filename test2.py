import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QScrollArea, QGridLayout, QComboBox
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from PIL import Image
import sys

def pil2pixmap(im):
    im = im.convert("RGBA")
    data = im.tobytes("raw", "RGBA")
    qimg = QImage(data, im.width, im.height, QImage.Format_RGBA8888)
    return QPixmap.fromImage(qimg)



SUPPORTED_FORMATS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')

class ImageBox(QWidget):
    def __init__(self, img_path, visibility_callback=None):
        super().__init__()
        self.img_path = img_path
        self.hidden = False
        self.visibility_callback = visibility_callback

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Load and resize image
        pil_img = Image.open(img_path)
        pil_img.thumbnail((150, 150))

        # Convert PIL image to QPixmap without saving to disk
        
        pixmap = pil2pixmap(pil_img)

        self.img_label = QLabel()
        self.img_label.setPixmap(pixmap)
        self.img_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.img_label)

        # Name label
        name = os.path.splitext(os.path.basename(img_path))[0]
        self.name_label = QLabel(name)
        self.name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.name_label)

        # Hide button
        self.toggle_btn = QPushButton("Hide")
        self.toggle_btn.clicked.connect(self.toggle_visibility)
        layout.addWidget(self.toggle_btn)

    def toggle_visibility(self):
        self.hidden = not self.hidden
        self.img_label.setVisible(not self.hidden)
        self.toggle_btn.setText("Unhide" if self.hidden else "Hide")
        if self.visibility_callback:
            self.visibility_callback()


    def unhide(self):
        if self.hidden:
            self.hidden = False
            self.img_label.setVisible(True)
            self.toggle_btn.setText("Hide")
        if self.visibility_callback:
            self.visibility_callback()


class ImageOrganizerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Organizer")
        self.setStyleSheet("""
            QWidget {
                background-color: #1B1F29;
                color: #E0E6ED;
                font-family: "Segoe UI", sans-serif;
                font-size: 10pt;
            }

            QPushButton {
                background-color: #2C3E50;
                color: #E0E6ED;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }

            QPushButton:hover {
                background-color: #34495E;
            }

            QPushButton:pressed {
                background-color: #1A252F;
            }

            QComboBox {
                background-color: #2C3E50;
                color: #E0E6ED;
                border: 1px solid #00ADB5;
                padding: 4px;
                border-radius: 4px;
            }

            QComboBox QAbstractItemView {
                background-color: #1F2A36;
                selection-background-color: #00ADB5;
                selection-color: white;
                border: none;
            }

            QLabel {
                color: #E0E6ED;
            }

            QScrollArea {
                background-color: #1B1F29;
            }

            QScrollBar:vertical {
                background: #2C3E50;
                width: 10px;
            }

            QScrollBar::handle:vertical {
                background: #00ADB5;
                border-radius: 5px;
                min-height: 20px;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
                background: none;
            }
        """)


        self.resize(800, 600)

        self.image_boxes = []

        # Layouts
        main_layout = QVBoxLayout(self)
        control_layout = QHBoxLayout()
        self.grid_layout = QGridLayout()

        # Top control buttons
        add_btn = QPushButton("Add Folder")
        add_btn.clicked.connect(self.add_folder)
        control_layout.addWidget(add_btn)

        unhide_all_btn = QPushButton("Unhide All")
        unhide_all_btn.clicked.connect(self.unhide_all_images)
        control_layout.addWidget(unhide_all_btn)

        control_layout.addSpacing(20)
        control_layout.addWidget(QLabel("Choosing:"))

        self.dropdown = QComboBox()
        self.dropdown.addItem("Select Image")
        control_layout.addWidget(self.dropdown)

        main_layout.addLayout(control_layout)

        # Scroll area
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_widget.setLayout(self.grid_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            for filename in os.listdir(folder):
                if filename.lower().endswith(SUPPORTED_FORMATS):
                    full_path = os.path.join(folder, filename)
                    box = ImageBox(full_path, visibility_callback=self.refresh_dropdown)
                    self.image_boxes.append(box)

            self.refresh_grid()

    def refresh_grid(self):
        # Clear previous layout
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        self.refresh_dropdown()


        cols = 4
        for i, box in enumerate(self.image_boxes):
            row, col = divmod(i, cols)
            self.grid_layout.addWidget(box, row, col)
            if not box.hidden:
                name = os.path.splitext(os.path.basename(box.img_path))[0]
                self.dropdown.addItem(name)

    def unhide_all_images(self):
        for box in self.image_boxes:
            box.unhide()
        self.refresh_grid()
    def refresh_dropdown(self):
        self.dropdown.clear()
        self.dropdown.addItem("Select Image")
        for box in self.image_boxes:
            if not box.hidden:
                name = os.path.splitext(os.path.basename(box.img_path))[0]
                self.dropdown.addItem(name)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageOrganizerApp()
    window.show()
    sys.exit(app.exec_())
