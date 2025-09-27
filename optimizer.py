import sys
import os
import subprocess
import webbrowser
import requests
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTabWidget, QMessageBox, QScrollArea, QGroupBox, QCheckBox,
    QComboBox, QDialog, QFormLayout, QProgressDialog, QMenuBar
)
from PyQt6.QtGui import QIcon, QFont, QColor, QAction
from PyQt6.QtCore import Qt, QSettings, QThread, pyqtSignal

# Function to check if running as admin
def is_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

# If not admin, relaunch as admin
if not is_admin():
    import ctypes
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit(0)

# App settings
settings = QSettings("DiplomatSoft", "WindowsOptimizer")

class DownloadThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    def __init__(self, url, file_path):
        super().__init__()
        self.url = url
        self.file_path = file_path

    def run(self):
        response = requests.get(self.url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024
        written = 0
        with open(self.file_path, 'wb') as f:
            for data in response.iter_content(block_size):
                written += len(data)
                f.write(data)
                if total_size > 0:
                    self.progress.emit(int(written / total_size * 100))
        self.finished.emit(self.file_path)

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        layout = QFormLayout(self)

        # Theme switcher
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        current_theme = settings.value("theme", "Light")
        self.theme_combo.setCurrentText(current_theme)
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        layout.addRow("Theme:", self.theme_combo)

        # Telegram link
        tg_button = QPushButton("Telegram: @biographydiplomat")
        tg_button.clicked.connect(lambda: webbrowser.open("https://t.me/biographydiplomat"))
        layout.addRow(tg_button)

        # Auto-startup toggle
        self.autostart_check = QCheckBox("Run on startup")
        autostart = settings.value("autostart", False, type=bool)
        self.autostart_check.setChecked(autostart)
        self.autostart_check.stateChanged.connect(self.toggle_autostart)
        layout.addRow(self.autostart_check)

        # Cache cleanup interval
        self.cache_interval = QComboBox()
        self.cache_interval.addItems(["Never", "Daily", "Weekly"])
        cache_freq = settings.value("cache_cleanup", "Never")
        self.cache_interval.setCurrentText(cache_freq)
        self.cache_interval.currentTextChanged.connect(lambda freq: settings.setValue("cache_cleanup", freq))
        layout.addRow("Auto-cache cleanup:", self.cache_interval)

        # Language selection
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Russian"])
        current_lang = settings.value("language", "English")
        self.lang_combo.setCurrentText(current_lang)
        self.lang_combo.currentTextChanged.connect(lambda lang: settings.setValue("language", lang))
        layout.addRow("Language:", self.lang_combo)

    def change_theme(self, theme):
        settings.setValue("theme", theme)
        self.parent().apply_theme()

    def toggle_autostart(self, state):
        settings.setValue("autostart", bool(state))
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS)
        if state:
            winreg.SetValueEx(key, "WindowsOptimizer", 0, winreg.REG_SZ, sys.executable)
        else:
            try:
                winreg.DeleteValue(key, "WindowsOptimizer")
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Windows Optimizer")
        self.setGeometry(100, 100, 1000, 800)
        self.setWindowIcon(QIcon.fromTheme("system-software-update"))

        # Menu Bar
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)
        file_menu = menu_bar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menu_bar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(lambda: QMessageBox.about(self, "About", "Windows Optimizer v2.0 by diplomat"))
        help_menu.addAction(about_action)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Tabs
        tabs = QTabWidget()
        main_layout.addWidget(tabs)

        # Security Tab
        security_widget = self.create_scroll_area()
        security_layout = QVBoxLayout(security_widget.widget())
        self.add_group(security_layout, "Windows Update", self.create_update_controls())
        self.add_group(security_layout, "Firewall", self.create_firewall_controls())
        self.add_group(security_layout, "Antivirus", self.create_antivirus_controls())
        self.add_group(security_layout, "Cloud Services", self.create_cloud_controls())
        self.add_group(security_layout, "Additional Security", self.create_additional_security_controls())
        tabs.addTab(security_widget, "Security")

        # Optimization Tab
        opt_widget = self.create_scroll_area()
        opt_layout = QVBoxLayout(opt_widget.widget())
        self.add_group(opt_layout, "Power Plan", self.create_powerplan_controls())
        self.add_group(opt_layout, "Telemetry", self.create_telemetry_controls())
        self.add_group(opt_layout, "Unnecessary Params", self.create_params_controls())
        self.add_group(opt_layout, "Tweaks", self.create_tweaks_controls())
        self.add_group(opt_layout, "Services", self.create_services_controls())
        self.add_group(opt_layout, "HPET", self.create_hpet_controls())
        self.add_group(opt_layout, "AI Optimization", self.create_ai_opt_controls())
        self.add_group(opt_layout, "Additional Optimizations", self.create_additional_opt_controls())
        self.add_group(opt_layout, "Advanced Tweaks", self.create_advanced_tweaks_controls())
        tabs.addTab(opt_widget, "Optimization")

        # Cleanup Tab (new for UWP and cleanup)
        cleanup_widget = self.create_scroll_area()
        cleanup_layout = QVBoxLayout(cleanup_widget.widget())
        self.add_group(cleanup_layout, "Remove UWP Apps", self.create_uwp_controls())
        self.add_group(cleanup_layout, "System Cleanup", self.create_cleanup_controls())
        tabs.addTab(cleanup_widget, "Cleanup")

        # Apps Tab
        apps_widget = self.create_scroll_area()
        apps_layout = QVBoxLayout(apps_widget.widget())
        self.add_group(apps_layout, "Install Drivers", self.create_drivers_controls())
        self.add_group(apps_layout, "Install Browsers", self.create_browsers_controls())
        self.add_group(apps_layout, "Install Apps", self.create_apps_controls())
        tabs.addTab(apps_widget, "Apps")

        # Customization Tab
        custom_widget = self.create_scroll_area()
        custom_layout = QVBoxLayout(custom_widget.widget())
        self.add_group(custom_layout, "Install Customization Tools", self.create_custom_tools_controls())
        self.add_group(custom_layout, "Theme Customizations", self.create_theme_custom_controls())
        self.add_group(custom_layout, "Additional Customizations", self.create_additional_custom_controls())
        tabs.addTab(custom_widget, "Customization")

        # Windows Tweaks Tab
        tweaks_widget = self.create_scroll_area()
        tweaks_layout = QVBoxLayout(tweaks_widget.widget())
        self.add_group(tweaks_layout, "Windows Tweaks", self.create_windows_tweaks_controls())
        tabs.addTab(tweaks_widget, "Windows Tweaks")

        # Resources Tab
        resources_widget = self.create_scroll_area()
        resources_layout = QVBoxLayout(resources_widget.widget())
        self.add_group(resources_layout, "My Resources", self.create_my_resources_controls())
        tabs.addTab(resources_widget, "Resources")

        # Footer
        footer_layout = QHBoxLayout()
        settings_button = QPushButton("Settings")
        settings_button.clicked.connect(self.open_settings)
        footer_layout.addWidget(settings_button)
        footer_layout.addStretch()
        signature = QLabel("Soft by diplomat")
        signature.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        footer_layout.addWidget(signature)
        main_layout.addLayout(footer_layout)

        self.apply_theme()

    def create_scroll_area(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner_widget = QWidget()
        scroll.setWidget(inner_widget)
        return scroll

    def add_group(self, layout, title, controls_layout):
        group = QGroupBox(title)
        group.setLayout(controls_layout)
        layout.addWidget(group)

    def create_update_controls(self):
        layout = QVBoxLayout()
        enable_btn = QPushButton("Enable Windows Update")
        enable_btn.clicked.connect(lambda: self.run_command('sc config wuauserv start= auto'))
        disable_btn = QPushButton("Disable Windows Update")
        disable_btn.clicked.connect(lambda: self.warning_exec('sc config wuauserv start= disabled', "Disabling updates may leave your system vulnerable. Proceed?"))
        layout.addWidget(enable_btn)
        layout.addWidget(disable_btn)
        return layout

    def create_firewall_controls(self):
        layout = QVBoxLayout()
        enable_btn = QPushButton("Enable Firewall")
        enable_btn.clicked.connect(lambda: self.run_command('netsh advfirewall set allprofiles state on'))
        disable_btn = QPushButton("Disable Firewall")
        disable_btn.clicked.connect(lambda: self.warning_exec('netsh advfirewall set allprofiles state off', "Disabling firewall can expose your system to risks. Proceed?"))
        layout.addWidget(enable_btn)
        layout.addWidget(disable_btn)
        return layout

    def create_antivirus_controls(self):
        layout = QVBoxLayout()
        disable_btn = QPushButton("Disable Antivirus")
        disable_btn.clicked.connect(lambda: self.warning_exec('Set-MpPreference -DisableRealtimeMonitoring $true', "Disabling antivirus is risky. Proceed?", powershell=True))
        remove_btn = QPushButton("Remove Antivirus")
        remove_btn.clicked.connect(lambda: self.warning_exec('Remove-WindowsCapability -Online -Name "Microsoft.Windows.Defender.*"', "Removing antivirus is very risky. Proceed?", powershell=True))
        layout.addWidget(disable_btn)
        layout.addWidget(remove_btn)
        return layout

    def create_cloud_controls(self):
        layout = QVBoxLayout()
        disable_onedrive_btn = QPushButton("Disable OneDrive")
        disable_onedrive_btn.clicked.connect(lambda: self.warning_exec('reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\OneDrive" /v "DisableFileSyncNGSC" /t REG_DWORD /d 1 /f', "Disabling OneDrive. Proceed?"))
        uninstall_onedrive_btn = QPushButton("Uninstall OneDrive")
        uninstall_onedrive_btn.clicked.connect(lambda: self.warning_exec('%SystemRoot%\\SysWOW64\\OneDriveSetup.exe /uninstall', "Uninstalling OneDrive. Proceed?"))
        layout.addWidget(disable_onedrive_btn)
        layout.addWidget(uninstall_onedrive_btn)
        return layout

    def create_additional_security_controls(self):
        layout = QVBoxLayout()
        disable_smartscreen_btn = QPushButton("Disable SmartScreen")
        disable_smartscreen_btn.clicked.connect(lambda: self.warning_exec('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System" /v "EnableSmartScreen" /t REG_DWORD /d 0 /f', "Disabling SmartScreen. Proceed?"))
        disable_uac_btn = QPushButton("Disable UAC")
        disable_uac_btn.clicked.connect(lambda: self.warning_exec('reg add HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System /v EnableLUA /t REG_DWORD /d 0 /f', "Disabling UAC is risky. Proceed?"))
        layout.addWidget(disable_smartscreen_btn)
        layout.addWidget(disable_uac_btn)
        return layout

    def create_uwp_controls(self):
        layout = QVBoxLayout()
        self.uwp_checkboxes = {}
        uwp_apps = [
            "Microsoft.Edge", "Microsoft.WindowsCalculator", "Microsoft.Store", "Microsoft.XboxApp",
            "Microsoft.BingWeather", "Microsoft.MicrosoftSolitaireCollection", "Microsoft.People",
            "Microsoft.WindowsAlarms", "Microsoft.WindowsCamera", "Microsoft.WindowsMaps",
            "Microsoft.WindowsSoundRecorder", "Microsoft.ZuneMusic", "Microsoft.ZuneVideo"
        ]
        for app in uwp_apps:
            name = app.split('.')[-1]
            cb = QCheckBox(f"Remove {name}")
            self.uwp_checkboxes[app] = cb
            layout.addWidget(cb)

        remove_selected_btn = QPushButton("Remove Selected UWP Apps")
        remove_selected_btn.clicked.connect(self.remove_selected_uwp)
        remove_all_btn = QPushButton("Remove All UWP Apps")
        remove_all_btn.clicked.connect(lambda: self.warning_exec(self.get_remove_all_uwp_command(), "Removing all UWP apps. Proceed?", powershell=True))
        layout.addWidget(remove_selected_btn)
        layout.addWidget(remove_all_btn)
        return layout

    def get_remove_all_uwp_command(self):
        return 'Get-AppxPackage * | Remove-AppxPackage'

    def remove_selected_uwp(self):
        for app, cb in self.uwp_checkboxes.items():
            if cb.isChecked():
                self.run_command(f'Get-AppxPackage {app} | Remove-AppxPackage', powershell=True)
                cb.setChecked(False)
        QMessageBox.information(self, "Success", "Selected UWP apps removed.")

    def create_cleanup_controls(self):
        layout = QVBoxLayout()
        clean_temp_btn = QPushButton("Clean Temporary Files")
        clean_temp_btn.clicked.connect(lambda: self.run_command('powershell -c "Remove-Item -Path $env:TEMP\\* -Recurse -Force -ErrorAction SilentlyContinue"'))
        disk_cleanup_btn = QPushButton("Run Disk Cleanup")
        disk_cleanup_btn.clicked.connect(lambda: self.run_command('cleanmgr.exe /verylowdisk'))
        clear_prefetch_btn = QPushButton("Clear Prefetch")
        clear_prefetch_btn.clicked.connect(lambda: self.run_command('powershell -c "Remove-Item -Path C:\\Windows\\Prefetch\\* -Recurse -Force -ErrorAction SilentlyContinue"'))
        clear_recycle_btn = QPushButton("Empty Recycle Bin")
        clear_recycle_btn.clicked.connect(lambda: self.run_command('powershell -c "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"', powershell=True))
        layout.addWidget(clean_temp_btn)
        layout.addWidget(disk_cleanup_btn)
        layout.addWidget(clear_prefetch_btn)
        layout.addWidget(clear_recycle_btn)
        return layout

    def create_drivers_controls(self):
        layout = QVBoxLayout()
        nvidia_btn = QPushButton("Install Nvidia Drivers (Clean)")
        nvidia_btn.clicked.connect(self.install_nvidia)
        amd_btn = QPushButton("Install AMD Drivers (Clean)")
        amd_btn.clicked.connect(self.install_amd)
        intel_btn = QPushButton("Install Intel Drivers")
        intel_btn.clicked.connect(lambda: self.run_command('winget install -e --id Intel.IntelArcControlCenter'))
        layout.addWidget(nvidia_btn)
        layout.addWidget(amd_btn)
        layout.addWidget(intel_btn)
        return layout

    def install_nvidia(self):
        self.run_command('winget install -e --id Nvidia.GeForceExperience --silent')

    def install_amd(self):
        self.run_command('winget install -e --id AMD.RyzenMaster --silent')

    def create_powerplan_controls(self):
        layout = QVBoxLayout()
        create_btn = QPushButton("Create & Activate High Performance Plan")
        create_btn.clicked.connect(self.create_powerplan)
        label = QLabel("For PC: Maximizes CPU/GPU performance, may increase power usage.")
        layout.addWidget(create_btn)
        layout.addWidget(label)
        balanced_btn = QPushButton("Set Balanced Power Plan")
        balanced_btn.clicked.connect(lambda: self.run_command('powercfg -setactive 381b4222-f694-41f0-9685-ff5bb260df2e'))
        layout.addWidget(balanced_btn)
        return layout

    def create_powerplan(self):
        self.run_command('powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61')
        self.run_command('powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c')

    def create_telemetry_controls(self):
        layout = QVBoxLayout()
        disable_btn = QPushButton("Disable Telemetry")
        disable_btn.clicked.connect(lambda: self.run_command('sc config DiagTrack start= disabled && sc config dmwappushservice start= disabled'))
        layout.addWidget(disable_btn)
        return layout

    def create_params_controls(self):
        layout = QVBoxLayout()
        disable_btn = QPushButton("Disable Unnecessary Params")
        disable_btn.clicked.connect(lambda: self.run_command('reg add HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced /v ShowCortanaButton /t REG_DWORD /d 0 /f'))
        layout.addWidget(disable_btn)
        return layout

    def create_tweaks_controls(self):
        layout = QVBoxLayout()
        apply_btn = QPushButton("Apply Optimization Tweaks")
        apply_btn.clicked.connect(self.apply_tweaks)
        layout.addWidget(apply_btn)
        return layout

    def apply_tweaks(self):
        commands = [
            'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v ListviewAlphaSelect /t REG_DWORD /d 0 /f',
            'reg add "HKCU\\Control Panel\\Desktop" /v MenuShowDelay /t REG_SZ /d 0 /f',
            'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 2 /f',
            'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile" /v SystemResponsiveness /t REG_DWORD /d 0 /f',
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerThrottling" /v PowerThrottlingOff /t REG_DWORD /d 1 /f',
        ]
        for cmd in commands:
            self.run_command(cmd)

    def create_services_controls(self):
        layout = QVBoxLayout()
        disable_btn = QPushButton("Disable Unnecessary Services")
        disable_btn.clicked.connect(self.disable_unnecessary_services)
        layout.addWidget(disable_btn)
        return layout

    def disable_unnecessary_services(self):
        services = ["XboxNetApiSvc", "WSearch", "SysMain", "RetailDemo", "WMPNetworkSvc", "TabletInputService"]
        for svc in services:
            self.run_command(f'sc config {svc} start= disabled')

    def create_hpet_controls(self):
        layout = QVBoxLayout()
        enable_btn = QPushButton("Enable HPET")
        enable_btn.clicked.connect(lambda: self.run_command('bcdedit /deletevalue useplatformclock'))
        disable_btn = QPushButton("Disable HPET")
        disable_btn.clicked.connect(lambda: self.run_command('bcdedit /set useplatformclock false'))
        layout.addWidget(enable_btn)
        layout.addWidget(disable_btn)
        return layout

    def create_ai_opt_controls(self):
        layout = QVBoxLayout()
        optimize_btn = QPushButton("Optimize for AI (Disable Background ML)")
        optimize_btn.clicked.connect(lambda: self.run_command('sc config WSearch start= disabled'))
        layout.addWidget(optimize_btn)
        return layout

    def create_additional_opt_controls(self):
        layout = QVBoxLayout()
        clean_cache_btn = QPushButton("Clean System Cache")
        clean_cache_btn.clicked.connect(lambda: self.run_command('powershell -c "Remove-Item -Path $env:TEMP\\* -Recurse -Force -ErrorAction SilentlyContinue"'))
        defrag_btn = QPushButton("Defragment Drive")
        defrag_btn.clicked.connect(lambda: self.run_command('defrag C: /O /U /V'))
        optimize_startup_btn = QPushButton("Optimize Startup")
        optimize_startup_btn.clicked.connect(lambda: self.run_command('msconfig'))  # Opens msconfig for user to manage
        layout.addWidget(clean_cache_btn)
        layout.addWidget(defrag_btn)
        layout.addWidget(optimize_startup_btn)
        return layout

    def create_advanced_tweaks_controls(self):
        layout = QVBoxLayout()
        disable_animations_btn = QPushButton("Disable Animations")
        disable_animations_btn.clicked.connect(lambda: self.run_command('reg add "HKCU\\Control Panel\\Desktop\\WindowMetrics" /v MinAnimate /t REG_SZ /d 0 /f'))
        disable_transparency_btn = QPushButton("Disable Transparency")
        disable_transparency_btn.clicked.connect(lambda: self.run_command('reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v EnableTransparency /t REG_DWORD /d 0 /f'))
        enable_verbose_boot_btn = QPushButton("Enable Verbose Boot")
        enable_verbose_boot_btn.clicked.connect(lambda: self.run_command('bcdedit /set {current} bootstatuspolicy displayallfailures'))
        layout.addWidget(disable_animations_btn)
        layout.addWidget(disable_transparency_btn)
        layout.addWidget(enable_verbose_boot_btn)
        return layout

    def create_browsers_controls(self):
        layout = QVBoxLayout()
        firefox_btn = QPushButton("Install Firefox")
        firefox_btn.clicked.connect(lambda: self.run_command('winget install -e --id Mozilla.Firefox'))
        chrome_btn = QPushButton("Install Chrome")
        chrome_btn.clicked.connect(lambda: self.run_command('winget install -e --id Google.Chrome'))
        brave_btn = QPushButton("Install Brave")
        brave_btn.clicked.connect(lambda: self.run_command('winget install -e --id Brave.Brave'))
        opera_btn = QPushButton("Install Opera")
        opera_btn.clicked.connect(lambda: self.run_command('winget install -e --id Opera.Opera'))
        layout.addWidget(firefox_btn)
        layout.addWidget(chrome_btn)
        layout.addWidget(brave_btn)
        layout.addWidget(opera_btn)
        return layout

    def create_apps_controls(self):
        layout = QVBoxLayout()
        steam_btn = QPushButton("Install Steam")
        steam_btn.clicked.connect(lambda: self.run_command('winget install -e --id Valve.Steam'))
        gram_btn = QPushButton("Install 64gram (from GitHub)")
        gram_btn.clicked.connect(self.install_64gram)
        discord_btn = QPushButton("Install Discord")
        discord_btn.clicked.connect(lambda: self.run_command('winget install -e --id Discord.Discord'))
        vscode_btn = QPushButton("Install VS Code")
        vscode_btn.clicked.connect(lambda: self.run_command('winget install -e --id Microsoft.VisualStudioCode'))
        spotify_btn = QPushButton("Install Spotify")
        spotify_btn.clicked.connect(lambda: self.run_command('winget install -e --id Spotify.Spotify'))
        layout.addWidget(steam_btn)
        layout.addWidget(gram_btn)
        layout.addWidget(discord_btn)
        layout.addWidget(vscode_btn)
        layout.addWidget(spotify_btn)
        return layout

    def install_64gram(self):
        api_url = "https://api.github.com/repos/TDesktop-x64/tdesktop/releases/latest"
        response = requests.get(api_url)
        if response.status_code == 200:
            data = json.loads(response.text)
            download_url = None
            for asset in data.get('assets', []):
                if 'Setup' in asset['name'] and asset['name'].endswith('.exe'):
                    download_url = asset['browser_download_url']
                    break
            if not download_url:
                download_url = next((a['browser_download_url'] for a in data['assets'] if a['name'].endswith('.zip')), None)
        else:
            QMessageBox.warning(self, "Error", "Failed to fetch latest 64Gram release.")
            return

        if not download_url:
            QMessageBox.warning(self, "Error", "No suitable download found.")
            return

        file_path = os.path.join(os.environ['TEMP'], os.path.basename(download_url))
        progress = QProgressDialog("Downloading 64Gram...", "Cancel", 0, 100, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)

        thread = DownloadThread(download_url, file_path)
        thread.progress.connect(progress.setValue)
        thread.finished.connect(lambda path: self.complete_64gram_install(path, progress))
        thread.start()

    def complete_64gram_install(self, file_path, progress):
        progress.close()
        try:
            if file_path.endswith('.exe'):
                subprocess.run([file_path, '/silent'], check=True)
            elif file_path.endswith('.zip'):
                import zipfile
                extract_path = os.path.join(os.environ['PROGRAMFILES'], '64Gram')
                os.makedirs(extract_path, exist_ok=True)
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
            QMessageBox.information(self, "Success", "64Gram installed successfully.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Installation failed: {str(e)}")

    def create_custom_tools_controls(self):
        layout = QVBoxLayout()
        rainmeter_btn = QPushButton("Install Rainmeter")
        rainmeter_btn.clicked.connect(lambda: self.run_command('winget install -e --id Rainmeter.Rainmeter'))
        translucenttb_btn = QPushButton("Install TranslucentTB")
        translucenttb_btn.clicked.connect(lambda: self.run_command('winget install -e --id TranslucentTB.TranslucentTB'))
        startallback_btn = QPushButton("Install StartAllBack")
        startallback_btn.clicked.connect(lambda: webbrowser.open("https://www.startallback.com/download.php"))
        powertoys_btn = QPushButton("Install PowerToys")
        powertoys_btn.clicked.connect(lambda: self.run_command('winget install -e --id Microsoft.PowerToys'))
        explorerpatcher_btn = QPushButton("Install ExplorerPatcher")
        explorerpatcher_btn.clicked.connect(lambda: self.run_command('winget install -e --id valinet.ExplorerPatcher'))
        layout.addWidget(rainmeter_btn)
        layout.addWidget(translucenttb_btn)
        layout.addWidget(startallback_btn)
        layout.addWidget(powertoys_btn)
        layout.addWidget(explorerpatcher_btn)
        return layout

    def create_theme_custom_controls(self):
        layout = QVBoxLayout()
        dark_theme_btn = QPushButton("Apply System Dark Theme")
        dark_theme_btn.clicked.connect(lambda: self.run_command('reg add HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize /v AppsUseLightTheme /t REG_DWORD /d 0 /f'))
        light_theme_btn = QPushButton("Apply System Light Theme")
        light_theme_btn.clicked.connect(lambda: self.run_command('reg add HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize /v AppsUseLightTheme /t REG_DWORD /d 1 /f'))
        layout.addWidget(dark_theme_btn)
        layout.addWidget(light_theme_btn)
        return layout

    def create_additional_custom_controls(self):
        layout = QVBoxLayout()
        change_wallpaper_btn = QPushButton("Change Wallpaper (Opens Settings)")
        change_wallpaper_btn.clicked.connect(lambda: self.run_command('rundll32.exe shell32.dll,Control_RunDLL desk.cpl,,@desktop'))
        install_icons_btn = QPushButton("Install Custom Icons (Manual)")
        install_icons_btn.clicked.connect(lambda: webbrowser.open("https://www.deviantart.com/customization/icons/os/windows"))
        layout.addWidget(change_wallpaper_btn)
        layout.addWidget(install_icons_btn)
        return layout

    def create_windows_tweaks_controls(self):
        layout = QVBoxLayout()
        self.tweaks_checkboxes = {}
        tweaks = {
            "Disable Cortana": 'reg add HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search /v AllowCortana /t REG_DWORD /d 0 /f',
            "Disable Web Search in Start": 'reg add HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Search /v BingSearchEnabled /t REG_DWORD /d 0 /f',
            "Show File Extensions": 'reg add HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced /v HideFileExt /t REG_DWORD /d 0 /f',
            "Disable Lock Screen": 'reg add HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Personalization /v NoLockScreen /t REG_DWORD /d 1 /f',
            "Disable Startup Delay": 'reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Serialize /v StartupDelayInMSec /t REG_DWORD /d 0 /f',
            "Enable NumLock on Startup": 'reg add HKU\\.DEFAULT\\Control Panel\\Keyboard /v InitialKeyboardIndicators /t REG_SZ /d 2 /f',
            "Disable Game DVR": 'reg add HKCU\\System\\GameConfigStore /v GameDVR_Enabled /t REG_DWORD /d 0 /f',
            "Optimize SSD": 'fsutil behavior set disabledeletenotify 0',
            "Disable Hibernation": 'powercfg -h off',
            "Increase Icon Cache": 'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer" /v Max Cached Icons /t REG_SZ /d 2000 /f',
            "Disable Superfetch": 'sc config SysMain start= disabled',
            "Disable Background Apps": 'reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\BackgroundAccessApplications /v GlobalUserDisabled /t REG_DWORD /d 1 /f',
        }
        for name, cmd in tweaks.items():
            cb = QCheckBox(name)
            self.tweaks_checkboxes[name] = (cb, cmd)
            layout.addWidget(cb)

        apply_btn = QPushButton("Apply Selected Tweaks")
        apply_btn.clicked.connect(self.apply_selected_tweaks)
        layout.addWidget(apply_btn)
        return layout

    def apply_selected_tweaks(self):
        for name, (cb, cmd) in self.tweaks_checkboxes.items():
            if cb.isChecked():
                self.run_command(cmd)
                cb.setChecked(False)
        QMessageBox.information(self, "Success", "Tweaks applied. Some may require restart.")

    def create_my_resources_controls(self):
        layout = QVBoxLayout()
        tiktok_btn = QPushButton("TikTok @tracezero")
        tiktok_btn.clicked.connect(lambda: webbrowser.open("https://www.tiktok.com/@tracezero"))
        tg_btn = QPushButton("Telegram @biographydiplomat")
        tg_btn.clicked.connect(lambda: webbrowser.open("https://t.me/biographydiplomat"))
        win10_flibustier_btn = QPushButton("Clean Windows 10 from Flibustier")
        win10_flibustier_btn.clicked.connect(lambda: webbrowser.open("https://flibustier64.com/windows-10-by-flibustier/"))
        win11_flibustier_btn = QPushButton("Clean Windows 11 from Flibustier")
        win11_flibustier_btn.clicked.connect(lambda: webbrowser.open("https://flibustier64.com/windows-11-by-flibustier/"))
        layout.addWidget(tiktok_btn)
        layout.addWidget(tg_btn)
        layout.addWidget(win10_flibustier_btn)
        layout.addWidget(win11_flibustier_btn)
        return layout

    def run_command(self, cmd, powershell=False):
        try:
            if powershell:
                process = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True, check=True)
            else:
                process = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
            QMessageBox.information(self, "Success", f"Command executed successfully.\nOutput: {process.stdout}")
        except subprocess.CalledProcessError as e:
            QMessageBox.warning(self, "Error", f"Command failed: {e}\nError: {e.stderr}")

    def warning_exec(self, cmd, msg, powershell=False):
        reply = QMessageBox.warning(self, "Warning", msg, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.run_command(cmd, powershell)

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()

    def apply_theme(self):
        theme = settings.value("theme", "Light")
        if theme == "Dark":
            self.setStyleSheet("""
                QWidget {
                    background-color: #1e1e1e;
                    color: #ffffff;
                }
                QGroupBox {
                    border: 1px solid #555555;
                    margin-top: 1em;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555555;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #505050;
                }
                QCheckBox {
                    color: #ffffff;
                }
                QLabel {
                    color: #ffffff;
                }
                QComboBox {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555555;
                }
                QTabWidget::pane {
                    border: 1px solid #555555;
                }
                QTabBar::tab {
                    background: #2d2d2d;
                    color: #ffffff;
                    padding: 8px;
                }
                QTabBar::tab:selected {
                    background: #3c3c3c;
                }
                QScrollArea {
                    background-color: #1e1e1e;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #f0f0f0;
                    color: #000000;
                }
                QGroupBox {
                    border: 1px solid #cccccc;
                    margin-top: 1em;
                    color: #000000;
                }
                QPushButton {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #cccccc;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
                QCheckBox {
                    color: #000000;
                }
                QLabel {
                    color: #000000;
                }
                QComboBox {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #cccccc;
                }
                QTabWidget::pane {
                    border: 1px solid #cccccc;
                }
                QTabBar::tab {
                    background: #f0f0f0;
                    color: #000000;
                    padding: 8px;
                }
                QTabBar::tab:selected {
                    background: #ffffff;
                }
                QScrollArea {
                    background-color: #f0f0f0;
                }
            """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())