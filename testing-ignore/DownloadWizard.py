"""
This was a total failure ignore this file - Aidan (05/03/2023)
"""
import sys
import time
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QDialog,
    QProgressBar,
)
import pip


class DownloadWizard(QDialog):
    def __init__(self):
        super().__init__()

        self.downloading_label = QLabel("Downloading Python Libraries...")
        self.progress_bar = QProgressBar()

        # Create a cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)

        # Create a horizontal layout for the buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.cancel_button)

        # Create a vertical layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.downloading_label)
        main_layout.addWidget(self.progress_bar)
        main_layout.addLayout(button_layout)

        # Set the main layout for the dialog
        self.setLayout(main_layout)

        # Start the download
        self.download()

    def download(self):
        # Use pip to install the libraries
        self.progress_bar.setValue(0)
        time.sleep(1)
        pip.main(["install", "requests"])
        self.progress_bar.setValue(20)
        pip.main(["install", "logging"])
        self.progress_bar.setValue(40)
        pip.main(["install", "flask"])
        self.progress_bar.setValue(60)
        pip.main(["install", "geopy"])
        self.progress_bar.setValue(80)
        pip.main(["install", "datetime"])
        self.progress_bar.setValue(0)
        self.downloading_label.setText("Downloading...")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    wizard = DownloadWizard()
    wizard.show()
    sys.exit(app.exec_())
