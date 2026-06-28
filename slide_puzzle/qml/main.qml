import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import SlidePuzzle 1.0

ApplicationWindow {
    visible: true
    width: 640
    height: 780
    minimumWidth: 480
    minimumHeight: 620
    title: "Slide Puzzle — Shape Exit"

    PuzzleAdapter { id: puzzle }

    // ── state ─────────────────────────────────────────────────────────
    property int cellSize: 72
    property int selectedShapeId: -1
    property var legalDirs: []

    function selectShape(shapeId) {
        if (selectedShapeId === shapeId) {
            selectedShapeId = -1;
            legalDirs = [];
        } else {
            selectedShapeId = shapeId;
            legalDirs = puzzle.legalMovesFor(shapeId);
        }
    }

    // ── root ──────────────────────────────────────────────────────────
    Rectangle {
        anchors.fill: parent
        color: "#1a1a2e"

        Column {
            anchors.horizontalCenter: parent.horizontalCenter
            y: 24
            spacing: 16

            // Header row
            Row {
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 14
                layoutDirection: Qt.LeftToRight

                Text {
                    text: "Slide Puzzle"
                    font.pixelSize: 24
                    font.bold: true
                    color: "#e0e0e0"
                    anchors.verticalCenter: parent.verticalCenter
                }

                ComboBox {
                    id: puzzleSelector
                    model: puzzle.puzzleNames
                    font.pixelSize: 14
                    anchors.verticalCenter: parent.verticalCenter
                    onActivated: {
                        puzzle.selectPuzzle(index);
                        selectedShapeId = -1;
                        legalDirs = [];
                    }
                }
            }

            // ── Board ─────────────────────────────────────────────────
            Rectangle {
                id: boardFrame
                anchors.horizontalCenter: parent.horizontalCenter
                width: puzzle.boardCols * cellSize
                height: puzzle.boardRows * cellSize
                color: "#16213e"
                border.color: "#0f3460"
                border.width: 2
                clip: false

                // Grid background
                Repeater {
                    model: puzzle.boardRows
                    Rectangle {
                        y: index * cellSize
                        width: boardFrame.width
                        height: 1; color: "#1a2744"
                    }
                }
                Repeater {
                    model: puzzle.boardCols
                    Rectangle {
                        x: index * cellSize
                        height: boardFrame.height
                        width: 1; color: "#1a2744"
                    }
                }

                // Windows (edge exit markers)
                Repeater {
                    model: puzzle.windows
                    Rectangle {
                        required property var modelData
                        property var w: modelData

                        x: w.edge === "left"   ? -10
                         : w.edge === "right"  ? boardFrame.width - 6
                         : w.pos * cellSize + cellSize / 2 - 8
                        y: w.edge === "top"    ? -10
                         : w.edge === "bottom" ? boardFrame.height - 6
                         : w.pos * cellSize + cellSize / 2 - 8
                        width: 20
                        height: 20
                        radius: 10
                        color: w.color
                        border.color: "#ffffff"
                        border.width: 2
                    }
                }

                // Shape cells
                Repeater {
                    model: puzzle.shapes

                    delegate: Item {
                        required property var modelData
                        property var shapeData: modelData

                        Repeater {
                            model: shapeData.cells

                            delegate: Rectangle {
                                required property var modelData
                                property var cell: modelData

                                x: (shapeData.col + cell.col) * cellSize + 2
                                y: (shapeData.row + cell.row) * cellSize + 2
                                width: cellSize - 4
                                height: cellSize - 4
                                radius: 5
                                color: shapeData.color
                                border.width: selectedShapeId === shapeData.id ? 3 : 1

                                // darker border when not selected, white when selected
                                readonly property var baseBorder: Qt.darker(shapeData.color, 1.3)
                                border.color: selectedShapeId === shapeData.id ? "#ffffff" : baseBorder

                                // Shape-id label on single-cell shapes
                                Text {
                                    anchors.centerIn: parent
                                    text: shapeData.id
                                    color: "#ffffff"
                                    font.bold: true
                                    font.pixelSize: 16
                                    visible: shapeData.cells.length === 1
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: selectShape(shapeData.id)
                                }
                            }
                        }
                    }
                }
            }

            // ── Direction pad ─────────────────────────────────────────
            Rectangle {
                id: dirPad
                visible: selectedShapeId >= 0 && legalDirs.length > 0
                anchors.horizontalCenter: parent.horizontalCenter
                width: 170
                height: 130
                radius: 10
                color: "#0f3460"
                border.color: "#1a5276"
                border.width: 1

                Column {
                    anchors.centerIn: parent
                    spacing: 4

                    Row {
                        anchors.horizontalCenter: parent.horizontalCenter
                        spacing: 4
                        Item { width: 44; height: 44 }
                        DirButton {
                            dir: "up"; symbol: "\u25B2"
                            enabled: legalDirs.indexOf("up") >= 0
                            onSlide: { puzzle.slideShape(selectedShapeId, "up"); clearSel(); }
                        }
                        Item { width: 44; height: 44 }
                    }
                    Row {
                        anchors.horizontalCenter: parent.horizontalCenter
                        spacing: 4
                        DirButton {
                            dir: "left"; symbol: "\u25C0"
                            enabled: legalDirs.indexOf("left") >= 0
                            onSlide: { puzzle.slideShape(selectedShapeId, "left"); clearSel(); }
                        }
                        DirButton {
                            dir: "center"; symbol: "\u2716"
                            enabled: true
                            onSlide: clearSel()
                        }
                        DirButton {
                            dir: "right"; symbol: "\u25B6"
                            enabled: legalDirs.indexOf("right") >= 0
                            onSlide: { puzzle.slideShape(selectedShapeId, "right"); clearSel(); }
                        }
                    }
                    Row {
                        anchors.horizontalCenter: parent.horizontalCenter
                        spacing: 4
                        Item { width: 44; height: 44 }
                        DirButton {
                            dir: "down"; symbol: "\u25BC"
                            enabled: legalDirs.indexOf("down") >= 0
                            onSlide: { puzzle.slideShape(selectedShapeId, "down"); clearSel(); }
                        }
                        Item { width: 44; height: 44 }
                    }
                }
            }

            // ── Status ────────────────────────────────────────────────
            Row {
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 20

                Text {
                    text: "Moves: " + puzzle.moves
                    font.pixelSize: 16
                    color: "#a0a0a0"
                    anchors.verticalCenter: parent.verticalCenter
                }

                Text {
                    text: "Removed: " + puzzle.removed.length
                    font.pixelSize: 16
                    color: "#a0a0a0"
                    anchors.verticalCenter: parent.verticalCenter
                }

                Button {
                    text: "Reset"
                    onClicked: {
                        puzzle.reset();
                        selectedShapeId = -1;
                        legalDirs = [];
                    }
                }
            }

            // ── Removed shapes ────────────────────────────────────────
            Row {
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 8
                visible: puzzle.removed.length > 0

                Repeater {
                    model: puzzle.removed
                    Rectangle {
                        required property var modelData
                        width: 28; height: 28; radius: 4
                        color: modelData.color
                        border.color: Qt.darker(modelData.color, 1.3)
                        border.width: 1
                    }
                }
            }

            // ── Win message ──────────────────────────────────────────
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "\u2B50 Puzzle Solved! \u2B50"
                font.pixelSize: 22
                font.bold: true
                color: "#f1c40f"
                visible: puzzle.isWon
            }
        }
    }

    // ── helpers ──────────────────────────────────────────────────────
    function clearSel() {
        selectedShapeId = -1;
        legalDirs = [];
    }

    // ── D-pad button component ───────────────────────────────────────
    component DirButton: Rectangle {
        id: btn
        property string dir: ""
        property string symbol: ""
        signal slide()

        width: 44; height: 44; radius: 6
        color: enabled ? "#1a5276" : "#0d2137"
        border.color: enabled ? "#2980b9" : "#1a2744"
        border.width: 1

        Text {
            anchors.centerIn: parent
            text: btn.symbol
            font.pixelSize: 20
            color: btn.enabled ? "#ffffff" : "#555555"
        }

        MouseArea {
            anchors.fill: parent
            enabled: btn.enabled
            cursorShape: Qt.PointingHandCursor
            onClicked: btn.slide()
        }
    }
}