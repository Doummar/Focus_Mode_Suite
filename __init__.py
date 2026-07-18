# Focus Mode Suite
# Created by Adel Aitah
# GitHub: https://github.com/Doummar/Focus_Mode_Suite
# Copyright (c) 2026 Adel Aitah — All rights reserved
"""
Focus Mode Suite — distraction-free study environment
Hides menu bar, toolbars, and status bar automatically during study.
Configurable shortcut and auto-hide behaviors.
"""

from aqt import mw, gui_hooks
from aqt.qt import *

ADDON_NAME = "Focus Mode Suite"
ADDON_AUTHOR  = "Adel Aitah"
ADDON_VERSION = "1.0.0"
ADDON_URL     = "https://github.com/Doummar/Focus_Mode_Suite"
HANDLE = 12

# ── Config ────────────────────────────────────────────────────────────────────
import os

# Setup PyQt imports safely across PyQt5 and PyQt6
try:
    from PyQt6.QtGui import QAction, QKeySequence, QShortcut
    from PyQt6.QtCore import QTimer, Qt
    from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox
except ImportError:
    try:
        from PyQt5.QtWidgets import QAction, QShortcut, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox
        from PyQt5.QtGui import QKeySequence
        from PyQt5.QtCore import QTimer, Qt
    except ImportError:
        try:
            from PyQt6.QtWidgets import QAction, QShortcut, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox
            from PyQt6.QtGui import QKeySequence
            from PyQt6.QtCore import QTimer, Qt
        except ImportError:
            from aqt.qt import QAction, QKeySequence, QTimer, QShortcut, Qt, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox

# --- Configuration Settings ---
SHORTCUT_KEY = "F11"       # Keyboard shortcut to toggle focus mode
HIDE_TOP_BAR = True         # Hide the top menu and toolbars
HIDE_BOTTOM_BAR = True      # Hide the bottom sync/status bar
AUTO_HIDE_ON_STUDY = True   # Automatically enter focus mode when study begins
THREE_STEP_TOGGLE = True    # Cycle: Standard -> Ultra (Hide Card Template Top Header) -> Disabled
STARTING_STATE = 1          # 1 = Standard Focus, 2 = Ultra Focus

# Load configuration settings from Anki's configuration manager if available
try:
    _config = mw.addonManager.getConfig(__name__)
    if _config:
        SHORTCUT_KEY = _config.get("shortcut_key", SHORTCUT_KEY)
        HIDE_TOP_BAR = _config.get("hide_top_bar", HIDE_TOP_BAR)
        HIDE_BOTTOM_BAR = _config.get("hide_bottom_bar", HIDE_BOTTOM_BAR)
        AUTO_HIDE_ON_STUDY = _config.get("auto_hide_on_study", AUTO_HIDE_ON_STUDY)
        THREE_STEP_TOGGLE = _config.get("three_step_toggle", THREE_STEP_TOGGLE)
        STARTING_STATE = _config.get("starting_state", STARTING_STATE)
except Exception as _e:
    print(f"Focus Mode: Error loading configuration: {_e}")

# Focus Mode state tracker (0 = Disabled, 1 = Standard, 2 = Ultra)
focus_mode_state = STARTING_STATE
_current_applied_state = None

def update_card_top_side_visibility():
    """Dynamically hides or shows the card template's top bar in real-time on the current card."""
    if not (hasattr(mw, "reviewer") and mw.reviewer and hasattr(mw.reviewer, "web") and mw.reviewer.web):
        return
    
    if focus_mode_state == 2:
        # Ultra mode: Inject CSS style sheet and programmatically hide top template distraction headers
        js = """
        (function() {
            var style = document.getElementById("focus-mode-dynamic-hide");
            if (!style) {
                style = document.createElement("style");
                style.id = "focus-mode-dynamic-hide";
                style.innerHTML = ".top-header, .stats-bar, #header, #stats, .anki-header, .card-stats-bar, .timer, .clock, .progress-bar, .header, .card-header, .card-top, .stats, .deck-name, .deck-info, .timer-bar, .time, .clock-bar, .indicator, .indicators, .count, .counts, .counter, .counters, .remaining, .left, .pomodoro, #pomodoro, .pomodoro-timer, #pomodoro-timer, .pomodoro_timer, #pomodoro_timer, .pomodoro-clock, #focus-mode-front-hide, .pomodoro_clock, #pomodoro_clock, .pomodoro-counter, #pomodoro-counter, .pomodoro_counter, #pomodoro_counter, .pomodoro-indicator, #pomodoro-indicator, .pomodoro_indicator, #pomodoro_indicator, .pomodoro-dot, #pomodoro-dot, .pomodoro_dot, #pomodoro_dot, .minimalistic-pomodoro, .minimalist-pomodoro, #minimalistic-pomodoro, #minimalist-pomodoro, .pomo-timer, #pomo-timer, .pomo-clock, #pomo-clock, .pomo-counter, #pomo-counter, .pomodoro-container, #pomodoro-container, .anki-pomodoro, #anki-pomodoro, .pomodoro-count, #pomodoro-count, .pomodoro-remaining, #pomodoro-remaining, .pomo, #pomo, .pomodoro-box, #pomodoro-box, .pomodoro_box, #pomodoro_box, .pomodoro-stats, #pomodoro-stats, .pomodoro-stat, #pomodoro-stat { display: none !important; }";
                document.head.appendChild(style);
            }
            
            // Programmatically hide matching elements with ultra-optimized target selector (no heavy tag scans!)
            try {
                var els = document.querySelectorAll('.top-header, .stats-bar, #header, #stats, .anki-header, .card-stats-bar, .timer, .clock, .progress-bar, .header, .card-header, .card-top, .stats, .deck-name, .deck-info, .timer-bar, .time, .clock-bar, .indicator, .indicators, .count, .counts, .counter, .counters, .remaining, .left, .pomodoro, #pomodoro, .pomodoro-timer, #pomodoro-timer, .pomodoro_timer, #pomodoro_timer, .pomodoro-clock, #focus-mode-front-hide, .pomodoro_clock, #pomodoro_clock, .pomodoro-counter, #pomodoro-counter, .pomodoro_counter, #pomodoro_counter, .pomodoro-indicator, #pomodoro-indicator, .pomodoro_indicator, #pomodoro_indicator, .pomodoro-dot, #pomodoro-dot, .pomodoro_dot, #pomodoro_dot, .minimalistic-pomodoro, .minimalist-pomodoro, #minimalistic-pomodoro, #minimalist-pomodoro, .pomo-timer, #pomo-timer, .pomo-clock, #pomo-clock, .pomo-counter, #pomo-counter, .pomodoro-container, #pomodoro-container, .anki-pomodoro, #anki-pomodoro, .pomodoro-count, #pomodoro-count, .pomodoro-remaining, #pomodoro-remaining, .pomo, #pomo, .pomodoro-box, #pomodoro-box, .pomodoro_box, #pomodoro_box, .pomodoro-stats, #pomodoro-stats, .pomodoro-stat, #pomodoro-stat, [id*="timer" i], [class*="timer" i], [id*="clock" i], [class*="clock" i], [id*="pomo" i], [class*="pomo" i], [id*="counter" i], [class*="counter" i], [id*="progress" i], [class*="progress" i]');
                for (var i = 0; i < els.length; i++) {
                    var el = els[i];
                    if (!el || el.id === "qa" || el.tagName === "BODY" || el.tagName === "HTML") continue;
                    if (el.style.display !== "none") {
                        el.style.setProperty("display", "none", "important");
                    }
                }
            } catch(err) {}
        })();
        """
    else:
        # Standard or Disabled: Remove dynamic hide style sheet
        js = """
        (function() {
            var style = document.getElementById("focus-mode-dynamic-hide");
            if (style) {
                style.remove();
            }
            
            // Programmatically restore hidden elements with ultra-optimized target selector
            try {
                var els = document.querySelectorAll('.top-header, .stats-bar, #header, #stats, .anki-header, .card-stats-bar, .timer, .clock, .progress-bar, .header, .card-header, .card-top, .stats, .deck-name, .deck-info, .timer-bar, .time, .clock-bar, .indicator, .indicators, .count, .counts, .counter, .counters, .remaining, .left, .pomodoro, #pomodoro, .pomodoro-timer, #pomodoro-timer, .pomodoro_timer, #pomodoro_timer, .pomodoro-clock, #focus-mode-front-hide, .pomodoro_clock, #pomodoro_clock, .pomodoro-counter, #pomodoro-counter, .pomodoro_counter, #pomodoro_counter, .pomodoro-indicator, #pomodoro-indicator, .pomodoro_indicator, #pomodoro_indicator, .pomodoro-dot, #pomodoro-dot, .pomodoro_dot, #pomodoro_dot, .minimalistic-pomodoro, .minimalist-pomodoro, #minimalistic-pomodoro, #minimalist-pomodoro, .pomo-timer, #pomo-timer, .pomo-clock, #pomo-clock, .pomo-counter, #pomo-counter, .pomodoro-container, #pomodoro-container, .anki-pomodoro, #anki-pomodoro, .pomodoro-count, #pomodoro-count, .pomodoro-remaining, #pomodoro-remaining, .pomo, #pomo, .pomodoro-box, #pomodoro-box, .pomodoro_box, #pomodoro_box, .pomodoro-stats, #pomodoro-stats, .pomodoro-stat, #pomodoro-stat, [id*="timer" i], [class*="timer" i], [id*="clock" i], [class*="clock" i], [id*="pomo" i], [class*="pomo" i], [id*="counter" i], [class*="counter" i], [id*="progress" i], [class*="progress" i]');
                for (var i = 0; i < els.length; i++) {
                    var el = els[i];
                    if (el && el.style && el.style.display === "none") {
                        el.style.removeProperty("display");
                    }
                }
            } catch(err) {}
        })();
        """
    
    try:
        mw.reviewer.web.eval(js)
    except Exception:
        try:
            mw.reviewer.web.page().runJavaScript(js)
        except Exception:
            pass

def on_card_will_show(text: str, card, kind: str) -> str:
    """Stabilizes or hides any custom clocks/stats bars built into card templates."""
    if focus_mode_state == 2 and HIDE_TOP_BAR:
        hide_css = """
<style id="focus-mode-stabilizer">
.top-header, .stats-bar, #header, #stats, .anki-header, .card-stats-bar, .timer, .clock, .progress-bar, .header, .card-header, .card-top, .stats, .deck-name, .deck-info, .timer-bar, .time, .clock-bar, .indicator, .indicators, .count, .counts, .counter, .counters, .remaining, .left, .pomodoro, #pomodoro, .pomodoro-timer, #pomodoro-timer, .pomodoro_timer, #pomodoro_timer, .pomodoro-clock, #pomodoro-clock, .pomodoro_clock, #pomodoro_clock, .pomodoro-counter, #pomodoro-counter, .pomodoro_counter, #pomodoro_counter, .pomodoro-indicator, #pomodoro-indicator, .pomodoro_indicator, #pomodoro_indicator, .pomodoro-dot, #pomodoro-dot, .pomodoro_dot, #pomodoro_dot, .minimalistic-pomodoro, .minimalist-pomodoro, #minimalistic-pomodoro, #minimalist-pomodoro, .pomo-timer, #pomo-timer, .pomo-clock, #pomo-clock, .pomo-counter, #pomo-counter, .pomodoro-container, #pomodoro-container, .anki-pomodoro, #anki-pomodoro, .pomodoro-count, #pomodoro-count, .pomodoro-remaining, #pomodoro-remaining, .pomo, #pomo, .pomodoro-box, #pomodoro-box, .pomodoro_box, #pomodoro_box, .pomodoro-stats, #pomodoro-stats, .pomodoro-stat, #pomodoro-stat {
    display: none !important;
}
</style>
<script>
(function() {
    function hideTopElements() {
        try {
            var els = document.querySelectorAll('.top-header, .stats-bar, #header, #stats, .anki-header, .card-stats-bar, .timer, .clock, .progress-bar, .header, .card-header, .card-top, .stats, .deck-name, .deck-info, .timer-bar, .time, .clock-bar, .indicator, .indicators, .count, .counts, .counter, .counters, .remaining, .left, .pomodoro, #pomodoro, .pomodoro-timer, #pomodoro-timer, .pomodoro_timer, #pomodoro_timer, .pomodoro-clock, #pomodoro-clock, .pomodoro_clock, #pomodoro_clock, .pomodoro-counter, #pomodoro-counter, .pomodoro_counter, #pomodoro_counter, .pomodoro-indicator, #pomodoro-indicator, .pomodoro_indicator, #pomodoro_indicator, .pomodoro-dot, #pomodoro-dot, .pomodoro_dot, #pomodoro_dot, .minimalistic-pomodoro, .minimalist-pomodoro, #minimalistic-pomodoro, #minimalist-pomodoro, .pomo-timer, #pomo-timer, .pomo-clock, #pomo-clock, .pomo-counter, #pomo-counter, .pomodoro-container, #pomodoro-container, .anki-pomodoro, #anki-pomodoro, .pomodoro-count, #pomodoro-count, .pomodoro-remaining, #pomodoro-remaining, .pomo, #pomo, .pomodoro-box, #pomodoro-box, .pomodoro_box, #pomodoro_box, .pomodoro-stats, #pomodoro-stats, .pomodoro-stat, #pomodoro-stat, [id*="timer" i], [class*="timer" i], [id*="clock" i], [class*="clock" i], [id*="pomo" i], [class*="pomo" i], [id*="counter" i], [class*="counter" i], [id*="progress" i], [class*="progress" i]');
            for (var i = 0; i < els.length; i++) {
                var el = els[i];
                if (!el || el.id === "qa" || el.tagName === "BODY" || el.tagName === "HTML") continue;
                if (el.style.display !== "none") {
                    el.style.setProperty("display", "none", "important");
                }
            }
        } catch(err) {}
    }
    
    hideTopElements();
    setTimeout(hideTopElements, 50);
    setTimeout(hideTopElements, 250);
})();
</script>
"""
        return hide_css + text
    elif focus_mode_state == 1 and HIDE_TOP_BAR:
        stable_css = """
<style id="focus-mode-stabilizer">
/* Prevent custom template header, timer, clock, progress bars, or stats from fading, animating, or flashing on flip */
.top-header, .stats-bar, #header, #stats, .anki-header, .card-stats-bar, .timer, .clock, .progress-bar, .header, .card-header, .card-top, .stats, .deck-name, .deck-info, .timer-bar, .time, .clock-bar, .indicator, .indicators, .count, .counts, .counter, .counters, .remaining, .left, .pomodoro, #pomodoro, .pomodoro-timer, #pomodoro-timer, .pomodoro_timer, #pomodoro_timer, .pomodoro-clock, #focus-mode-front-hide, .pomodoro_clock, #pomodoro_clock, .pomodoro-counter, #pomodoro-counter, .pomodoro_counter, #pomodoro_counter, .pomodoro-indicator, #pomodoro-indicator, .pomodoro_indicator, #pomodoro_indicator, .pomodoro-dot, #pomodoro-dot, .pomodoro_dot, #pomodoro_dot, .minimalistic-pomodoro, .minimalist-pomodoro, #minimalistic-pomodoro, #minimalist-pomodoro, .pomo-timer, #pomo-timer, .pomo-clock, #pomo-clock, .pomo-counter, #pomo-counter, .pomodoro-container, #pomodoro-container, .anki-pomodoro, #anki-pomodoro, .pomodoro-count, #pomodoro-count, .pomodoro-remaining, #pomodoro-remaining, .pomo, #pomo, .pomodoro-box, #pomodoro-box, .pomodoro_box, #pomodoro_box, .pomodoro-stats, #pomodoro-stats, .pomodoro-stat, #pomodoro-stat {
    transition: none !important;
    animation: none !important;
    opacity: 1 !important;
    transform: none !important;
}
</style>
"""
        return stable_css + text
    return text

def set_focus_mode_visible(enabled: bool):
    """Controls the visibility of the Anki main interface bars with anti-flicker protection."""
    global _current_applied_state
    
    # Redundant trigger prevention to completely avoid flickering/re-fading during card flip
    state_key = (enabled, focus_mode_state)
    if _current_applied_state == state_key:
        return
    _current_applied_state = state_key

    # Toggle Full Screen in Ultra Focus Mode to hide operating system title bar
    try:
        if enabled and focus_mode_state == 2 and HIDE_TOP_BAR:
            if not mw.isFullScreen():
                mw._was_maximized = mw.isMaximized()
                mw.showFullScreen()
        else:
            if mw.isFullScreen():
                if hasattr(mw, "_was_maximized") and mw._was_maximized:
                    mw.showMaximized()
                else:
                    mw.showNormal()
    except Exception as e:
        print(f"Focus Mode: Error toggling fullscreen/titlebar: {e}")

    # Prevent bright/gray flashes during layout redraws by dynamically setting the main window background 
    # to perfectly match Anki's active dark or light theme background color!
    try:
        from aqt.theme import theme_manager
        is_dark = theme_manager.night_mode
    except Exception:
        is_dark = False
    
    bg_color = "#2f2f2f" if is_dark else "#ffffff"
    try:
        mw.setStyleSheet(f"QMainWindow {{ background-color: {bg_color}; }}")
    except Exception:
        pass

    # Clean layout margins and spacing of central widget to prevent thin white/gray border lines at edges
    try:
        layout = mw.centralWidget().layout()
        if layout:
            if not hasattr(mw, "_original_layout_margins"):
                try:
                    mw._original_layout_margins = layout.getContentsMargins()
                    mw._original_layout_spacing = layout.spacing()
                except Exception:
                    mw._original_layout_margins = (0, 0, 0, 0)
                    mw._original_layout_spacing = 0
            
            if enabled:
                layout.setSpacing(0)
                layout.setContentsMargins(0, 0, 0, 0)
            else:
                l, t, r, b = mw._original_layout_margins
                layout.setSpacing(mw._original_layout_spacing)
                layout.setContentsMargins(l, t, r, b)
    except Exception:
        pass

    # 1. Toggle Menu Bar (File, Edit, Tools, Help, etc.)
    if hasattr(mw, "form") and mw.form and hasattr(mw.form, "menuBar") and mw.form.menuBar:
        try:
            mw.form.menuBar.setVisible(not (enabled and HIDE_TOP_BAR))
        except Exception as e:
            print(f"Focus Mode: Error toggling menuBar: {e}")
            
    # Direct top-level menu bar hide (critical for modern Windows/Linux PyQt layout)
    try:
        if hasattr(mw, "menuBar") and callable(mw.menuBar) and mw.menuBar():
            mw.menuBar().setVisible(not (enabled and HIDE_TOP_BAR))
    except Exception as e:
        print(f"Focus Mode: Error toggling main QMainWindow menuBar: {e}")

    # 2. Toggle Top Toolbar (Decks, Add, Browse, Stats, Sync, etc.)
    toolbar_widgets = []
    if hasattr(mw, "toolbarWeb") and mw.toolbarWeb:
        toolbar_widgets.append(mw.toolbarWeb)
    if hasattr(mw, "toolbar") and mw.toolbar:
        if hasattr(mw.toolbar, "web") and mw.toolbar.web:
            toolbar_widgets.append(mw.toolbar.web)
        else:
            toolbar_widgets.append(mw.toolbar)
            
    # Recursively find any child QToolBars, QMenuBars and QDockWidgets to ensure third-party toolbar/sidebar addons are also hidden
    try:
        from PyQt6.QtWidgets import QToolBar, QMenuBar, QDockWidget
    except ImportError:
        try:
            from PyQt5.QtWidgets import QToolBar, QMenuBar, QDockWidget
        except ImportError:
            QToolBar = None
            QMenuBar = None
            QDockWidget = None

    if QToolBar:
        try:
            for toolbar in mw.findChildren(QToolBar):
                if toolbar not in toolbar_widgets:
                    toolbar_widgets.append(toolbar)
        except Exception as e:
            print(f"Focus Mode: Error finding child QToolBars: {e}")

    if QMenuBar:
        try:
            for menubar in mw.findChildren(QMenuBar):
                if menubar not in toolbar_widgets:
                    toolbar_widgets.append(menubar)
        except Exception as e:
            print(f"Focus Mode: Error finding child QMenuBars: {e}")

    if QDockWidget:
        try:
            for dock in mw.findChildren(QDockWidget):
                # Only hide dock widgets (sidebars) if Focus Mode is active and top bar hiding is enabled
                dock.setVisible(not (enabled and HIDE_TOP_BAR))
        except Exception as e:
            print(f"Focus Mode: Error toggling child QDockWidgets: {e}")
            
    for widget in toolbar_widgets:
        try:
            # Set QWebEngineView page background to transparent to completely prevent white/gray loading flashes
            if hasattr(widget, "page") and widget.page():
                try:
                    widget.page().setBackgroundColor(Qt.GlobalColor.transparent)
                except Exception:
                    try:
                        widget.page().setBackgroundColor(Qt.transparent)
                    except Exception:
                        pass
            
            # Smoothly transition opacity using JavaScript if it's a web view, to eliminate abrupt layout shifts
            if hasattr(widget, "page") and widget.page() and hasattr(widget.page(), "runJavaScript"):
                js_opacity = f"document.body.style.transition = 'opacity 0.2s ease-in-out'; document.body.style.opacity = '{'0' if (enabled and HIDE_TOP_BAR) else '1'}';"
                widget.page().runJavaScript(js_opacity)

            if hasattr(widget, "setVisible"):
                widget.setVisible(not (enabled and HIDE_TOP_BAR))
            elif hasattr(widget, "hide") and hasattr(widget, "show"):
                if enabled and HIDE_TOP_BAR:
                    widget.hide()
                else:
                    widget.show()
        except Exception as e:
            pass

    # 3. Toggle Bottom Toolbar / Sync bar
    bottom_widgets = []
    if hasattr(mw, "bottomWeb") and mw.bottomWeb:
        bottom_widgets.append(mw.bottomWeb)
    if hasattr(mw, "form") and mw.form and hasattr(mw.form, "statusBar") and mw.form.statusBar:
        bottom_widgets.append(mw.form.statusBar)
        
    for widget in bottom_widgets:
        try:
            # Prevent bottom bar flickering
            if hasattr(widget, "page") and widget.page():
                try:
                    widget.page().setBackgroundColor(Qt.GlobalColor.transparent)
                except Exception:
                    try:
                        widget.page().setBackgroundColor(Qt.transparent)
                    except Exception:
                        pass

            if hasattr(widget, "page") and widget.page() and hasattr(widget.page(), "runJavaScript"):
                js_opacity = f"document.body.style.transition = 'opacity 0.2s ease-in-out'; document.body.style.opacity = '{'0' if (enabled and HIDE_BOTTOM_BAR) else '1'}';"
                widget.page().runJavaScript(js_opacity)

            if hasattr(widget, "setVisible"):
                widget.setVisible(not (enabled and HIDE_BOTTOM_BAR))
            elif hasattr(widget, "hide") and hasattr(widget, "show"):
                if enabled and HIDE_BOTTOM_BAR:
                    widget.hide()
                else:
                    widget.show()
        except Exception as e:
            print(f"Focus Mode: Error toggling bottom widget: {e}")

    # 4. Find and toggle custom third-party add-on widgets (clocks, Pomodoro timers, stats)
    try:
        from PyQt6.QtWidgets import QWidget, QLabel
    except ImportError:
        try:
            from PyQt5.QtWidgets import QWidget, QLabel
        except ImportError:
            QWidget = None
            QLabel = None

    if QWidget:
        # Lazy scan and cache third-party widgets once per review session to avoid extremely heavy findChildren(QWidget) calls on every card flip!
        if not hasattr(mw, "_focus_mode_pomo_widgets") or mw._focus_mode_pomo_widgets is None:
            pomo_widgets = []
            try:
                for widget in mw.findChildren(QWidget):
                    # Avoid hiding critical Anki main UI containers and reviewers
                    class_name = widget.__class__.__name__.lower()
                    module_name = widget.__class__.__module__.lower() if hasattr(widget.__class__, "__module__") else ""
                    obj_name = widget.objectName().lower() if hasattr(widget, "objectName") else ""
                    
                    # Skip core widgets to prevent messing up Anki's main window structure
                    if widget == mw.reviewer.web or widget == mw.web or widget == mw.centralWidget():
                        continue
                    if class_name in ["qmainwindow", "qsplitter", "qstackedwidget", "qtabwidget", "ankidockwidget", "ankiwebview"]:
                        continue
                    
                    is_pomo_or_timer = False
                    
                    # Check class/module/object name for target terms
                    keywords = ["pomo", "pomodoro", "timer", "clock", "stat", "progress", "count", "remaining", "left", "shorsteka", "lucaspeixoto"]
                    for kw in keywords:
                        if kw in class_name or kw in module_name or kw in obj_name:
                            is_pomo_or_timer = True
                            break
                    
                    # Check label text for timer/counter patterns
                    if not is_pomo_or_timer and QLabel and isinstance(widget, QLabel):
                        try:
                            text = widget.text().strip().lower()
                            import re
                            if "left" in text or "●" in text or "remaining" in text or re.search(r'd+:d+', text):
                                is_pomo_or_timer = True
                        except Exception:
                            pass
                    
                    if is_pomo_or_timer:
                        pomo_widgets.append(widget)
            except Exception as e:
                print(f"Focus Mode: Error scanning third-party widgets: {e}")
            mw._focus_mode_pomo_widgets = pomo_widgets

        # Toggle visibility using the ultra-fast cache!
        try:
            valid_widgets = []
            for widget in mw._focus_mode_pomo_widgets:
                try:
                    # Verify C++ object still exists
                    if not widget or widget.parent() is None:
                        pass
                except (RuntimeError, AttributeError):
                    continue
                
                valid_widgets.append(widget)
                hide_widget = (enabled and focus_mode_state == 2)
                
                if hasattr(widget, "setVisible"):
                    widget.setVisible(not hide_widget)
                elif hasattr(widget, "hide") and hasattr(widget, "show"):
                    if hide_widget:
                        widget.hide()
                    else:
                        widget.show()
            # Update cache to filter out any deleted widgets
            mw._focus_mode_pomo_widgets = valid_widgets
        except Exception as e:
            print(f"Focus Mode: Error toggling cached widgets: {e}")

def delayed_hide():
    """Applies focus mode visibility settings if currently in review state."""
    global focus_mode_state
    if mw.state == "review":
        if focus_mode_state > 0:
            set_focus_mode_visible(True)
            # Dynamic top-side card template hiding on currently loaded card
            update_card_top_side_visibility()

def schedule_delayed_hide():
    """Schedules staggered hide calls to capture slower drawing / redrawing cycles."""
    global focus_mode_state
    if mw.state == "review":
        if focus_mode_state > 0:
            # Greatly optimized: Only schedule 2 lightweight timers instead of 6 heavy ones to keep Anki extremely fast!
            for delay in [50, 300]:
                QTimer.singleShot(delay, delayed_hide)

def on_state_did_change(new_state: str, old_state: str):
    """Called automatically when Anki's main window state changes."""
    global focus_mode_state, _current_applied_state
    
    _current_applied_state = None  # Force re-evaluation on screen/state transition
    # Reset widget cache on state transition so we get a fresh scan if study begins
    try:
        mw._focus_mode_pomo_widgets = None
    except Exception:
        pass
        
    # Enter Focus Mode automatically if we start studying/reviewing
    if new_state == "review":
        if AUTO_HIDE_ON_STUDY:
            focus_mode_state = STARTING_STATE  # Automatically activate default focus mode
            schedule_delayed_hide()
        else:
            focus_mode_state = 0
            set_focus_mode_visible(False)
            update_card_top_side_visibility()
    else:
        # Restore normal toolbars when returning to Deck List / Deck Browser
        set_focus_mode_visible(False)

def on_reviewer_state_changed(card=None):
    """Triggered during active reviewing to keep toolbars hidden with staggered delays."""
    global focus_mode_state
    if mw.state == "review":
        if focus_mode_state > 0:
            schedule_delayed_hide()

def toggle_focus_mode():
    """Toggles Focus Mode state manually and updates UI."""
    global focus_mode_state, _current_applied_state
    
    _current_applied_state = None  # Force re-evaluation
    
    # Cycle states: 0 -> 1 -> 2 -> 0 (if THREE_STEP_TOGGLE is True)
    if THREE_STEP_TOGGLE:
        focus_mode_state = (focus_mode_state + 1) % 3
    else:
        focus_mode_state = 0 if focus_mode_state > 0 else STARTING_STATE
    
    if mw.state == "review":
        if focus_mode_state > 0:
            schedule_delayed_hide()
        else:
            set_focus_mode_visible(False)
        
        # Real-time update of card top side elements
        update_card_top_side_visibility()
            
        from aqt.utils import tooltip
        if focus_mode_state == 2:
            tooltip("Focus Mode: Ultra (Card Header Hidden)")
        elif focus_mode_state == 1:
            tooltip("Focus Mode: Standard Enabled")
        else:
            tooltip("Focus Mode: Disabled")
    else:
        from aqt.utils import tooltip
        if focus_mode_state > 0:
            status_text = "Always Enable on Study"
        else:
            status_text = "Manual Toggle Only"
        tooltip(f"Focus Mode: {status_text}")

def init_focus_mode():
    """Initializes the shortcut action and adds it to the main window."""
    global focus_mode_state
    
    # Force restore standard toolbars on startup to prevent any stuck hidden states
    try:
        if mw.state != "review":
            set_focus_mode_visible(False)
    except Exception:
        pass

    # Safe startup full-screen restoration check:
    # If the user exited Anki while in the third (Ultra) mode, Anki's geometry manager
    # might save the window state as full-screen. Upon restarting, we must automatically
    # restore standard maximized/normal layout if focus mode is not actively ultra.
    def startup_fullscreen_check():
        try:
            if mw.isFullScreen() and (mw.state != "review" or focus_mode_state != 2):
                if hasattr(mw, "_was_maximized") and mw._was_maximized:
                    mw.showMaximized()
                else:
                    mw.showNormal()
        except Exception:
            pass

    try:
        # Run a single startup check after 1000ms to keep Anki startup fast and lightweight
        QTimer.singleShot(1000, startup_fullscreen_check)
    except Exception:
        pass

    # Prevent duplicate shortcuts
    if hasattr(mw, "focus_mode_shortcut") and mw.focus_mode_shortcut:
        try:
            mw.focus_mode_shortcut.setKey(QKeySequence(SHORTCUT_KEY))
            mw.focus_mode_shortcut.setEnabled(True)
            return
        except Exception:
            pass

    # Disable or clear any conflicting menu actions in Anki with the same shortcut
    try:
        for action in mw.findChildren(QAction):
            if action.shortcut() and action.shortcut().toString() == SHORTCUT_KEY:
                # Clear shortcut of the conflicting action to avoid conflict when menu bar is shown
                action.setShortcut(QKeySequence(""))
    except Exception as e:
        print(f"Focus Mode: Error clearing conflicting actions: {e}")

    # Create the low-level QShortcut with ApplicationShortcut context
    try:
        shortcut = QShortcut(QKeySequence(SHORTCUT_KEY), mw)
        shortcut.activated.connect(toggle_focus_mode)
        # Set ApplicationShortcut context so it is triggered globally even if the focus is in the webview
        try:
            context = Qt.ShortcutContext.ApplicationShortcut
        except Exception:
            context = getattr(Qt, "ApplicationShortcut", getattr(Qt.ShortcutContext, "ApplicationShortcut", None))
        
        if context is not None:
            shortcut.setContext(context)
        
        # Store on mw to prevent garbage collection
        mw.focus_mode_shortcut = shortcut
    except Exception as e:
        print(f"Focus Mode: Error creating QShortcut: {e}")
        # Fallback to standard QAction if QShortcut fails
        try:
            # Prevent duplicate actions
            for action in mw.actions():
                if action.text() == "Toggle Focus Mode":
                    return
            action = QAction("Toggle Focus Mode", mw)
            action.setShortcut(QKeySequence(SHORTCUT_KEY))
            action.triggered.connect(toggle_focus_mode)
            mw.addAction(action)
        except Exception as e2:
            print(f"Focus Mode: Fallback QAction failed: {e2}")
    
    # Initial trigger check
    if mw.state == "review":
        if AUTO_HIDE_ON_STUDY:
            focus_mode_state = STARTING_STATE
            schedule_delayed_hide()
        else:
            focus_mode_state = 0
            set_focus_mode_visible(False)
            update_card_top_side_visibility()

def on_configure():
    """Opens a custom PyQt configuration dialog when clicked in Anki's Add-ons manager."""
    # Read current config or set defaults
    config = {}
    try:
        config = mw.addonManager.getConfig(__name__) or {}
    except Exception:
        pass

    # Ensure keys are present
    if "shortcut_key" not in config:
        config["shortcut_key"] = SHORTCUT_KEY
    if "hide_top_bar" not in config:
        config["hide_top_bar"] = HIDE_TOP_BAR
    if "hide_bottom_bar" not in config:
        config["hide_bottom_bar"] = HIDE_BOTTOM_BAR
    if "auto_hide_on_study" not in config:
        config["auto_hide_on_study"] = AUTO_HIDE_ON_STUDY
    if "three_step_toggle" not in config:
        config["three_step_toggle"] = THREE_STEP_TOGGLE
    if "starting_state" not in config:
        config["starting_state"] = STARTING_STATE

    dialog = QDialog(mw)
    dialog.setWindowTitle("Focus Mode Settings")
    dialog.setMinimumWidth(340)
    
    layout = QVBoxLayout()
    
    # Shortcut Key Row
    row_key = QHBoxLayout()
    lbl_key = QLabel("Shortcut Key (e.g. F11, Ctrl+H):")
    txt_key = QLineEdit(config.get("shortcut_key", "F11"))
    row_key.addWidget(lbl_key)
    row_key.addWidget(txt_key)
    layout.addLayout(row_key)
    
    # Starting State Row
    row_start = QHBoxLayout()
    lbl_start = QLabel("Default Starting Mode on Study:")
    cmb_start = QComboBox()
    cmb_start.addItem("Standard Focus (Mode 1)", 1)
    cmb_start.addItem("Ultra Focus (Mode 2)", 2)
    
    # Select the current config starting state
    current_start = config.get("starting_state", STARTING_STATE)
    if current_start == 2:
        cmb_start.setCurrentIndex(1)
    else:
        cmb_start.setCurrentIndex(0)
        
    row_start.addWidget(lbl_start)
    row_start.addWidget(cmb_start)
    layout.addLayout(row_start)
    
    # Checkboxes
    chk_top = QCheckBox("Hide top menus and toolbars")
    chk_top.setChecked(config.get("hide_top_bar", True))
    layout.addWidget(chk_top)
    
    chk_bottom = QCheckBox("Hide bottom status/sync bar")
    chk_bottom.setChecked(config.get("hide_bottom_bar", True))
    layout.addWidget(chk_bottom)
    
    chk_auto = QCheckBox("Auto enter Focus Mode when starting study")
    chk_auto.setChecked(config.get("auto_hide_on_study", True))
    layout.addWidget(chk_auto)

    chk_three = QCheckBox("Enable 3-Step Shortcut Cycle (Standard -> Ultra -> Off)")
    chk_three.setChecked(config.get("three_step_toggle", True))
    layout.addWidget(chk_three)
    
    # Live change notice
    lbl_info = QLabel("Changes apply immediately! No Anki restart required.")
    lbl_info.setStyleSheet("color: #666; font-size: 10px; margin-top: 5px;")
    lbl_info.setWordWrap(True)
    layout.addWidget(lbl_info)

    # Save & Cancel & Report Bug Buttons
    buttons = QHBoxLayout()
    btn_save = QPushButton("Save Settings")
    btn_cancel = QPushButton("Cancel")
    btn_bug = QPushButton("Report a Bug")
    btn_bug.setStyleSheet("color: #d32f2f; font-weight: bold;")
    
    def report_bug():
        import webbrowser
        webbrowser.open("https://github.com/Doummar/Focus_Mode_Suite/issues")
    btn_bug.clicked.connect(report_bug)
    
    buttons.addWidget(btn_save)
    buttons.addWidget(btn_cancel)
    buttons.addWidget(btn_bug)
    layout.addLayout(buttons)
    
    def save():
        global SHORTCUT_KEY, HIDE_TOP_BAR, HIDE_BOTTOM_BAR, AUTO_HIDE_ON_STUDY, THREE_STEP_TOGGLE, STARTING_STATE, focus_mode_state
        
        config["shortcut_key"] = txt_key.text().strip()
        config["hide_top_bar"] = chk_top.isChecked()
        config["hide_bottom_bar"] = chk_bottom.isChecked()
        config["auto_hide_on_study"] = chk_auto.isChecked()
        config["three_step_toggle"] = chk_three.isChecked()
        config["starting_state"] = cmb_start.itemData(cmb_start.currentIndex())
        
        try:
            mw.addonManager.writeConfig(__name__, config)
        except Exception as e:
            print(f"Focus Mode: Error writing config: {e}")
            
        SHORTCUT_KEY = config["shortcut_key"]
        HIDE_TOP_BAR = config["hide_top_bar"]
        HIDE_BOTTOM_BAR = config["hide_bottom_bar"]
        AUTO_HIDE_ON_STUDY = config["auto_hide_on_study"]
        THREE_STEP_TOGGLE = config["three_step_toggle"]
        STARTING_STATE = config["starting_state"]
        
        # If currently in review state, update the visibility immediately
        if mw.state == "review":
            if AUTO_HIDE_ON_STUDY:
                focus_mode_state = STARTING_STATE
                schedule_delayed_hide()
            else:
                focus_mode_state = 0
                set_focus_mode_visible(False)
                update_card_top_side_visibility()
        else:
            set_focus_mode_visible(False)
            
        # Re-initialize the shortcut key immediately with the new hotkey!
        try:
            if hasattr(mw, "focus_mode_shortcut") and mw.focus_mode_shortcut:
                mw.focus_mode_shortcut.setKey(QKeySequence(SHORTCUT_KEY))
        except Exception as ex:
            print(f"Focus Mode: Error live-updating shortcut: {ex}")
            # Fallback re-init
            init_focus_mode()
            
        dialog.accept()
        from aqt.utils import tooltip
        tooltip("Focus Mode Configuration Saved and Applied!")
        
    btn_save.clicked.connect(save)
    btn_cancel.clicked.connect(dialog.reject)
    
    dialog.setLayout(layout)
    dialog.exec()

# --- Monkey-patching Toolbar draw to ensure it stays hidden under focus mode ---
_original_toolbar_draw = None

def focus_mode_toolbar_draw(*args, **kwargs):
    global focus_mode_state, _original_toolbar_draw
    if _original_toolbar_draw:
        try:
            _original_toolbar_draw(*args, **kwargs)
        except Exception as e:
            pass
            
    # If focus mode is active and we are studying, keep it hidden
    if mw.state == "review" and focus_mode_state > 0:
        schedule_delayed_hide()

if hasattr(mw, "toolbar") and mw.toolbar and hasattr(mw.toolbar, "draw"):
    try:
        _original_toolbar_draw = mw.toolbar.draw
        mw.toolbar.draw = focus_mode_toolbar_draw
    except Exception as e:
        print(f"Focus Mode: Error monkey-patching toolbar draw: {e}")

# Register Hooks
gui_hooks.state_did_change.append(on_state_did_change)
try:
    gui_hooks.reviewer_did_show_question.append(on_reviewer_state_changed)
    gui_hooks.reviewer_did_show_answer.append(lambda card: on_reviewer_state_changed())
    gui_hooks.card_will_show.append(on_card_will_show)
except Exception:
    pass

# Restore visibility and exit full screen cleanly on exit / close / profile unload
def cleanup_focus_mode_on_close(*args, **kwargs):
    global focus_mode_state, _current_applied_state
    _current_applied_state = None
    try:
        # Force set_focus_mode_visible(False) to restore everything
        set_focus_mode_visible(False)
        # Restore card top side elements
        focus_mode_state = 0
        update_card_top_side_visibility()
    except Exception as e:
        print(f"Focus Mode: Error during cleanup on close: {e}")

# Register profile will unload hook to clean up before closing
try:
    gui_hooks.profile_will_unload.append(cleanup_focus_mode_on_close)
except Exception:
    pass

# Override mw.closeEvent to clean up right before window closes
try:
    if mw is not None:
        _original_close_event = mw.closeEvent
        def focus_mode_close_event(event):
            cleanup_focus_mode_on_close()
            if _original_close_event:
                _original_close_event(event)
        mw.closeEvent = focus_mode_close_event
except Exception:
    pass

# Direct initialization if window is already loaded, otherwise use hook
if mw is not None and hasattr(mw, "state") and mw.state is not None:
    init_focus_mode()
else:
    gui_hooks.main_window_did_init.append(init_focus_mode)

# Register custom configuration action so clicking "Config" opens the dialog
try:
    mw.addonManager.setConfigAction(__name__, on_configure)
except Exception as e:
    print(f"Focus Mode: Error registering config action: {e}")
