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
        var ok = puzzle.slideShape(shapeId, direction);
        if (ok) {
            // update legal dirs for the moved shape if still selected
        }
        return ok;
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
                        solving = false;
                        solveTimer.stop();
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
                clip: true

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

                // Shape cells – draggable
                Repeater {
                    id: shapesRepeater
                    model: puzzle.shapes

                    delegate: Item {
                        required property var modelData
                        property var shapeData: modelData
                        // bounding box of all cells for the drag area
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

                        x: shapeData.col * cellSize + 2 + (dragItem.dragActive ? dragItem.dx : 0)
                        y: shapeData.row * cellSize + 2 + (dragItem.dragActive ? dragItem.dy : 0)
                        width: bbox.width
                        height: bbox.height

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
                                radius: 5
                                color: shapeData.color
                                border.width: 1
                                readonly property var baseBorder: Qt.darker(shapeData.color, 1.3)
                                border.color: baseBorder

                                Text {
                                    anchors.centerIn: parent
                                    text: shapeData.id
                                    color: "#ffffff"
                                    font.bold: true
                                    font.pixelSize: 16
                                    visible: shapeData.cells.length === 1
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
                                // Reset visual offset immediately
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
                        solving = false;
                        solveTimer.stop();
                    }
                }

                Button {
                    text: solving ? "Solving..." : "Solve"
                    enabled: !solving
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
}