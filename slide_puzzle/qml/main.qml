import QtQuick 2.15
import QtQuick.Controls 2.15
import SlidePuzzle 1.0

ApplicationWindow {
    visible: true
    width: 480
    height: 640
    title: "Slide Puzzle"

    PuzzleAdapter {
        id: puzzle
        size: 3
        board: [1, 2, 3, 4, 5, 6, 7, 8, 0]
    }

    Rectangle {
        anchors.fill: parent
        color: "#f5f5f5"

        Column {
            anchors.horizontalCenter: parent.horizontalCenter
            y: 40
            spacing: 16

            Text {
                text: "Slide Puzzle"
                font.pixelSize: 24
                font.bold: true
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Grid {
                id: boardGrid
                columns: puzzle.size
                rows: puzzle.size
                spacing: 4
                anchors.horizontalCenter: parent.horizontalCenter

                Repeater {
                    model: puzzle.size * puzzle.size

                    Rectangle {
                        width: 80
                        height: 80
                        radius: 8
                        color: puzzle.board[index] === 0 ? "#f5f5f5" : "#e0e0e0"
                        border.color: "#cccccc"
                        border.width: 1

                        Text {
                            text: puzzle.board[index]
                            font.pixelSize: 24
                            anchors.centerIn: parent
                            visible: puzzle.board[index] !== 0
                        }

                        MouseArea {
                            anchors.fill: parent
                            enabled: puzzle.board[index] !== 0
                            onClicked: puzzle.move(puzzle.board[index])
                        }
                    }
                }
            }

            Text {
                text: "Moves: " + puzzle.moves
                font.pixelSize: 16
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Button {
                text: "New Game"
                anchors.horizontalCenter: parent.horizontalCenter
                onClicked: {
                    for (var i = 0; i < 100; i++) {
                        var legal = puzzle.legalMoves();
                        if (legal.length > 0) {
                            var tile = legal[Math.floor(Math.random() * legal.length)];
                            puzzle.move(tile);
                        }
                    }
                }
            }
        }
    }
}