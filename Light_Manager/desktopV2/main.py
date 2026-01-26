#-*- coding: utf-8 -*-
"""
الملف الرئيسي لتشغيل تطبيق منظومة المهندس 3.
"""

import sys
from PyQt5.QtWidgets import QApplication
from views.main_window import MainWindow
# from controllers.main_controller import MainController

def main():
    """
    الدالة الرئيسية لتشغيل التطبيق.
    """
    app = QApplication(sys.argv)
    main_window = MainWindow()
    # controller = MainController(main_window)
    main_window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
