from PyQt5.Qt               import QApplication
from core.qt.main_window    import MainWindow

import sys


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()

# Для работы требуется установить:
# 1) Tesseract-OCR (+ докачать через установщик: cyrillic, Russian)
# 2) GhostScript
# 3) Прописать пути до папок в переменные среды