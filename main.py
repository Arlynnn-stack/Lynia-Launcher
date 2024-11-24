import os
import threading
import ctypes
import customtkinter as ctk
from tkinter import PhotoImage
import updater
import injector
import requests


def fetch_scripts_from_repo():
    """Dapatkan senarai skrip dari GitHub."""
    url = "https://api.github.com/repos/Arlynnn-stack/Update-Repo-1/contents/scripts"
    response = requests.get(url)
    if response.status_code == 200:
        files = response.json()
        return [file["name"].replace(".lua", "") for file in files if file["name"].endswith(".lua")]
    return []


def download_lua_script(script_name, save_path):
    """Muat turun skrip Lua dari GitHub."""
    url = f"https://raw.githubusercontent.com/Arlynnn-stack/Update-Repo-1/main/scripts/{script_name}.lua"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(save_path, "wb") as file:
                file.write(response.content)
            return True
    except Exception as e:
        print(f"Exception: {e}")
    return False


class LynnnMenuLaunchpad(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("LynnnMenu Launcher")
        self.geometry("400x400")
        self.resizable(False, False)
        self.disable_resize_and_maximize()

        # Tema CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # UI Utama
        self.title_label = ctk.CTkLabel(self, text="Welcome babe ;3", font=("Helvetica", 24, "bold"))
        self.title_label.pack(pady=20)

        self.status_label = ctk.CTkLabel(self, text="Ready", font=("Helvetica", 14))
        self.status_label.pack()

        # Loading Animation Placeholder
        self.loading_label = ctk.CTkLabel(self, text="")
        self.loading_label.pack(pady=(10, 0))

        # Tab System
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(pady=20, padx=20, fill="both", expand=True)

        # Tab Main
        self.tab_main = self.tab_view.add("Main")
        self.update_button = ctk.CTkButton(self.tab_main, text="Update", command=self.start_check_for_updates)
        self.update_button.pack(pady=10)

        self.inject_button = ctk.CTkButton(self.tab_main, text="Inject", command=self.start_injection)
        self.inject_button.pack(pady=10)

        # Tab Scripts
        self.tab_scripts = self.tab_view.add("Scripts")
        self.script_listbox = ctk.CTkComboBox(self.tab_scripts, values=["Loading scripts..."])
        self.script_listbox.pack(pady=10)

        self.download_button = ctk.CTkButton(self.tab_scripts, text="Download Script", command=self.start_download_script)
        self.download_button.pack(pady=10)

        # Tab Config
        self.tab_config = self.tab_view.add("Config")
        self.reset_config_button = ctk.CTkButton(self.tab_config, text="Reset Config", command=self.reset_config)
        self.reset_config_button.pack(pady=10)

        # Made by label
        self.made_by_label = ctk.CTkLabel(self, text="2024 LynnnMenu - Developer: Lynnn", font=("Helvetica", 12))
        self.made_by_label.pack(side="bottom", pady=10)

        # Muatkan senarai skrip
        self.load_scripts()

    def load_scripts(self):
        """Muatkan senarai skrip ke ComboBox."""
        script_names = fetch_scripts_from_repo()
        if script_names:
            self.script_listbox.configure(values=script_names)
        else:
            self.script_listbox.configure(values=["No scripts found"])

    def start_check_for_updates(self):
        threading.Thread(target=self.check_for_updates).start()

    def check_for_updates(self):
        self.show_loading_animation("Checking for updates...")
        try:
            if updater.download_if_needed():
                self.show_popup("Update successful!")
            else:
                self.show_popup("No update needed.")
        except Exception as e:
            self.show_popup(f"Update failed: {e}")
        self.hide_loading_animation()

    def start_injection(self):
        threading.Thread(target=self.injection).start()

    def injection(self):
        self.show_loading_animation("Injecting LynnnMenu...")
        pID = injector.find_process_id("GTA5.exe")
        if pID:
            dll_path = os.path.join(os.getenv("APPDATA"), "Lynia", "LynnnMenu.dll")
            try:
                injector.inject_dll(pID, dll_path)
                self.show_popup("LynnnMenu injected successfully!")
            except Exception as e:
                self.show_popup(f"Injection failed: {e}")
        else:
            self.show_popup("GTA5 process not found!")
        self.hide_loading_animation()

    def start_download_script(self):
        threading.Thread(target=self.download_script).start()

    def download_script(self):
        script_name = self.script_listbox.get()
        if script_name and script_name != "No scripts found":
            download_folder = os.path.join(os.getenv("APPDATA"), "LynnnMenu", "scripts")
            os.makedirs(download_folder, exist_ok=True)
            save_path = os.path.join(download_folder, f"{script_name}.lua")

            self.show_loading_animation(f"Downloading {script_name}...")
            if download_lua_script(script_name, save_path):
                self.show_popup(f"{script_name} has been downloaded!")
            else:
                self.show_popup("Failed to download the script.")
            self.hide_loading_animation()
        else:
            self.show_popup("Please select a valid script.")

    def reset_config(self):
        """Reset fail konfigurasi."""
        settings_path = os.path.join(os.getenv("APPDATA"), "LynnnMenu", "settings.json")
        if os.path.exists(settings_path):
            try:
                os.remove(settings_path)
                self.show_popup("Config has been reset successfully!")
            except Exception as e:
                self.show_popup(f"Failed to reset config: {e}")
        else:
            self.show_popup("No settings file found to reset.")

    def show_loading_animation(self, message):
        """Tunjukkan spinner loading animation dan mesej status."""
        self.status_label.configure(text=message)
        self.loading_label.configure(text="⏳")

    def hide_loading_animation(self):
        """Hentikan spinner loading dan kembalikan status kepada 'Ready'."""
        self.loading_label.configure(text="")
        self.status_label.configure(text="Ready")

    def show_popup(self, message):
        """Tunjukkan popup ringkas dengan mesej hasil operasi."""
        popup = ctk.CTkToplevel(self)
        popup.title("Status")
        popup.geometry("300x150")
        popup.resizable(False, False)

        label = ctk.CTkLabel(popup, text=message, font=("Helvetica", 14), justify="center", wraplength=280)
        label.pack(pady=(20, 10), padx=10)

        close_button = ctk.CTkButton(popup, text="Close", command=popup.destroy)
        close_button.pack(pady=(10, 20))
        popup.after(3000, popup.destroy)

    def disable_resize_and_maximize(self):
        """Disable resize dan maximize."""
        hwnd = ctypes.windll.user32.GetActiveWindow()
        if hwnd:
            GWL_STYLE = -16
            WS_MAXIMIZEBOX = 0x00010000
            WS_SIZEBOX = 0x00040000
            style = ctypes.windll.user32.GetWindowLongPtrW(hwnd, GWL_STYLE)
            style &= ~WS_MAXIMIZEBOX
            style &= ~WS_SIZEBOX
            ctypes.windll.user32.SetWindowLongPtrW(hwnd, GWL_STYLE, style)


if __name__ == "__main__":
    app = LynnnMenuLaunchpad()
    app.mainloop()
