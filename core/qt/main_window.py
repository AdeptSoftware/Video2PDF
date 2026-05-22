# main_window.py
from PyQt5.QtCore       import QSize
from PyQt5.QtWidgets    import QMainWindow, QGridLayout, QLabel, QLineEdit, QPushButton, QListWidget, QComboBox
from PyQt5.QtWidgets    import QWidget, QFileDialog, QSpinBox, QMessageBox
from pathlib            import Path
from PIL                import Image

import core.split_video
import ocrmypdf
import shutil
import cv2


ROTATE_MAP = {
    0: None,
    1: cv2.ROTATE_90_COUNTERCLOCKWISE,
    2: cv2.ROTATE_180,
    3: cv2.ROTATE_90_CLOCKWISE
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._output_frames     = Path("./output/")
        # Объявление элементов управления
        # Видео для преобразования
        self._lbl_input_video   = QLabel("Видео:")
        self._txt_input_video   = QLineEdit(self)
        self._btn_input_video   = QPushButton("🗀")
        # Параметры преобразования
        self._lbl_params        = QLabel("Параметры кадрирования:")
        self._lbl_frame_delay   = QLabel("Задержка, мс:")
        self._spn_frame_delay   = QSpinBox(self)
        self._lbl_frame_start   = QLabel("Начало, мс:")
        self._spn_frame_start   = QSpinBox(self)
        self._lbl_rotate        = QLabel("Поворот:")
        self._cbx_rotate        = QComboBox(self)
        self._lbl_rect          = QLabel("Обрезка:")
        self._spn_left          = QSpinBox(self)
        self._spn_top           = QSpinBox(self)
        self._spn_right         = QSpinBox(self)
        self._spn_bottom        = QSpinBox(self)
        self._btn_split_video   = QPushButton("Кадрировать")
        # Кадры
        self._lbl_frames        = QLabel("Кадры:")
        self._lst_frames        = QListWidget(self)
        # Завершающий этап
        self._btn_make_pdf      = QPushButton("PDF")
        self._btn_ocr_pdf       = QPushButton("OCR")

        # Настройка внешнего вида
        self._setup_window_settings()
        self._reset_user_interface()
        self._setup_callbacks()
        self._setup_layout()

    def _setup_window_settings(self):
        self.setWindowTitle("Конвертер mp4 в pdf")
        self.setFixedSize(QSize(1000, 600))

    def _setup_layout(self):
        widget = QWidget(self)
        self.setCentralWidget(widget)

        layout1 = QGridLayout()
        layout1.addWidget(self._lbl_input_video, 0, 0)
        layout1.addWidget(self._txt_input_video, 0, 1)
        layout1.addWidget(self._btn_input_video, 0, 2)
        layout1.setContentsMargins(0, 0, 0, 0)
        layout1.setSpacing(5)

        layout2 = QGridLayout()
        layout2.addWidget(self._lbl_frame_delay, 0, 0)
        layout2.addWidget(self._spn_frame_delay, 0, 1)
        layout2.addWidget(self._lbl_frame_start, 0, 2)
        layout2.addWidget(self._spn_frame_start, 0, 3)
        layout2.addWidget(self._lbl_rotate,      0, 4)
        layout2.addWidget(self._cbx_rotate,      0, 5)
        layout2.addWidget(self._lbl_rect,        0, 6)
        layout2.addWidget(self._spn_left,        0, 7)
        layout2.addWidget(self._spn_top,         0, 8)
        layout2.addWidget(self._spn_right,       0, 9)
        layout2.addWidget(self._spn_bottom,      0, 10)
        layout2.setContentsMargins(0, 5, 0, 0)
        layout2.setSpacing(5)

        layout3 = QGridLayout()
        layout3.addWidget(self._btn_make_pdf,    0, 0)
        layout3.addWidget(self._btn_ocr_pdf,     0, 1)
        layout3.setContentsMargins(0, 5, 0, 0)
        layout3.setSpacing(5)

        layout = QGridLayout(widget)
        layout.addLayout(layout1,                0, 0)
        layout.addWidget(self._lbl_params,       1, 0)
        layout.addLayout(layout2,                2, 0)
        layout.addWidget(self._btn_split_video,  3, 0)
        layout.addWidget(self._lbl_frames,       4, 0)
        layout.addWidget(self._lst_frames,       5, 0)
        layout.addLayout(layout3,                6, 0)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        self.setLayout(layout)

    def _reset_user_interface(self):
        self._txt_input_video.setDisabled(True)
        self._disable_frame_settings(True)
        self._disable_frame_list(True)
        self._disable_last_buttons(False)

        self._txt_input_video.setText("")
        self._txt_input_video.setPlaceholderText("Выберите файл для преобразования →")
        self._btn_input_video.setFixedWidth(50)

        self._spn_frame_delay.setSuffix(" ms")
        self._spn_frame_delay.setSingleStep(1)
        self._spn_frame_delay.setMaximum(60000)
        self._spn_frame_delay.setMinimum(0)
        self._spn_frame_delay.setValue(500)

        self._spn_frame_start.setValue(0)
        self._spn_frame_start.setMinimum(0)
        self._spn_frame_start.setMaximum(60000)

        self._spn_top.setMinimum(0)
        self._spn_left.setMinimum(0)
        self._spn_right.setMinimum(0)
        self._spn_bottom.setMinimum(0)

        self._spn_top.setValue(0)
        self._spn_left.setValue(0)
        self._spn_right.setValue(0)
        self._spn_bottom.setValue(0)

        self._cbx_rotate.addItems(["Без вращения", "90", "180", "270"])
        self._cbx_rotate.setCurrentIndex(0)

    def _disable_frame_settings(self, disable=True):
        self._lbl_frame_delay.setDisabled(disable)
        self._spn_frame_delay.setDisabled(disable)
        self._lbl_frame_start.setDisabled(disable)
        self._spn_frame_start.setDisabled(disable)
        self._lbl_rotate.setDisabled(disable)
        self._cbx_rotate.setDisabled(disable)
        self._lbl_rect.setDisabled(disable)
        self._spn_left.setDisabled(disable)
        self._spn_top.setDisabled(disable)
        self._spn_right.setDisabled(disable)
        self._spn_bottom.setDisabled(disable)
        self._btn_split_video.setDisabled(disable)

    def _disable_frame_list(self, disable=True):
        self._lst_frames.setDisabled(disable)

    def _disable_last_buttons(self, disable=True):
        self._btn_make_pdf.setDisabled(disable)
        self._btn_ocr_pdf.setDisabled(disable)

    def _setup_callbacks(self):
        self._btn_input_video.clicked.connect(self._on_btn_input_video_clicked)
        self._btn_split_video.clicked.connect(self._on_btn_split_video_clicked)
        self._btn_make_pdf.clicked.connect(self._on_btn_make_pdf_clicked)
        self._btn_ocr_pdf.clicked.connect(self._on_btn_ocr_pdf_clicked)

    def _on_btn_input_video_clicked(self):
        result = QFileDialog.getOpenFileName(self, "Открытие", "*", "*.mp4")
        if result:
            video = cv2.VideoCapture(result[0])
            if not video.isOpened():
                QMessageBox.warning(self, "Внимание", "Ошибка открытия видео. Возможно, повреждено!", QMessageBox.Ok)
                return

            w = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            t = int(video.get(cv2.CAP_PROP_FRAME_COUNT) / video.get(cv2.CAP_PROP_FPS)) * 1000
            video.release()

            self._txt_input_video.setText(result[0])
            self._disable_frame_settings(False)

            self._spn_frame_start.setMaximum(t)

            self._spn_top.setMaximum(h)
            self._spn_left.setMaximum(h)
            self._spn_right.setMaximum(w)
            self._spn_bottom.setMaximum(h)

            self._spn_top.setValue(0)
            self._spn_left.setValue(0)
            self._spn_right.setValue(w)
            self._spn_bottom.setValue(h)
            self._cbx_rotate.setCurrentIndex(0)

    def _on_btn_split_video_clicked(self):
        if self._split_video():
            self._lst_frames.clear()

    def _split_video(self):
        path = Path(self._txt_input_video.text())
        if not path.exists():
            QMessageBox.warning(self, "Внимание", "Видео удалено!", QMessageBox.Ok)
            return False

        video = cv2.VideoCapture(self._txt_input_video.text())
        if not video.isOpened():
            QMessageBox.warning(self, "Внимание", "Ошибка открытия видео. Возможно, повреждено!", QMessageBox.Ok)
            return False

        if self._output_frames.exists():
            shutil.rmtree(self._output_frames)
        self._output_frames.mkdir()

        rotate  = ROTATE_MAP.get(self._cbx_rotate.currentIndex())
        x1, y1  = self._spn_left.value(),  self._spn_top.value()
        x2, y2  = self._spn_right.value(), self._spn_bottom.value()
        delay   = self._spn_frame_delay.value()
        pos     = self._spn_frame_start.value()
        core.split_video.run(video, delay, pos, x1, x2, y1, y2, rotate)

        video.release()
        self._disable_last_buttons(False)
        return True

    def _on_btn_make_pdf_clicked(self):
        images = list(self._output_frames.glob("*.png"))
        if not images:
            QMessageBox.warning(self, "Внимание", "Изображений для преобразования не найдено!", QMessageBox.Ok)
            return

        lst = []
        for filename in images:
            img = Image.open(filename)
            if img.mode != "RGB":
                img = img.convert("RGB")
            lst.append(img)

        folder = self._output_frames
        lst[0].save(folder / "output.pdf", save_all=True, append_images=lst[1:])
        print(f"{folder / 'output.pdf'} создан!")


    def _on_btn_ocr_pdf_clicked(self):
        folder = self._output_frames
        ocrmypdf.ocr(folder / "output.pdf", folder / "output_ocr.pdf", language="rus", deskew=True, force_ocr=True)
        print(f"{folder / 'output_ocr.pdf'} создан!")


