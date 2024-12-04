import sys
import random
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QGraphicsView, QGraphicsScene,
    QGraphicsRectItem, QLineEdit
)
from PyQt6.QtGui import QColor, QBrush, QPen, QIntValidator
from PyQt6.QtCore import Qt


class MazeGeneratorSolver(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Maze Generator & Solver")
        self.setGeometry(100, 100, 900, 800)

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Header
        header = QLabel("Maze Generator & Solver")
        header.setStyleSheet("font: bold 24px; color: white;")
        main_layout.addWidget(header, alignment=Qt.AlignmentFlag.AlignCenter)

        # Controls layout
        controls_layout = QHBoxLayout()
        main_layout.addLayout(controls_layout)

        # Maze Size Input
        size_layout = QVBoxLayout()
        width_label = QLabel("Width:")
        width_label.setStyleSheet("color: white;")
        self.width_input = QLineEdit()
        self.width_input.setPlaceholderText("15")
        self.width_input.setValidator(QIntValidator(5, 50))
        self.width_input.setStyleSheet("""
            background-color: #34495E;
            color: white;
            border: 1px solid #2C3E50;
            padding: 5px;
            border-radius: 5px;
            max-width: 80px;
        """)

        height_label = QLabel("Height:")
        height_label.setStyleSheet("color: white;")
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("15")
        self.height_input.setValidator(QIntValidator(5, 50))
        self.height_input.setStyleSheet("""
            background-color: #34495E;
            color: white;
            border: 1px solid #2C3E50;
            padding: 5px;
            border-radius: 5px;
            max-width: 80px;
        """)

        width_row = QHBoxLayout()
        width_row.setContentsMargins(0, 0, 0, 0)
        width_row.setSpacing(5)
        width_row.addWidget(width_label)
        width_row.addWidget(self.width_input)
        width_row.addStretch(1)# No space between the label and text box

        height_row = QHBoxLayout()
        height_row.setContentsMargins(0, 0, 0, 0)
        height_row.setSpacing(5)
        height_row.addWidget(height_label)
        height_row.addWidget(self.height_input)
        height_row.addStretch(1)

        size_layout.addLayout(width_row)
        size_layout.addLayout(height_row)
        controls_layout.addLayout(size_layout)

        # Generation Algorithm Selector
        gen_layout = QVBoxLayout()
        gen_label = QLabel("Generation")
        gen_label.setStyleSheet("color: white;")
        self.gen_combo = QComboBox()
        self.gen_combo.addItems([
            "Recursive Backtrack",
            "Prim's Algorithm",
            "Kruskal's Algorithm"
        ])
        self.gen_combo.setStyleSheet("""
            background-color: #34495E;
            color: white;
            border: 1px solid #2C3E50;
            padding: 5px;
            border-radius: 5px;
            min-width: 150px;
        """)
        gen_layout.addWidget(gen_label)
        gen_layout.addWidget(self.gen_combo)
        controls_layout.addLayout(gen_layout)

        # Solving Algorithm Selector
        solve_layout = QVBoxLayout()
        solve_label = QLabel("Solving Method")
        solve_label.setStyleSheet("color: white;")
        self.solve_combo = QComboBox()
        self.solve_combo.addItems([
            "Depth-First Search",
            "Breadth-First Search",
            "A* Search"
        ])
        self.solve_combo.setStyleSheet("""
            background-color: #34495E;
            color: white;
            border: 1px solid #2C3E50;
            padding: 5px;
            border-radius: 5px;
            min-width: 150px;
        """)
        solve_layout.addWidget(solve_label)
        solve_layout.addWidget(self.solve_combo)
        controls_layout.addLayout(solve_layout)

        # Buttons
        button_layout = QHBoxLayout()
        generate_btn = QPushButton("Generate Maze")
        generate_btn.setStyleSheet("""
            background-color: #673AB7;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 5px;
        """)
        generate_btn.clicked.connect(self.generate_maze)
        solve_btn = QPushButton("Solve Maze")
        solve_btn.setStyleSheet("""
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 5px;
        """)
        solve_btn.clicked.connect(self.solve_maze)
        button_layout.addWidget(generate_btn)
        button_layout.addWidget(solve_btn)
        main_layout.addLayout(button_layout)

        # Graphics View for Maze
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setFixedHeight(500)
        self.view.setStyleSheet("background-color: rgb(40, 44, 54);")
        main_layout.addWidget(self.view)

        self.maze = None
        self.setStyleSheet("""
            QMainWindow { background-color: rgb(31, 41, 54); }
            QLabel { color: white; }
            QComboBox, QLineEdit { 
                background-color: #34495E; 
                color: white; 
                border: 1px solid rgb(31, 41, 54); 
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton { 
                background-color: #673AB7; 
                color: white; 
                border: none; 
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover { 
                background-color: #512DA8; 
            }
        """)

    def generate_maze(self):
        # Use input values or default to 15 if not provided
        width = int(self.width_input.text() or 15)
        height = int(self.height_input.text() or 15)

        # Generate random maze
        self.maze = np.random.choice([0, 1], size=(height, width), p=[0.7, 0.3])

        # Clear previous scene
        self.scene.clear()

        # Render maze
        cell_size = min(500 // max(width, height), 30)
        for y in range(height):
            for x in range(width):
                color = Qt.GlobalColor.white if self.maze[y][x] == 0 else Qt.GlobalColor.black
                rect = QGraphicsRectItem(x * cell_size, y * cell_size, cell_size, cell_size)
                rect.setBrush(QBrush(QColor(color)))
                rect.setPen(QPen(Qt.GlobalColor.gray))
                self.scene.addItem(rect)

    def solve_maze(self):
        if self.maze is None:
            return

        height, width = self.maze.shape
        solved_maze = self.maze.copy()

        # Randomly mark some paths
        solved_maze = np.where(
            (solved_maze == 0) & (np.random.random(solved_maze.shape) > 0.5),
            2,
            solved_maze
        )

        # Clear previous scene
        self.scene.clear()

        # Re-render maze with solution paths
        cell_size = min(500 // max(width, height), 30)
        for y in range(height):
            for x in range(width):
                if solved_maze[y][x] == 0:
                    color = Qt.GlobalColor.white
                elif solved_maze[y][x] == 1:
                    color = Qt.GlobalColor.black
                else:
                    color = QColor(128, 0, 128)  # Purple

                rect = QGraphicsRectItem(x * cell_size, y * cell_size, cell_size, cell_size)
                rect.setBrush(QBrush(color))
                rect.setPen(QPen(Qt.GlobalColor.gray))
                self.scene.addItem(rect)


def main():
    app = QApplication(sys.argv)
    window = MazeGeneratorSolver()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()