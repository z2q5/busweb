import kivy
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton

# بيانات الطلاب (Ministry ID -> اسم + باص + حالة)
students = {
    "777442": {"name": "Ahmed", "bus": "1", "status": "Not set"},
    "777443": {"name": "Mohammed", "bus": "1", "status": "Not set"},
    "777444": {"name": "Sara", "bus": "2", "status": "Not set"},
    "777445": {"name": "Laila", "bus": "3", "status": "Not set"},
    "777446": {"name": "Hassan", "bus": "2", "status": "Not set"},
    "777447": {"name": "Mona", "bus": "1", "status": "Not set"},
    "777448": {"name": "Khalid", "bus": "3", "status": "Not set"},
    "777449": {"name": "Noura", "bus": "1", "status": "Not set"},
    "777450": {"name": "Omar", "bus": "2", "status": "Not set"},
    "777451": {"name": "Fatima", "bus": "3", "status": "Not set"},
}

# باسوردات الباصات
bus_passwords = {"1": "1111", "2": "2222", "3": "3333"}

KV = """
ScreenManager:
    MenuScreen:
    StudentLoginScreen:
    DriverLoginScreen:
    DriverViewScreen:

<MenuScreen>:
    name: "menu"
    MDBoxLayout:
        orientation: "vertical"
        spacing: "20dp"
        padding: "20dp"
        MDLabel:
            text: "Bus Attendance System"
            halign: "center"
            font_style: "H4"
        MDRaisedButton:
            text: "Login as Student"
            pos_hint: {"center_x": 0.5}
            on_release: root.manager.current = "student_login"
        MDRaisedButton:
            text: "Login as Driver"
            pos_hint: {"center_x": 0.5}
            on_release: root.manager.current = "driver_login"

<StudentLoginScreen>:
    name: "student_login"
    MDBoxLayout:
        orientation: "vertical"
        spacing: "15dp"
        padding: "20dp"
        MDTextField:
            id: student_id
            hint_text: "Enter Ministry ID"
            mode: "rectangle"
        MDRaisedButton:
            text: "Going"
            pos_hint: {"center_x": 0.5}
            on_release: app.mark_attendance(student_id.text, "Going")
        MDRaisedButton:
            text: "Not Going"
            pos_hint: {"center_x": 0.5}
            on_release: app.mark_attendance(student_id.text, "Not Going")
        MDRaisedButton:
            text: "Back"
            pos_hint: {"center_x": 0.5}
            on_release: root.manager.current = "menu"

<DriverLoginScreen>:
    name: "driver_login"
    MDBoxLayout:
        orientation: "vertical"
        spacing: "15dp"
        padding: "20dp"
        MDTextField:
            id: bus_number
            hint_text: "Bus Number (1, 2, 3)"
            mode: "rectangle"
        MDTextField:
            id: bus_pass
            hint_text: "Password"
            mode: "rectangle"
            password: True
        MDRaisedButton:
            text: "Login"
            pos_hint: {"center_x": 0.5}
            on_release: app.driver_login(bus_number.text, bus_pass.text)
        MDRaisedButton:
            text: "Back"
            pos_hint: {"center_x": 0.5}
            on_release: root.manager.current = "menu"

<DriverViewScreen>:
    name: "driver_view"
    MDBoxLayout:
        id: driver_box
        orientation: "vertical"
        spacing: "10dp"
        padding: "20dp"
"""

class MenuScreen(Screen): pass
class StudentLoginScreen(Screen): pass
class DriverLoginScreen(Screen): pass
class DriverViewScreen(Screen): pass

class BusApp(MDApp):
    dialog = None
    current_bus = None

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        return Builder.load_string(KV)

    def mark_attendance(self, student_id, status):
        if student_id in students:
            students[student_id]["status"] = status
            self.show_dialog(f"{students[student_id]['name']} marked as {status}")
        else:
            self.show_dialog("Invalid Ministry ID!")

    def driver_login(self, bus_number, password):
        if bus_number in bus_passwords and bus_passwords[bus_number] == password:
            self.current_bus = bus_number
            self.show_driver_view()
            self.root.current = "driver_view"
        else:
            self.show_dialog("Invalid bus or password!")

    def show_driver_view(self):
        screen = self.root.get_screen("driver_view")
        box = screen.ids.driver_box
        box.clear_widgets()

        box.add_widget(MDLabel(text=f"Bus {self.current_bus} Students", halign="center", bold=True))

        going_count, notgoing_count = 0, 0
        for sid, info in students.items():
            if info["bus"] == self.current_bus:
                status = info["status"]
                if status == "Going": going_count += 1
                elif status == "Not Going": notgoing_count += 1
                box.add_widget(MDLabel(text=f"{info['name']} ({sid}) - {status}", halign="left"))

        box.add_widget(MDLabel(text=f"Going: {going_count} | Not Going: {notgoing_count}", halign="center", bold=True))
        box.add_widget(MDRaisedButton(text="Refresh", pos_hint={"center_x": 0.5}, on_release=lambda x: self.show_driver_view()))
        box.add_widget(MDRaisedButton(text="Back", pos_hint={"center_x": 0.5}, on_release=lambda x: self.go_back()))

    def go_back(self): self.root.current = "menu"

    def show_dialog(self, text):
        if not self.dialog:
            self.dialog = MDDialog(title="Info", type="custom", content_cls=MDLabel(text=text, halign="center"))
        else:
            self.dialog.content_cls.text = text
        self.dialog.open()

if __name__ == "__main__":
    BusApp().run()
