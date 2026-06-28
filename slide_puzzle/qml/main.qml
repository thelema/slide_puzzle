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
    property bool solving: false
    property var solveMoves: []
    property int solveIndex: 0

    function trySlideShape(shapeId, direction) {
        return puzzle.slideShape(shapeId, direction);
    }

    // ── auto-solve player ─────────────────────────────────────────────
    Timer {
        id: solveTimer
        interval: 400
        repeat: false
        onTriggered: {
            if (solveIndex < solveMoves.length) {
                var m = solveMoves[solveIndex];
                puzzle.slideShape(m.shape_id, m.direction);
                solveIndex++;
                solveTimer.start();
            } else {
                solving = false;
            }
        }
    }

    // ── root ──────────────────────────────────────────────────────────
    Rectangle {
        anchors.fill: parent
        color: "#1a1a2e"

        Column {
            anchors.horizontalCenter: parent.horizontalCenter
            y: 20
            spacing: 14

            // ── Title & puzzle selector ──────────────────────────────
            Column {
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 8

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: "Slide Puzzle"
                    font.pixelSize: 26
                    font.bold: true
                    color: "#ffffff"
                }

                ComboBox {
                    id: puzzleSelector
                    anchors.horizontalCenter: parent.horizontalCenter
                    model: puzzle.puzzleNames
                    font.pixelSize: 14
                    font.bold: true
                    // Dark bg, light text for dropdown button
                    contentItem: Text {
                        text: puzzleSelector.displayText
                        color: "#ffffff"
                        font: puzzleSelector.font
                        verticalAlignment: Text.AlignVCenter
                        horizontalAlignment: Text.AlignLeft
                        leftPadding: 8
                    }
                    background: Rectangle {
                        radius: 6
                        color: "#0f3460"
                        border.color: "#1a5276"
                        implicitWidth: 160
                        implicitHeight: 32
                    }
                    // Dark popup menu items
                    delegate: ItemDelegate {
                        width: puzzleSelector.width
                        contentItem: Text {
                            text: modelData
                            color: "#ffffff"
                            font: puzzleSelector.font
                            verticalAlignment: Text.AlignVCenter
                            horizontalAlignment: Text.AlignLeft
                            leftPadding: 8
                        }
                        background: Rectangle {
                            color: puzzleSelector.highlightedIndex === index ? "#1a5276" : "#0f3460"
                        }
                    }
                    popup: Popup {
                        y: puzzleSelector.height + 2
                        width: puzzleSelector.width
                        padding: 0
                        contentItem: ListView {
                            clip: true
                            implicitHeight: contentHeight
                            model: puzzleSelector.delegateModel
                            currentIndex: puzzleSelector.highlightedIndex
                        }
                        background: Rectangle {
                            color: "#0f3460"
                            radius: 6
                            border.color: "#1a5276"
                        }
                    }

                    onActivated: {
                        puzzle.selectPuzzle(index);
                        solving = false;
                        solveTimer.stop();
                    }
                }
            }

            // ── Board wrapper (includes external drop zones) ─────────
            Item {
                id: boardWrapper
                anchors.horizontalCenter: parent.horizontalCenter
                width: puzzle.boardCols * cellSize + 28  // room for external windows
                height: puzzle.boardRows * cellSize + 28

                // ── Board frame ──────────────────────────────────────
                Rectangle {
                    id: boardFrame
                    x: 14; y: 14
                    width: puzzle.boardCols * cellSize
                    height: puzzle.boardRows * cellSize
                    color: "#16213e"
                    border.color: "#2a5a8a"
                    border.width: 3
                    clip: true

                    // Grid lines (lighter for better contrast)
                    Repeater {
                        model: puzzle.boardRows + 1
                        Rectangle {
                            y: index * cellSize - 1
                            width: boardFrame.width
                            height: 1; color: "#2a4a6a"
                        }
                    }
                    Repeater {
                        model: puzzle.boardCols + 1
                        Rectangle {
                            x: index * cellSize - 1
                            height: boardFrame.height
                            width: 1; color: "#2a4a6a"
                        }
                    }
                }

                // ── Windows as external drop zones ───────────────────
                Repeater {
                    model: puzzle.windows

                    Rectangle {
                        required property var modelData
                        property var w: modelData

                        readonly property real cx: w.edge === "left"   ? 0
                                                 : w.edge === "right"  ? boardWrapper.width - 20
                                                 : 14 + w.pos * cellSize + cellSize / 2 - 10
                        readonly property real cy: w.edge === "top"    ? 0
                                                 : w.edge === "bottom" ? boardWrapper.height - 20
                                                 : 14 + w.pos * cellSize + cellSize / 2 - 10

                        x: cx; y: cy
                        width: 20; height: 20; radius: 10
                        color: w.color
                        border.color: "#ffffff"
                        border.width: 2
                        // Arrow indicator pointing inward
                        Rectangle {
                            anchors.centerIn: parent
                            width: 8; height: 8; radius: 4
                            color: "#ffffff"
                            opacity: 0.6
                        }
                        // Glow ring
                        Rectangle {
                            anchors.centerIn: parent
                            width: 28; height: 28; radius: 14
                            color: "transparent"
                            border.color: w.color
                            border.width: 2
                            opacity: 0.4
                        }
                    }
                }

                // ── Shape cells – draggable ──────────────────────────
                Repeater {
                    id: shapesRepeater
                    model: puzzle.shapes

                    delegate: Item {
                        required property var modelData
                        property var shapeData: modelData

                        property rect bbox: {
                            var minR = 9999, minC = 9999, maxR = -1, maxC = -1;
                            for (var i = 0; i < shapeData.cells.length; i++) {
                                var c = shapeData.cells[i];
                                minR = Math.min(minR, c.row);
                                minC = Math.min(minC, c.col);
                                maxR = Math.max(maxR, c.row);
                                maxC = Math.max(maxC, c.col);
                            }
                            return Qt.rect(minC * cellSize, minR * cellSize,
                                           (maxC - minC + 1) * cellSize,
                                           (maxR - minR + 1) * cellSize);
                        }

                        // Position relative to boardWrapper, offset by boardFrame (14,14) + board padding
                        x: 14 + shapeData.col * cellSize + 2 + (dragItem.dragActive ? dragItem.dx : 0)
                        y: 14 + shapeData.row * cellSize + 2 + (dragItem.dragActive ? dragItem.dy : 0)
                        width: bbox.width
                        height: bbox.height

                        // Drop shadow
                        Rectangle {
                            anchors.fill: parent
                            anchors.leftMargin: 3; anchors.topMargin: 3
                            color: "#000000"
                            opacity: 0.25
                            radius: 6
                        }

                        // Individual cell rects
                        Repeater {
                            model: shapeData.cells

                            delegate: Rectangle {
                                required property var modelData
                                property var cell: modelData

                                x: cell.col * cellSize
                                y: cell.row * cellSize
                                width: cellSize - 4
                                height: cellSize - 4
                                radius: 6
                                color: shapeData.color
                                border.width: 1
                                readonly property var baseBorder: Qt.darker(shapeData.color, 1.3)
                                border.color: baseBorder

                                // Shape-id label – crisp rendering
                                Text {
                                    anchors.centerIn: parent
                                    text: shapeData.id
                                    color: "#ffffff"
                                    font.bold: true
                                    font.pixelSize: 18
                                    font.family: "sans-serif"
                                    style: Text.Raised
                                    styleColor: "#000000"
                                    visible: shapeData.cells.length === 1
                                    renderType: Text.NativeRendering
                                }
                            }
                        }

                        // Drag controller
                        MouseArea {
                            id: dragItem
                            property bool dragActive: false
                            property real startX: 0
                            property real startY: 0
                            property real dx: 0
                            property real dy: 0
                            anchors.fill: parent
                            cursorShape: Qt.OpenHandCursor
                            enabled: !solving
                            drag.filterChildren: true

                            onPressed: function(mouse) {
                                cursorShape = Qt.ClosedHandCursor;
                                dragActive = true;
                                startX = mouse.x;
                                startY = mouse.y;
                                dx = 0;
                                dy = 0;
                            }

                            onMouseXChanged: function(mouse) {
                                if (dragActive) {
                                    dx = mouse.x - startX;
                                    dy = mouse.y - startY;
                                }
                            }

                            onMouseYChanged: function(mouse) {
                                if (dragActive) {
                                    dx = mouse.x - startX;
                                    dy = mouse.y - startY;
                                }
                            }

                            onReleased: function(mouse) {
                                cursorShape = Qt.OpenHandCursor;
                                dragActive = false;
                                var threshold = cellSize * 0.35;
                                var dir = "";
                                if (Math.abs(dx) > Math.abs(dy)) {
                                    if (dx > threshold) dir = "right";
                                    else if (dx < -threshold) dir = "left";
                                } else {
                                    if (dy > threshold) dir = "down";
                                    else if (dy < -threshold) dir = "up";
                                }
                                dx = 0;
                                dy = 0;
                                if (dir !== "") {
                                    trySlideShape(shapeData.id, dir);
                                }
                            }
                        }
                    }
                }
            }

            // ── Status bar: stats left, buttons right ────────────────
            Rectangle {
                anchors.horizontalCenter: parent.horizontalCenter
                width: Math.max(boardWrapper.width, 340)
                height: 42
                radius: 8
                color: "#0f3460"
                border.color: "#1a5276"
                border.width: 1

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 16
                    anchors.rightMargin: 8
                    spacing: 0

                    // Stats group
                    Row {
                        Layout.alignment: Qt.AlignVCenter
                        spacing: 20

                        Text {
                            text: "Moves: " + puzzle.moves
                            font.pixelSize: 15
                            font.bold: true
                            color: "#c0d8f0"
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        Text {
                            text: "Removed: " + puzzle.removed.length
                            font.pixelSize: 15
                            font.bold: true
                            color: "#c0d8f0"
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }

                    Item { Layout.fillWidth: true; height: 1 }

                    // Buttons group (pushed to the right by the spacer)
                    Row {
                        Layout.alignment: Qt.AlignVCenter
                        spacing: 8

                        Button {
                            id: resetBtn
                            text: "Reset"
                            font.bold: true
                            font.pixelSize: 13
                            implicitWidth: 80
                            implicitHeight: 30

                            contentItem: Text {
                                text: resetBtn.text
                                color: "#ffffff"
                                font: resetBtn.font
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                            background: Rectangle {
                                radius: 6
                                color: resetBtn.down ? "#1a5276" : "#2980b9"
                                border.color: "#3498db"
                                border.width: 1
                            }

                            onClicked: {
                                puzzle.reset();
                                solving = false;
                                solveTimer.stop();
                            }
                        }

                        Button {
                            id: solveBtn
                            text: solving ? "Solving\u2026" : "Solve"
                            enabled: !solving
                            font.bold: true
                            font.pixelSize: 13
                            implicitWidth: 80
                            implicitHeight: 30

                            contentItem: Text {
                                text: solveBtn.text
                                color: "#ffffff"
                                font: solveBtn.font
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                            background: Rectangle {
                                radius: 6
                                color: solveBtn.down || !solveBtn.enabled ? "#1a6b3c" : "#27ae60"
                                border.color: "#2ecc71"
                                border.width: 1
                            }

                            onClicked: {
                                var solution = puzzle.solve();
                                if (solution.length > 0) {
                                    solveMoves = solution;
                                    solveIndex = 0;
                                    solving = true;
                                    puzzle.reset();
                                    solveTimer.start();
                                }
                            }
                        }
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
                        width: 26; height: 26; radius: 4
                        color: modelData.color
                        border.color: Qt.darker(modelData.color, 1.3)
                        border.width: 1
                    }
                }
            }

            // ── Win message ──────────────────────────────────────────
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "\u2B50 Puzzle Solved! \uD83C\uDF89"
                font.pixelSize: 22
                font.bold: true
                color: "#f1c40f"
                style: Text.Raised
                styleColor: "#000000"
                visible: puzzle.isWon
            }
        }
    }
}