from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType

from slide_puzzle.qmladapter import PuzzleAdapter


def main() -> int:
    app = QGuiApplication(sys.argv)
    qmlRegisterType(PuzzleAdapter, "SlidePuzzle", 1, 0, "PuzzleAdapter")

    engine = QQmlApplicationEngine()
    qml_path = Path(__file__).resolve().parent / "slide_puzzle" / "qml" / "main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_path)))
    if not engine.rootObjects():
        return -1
    return app.exec()


if __name__ == "__main__":
    main()
