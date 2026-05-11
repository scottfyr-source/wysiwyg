import sys
import time
import ctypes
import uuid
import json
import os
from ctypes import wintypes
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QListWidget, QListWidgetItem, QLabel, QDialog, QMessageBox,
    QHBoxLayout, QPushButton, QBoxLayout, QMenu, QFrame, QInputDialog, QAbstractItemView
)
from PySide6.QtCore import Qt, QTimer, Slot, Signal, QCoreApplication, QPoint, QEvent
from PySide6.QtGui import QGuiApplication, QAction, QWheelEvent, QIcon, QActionGroup
import pyautogui
import pyperclip

# Windows AppBar Constants and Structures
class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long),
                ("top", ctypes.c_long),
                ("right", ctypes.c_long),
                ("bottom", ctypes.c_long)]

class APPBARDATA(ctypes.Structure):
    _fields_ = [
        ('cbSize', wintypes.DWORD),
        ('hWnd', wintypes.HWND),
        ('uCallbackMessage', wintypes.UINT),
        ('uEdge', wintypes.UINT),
        ('rc', RECT),
        ('lParam', wintypes.LPARAM),
    ]

ABM_NEW = 0x00000000
ABM_REMOVE = 0x00000001
ABM_QUERYPOS = 0x00000002
ABM_SETPOS = 0x00000003
ABE_TOP = 1

class HorizontalScrollListWidget(QListWidget):
    """ListWidget that scrolls horizontally with the mouse wheel when flow is LeftToRight."""
    order_changed = Signal()
    items_dropped_in_folder = Signal(list, str)

    def wheelEvent(self, event: QWheelEvent):
        if self.flow() == QListWidget.LeftToRight:
            bar = self.horizontalScrollBar()
            if bar:
                # Scroll horizontally based on vertical wheel delta
                delta = event.angleDelta().y()
                bar.setValue(bar.value() - delta)
                event.accept()
        else:
            super().wheelEvent(event)

    def dropEvent(self, event):
        target_item = self.itemAt(event.pos())
        drop_pos = self.dropIndicatorPosition()
        
        if drop_pos == QAbstractItemView.OnItem and target_item:
            target_widget = self.itemWidget(target_item)
            if target_widget and target_widget.item_data.get('type') == 'folder':
                dragged_data = []
                for item in self.selectedItems():
                    if item == target_item: continue
                    w = self.itemWidget(item)
                    if w and w.item_data.get('type') == 'item':
                        dragged_data.append(w.item_data)
                if dragged_data:
                    event.setDropAction(Qt.IgnoreAction)
                    event.accept()
                    self.items_dropped_in_folder.emit(dragged_data, target_widget.item_data['id'])
                    return

        super().dropEvent(event)
        if self.dragDropMode() == QAbstractItemView.InternalMove:
            self.order_changed.emit()

class ClipboardItemWidget(QWidget):
    """
    Custom widget for each entry in the clipboard history list.
    It contains the clipboard text, a 'Keep' checkbox, and emits a signal when clicked.
    """
    paste_requested = Signal(str)
    delete_requested = Signal(dict)
    keep_toggled = Signal()
    folder_toggled = Signal(dict)
    folder_pinned = Signal()
    item_edited = Signal()

    def __init__(self, item_data, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.item_data = item_data
        self.is_docked = False
        self.dock_index = 0
        self.dock_font_size = 10
        self.item_type = self.item_data.get('type', 'item')

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        self.icon_label = QLabel()
        self.icon_label.setFixedWidth(20)
        self.icon_label.setAlignment(Qt.AlignCenter)

        self.label = QLabel()
        self.setToolTip(self.item_data.get('text', self.item_data.get('name', '')))

        layout.addWidget(self.icon_label)
        layout.addWidget(self.label, 1)  # Label takes up expanding space
        self.update_style()
        self.set_docked(False)

    def set_docked(self, docked, index=0, font_size=10):
        self.is_docked = docked
        self.dock_index = index
        self.dock_font_size = font_size

        """Adjusts appearance based on docked state."""
        text = self.item_data.get('text', '')
        if docked:
            self.layout().setContentsMargins(5, 0, 5, 0)
            self.layout().setSpacing(5)
            if self.item_type == 'folder':
                self.label.setText(self.item_data.get('name', 'Folder'))
            else:
                # Show first few words (e.g., 10)
                words = text.split()
                display_text = " ".join(words[:10])
                if len(words) > 10:
                    display_text += "..."
                self.label.setText(display_text)
            self.setMaximumWidth(350)
            self.setFixedHeight(40)
        else:
            self.layout().setContentsMargins(5, 5, 5, 5)
            self.layout().setSpacing(6)
            if self.item_type == 'folder':
                self.label.setText(self.item_data.get('name', 'Folder'))
            else:
                display_text = (text[:75] + '...') if len(text) > 75 else text
                self.label.setText(display_text.replace('\n', ' ').replace('\r', ''))
            self.setMaximumWidth(16777215)
            self.setMinimumHeight(0)
            self.setMaximumHeight(16777215)
        self.update_style()

    def update_style(self):
        """Updates the visual style based on the keep state."""
        if self.item_type == 'folder':
            self.update_folder_style()
        else:
            self.update_item_style()

    def update_item_style(self):
        is_kept = self.item_data.get('keep', False)
        self.icon_label.setText("📌" if is_kept else "")
        
        main_window = self.window()
        is_dark = getattr(main_window, 'dark_mode', False)

        color = self.item_data.get('color')
        border_left_style = f"border-left: 4px solid {color if color else 'transparent'};"

        if self.is_docked:
            bg_color = "#3c3c3c" if self.dock_index % 2 == 0 else "#4a4a4a"
            text_color = "#00FFFF" if is_kept else "#e0e0e0"
            self.setStyleSheet(f"""
                ClipboardItemWidget {{ 
                    border: none; margin: 0px; padding: 0px; background-color: {bg_color}; 
                    {border_left_style}
                }}
                ClipboardItemWidget:hover {{ background-color: #FFFF00; }}
                QLabel {{ border: none; margin: 0px; padding: 0px; font-size: {self.dock_font_size}px; color: {text_color}; background: transparent; font-weight: {'bold' if is_kept else 'normal'}; }}
                ClipboardItemWidget:hover QLabel {{ color: #000000; }}
            """)
        else:
            if is_dark:
                bg_color = "#1e1e1e"
                text_color = "#00FFFF" if is_kept else "#e0e0e0"
                border_style = "1px solid #444444"
            else:
                bg_color = "#ffffff"
                text_color = "#0000FF" if is_kept else "#333333"
                border_style = "1px solid #cccccc"

            self.setStyleSheet(f"""
                ClipboardItemWidget {{ 
                    background-color: {bg_color}; 
                    border-bottom: {border_style};
                    {border_left_style}
                }}
                ClipboardItemWidget:hover {{ background-color: #FFFF00; }}
                QLabel {{ font-size: {self.dock_font_size}px; color: {text_color}; background: transparent; font-weight: {'bold' if is_kept else 'normal'}; }}
                ClipboardItemWidget:hover QLabel {{ color: #000000; }}
            """)

    def update_folder_style(self):
        is_collapsed = self.item_data.get('collapsed', True)
        icon = "▶" if is_collapsed else "▼"
        self.icon_label.setText(f"{icon} 📁")

        main_window = self.window()
        is_dark = getattr(main_window, 'dark_mode', False)

        color = self.item_data.get('color')
        border_left_style = f"border-left: 4px solid {color if color else 'transparent'};"

        if self.is_docked:
            bg_color = "#555555"
            text_color = "#FAD5A5" # Light orange for folders
            self.setStyleSheet(f"""
                ClipboardItemWidget {{ 
                    border: none; margin: 0px; padding: 0px; background-color: {bg_color}; 
                    {border_left_style}
                }}
                ClipboardItemWidget:hover {{ background-color: #FFFF00; }}
                QLabel {{ border: none; margin: 0px; padding: 0px; font-size: {self.dock_font_size}px; color: {text_color}; background: transparent; font-weight: bold; }}
                ClipboardItemWidget:hover QLabel {{ color: #000000; }}
            """)
        else:
            bg_color = "#444444" if is_dark else "#e0e0e0"
            text_color = "#FAD5A5" if is_dark else "#a16600"
            border_style = "1px solid #555" if is_dark else "1px solid #b0b0b0"
            self.setStyleSheet(f"""
                ClipboardItemWidget {{ 
                    background-color: {bg_color}; 
                    border-bottom: {border_style}; 
                    {border_left_style}
                }}
                ClipboardItemWidget:hover {{ background-color: #FFFF00; }}
                QLabel {{ font-size: {self.dock_font_size}px; color: {text_color}; background: transparent; font-weight: bold; }}
                ClipboardItemWidget:hover QLabel {{ color: #000000; }}
            """)

    def contextMenuEvent(self, event):
        """Handle right-click context menu."""
        menu = QMenu(self)
        main_window = self.window()

        if self.item_type == 'item':
            keep_action = QAction("Keep", self)
            keep_action.setCheckable(True)
            keep_action.setChecked(self.item_data.get('keep', False))
            keep_action.triggered.connect(self.toggle_keep)
            menu.addAction(keep_action)
            
            edit_action = QAction("Edit Item", self)
            edit_action.triggered.connect(self.edit_item)
            menu.addAction(edit_action)

            # Add to folder submenu
            folders = [item for item in main_window.clipboard_history if item.get('type') == 'folder']
            if folders:
                folder_menu = menu.addMenu("Add to Folder")
                for folder in folders:
                    action = QAction(folder.get('name'), self)
                    action.triggered.connect(lambda checked, f=folder: main_window.move_item_to_folder(self.item_data, f['id']))
                    folder_menu.addAction(action)
                if self.item_data.get('parent_id'):
                    folder_menu.addSeparator()
                    action = QAction("Move to Top Level", self)
                    action.triggered.connect(lambda: main_window.move_item_to_folder(self.item_data, None))
                    folder_menu.addAction(action)
            menu.addSeparator()
        elif self.item_type == 'folder':
            pin_action = QAction("Pin Folder", self)
            pin_action.setCheckable(True)
            pin_action.setChecked(self.item_data.get('pinned', False))
            pin_action.triggered.connect(self.toggle_pinned)
            menu.addAction(pin_action)
            menu.addSeparator()

        # Add color menu for both items and folders
        color_menu = menu.addMenu("Set Color")
        colors = {
            "Red": "#e57373", "Green": "#81c784", "Blue": "#64b5f6",
            "Yellow": "#fff176", "Orange": "#ffb74d", "Purple": "#ba68c8"
        }

        color_group = QActionGroup(self)
        color_group.setExclusive(True)

        default_action = QAction("Default", self)
        default_action.setCheckable(True)
        if self.item_data.get('color') is None:
            default_action.setChecked(True)
        default_action.triggered.connect(lambda: self.set_item_color(None))
        color_menu.addAction(default_action)
        color_group.addAction(default_action)
        color_menu.addSeparator()

        for name, hex_code in colors.items():
            action = QAction(name, self)
            action.setCheckable(True)
            if self.item_data.get('color') == hex_code:
                action.setChecked(True)
            action.triggered.connect(lambda checked, c=hex_code: self.set_item_color(c))
            color_menu.addAction(action)
            color_group.addAction(action)
        
        menu.addSeparator()
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.delete_requested.emit(self.item_data))
        menu.addAction(delete_action)
        
        menu.addSeparator()
        
        if hasattr(main_window, 'appbar_registered'):
            if main_window.appbar_registered:
                dock_action = QAction("Undock", self)
                dock_action.triggered.connect(main_window.undock_window)
            else:
                dock_action = QAction("Dock to Top", self)
                dock_action.triggered.connect(main_window.dock_window)
            menu.addAction(dock_action)
            
            clear_action = QAction("Clear All", self)
            clear_action.triggered.connect(main_window.clear_all)
            menu.addAction(clear_action)
            clear_unpinned_action_ctx = QAction("Clear Unpinned", self)
            clear_unpinned_action_ctx.triggered.connect(main_window.clear_unpinned)
            menu.addAction(clear_unpinned_action_ctx)
            
            close_action = QAction("Close", self)
            close_action.triggered.connect(main_window.close)
            menu.addAction(close_action)
        
        menu.exec(event.globalPos())

    def toggle_keep(self):
        self.item_data['keep'] = not self.item_data.get('keep', False)
        self.update_style()
        self.keep_toggled.emit()

    def toggle_pinned(self):
        self.item_data['pinned'] = not self.item_data.get('pinned', False)
        self.update_style()
        self.folder_pinned.emit()

    def edit_item(self):
        current_text = self.item_data.get('text', '')
        text, ok = QInputDialog.getMultiLineText(self, "Edit Item", "Modify clipboard text:", current_text)
        if ok and text != current_text:
            self.item_data['text'] = text
            self.setToolTip(text)
            self.set_docked(self.is_docked, self.dock_index, self.dock_font_size)
            self.item_edited.emit()

    def set_item_color(self, color_hex):
        """Sets the color for the item and triggers a style update and save."""
        self.item_data['color'] = color_hex
        self.update_style()
        self.item_edited.emit()

class FolderManagerDialog(QDialog):
    def __init__(self, main_app, parent=None):
        super().__init__(parent)
        self.main_app = main_app
        self.setWindowTitle("Manage Folders")
        self.setMinimumWidth(300)

        if getattr(self.main_app, 'dark_mode', False):
            self.setStyleSheet("""
                QDialog { background-color: #1e1e1e; color: #e0e0e0; }
                QListWidget { background-color: #2b2b2b; color: #e0e0e0; border: 1px solid #444; }
                QListWidget::item:selected { background-color: #444; color: #ffffff; }
                QPushButton { background-color: #333333; color: #e0e0e0; border: 1px solid #555; padding: 5px; }
                QPushButton:hover { background-color: #444444; }
                QMessageBox { background-color: #1e1e1e; color: #e0e0e0; }
                QInputDialog { background-color: #1e1e1e; color: #e0e0e0; }
                QLabel { color: #e0e0e0; }
                QLineEdit { background-color: #2b2b2b; color: #e0e0e0; border: 1px solid #444; }
            """)

        layout = QVBoxLayout(self)

        self.list_widget = QListWidget()
        self.populate_folders()
        layout.addWidget(self.list_widget)

        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_folder)
        button_layout.addWidget(add_btn)

        rename_btn = QPushButton("Rename")
        rename_btn.clicked.connect(self.rename_folder)
        button_layout.addWidget(rename_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_folder)
        button_layout.addWidget(delete_btn)

        layout.addLayout(button_layout)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def populate_folders(self):
        self.list_widget.clear()
        folders = [item for item in self.main_app.clipboard_history if item.get('type') == 'folder']
        for folder in folders:
            self.list_widget.addItem(folder['name'])

    def add_folder(self):
        text, ok = QInputDialog.getText(self, "Add Folder", "Enter new folder name:")
        if ok and text:
            if any(f.get('name', '').lower() == text.lower() for f in self.main_app.clipboard_history if f.get('type') == 'folder'):
                QMessageBox.warning(self, "Duplicate Name", "A folder with that name already exists.")
                return

            new_folder = {
                'id': str(uuid.uuid4()),
                'type': 'folder',
                'name': text,
                'collapsed': True
            }
            self.main_app.clipboard_history.insert(0, new_folder)
            self.list_widget.insertItem(0, text)

    def rename_folder(self):
        current_item = self.list_widget.currentItem()
        if not current_item:
            return
        
        old_name = current_item.text()
        text, ok = QInputDialog.getText(self, "Rename Folder", "Enter new name:", text=old_name)
        
        if ok and text and text != old_name:
            if any(f.get('name', '').lower() == text.lower() for f in self.main_app.clipboard_history if f.get('type') == 'folder'):
                QMessageBox.warning(self, "Duplicate Name", "A folder with that name already exists.")
                return

            for folder in self.main_app.clipboard_history:
                if folder.get('type') == 'folder' and folder['name'] == old_name:
                    folder['name'] = text
                    current_item.setText(text)
                    break

    def delete_folder(self):
        current_item = self.list_widget.currentItem()
        if not current_item:
            return
        
        folder_name = current_item.text()
        reply = QMessageBox.question(self, "Delete Folder", 
                                     f"Are you sure you want to delete the folder '{folder_name}'?\nItems inside will be moved to the top level.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            folder_to_delete = None
            for folder in self.main_app.clipboard_history:
                if folder.get('type') == 'folder' and folder['name'] == folder_name:
                    folder_to_delete = folder
                    break
            
            if folder_to_delete:
                folder_id = folder_to_delete['id']
                for item in self.main_app.clipboard_history:
                    if item.get('parent_id') == folder_id:
                        item['parent_id'] = None
                
                self.main_app.clipboard_history.remove(folder_to_delete)
                self.list_widget.takeItem(self.list_widget.row(current_item))

class ClipTrayApp(QWidget):
    """
    The main application window that holds the clipboard history.
    """
    def __init__(self):
        super().__init__()
        self.clipboard_history = []
        self.max_items = 10
        self.docked_font_size = 10
        self.undocked_font_size = 12
        self.top_pins = False
        self.last_clipboard_content = ""
        self.is_pasting = False
        self.sort_mode = False
        self.temp_sort_mode = False
        self.appbar_registered = False
        self.dark_mode = False
        self.base_path = ""
        
        if getattr(sys, 'frozen', False):
            self.base_path = os.path.dirname(sys.executable)
        else:
            self.base_path = os.path.dirname(os.path.abspath(__file__))
            
        self.history_file = os.path.join(self.base_path, "clipboard_history.json")
        self.settings_file = os.path.join(self.base_path, "settings.json")

        self.load_settings()
        self.init_ui()
        self.load_history()
        self.setup_clipboard_monitor()
        
        QCoreApplication.instance().installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Control:
                self.on_ctrl_state_changed(True)
        elif event.type() == QEvent.KeyRelease:
            if event.key() == Qt.Key_Control:
                self.on_ctrl_state_changed(False)
        elif event.type() == QEvent.WindowDeactivate:
            self.on_ctrl_state_changed(False)
        return super().eventFilter(obj, event)

    def on_ctrl_state_changed(self, is_pressed):
        if is_pressed:
            if not self.sort_mode and not self.temp_sort_mode:
                self.temp_sort_mode = True
                self.set_drag_drop_state(True)
        elif self.temp_sort_mode:
            self.temp_sort_mode = False
            self.set_drag_drop_state(self.sort_mode)

    def init_ui(self):
        """Initialize the application's user interface."""
        self.setWindowTitle("UberPaste")
        icon_path = os.path.join(self.base_path, "UberPaste.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        # Set window flags: Always on top and acts as a tool window (no taskbar icon by default)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)

        main_layout = QBoxLayout(QBoxLayout.TopToBottom)

        self.options_btn = QPushButton("Options")
        self.options_btn.clicked.connect(self.show_options_menu)
        main_layout.addWidget(self.options_btn)

        self.list_widget = HorizontalScrollListWidget()
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        self.list_widget.customContextMenuRequested.connect(self.show_app_context_menu)
        self.list_widget.order_changed.connect(self.rebuild_history_from_view)
        self.list_widget.items_dropped_in_folder.connect(self.on_items_dropped_in_folder)
        main_layout.addWidget(self.list_widget)

        self.setLayout(main_layout)
        self.apply_theme()
        self.set_drag_drop_state(self.sort_mode)

    def apply_theme(self):
        """Applies the current theme (Dark/Light) to the main window and controls."""
        if self.dark_mode:
            self.setStyleSheet("QWidget { background-color: #121212; color: #ffffff; }")
            self.list_widget.setStyleSheet("QListWidget { background-color: #1e1e1e; border: none; } QListWidget::item { border-bottom: 1px solid #444; }")
        else:
            self.setStyleSheet("QWidget { background-color: #f0f0f0; color: #000000; }")
            self.list_widget.setStyleSheet("QListWidget { background-color: #ffffff; border: none; } QListWidget::item { border-bottom: 1px solid #ccc; }")

        # Options button style (Yellow background, Black text)
        self.options_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFF00;
                color: #000000;
                border: 1px solid #FFFF00;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #CCCC00; }
        """)

    def setup_clipboard_monitor(self):
        """Set up a timer to periodically check for clipboard changes."""
        self.clipboard_timer = QTimer(self)
        self.clipboard_timer.setInterval(500)  # Check every 500ms
        self.clipboard_timer.timeout.connect(self.check_clipboard)
        self.clipboard_timer.start()
        # Initialize with current clipboard content
        self.check_clipboard()

    @Slot()
    def check_clipboard(self):
        """Checks the clipboard for new content and updates the history."""
        if self.is_pasting:
            return

        try:
            # Use Qt's integrated clipboard access
            current_content = QGuiApplication.clipboard().text()
        except Exception:
            # This can happen with non-text clipboard data (e.g., images)
            return

        if current_content and current_content != self.last_clipboard_content:
            self.last_clipboard_content = current_content
            self.add_clipboard_item(current_content)

    def load_history(self):
        """Loads clipboard history from a JSON file."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)

                migrated = False
                for item in history:
                    if 'id' not in item:
                        item['id'] = str(uuid.uuid4())
                        migrated = True
                    if 'type' not in item:
                        item['type'] = 'item'
                    if item.get('type') == 'item' and 'parent_id' not in item:
                        item['parent_id'] = None

                self.clipboard_history = history
                if migrated:
                    self.save_history()

                self.update_list_widget()
            except (json.JSONDecodeError, OSError) as e:
                print(f"Failed to load history: {e}")

    def load_settings(self):
        """Loads application settings."""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    self.max_items = settings.get('max_items', 10)
                    self.docked_font_size = settings.get('docked_font_size', 10)
                    self.undocked_font_size = settings.get('undocked_font_size', 12)
                    self.top_pins = settings.get('top_pins', False)
                    self.dark_mode = settings.get('dark_mode', False)
                    self.sort_mode = settings.get('sort_mode', False)
                    # Load window geometry if it exists
                    geometry = settings.get('window_geometry')
                    if geometry and not self.appbar_registered:
                        self.setGeometry(
                            geometry.get('x', 100), geometry.get('y', 100),
                            geometry.get('width', 450), geometry.get('height', 350)
                        )
            except Exception as e:
                print(f"Failed to load settings: {e}")

    def save_settings(self):
        """Saves application settings."""
        settings = {
            'max_items': self.max_items,
            'docked_font_size': self.docked_font_size,
            'undocked_font_size': self.undocked_font_size,
            'dark_mode': self.dark_mode,
            'top_pins': self.top_pins,
            'sort_mode': self.sort_mode,
        }
        # Save window geometry if not docked and not minimized
        if not self.appbar_registered and not self.isMinimized():
            g = self.geometry()
            settings['window_geometry'] = {
                'x': g.x(), 'y': g.y(),
                'width': g.width(), 'height': g.height()
            }
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def show_options_menu(self):
        """Displays the options menu for settings."""
        menu = QMenu(self)
        
        # Dock/Undock Action
        if self.appbar_registered:
            dock_action = QAction("Undock Window", self)
            dock_action.triggered.connect(self.undock_window)
        else:
            dock_action = QAction("Dock to Top", self)
            dock_action.triggered.connect(self.dock_window)
        menu.addAction(dock_action)
        
        menu.addSeparator()

        # Dark Mode Toggle
        dark_action = QAction("Dark Mode", self)
        dark_action.setCheckable(True)
        dark_action.setChecked(self.dark_mode)
        dark_action.triggered.connect(self.toggle_dark_mode)
        menu.addAction(dark_action)
        
        # Top Pins Toggle
        top_pins_action = QAction("Top Pins", self)
        top_pins_action.setCheckable(True)
        top_pins_action.setChecked(self.top_pins)
        top_pins_action.triggered.connect(self.toggle_top_pins)
        menu.addAction(top_pins_action)

        sort_mode_action = QAction("Sort Mode", self)
        sort_mode_action.setCheckable(True)
        sort_mode_action.setChecked(self.sort_mode)
        sort_mode_action.triggered.connect(self.toggle_sort_mode)
        menu.addAction(sort_mode_action)
        
        # Font Size Submenu
        font_menu = menu.addMenu("Docked Font Size")
        for size in [8, 10, 12, 14]:
            action = QAction(f"{size}px", self)
            action.setCheckable(True)
            action.setChecked(self.docked_font_size == size)
            action.triggered.connect(lambda checked, s=size: self.set_docked_font_size(s))
            font_menu.addAction(action)

        # Undocked Font Size Submenu
        undocked_font_menu = menu.addMenu("Undocked Font Size")
        for size in [10, 12, 14, 16, 18]:
            action = QAction(f"{size}px", self)
            action.setCheckable(True)
            action.setChecked(self.undocked_font_size == size)
            action.triggered.connect(lambda checked, s=size: self.set_undocked_font_size(s))
            undocked_font_menu.addAction(action)

        # History Limit Submenu
        history_menu = menu.addMenu("History Limit")
        for limit in [10, 20, 30]:
            action = QAction(f"{limit} Items", self)
            action.setCheckable(True)
            action.setChecked(self.max_items == limit)
            action.triggered.connect(lambda checked, l=limit: self.set_history_limit(l))
            history_menu.addAction(action)

        menu.addSeparator()

        manage_folders_action = QAction("Manage Folders", self)
        manage_folders_action.triggered.connect(self.manage_folders)
        menu.addAction(manage_folders_action)

        clear_unpinned_action = QAction("Clear Unpinned", self)
        clear_unpinned_action.triggered.connect(self.clear_unpinned)
        menu.addAction(clear_unpinned_action)

        clear_all_action = QAction("Clear All", self)
        clear_all_action.triggered.connect(self.clear_all)
        menu.addAction(clear_all_action)
            
        # Show menu below the button
        menu.exec(self.options_btn.mapToGlobal(QPoint(0, self.options_btn.height())))

    @Slot()
    def save_history(self):
        """Saves clipboard history to a JSON file."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.clipboard_history, f, indent=4)
        except OSError as e:
            print(f"Failed to save history: {e}")

    def toggle_dark_mode(self, checked):
        self.dark_mode = checked
        self.save_settings()
        self.apply_theme()
        self.update_list_widget()

    def toggle_top_pins(self, checked):
        self.top_pins = checked
        if self.top_pins:
            self.sort_history()
        self.save_settings()
        self.update_list_widget()

    def toggle_sort_mode(self, checked):
        self.sort_mode = checked
        self.save_settings()
        if self.sort_mode:
            self.temp_sort_mode = False
        self.set_drag_drop_state(self.sort_mode or self.temp_sort_mode)

    def set_drag_drop_state(self, enabled):
        if enabled:
            self.list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
            self.list_widget.setDragEnabled(True)
            self.list_widget.setAcceptDrops(True)
            self.list_widget.setDropIndicatorShown(True)
            self.list_widget.setDragDropMode(QAbstractItemView.InternalMove)
        else:
            self.list_widget.setSelectionMode(QAbstractItemView.NoSelection)
            self.list_widget.setDragDropMode(QAbstractItemView.NoDragDrop)
            self.list_widget.setDragEnabled(False)
            self.list_widget.setAcceptDrops(False)
            self.list_widget.clearSelection()


    def sort_history(self):
        """Sorts history to keep pinned items at the top if enabled."""
        if self.top_pins:
            pinned_folders = [item for item in self.clipboard_history if item.get('type') == 'folder' and item.get('pinned', False)]
            pinned_items = [item for item in self.clipboard_history if item.get('type') == 'item' and item.get('keep', False)]
            
            pinned_ids = {item['id'] for item in pinned_folders} | {item['id'] for item in pinned_items}
            
            other_items = [item for item in self.clipboard_history if item['id'] not in pinned_ids]
            
            self.clipboard_history = pinned_folders + pinned_items + other_items
    def set_docked_font_size(self, size):
        self.docked_font_size = size
        self.save_settings()
        if self.appbar_registered:
            self.update_items_layout(docked=True)

    def set_undocked_font_size(self, size):
        self.undocked_font_size = size
        self.save_settings()
        if not self.appbar_registered:
            self.update_items_layout(docked=False)

    def set_history_limit(self, limit):
        self.max_items = limit
        self.save_settings()
        # Trim history if needed
        if len(self.clipboard_history) > self.max_items:
            for i in range(len(self.clipboard_history) - 1, -1, -1):
                if len(self.clipboard_history) <= self.max_items:
                    break
                if not self.clipboard_history[i].get('keep', False) and self.clipboard_history[i].get('type', 'item') != 'folder':
                    del self.clipboard_history[i]
            self.save_history()
            self.update_list_widget()

    def add_clipboard_item(self, text):
        """Adds a new item to the clipboard history and updates the UI."""
        # Avoid adding duplicates if the same item is already at the top
        if self.clipboard_history and self.clipboard_history[0].get('text') == text:
            return

        # If the list is full, remove the oldest non-kept item
        if len(self.clipboard_history) >= self.max_items:
            removed_item = False
            # Iterate from the oldest (end of list) to find an item to remove
            for i in range(len(self.clipboard_history) - 1, -1, -1):
                if not self.clipboard_history[i].get('keep', False) and self.clipboard_history[i].get('type', 'item') != 'folder':
                    del self.clipboard_history[i]
                    removed_item = True
                    break
            # If all items are 'kept', we can't add the new one
            if not removed_item:
                print("Clipboard history is full and all items are kept. New item not added.")
                return

        # Add the new item to the top of the list (index 0)
        new_item_data = {'id': str(uuid.uuid4()), 'type': 'item', 'text': text, 'keep': False, 'parent_id': None}
        self.clipboard_history.insert(0, new_item_data)

        if self.top_pins:
            self.sort_history()

        self.save_history()
        self.update_list_widget()

    def update_list_widget(self):
        """Clears and repopulates the list widget from the history data."""
        self.list_widget.clear()

        items_by_parent = {None: []}
        for item in self.clipboard_history:
            if item.get('type') == 'folder':
                if item['id'] not in items_by_parent:
                    items_by_parent[item['id']] = []
            
            parent_id = item.get('parent_id')
            if parent_id not in items_by_parent:
                items_by_parent[parent_id] = []
            
            # This logic is to handle items whose parents were deleted
            if item.get('type') == 'item' and parent_id and parent_id not in [f['id'] for f in self.clipboard_history if f.get('type') == 'folder']:
                item['parent_id'] = None
                parent_id = None

            # Add folders to top level
            if item.get('type') == 'folder':
                 items_by_parent[None].append(item)
            # Add items to their parent, or top level
            elif item.get('type') == 'item':
                items_by_parent[parent_id].append(item)

        # This is a bit of a hack to keep the original order as much as possible
        # We rebuild a flat list that respects the folder hierarchy for display
        display_order = []
        temp_history = sorted(self.clipboard_history, key=lambda x: (x.get('parent_id') is not None, self.clipboard_history.index(x)))

        for item_data in temp_history:
            if item_data.get('parent_id') is None:
                display_order.append(item_data)
                if item_data.get('type') == 'folder' and not item_data.get('collapsed'):
                    children = [child for child in temp_history if child.get('parent_id') == item_data['id']]
                    display_order.extend(children)

        for i, item_data in enumerate(display_order):
            self.create_widget_for_item(item_data, i)

    def create_widget_for_item(self, item_data, index):
        list_item = QListWidgetItem(self.list_widget)
        
        is_pinned_folder = item_data.get('type') == 'folder' and item_data.get('pinned', False)

        if item_data.get('type') == 'folder':
            list_item.setFlags(list_item.flags() | Qt.ItemIsDropEnabled)
        else:
            list_item.setFlags(list_item.flags() & ~Qt.ItemIsDropEnabled)

        # Disable dragging for pinned folders
        if is_pinned_folder:
            list_item.setFlags(list_item.flags() & ~Qt.ItemIsDragEnabled)

        custom_widget = ClipboardItemWidget(item_data, self.list_widget)
        
        font_size = self.docked_font_size if self.appbar_registered else self.undocked_font_size
        custom_widget.set_docked(self.appbar_registered, index=index, font_size=font_size)
        
        custom_widget.paste_requested.connect(self.paste_item)
        custom_widget.delete_requested.connect(self.delete_item)
        custom_widget.keep_toggled.connect(self.on_keep_toggled)
        custom_widget.folder_toggled.connect(self.on_folder_toggled)
        custom_widget.folder_pinned.connect(self.on_folder_pinned)
        custom_widget.item_edited.connect(self.save_history)
        
        list_item.setSizeHint(custom_widget.sizeHint())
        
        self.list_widget.addItem(list_item)
        self.list_widget.setItemWidget(list_item, custom_widget)

    @Slot(QListWidgetItem)
    def on_item_clicked(self, list_item):
        widget = self.list_widget.itemWidget(list_item)
        if not widget: return
        item_data = widget.item_data

        if item_data.get('type') == 'folder':
            self.on_folder_toggled(item_data)
        elif not (self.sort_mode or self.temp_sort_mode):
            self.paste_item(item_data.get('text', ''))
        # In sort mode, clicking just selects, so we do nothing here.

    @Slot(dict)
    def on_keep_toggled(self):
        """Handle keep toggle to resort if necessary."""
        if self.top_pins:
            self.sort_history()
            self.update_list_widget()
        self.save_history()

    @Slot()
    def on_folder_pinned(self):
        """Handle folder pin toggle to resort if necessary."""
        if self.top_pins:
            self.sort_history()
            self.update_list_widget()
        self.save_history()

    @Slot(dict)
    def on_folder_toggled(self, item_data):
        for item in self.clipboard_history:
            if item['id'] == item_data['id']:
                item['collapsed'] = not item.get('collapsed', True)
                break
        self.save_history()
        self.update_list_widget()

    @Slot()
    def clear_all(self):
        """Clears all items from the history except folders."""
        self.clipboard_history = [item for item in self.clipboard_history if item.get('type') == 'folder']
        try:
            self.last_clipboard_content = QGuiApplication.clipboard().text()
        except Exception:
            pass
        self.save_history()
        self.update_list_widget()

    def clear_unpinned(self):
        """Clears unpinned items except folders."""
        self.clipboard_history = [item for item in self.clipboard_history if item.get('keep', False) or item.get('type') == 'folder']
        try:
            self.last_clipboard_content = QGuiApplication.clipboard().text()
        except Exception:
            pass
        self.save_history()
        self.update_list_widget()

    @Slot(list, str)
    def on_items_dropped_in_folder(self, dragged_data, folder_id):
        dragged_ids = {d['id'] for d in dragged_data}
        for item in self.clipboard_history:
            if item['id'] in dragged_ids:
                item['parent_id'] = folder_id
        self.save_history()
        self.update_list_widget()

    @Slot(dict)
    def delete_item(self, item_data):
        """Removes an item from history."""
        if item_data in self.clipboard_history:
            self.clipboard_history.remove(item_data)
            self.save_history()
            self.update_list_widget()

    @Slot(str)
    def paste_item(self, text_to_paste):
        """Pastes the selected text into the previously active window."""
        self.is_pasting = True
        self.hide()
        
        # Give focus back to the previous window (a small delay helps)
        time.sleep(0.1)

        try:
            # Save current clipboard, set it to the desired text, paste, and restore
            original_clipboard = pyperclip.paste()
            pyperclip.copy(text_to_paste)
            
            # Simulate Ctrl+V
            pyautogui.hotkey('ctrl', 'v')
            
            # Restore original clipboard content after a short delay
            time.sleep(0.1)
            pyperclip.copy(original_clipboard)

        except Exception as e:
            print(f"Error during paste operation: {e}")
        finally:
            # Process events to ensure clipboard is restored before we check it again
            QCoreApplication.processEvents()
            self.show()
            self.is_pasting = False
    
    def manage_folders(self):
        dialog = FolderManagerDialog(self)
        dialog.exec()
        self.save_history()
        self.update_list_widget()

    def move_item_to_folder(self, item_data, parent_id):
        for item in self.clipboard_history:
            if item['id'] == item_data['id']:
                item['parent_id'] = parent_id
                break
        self.save_history()
        self.update_list_widget()

    def rebuild_history_from_view(self):
        if not self.sort_mode:
            return

        # Get the new visual order of items from the QListWidget
        visible_items_in_new_order = [self.list_widget.itemWidget(self.list_widget.item(i)).item_data for i in range(self.list_widget.count())]
        visible_ids = {item['id'] for item in visible_items_in_new_order}

        # Get a map of all items from the old history for quick lookup
        old_history_map = {item['id']: item for item in self.clipboard_history}

        new_history = []
        processed_ids = set()
        current_parent_id = None

        # Iterate through the new visual order and reconstruct the list
        for visible_item_spec in visible_items_in_new_order:
            item_id = visible_item_spec['id']
            if item_id in processed_ids:
                continue

            item = old_history_map[item_id]
            
            if item.get('type') == 'folder':
                item['parent_id'] = None # Folders are always top level
                current_parent_id = item['id'] if not item.get('collapsed') else None
            else:
                item['parent_id'] = current_parent_id

            new_history.append(item)
            processed_ids.add(item_id)

            # If a folder is collapsed, its children were not in the visual list, so we need to find them and add them back
            if item.get('type') == 'folder' and item.get('collapsed'):
                children = [child for child in self.clipboard_history if child.get('parent_id') == item_id]
                for child in children:
                    if child['id'] not in processed_ids:
                        new_history.append(child)
                        processed_ids.add(child['id'])

        self.clipboard_history = new_history
        self.save_history()

    def closeEvent(self, event):
        """Ensure we unregister the appbar when closing."""
        self.save_settings()
        self.clipboard_timer.stop()
        if self.appbar_registered:
            self.unregister_appbar()
        super().closeEvent(event)
        QCoreApplication.quit()

    def enterEvent(self, event):
        """Raise window to front on mouse-over."""
        self.raise_()
        super().enterEvent(event)

    def show_app_context_menu(self, pos):
        """Shows context menu for the app (dock/undock, close) on background click."""
        if self.list_widget.itemAt(pos):
            return
        
        menu = QMenu(self)
        if self.appbar_registered:
            dock_action = QAction("Undock", self)
            dock_action.triggered.connect(self.undock_window)
        else:
            dock_action = QAction("Dock to Top", self)
            dock_action.triggered.connect(self.dock_window)
        menu.addAction(dock_action)
        
        clear_action = QAction("Clear All", self)
        clear_action.triggered.connect(self.clear_all)
        menu.addAction(clear_action)

        clear_unpinned_action = QAction("Clear Unpinned", self)
        clear_unpinned_action.triggered.connect(self.clear_unpinned)
        menu.addAction(clear_unpinned_action)
        
        close_action = QAction("Close", self)
        close_action.triggered.connect(self.close)
        menu.addAction(close_action)
        
        menu.exec(self.list_widget.mapToGlobal(pos))

    def dock_window(self):
        """Docks the window to the top of the screen and reserves space."""
        self.saved_geometry = self.geometry()
        
        # Switch to horizontal layout
        self.layout().setDirection(QBoxLayout.LeftToRight)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.options_btn.hide()
        
        # Configure list for horizontal row
        self.list_widget.setFlow(QListWidget.LeftToRight)
        self.list_widget.setWrapping(False)
        self.list_widget.setSpacing(0)
        self.list_widget.setFrameShape(QFrame.NoFrame)
        self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFixedHeight(40)
        self.list_widget.setStyleSheet("""
            QListWidget { background-color: #2b2b2b; border: none; }
            QListWidget::item { border: none; background: transparent; }
        """)
        
        self.update_items_layout(docked=True)

        # Remove frame and keep on top
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.show() # Must show to ensure valid HWND
        self.register_appbar()

    def undock_window(self):
        """Restores the window to its floating state."""
        self.unregister_appbar()
        
        # Restore vertical layout
        self.layout().setDirection(QBoxLayout.TopToBottom)
        self.layout().setContentsMargins(11, 11, 11, 11)
        self.options_btn.show()
        
        # Restore list
        self.list_widget.setFlow(QListWidget.TopToBottom)
        self.list_widget.setWrapping(False)
        self.list_widget.setSpacing(0)
        self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.apply_theme() # Re-apply theme to restore borders and colors
        
        self.setMinimumHeight(0)
        self.setMaximumHeight(16777215)
        
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)
        if hasattr(self, 'saved_geometry'):
            self.setGeometry(self.saved_geometry)
            
        self.toggle_sort_mode(self.sort_mode) # Re-apply sort mode settings
        self.update_items_layout(docked=False)
        self.show()

    def update_items_layout(self, docked):
        """Updates all list items to match the docked state."""
        font_size = self.docked_font_size if docked else self.undocked_font_size
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            widget = self.list_widget.itemWidget(item)
            if widget:
                widget.set_docked(docked, index=i, font_size=font_size)
                widget.adjustSize()
                item.setSizeHint(widget.sizeHint())
        self.list_widget.doItemsLayout()

    def register_appbar(self):
        """Registers the window as an AppBar using Windows API."""
        if self.appbar_registered:
            return

        hwnd = int(self.winId())
        abd = APPBARDATA()
        abd.cbSize = ctypes.sizeof(APPBARDATA)
        abd.hWnd = hwnd
        abd.uEdge = ABE_TOP

        # 1. Register new AppBar
        ctypes.windll.shell32.SHAppBarMessage(ABM_NEW, ctypes.byref(abd))

        # 2. Request Position and Size
        screen_width = ctypes.windll.user32.GetSystemMetrics(0)
        abd.rc.left = 0
        abd.rc.top = 0
        abd.rc.right = screen_width
        abd.rc.bottom = self.height()

        # 3. Query and Set Position (System adjusts rc.top/bottom if needed)
        ctypes.windll.shell32.SHAppBarMessage(ABM_QUERYPOS, ctypes.byref(abd))
        abd.rc.bottom = abd.rc.top + self.height() # Force our height
        ctypes.windll.shell32.SHAppBarMessage(ABM_SETPOS, ctypes.byref(abd))

        # 4. Move Window to final reserved space
        self.setGeometry(abd.rc.left, abd.rc.top, abd.rc.right - abd.rc.left, abd.rc.bottom - abd.rc.top)
        self.appbar_registered = True

    def unregister_appbar(self):
        """Unregisters the AppBar, releasing the screen space."""
        if not self.appbar_registered:
            return
            
        hwnd = int(self.winId())
        abd = APPBARDATA()
        abd.cbSize = ctypes.sizeof(APPBARDATA)
        abd.hWnd = hwnd
        
        ctypes.windll.shell32.SHAppBarMessage(ABM_REMOVE, ctypes.byref(abd))
        self.appbar_registered = False

def main():
    # This attribute can help prevent "SetProcessDpiAwarenessContext() failed: Access is denied"
    # errors when the application is launched from another process (like the main WYSIWYG tool)
    # that has already set the DPI awareness for the process tree. We are telling Qt not to
    # try and manage DPI scaling itself in this case.
    # QCoreApplication.setAttribute(Qt.AA_DisableHighDpiScaling) # Deprecated in Qt6
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    main_window = ClipTrayApp()
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
def main():
    # This attribute can help prevent "SetProcessDpiAwarenessContext() failed: Access is denied"
    # errors when the application is launched from another process (like the main WYSIWYG tool)
    # that has already set the DPI awareness for the process tree. We are telling Qt not to
    # try and manage DPI scaling itself in this case.
    # QCoreApplication.setAttribute(Qt.AA_DisableHighDpiScaling) # Deprecated in Qt6
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    main_window = ClipTrayApp()
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
