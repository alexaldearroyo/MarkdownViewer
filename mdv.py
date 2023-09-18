import sys
import os
import mistune


from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMenu, QAction, QTabWidget, QTabBar, QShortcut, QLabel, QStackedWidget, QTextEdit, QTextBrowser
from PyQt5.QtCore import Qt, QEvent, QUrl
from PyQt5.QtGui import QGuiApplication, QPainter, QPalette, QBrush, QKeySequence, QDesktopServices
from PyQt5.QtWebEngineWidgets import QWebEngineView



def is_dark_mode():
    app = QGuiApplication.instance()
    return app.palette().window().color().lightness() < 128

class MyApp(QApplication):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_win = None

    def event(self, event):
        if event.type() == QEvent.FileOpen:
            if self.main_win:
                self.main_win.openMd(event.file())
            return True
        return super().event(event)


class MarkdownViewer(QMainWindow):
    
    def __init__(self, files_to_open=None):
        super().__init__()
        
        self.dark_mode = is_dark_mode()
        
        self.initUI()
        
        if files_to_open:
            for file in files_to_open:
                self.openMd(file)
            
    def keyPressEvent(self, event):
        
        if event.key() == Qt.Key_O and (event.modifiers() & Qt.ControlModifier):
            self.openMd()
            return

        if event.key() == Qt.Key_W and (event.modifiers() & Qt.ControlModifier):
            self.closeMd()
            return

        super().keyPressEvent(event)

    def get_style(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        theme = 'dark_theme' if self.dark_mode else 'light_theme'
        css_file_path = os.path.join(base_path, 'themes', f'{theme}.css')
        with open(css_file_path, 'r', encoding='utf-8') as f:
            custom_css = """
            p, li {
                line-height: 1.5;
                font-size: 14px;
            }
            """
            headers_css = """
            h1, h2, h3, h4, h5, h6 {
                border-bottom: 1px solid #ccc;
                padding-bottom: 8px;
                margin-bottom: 16px;
            }
            """
            image_css = """
            img {
                max-width: 100%;
                height: auto;
            }
            """
            return f'<style>{f.read()}{custom_css}{headers_css}{image_css}</style>'

    def nextTab(self):
        next_index = (self.tabs.currentIndex() + 1) % self.tabs.count()
        self.tabs.setCurrentIndex(next_index)
        
    def prevTab(self):
        prev_index = (self.tabs.currentIndex() - 1) % self.tabs.count()
        self.tabs.setCurrentIndex(prev_index)

    def initUI(self):
        self.setWindowTitle("Markdown Viewer")
        
        # Create a QStackedWidget to hold the tabs
        self.stackedWidget = QStackedWidget(self)
        self.setCentralWidget(self.stackedWidget)
        
        # Tabs
        self.tabs = CustomTabWidget(self)
        self.tabs.setTabBar(CustomTabBar())
        
        # Set the tabs as movable and closable
        self.tabs.setMovable(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.closeTab)
                
        # Tab navigation
        nextTabShortcut = QShortcut(QKeySequence(Qt.ControlModifier | Qt.ShiftModifier | Qt.Key_BracketRight), self)
        nextTabShortcut.activated.connect(self.nextTab)

        prevTabShortcut = QShortcut(QKeySequence(Qt.ControlModifier | Qt.ShiftModifier | Qt.Key_BracketLeft), self)
        prevTabShortcut.activated.connect(self.prevTab)

        # Menu bar
        menubar = self.menuBar()
        fileMenu = QMenu('File', self)
        menubar.addMenu(fileMenu)

        # Open file action
        openFileAction = QAction('Open', self)
        openFileAction.triggered.connect(self.openMd)
        fileMenu.addAction(openFileAction)
        
        # Close file action
        closeFileAction = QAction('Close', self)
        closeFileAction.triggered.connect(self.closeMd)
        fileMenu.addAction(closeFileAction)

        self.setGeometry(100, 100, 800, 600)
        
        # Welcome Label
        self.welcomeLabel = QLabel(self)
        self.welcomeLabel.setText("Welcome to Markdown Viewer\n\nCmd + O to open a file")
        self.welcomeLabel.setAlignment(Qt.AlignCenter)
        self.welcomeLabel.setStyleSheet("font-size: 18px; color: gray;")
        
        # Add the welcome label and the tabs to the stacked widget
        self.stackedWidget.addWidget(self.welcomeLabel)
        self.stackedWidget.addWidget(self.tabs)
        
    def openMd(self, filePath=None):
        
        if not filePath:
            options = QFileDialog.Options()
            filePath, _ = QFileDialog.getOpenFileName(self, "Open Markdown File", "", "Markdown Files (*.md);;All Files (*)", options=options)
        
        if filePath:
            with open(filePath, 'r') as f:
                md_content = f.read()

            html_content = mistune.markdown(md_content)
            html_content = self.get_style() + html_content

            # Create a new QWebEngineView for the file content
            web_view = QWebEngineView(self)

            # Set the base URL to the directory of the .md file
            base_url = QUrl.fromLocalFile(os.path.dirname(os.path.abspath(filePath)) + os.sep)
            web_view.setHtml(html_content, base_url)

            # Add padding and bg color to the text edit
            padding = 20
            bg_color = "#212124" if self.dark_mode else "white"            
            web_view.setStyleSheet(f"QTextBrowser {{ padding: {padding}px; background-color: {bg_color}; }}")

            # Add the QWebEngineView to the QTabWidget, using the file name as the tab title
            index = self.tabs.addTab(web_view, os.path.basename(filePath))

            # Set the new tab as the current tab
            self.tabs.setCurrentIndex(index)

            # Set the tab color according to the mode (dark or light)
            if self.dark_mode:
                self.tabs.tabBar().setTabData(index, "#333")
            else:
                self.tabs.tabBar().setTabData(index, "white")
                    
            if self.stackedWidget.currentWidget() != self.tabs:
                self.stackedWidget.setCurrentWidget(self.tabs)

                  
    def closeMd(self):
        current_index = self.tabs.currentIndex()
        if current_index != -1:
            self.tabs.removeTab(current_index)
            if self.tabs.count() == 0:
                self.stackedWidget.setCurrentWidget(self.welcomeLabel)
        else:
            self.close()
           
    def closeTab(self, index):
        self.tabs.removeTab(index)
        if self.tabs.count() == 0:
            self.stackedWidget.setCurrentWidget(self.welcomeLabel)
        
        
class CustomTabWidget(QTabWidget):
    
    def __init__(self, *args, **kwargs):
        super(CustomTabWidget, self).__init__(*args, **kwargs)
        self.border_thickness = 1
        self.setStyleSheet(f"QTabWidget::pane {{ border-top: {self.border_thickness}px solid transparent; }}")


class CustomTabBar(QTabBar):

    def tabSizeHint(self, index):
        size = super().tabSizeHint(index)
        size.setHeight(30)
        return size

    def paintEvent(self, event):
        painter = QPainter(self)

        # Use the background color of the window content for the tab bar
        bgColor = self.window().palette().color(QPalette.Window)
        darkerColor = bgColor.darker(150)
        
        for index in range(self.count()):
            tabRect = self.tabRect(index)
            
            if index == self.currentIndex():
                painter.setBrush(QBrush(bgColor))
            else:
                painter.setBrush(QBrush(darkerColor))
            
            painter.setPen(Qt.NoPen)
            
            if index != self.currentIndex():
                tabRect.adjust(0, 2, 0, -2)
            painter.drawRect(tabRect)

            textPen = self.palette().color(QPalette.WindowText)
            painter.setPen(textPen)
            painter.drawText(tabRect, Qt.AlignVCenter | Qt.AlignHCenter, self.tabText(index))

        
if __name__ == '__main__':
    app = MyApp(sys.argv)
    files_to_open = [arg for arg in sys.argv[1:] if arg.endswith('.md')]
    viewer = MarkdownViewer(files_to_open=files_to_open)
    app.main_win = viewer
    viewer.show()
    sys.exit(app.exec_())


