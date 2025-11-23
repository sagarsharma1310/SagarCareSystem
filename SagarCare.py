
import os
import sqlite3
import random
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox, filedialog

# ---------------------- DATABASE SETUP ----------------------
DB_PATH = "hospital.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Admissions table;
cursor.execute("""
CREATE TABLE IF NOT EXISTS admission (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT UNIQUE,
    patient_name TEXT,
    age INTEGER,
    contact TEXT,
    gender TEXT,
    disease TEXT,
    admit_date TEXT,
    blood_group TEXT,
    doctor_name TEXT
)
""")

# Add room_no
cursor.execute("PRAGMA table_info(admission)")
cols = [r[1] for r in cursor.fetchall()]
if 'room_no' not in cols:
    try:
        cursor.execute("ALTER TABLE admission ADD COLUMN room_no TEXT")
    except sqlite3.OperationalError:
        pass

# Nurse treatment records
cursor.execute("""
CREATE TABLE IF NOT EXISTS nurse_treatment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT,
    nurse_name TEXT,
    nurse_notes TEXT,
    shift TEXT,
    prescription TEXT,
    date TEXT
)
""")

# New staff tables: doctors and nurses
cursor.execute("""
CREATE TABLE IF NOT EXISTS doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    specialization TEXT,
    contact TEXT,
    shift TEXT,
    photo_path TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS nurses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact TEXT,
    shift TEXT,
    photo_path TEXT
)
""")

# Rooms table
cursor.execute("""
CREATE TABLE IF NOT EXISTS rooms (
    room_no TEXT PRIMARY KEY,
    type TEXT,
    status TEXT,
    patient_id TEXT
)
""")

# Simple initial room data (if empty)
cursor.execute("SELECT COUNT(*) FROM rooms")
if cursor.fetchone()[0] == 0:
    initial_rooms = [
        ('101', 'Private', 'Available', None),
        ('102', 'Shared', 'Available', None),
        ('201', 'ICU', 'Available', None),
        ('202', 'Shared', 'Available', None)
    ]
    cursor.executemany("INSERT OR IGNORE INTO rooms (room_no, type, status, patient_id) VALUES (?, ?, ?, ?)", initial_rooms)

conn.commit()

# ---------------------- APPLICATION ----------------------
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")


class HospitalApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sagar Care Hospital System")
        self.geometry("1100x700")

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=10)
        self.sidebar.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)

        ctk.CTkLabel(self.sidebar, text="SAGAR CARE", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=12, pady=18)

        ctk.CTkButton(self.sidebar, text="Dashboard", command=self.show_dashboard).grid(row=1, column=0, padx=12, pady=6, sticky="ew")
        ctk.CTkButton(self.sidebar, text="New Admission", command=self.show_admission_form).grid(row=2, column=0, padx=12, pady=6, sticky="ew")
        ctk.CTkButton(self.sidebar, text="Admitted Patients", command=self.show_admitted_patients).grid(row=3, column=0, padx=12, pady=6, sticky="ew")
        ctk.CTkButton(self.sidebar, text="Room Availability", command=self.show_room_availability).grid(row=4, column=0, padx=12, pady=6, sticky="ew")
        ctk.CTkButton(self.sidebar, text="Staff", command=self.show_staff_page).grid(row=5, column=0, padx=12, pady=6, sticky="ew")
        ctk.CTkButton(self.sidebar, text="Bill", command=self.show_billing_page).grid(row=6, column=0, padx=12, pady=6, sticky="ew")
       # ctk.CTkButton(self.sidebar, text="Ambulance Status", command=lambda: self.show_message("Not Implemented", "Ambulance page not in this build.")).grid(row=7, column=0, padx=12, pady=6, sticky="ew")
        ctk.CTkButton(self.sidebar, text="Exit", command=self.on_closing, fg_color="#ff4444").grid(row=8, column=0, padx=12, pady=20, sticky="ew")

        # Main content area
        self.main_area = ctk.CTkFrame(self, corner_radius=10)
        self.main_area.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.current_widgets = []

        # Start at dashboard
        self.show_dashboard()

    # ---------------------- Utilities ----------------------
    def clear_main(self):
        for w in self.current_widgets:
            try:
                w.destroy()
            except:
                pass
        self.current_widgets = []

    def show_message(self, title, message):
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("400x160")
        ctk.CTkLabel(dialog, text=message, wraplength=360).pack(padx=20, pady=20)
        ctk.CTkButton(dialog, text="OK", command=dialog.destroy).pack(pady=10)

    def on_closing(self):
        conn.commit()
        conn.close()
        self.destroy()

    # ---------------------- Dashboard ----------------------
    def show_dashboard(self):
        self.clear_main()
        frame = ctk.CTkFrame(self.main_area)
        frame.pack(fill="both", expand=True)
        self.current_widgets.append(frame)

        ctk.CTkLabel(frame, text="Dashboard", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)

        cursor.execute("SELECT COUNT(*) FROM admission")
        patients = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM doctors")
        doctors = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM nurses")
        nurses = cursor.fetchone()[0]

        stats_frame = ctk.CTkFrame(frame)
        stats_frame.pack(padx=20, pady=10, fill="x")
        self.current_widgets.append(stats_frame)

        ctk.CTkLabel(stats_frame, text=f"Admitted Patients: {patients}", font=ctk.CTkFont(size=16)).grid(row=0, column=0, padx=20, pady=10)
        ctk.CTkLabel(stats_frame, text=f"Doctors: {doctors}", font=ctk.CTkFont(size=16)).grid(row=0, column=1, padx=20, pady=10)
        ctk.CTkLabel(stats_frame, text=f"Nurses: {nurses}", font=ctk.CTkFont(size=16)).grid(row=0, column=2, padx=20, pady=10)

    # ---------------------- Admission Form ----------------------
    def show_admission_form(self):
        self.clear_main()
        frame = ctk.CTkFrame(self.main_area)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.current_widgets.append(frame)

        ctk.CTkLabel(frame, text="New Patient Admission", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, columnspan=2, pady=10)

        labels = ["Patient Name", "Age", "Contact", "Gender", "Disease", "Blood Group"]
        self.admission_entries = {}

        for i, label in enumerate(labels):
            ctk.CTkLabel(frame, text=label).grid(row=i+1, column=0, sticky="w", padx=10, pady=6)
            if label == "Gender":
                var = ctk.StringVar(value="Male")
                opt = ctk.CTkOptionMenu(frame, variable=var, values=["Male", "Female", "Other"])
                opt.grid(row=i+1, column=1, padx=10, pady=6, sticky="ew")
                self.admission_entries[label] = var
            else:
                entry = ctk.CTkEntry(frame)
                entry.grid(row=i+1, column=1, padx=10, pady=6, sticky="ew")
                self.admission_entries[label] = entry

        # Doctor choice
        ctk.CTkLabel(frame, text="Doctor Name").grid(row=len(labels)+1, column=0, padx=10, pady=6, sticky="w")
        cursor.execute("SELECT name FROM doctors ORDER BY name")
        doctors = [d[0] for d in cursor.fetchall()]
        doctors = doctors if doctors else ["No Doctors Available"]
        self.doctor_var = ctk.StringVar(value=doctors[0])
        doc_menu = ctk.CTkOptionMenu(frame, variable=self.doctor_var, values=doctors)
        doc_menu.grid(row=len(labels)+1, column=1, padx=10, pady=6, sticky="ew")

        # Room choice (only available rooms)
        ctk.CTkLabel(frame, text="Room Number").grid(row=len(labels)+2, column=0, padx=10, pady=6, sticky="w")
        cursor.execute("SELECT room_no FROM rooms WHERE status='Available' ORDER BY room_no")
        rooms = [r[0] for r in cursor.fetchall()]
        rooms = rooms if rooms else ["No Rooms Available"]
        self.room_var = ctk.StringVar(value=rooms[0])
        room_menu = ctk.CTkOptionMenu(frame, variable=self.room_var, values=rooms)
        room_menu.grid(row=len(labels)+2, column=1, padx=10, pady=6, sticky="ew")

        # Assign Nurse in choice
        ctk.CTkLabel(frame, text="Assign Nurse").grid(row=len(labels)+3, column=0, padx=10, pady=6, sticky="w")
        cursor.execute("SELECT id, name FROM nurses ORDER BY name")
        nurses = [f"{r[0]}: {r[1]}" for r in cursor.fetchall()]
        nurses = nurses if nurses else ["None"]
        self.nurse_var = ctk.StringVar(value=nurses[0])
        nurse_menu = ctk.CTkOptionMenu(frame, variable=self.nurse_var, values=nurses)
        nurse_menu.grid(row=len(labels)+3, column=1, padx=10, pady=6, sticky="ew")

        submit_btn = ctk.CTkButton(frame, text="Admit Patient", command=self.save_admission, fg_color="#00cc99")
        submit_btn.grid(row=len(labels)+4, column=1, pady=20, sticky="e")

    def save_admission(self):
        get = lambda k: (self.admission_entries[k].get() if not isinstance(self.admission_entries[k], ctk.StringVar) else self.admission_entries[k].get())
        name = get("Patient Name").strip()
        age = get("Age").strip()
        contact = get("Contact").strip()
        gender = get("Gender").strip()
        disease = get("Disease").strip()
        blood = get("Blood Group").strip()
        doctor = self.doctor_var.get().strip()
        room_sel = self.room_var.get().strip()
        nurse_selection = self.nurse_var.get()

        if not all([name, age, contact, gender, disease, blood, doctor]) or doctor == "No Doctors Available":
            self.show_message("Validation", "Please fill all patient fields and select a doctor.")
            return

        if room_sel == "No Rooms Available":
            self.show_message("Validation", "No rooms are available. Please add rooms first.")
            return

        patient_id = "P" + str(random.randint(10000, 99999))
        admit_date = datetime.now().strftime("%Y-%m-%d %H:%M")

        cursor.execute("INSERT INTO admission (patient_id, patient_name, age, contact, gender, disease, admit_date, blood_group, doctor_name, room_no) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (patient_id, name, age, contact, gender, disease, admit_date, blood, doctor, room_sel))
        conn.commit()

        # Mark room as occupied
        cursor.execute("UPDATE rooms SET status='Occupied', patient_id=? WHERE room_no=?", (patient_id, room_sel))
        conn.commit()

        # add a nurse to patient if selected
        if nurse_selection and nurse_selection != "None":
            nurse_id = nurse_selection.split(":")[0]
            nurse_name = nurse_selection.split(": ")[1]
            cursor.execute("INSERT INTO nurse_treatment (patient_id, nurse_name, nurse_notes, shift, prescription, date) VALUES (?, ?, ?, ?, ?, ?)",
                           (patient_id, nurse_name, "Assigned on admission", "", "", admit_date))
            conn.commit()

        messagebox.showinfo("Success", f"{name} admitted with Patient ID {patient_id} and Room {room_sel}.")
        self.show_admission_form()

    # ---------------------- Admitted Patients ----------------------
    def show_admitted_patients(self):
        self.clear_main()
        frame = ctk.CTkFrame(self.main_area)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.current_widgets.append(frame)

        ctk.CTkLabel(frame, text="Admitted Patients", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

        list_frame = ctk.CTkFrame(frame)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.current_widgets.append(list_frame)

        cursor.execute("SELECT patient_id, patient_name, disease, doctor_name, room_no FROM admission ORDER BY patient_name")
        rows = cursor.fetchall()

        if not rows:
            ctk.CTkLabel(list_frame, text="No admitted patients.").pack(pady=10)
            return

        for r in rows:
            pid, name, disease, doctor, roomno = r
            item = ctk.CTkFrame(list_frame, corner_radius=8)
            item.pack(fill="x", pady=6)
            self.current_widgets.append(item)

            ctk.CTkLabel(item, text=f"{name}  |  {disease}  |  Room: {roomno}", font=ctk.CTkFont(size=16)).pack(side="left", padx=12, pady=10)
            ctk.CTkButton(item, text="View Details", command=lambda p=pid: self.view_patient_details(p)).pack(side="right", padx=12, pady=8)

    def view_patient_details(self, patient_id):
        self.clear_main()
        frame = ctk.CTkFrame(self.main_area)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.current_widgets.append(frame)

        ctk.CTkLabel(frame, text="Patient Details", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=10)

        cursor.execute("SELECT patient_id, patient_name, age, contact, gender, disease, admit_date, blood_group, doctor_name, room_no FROM admission WHERE patient_id=?", (patient_id,))
        data = cursor.fetchone()
        if not data:
            self.show_message("Not found", "Patient record not found.")
            return

        pid, name, age, contact, gender, disease, admit_date, blood_group, doctor, roomno = data

        info = ctk.CTkFrame(frame)
        info.pack(fill="x", padx=10, pady=8)
        self.current_widgets.append(info)

        ctk.CTkLabel(info, text=f"Patient ID: {pid}", font=ctk.CTkFont(size=14)).grid(row=0, column=0, sticky="w", padx=8, pady=4)
        ctk.CTkLabel(info, text=f"Name: {name}", font=ctk.CTkFont(size=14)).grid(row=1, column=0, sticky="w", padx=8, pady=4)
        ctk.CTkLabel(info, text=f"Age: {age}", font=ctk.CTkFont(size=14)).grid(row=2, column=0, sticky="w", padx=8, pady=4)
        ctk.CTkLabel(info, text=f"Contact: {contact}", font=ctk.CTkFont(size=14)).grid(row=3, column=0, sticky="w", padx=8, pady=4)
        ctk.CTkLabel(info, text=f"Gender: {gender}", font=ctk.CTkFont(size=14)).grid(row=4, column=0, sticky="w", padx=8, pady=4)
        ctk.CTkLabel(info, text=f"Disease: {disease}", font=ctk.CTkFont(size=14)).grid(row=5, column=0, sticky="w", padx=8, pady=4)
        ctk.CTkLabel(info, text=f"Admit Date: {admit_date}", font=ctk.CTkFont(size=14)).grid(row=6, column=0, sticky="w", padx=8, pady=4)
        ctk.CTkLabel(info, text=f"Blood Group: {blood_group}", font=ctk.CTkFont(size=14)).grid(row=7, column=0, sticky="w", padx=8, pady=4)
        ctk.CTkLabel(info, text=f"Doctor Name: {doctor}", font=ctk.CTkFont(size=14, weight="bold"), text_color="#00ffcc").grid(row=8, column=0, sticky="w", padx=8, pady=8)
        ctk.CTkLabel(info, text=f"Room No: {roomno}", font=ctk.CTkFont(size=14, weight="bold"), text_color="#00ffcc").grid(row=9, column=0, sticky="w", padx=8, pady=8)

        # Discharge / Delete buttons
        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(fill="x", padx=10, pady=10)
        self.current_widgets.append(btn_frame)

        ctk.CTkButton(btn_frame, text="Discharge Patient", fg_color="#ff884d", command=lambda: self.discharge_patient(pid)).pack(side="left", padx=8)
        ctk.CTkButton(btn_frame, text="Delete Record", fg_color="#ff4444", command=lambda: self.delete_admission(pid)).pack(side="left", padx=8)

        # Nurse details
        ctk.CTkLabel(frame, text="Assigned / Nurse Records", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        n_frame = ctk.CTkFrame(frame)
        n_frame.pack(fill="both", expand=True, padx=10, pady=8)
        self.current_widgets.append(n_frame)

        cursor.execute("SELECT nurse_name, nurse_notes, shift, prescription, date FROM nurse_treatment WHERE patient_id=? ORDER BY date DESC", (patient_id,))
        notes = cursor.fetchall()

        if not notes:
            ctk.CTkLabel(n_frame, text="No nurse records found.").pack(pady=10)
        else:
            for rec in notes:
                nurse_name, nurse_notes, shift, prescription, date = rec
                box = ctk.CTkFrame(n_frame, corner_radius=8)
                box.pack(fill="x", pady=6, padx=6)
                self.current_widgets.append(box)

                ctk.CTkLabel(box, text=f"Nurse: {nurse_name}  |  Shift: {shift}  |  Date: {date}", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=8, pady=6)
                ctk.CTkLabel(box, text=f"Notes: {nurse_notes}").pack(anchor="w", padx=8, pady=2)
                ctk.CTkLabel(box, text=f"Prescription: {prescription}").pack(anchor="w", padx=8, pady=2)

    # ---------------------- Discharge / Delete ----------------------
    def discharge_patient(self, patient_id):
        # Free room if assigned
        cursor.execute("SELECT room_no FROM admission WHERE patient_id=?", (patient_id,))
        row = cursor.fetchone()
        if row and row[0]:
            room = row[0]
            cursor.execute("UPDATE rooms SET status='Available', patient_id=NULL WHERE room_no=?", (room,))

        # Delete admission record
        cursor.execute("DELETE FROM admission WHERE patient_id=?", (patient_id,))
        conn.commit()
        messagebox.showinfo("Discharged", f"Patient {patient_id} discharged and room freed.")
        self.show_admitted_patients()

    def delete_admission(self, patient_id):
        # Same as discharge but with different message
        cursor.execute("SELECT room_no FROM admission WHERE patient_id=?", (patient_id,))
        row = cursor.fetchone()
        if row and row[0]:
            room = row[0]
            cursor.execute("UPDATE rooms SET status='Available', patient_id=NULL WHERE room_no=?", (room,))
        cursor.execute("DELETE FROM admission WHERE patient_id=?", (patient_id,))
        conn.commit()
        messagebox.showinfo("Deleted", f"Admission record for {patient_id} deleted.")
        self.show_admitted_patients()

    # ---------------------- Room Availability Page ----------------------
    def show_room_availability(self):
        self.clear_main()
        frame = ctk.CTkFrame(self.main_area)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.current_widgets.append(frame)

        ctk.CTkLabel(frame, text="Room Availability", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

        top = ctk.CTkFrame(frame)
        top.pack(fill="x", padx=10, pady=6)
        self.current_widgets.append(top)

        ctk.CTkButton(top, text="Add Room", command=self.add_room_dialog).pack(side="right", padx=8)

        # Room list
        list_frame = ctk.CTkFrame(frame)
        list_frame.pack(fill="both", expand=True, padx=10, pady=8)
        self.current_widgets.append(list_frame)

        cursor.execute("SELECT room_no, type, status, patient_id FROM rooms ORDER BY room_no")
        rooms = cursor.fetchall()

        if not rooms:
            ctk.CTkLabel(list_frame, text="No rooms configured.").pack(pady=10)
            return

        for r in rooms:
            room_no, rtype, status, patient_id = r
            row = ctk.CTkFrame(list_frame)
            row.pack(fill="x", padx=8, pady=4)
            ctk.CTkLabel(row, text=f"Room {room_no}  |  {rtype}  |  {status}").pack(side="left", padx=8)
            ctk.CTkButton(row, text="Edit", width=80, command=lambda rn=room_no: self.edit_room_dialog(rn)).pack(side="right", padx=6)
            ctk.CTkButton(row, text="Delete", width=80, fg_color="#ff4444", command=lambda rn=room_no: self.delete_room(rn)).pack(side="right", padx=6)

    def add_room_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Room")
        dialog.geometry("400x240")

        ctk.CTkLabel(dialog, text="New Room", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, padx=12, pady=12)
        ctk.CTkLabel(dialog, text="Room No").grid(row=1, column=0, sticky="w", padx=12, pady=6)
        rn = ctk.CTkEntry(dialog)
        rn.grid(row=1, column=1, padx=12, pady=6)
        ctk.CTkLabel(dialog, text="Type").grid(row=2, column=0, sticky="w", padx=12, pady=6)
        tp = ctk.CTkEntry(dialog)
        tp.grid(row=2, column=1, padx=12, pady=6)
        ctk.CTkLabel(dialog, text="Status").grid(row=3, column=0, sticky="w", padx=12, pady=6)
        st_var = ctk.StringVar(value="Available")
        ctk.CTkOptionMenu(dialog, variable=st_var, values=["Available", "Occupied", "Cleaning"]).grid(row=3, column=1, padx=12, pady=6)

        def save():
            room_no = rn.get().strip()
            typ = tp.get().strip() or "General"
            status = st_var.get()
            if not room_no:
                messagebox.showerror("Validation", "Room number required")
                return
            cursor.execute("INSERT OR REPLACE INTO rooms (room_no, type, status, patient_id) VALUES (?, ?, ?, NULL)", (room_no, typ, status))
            conn.commit()
            dialog.destroy()
            self.show_room_availability()

        ctk.CTkButton(dialog, text="Save Room", command=save, fg_color="#00cc66").grid(row=4, column=1, padx=12, pady=12, sticky="e")

    def edit_room_dialog(self, room_no):
        cursor.execute("SELECT room_no, type, status, patient_id FROM rooms WHERE room_no=?", (room_no,))
        rec = cursor.fetchone()
        if not rec:
            self.show_message("Not found", "Room not found")
            return
        rn, rtype, status, patient_id = rec

        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Edit Room {rn}")
        dialog.geometry("420x240")

        ctk.CTkLabel(dialog, text=f"Edit Room {rn}", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, padx=12, pady=12)
        ctk.CTkLabel(dialog, text="Type").grid(row=1, column=0, sticky="w", padx=12, pady=6)
        tp = ctk.CTkEntry(dialog)
        tp.insert(0, rtype or "")
        tp.grid(row=1, column=1, padx=12, pady=6)
        ctk.CTkLabel(dialog, text="Status").grid(row=2, column=0, sticky="w", padx=12, pady=6)
        st_var = ctk.StringVar(value=status)
        ctk.CTkOptionMenu(dialog, variable=st_var, values=["Available", "Occupied", "Cleaning"]).grid(row=2, column=1, padx=12, pady=6)

        def save():
            new_type = tp.get().strip() or "General"
            new_status = st_var.get()
            # If making available, clear patient_id
            if new_status == 'Available':
                cursor.execute("UPDATE rooms SET type=?, status=?, patient_id=NULL WHERE room_no=?", (new_type, new_status, rn))
            else:
                cursor.execute("UPDATE rooms SET type=?, status=? WHERE room_no=?", (new_type, new_status, rn))
            conn.commit()
            dialog.destroy()
            self.show_room_availability()

        ctk.CTkButton(dialog, text="Save Changes", command=save, fg_color="#00cc66").grid(row=3, column=1, padx=12, pady=12, sticky="e")

    def delete_room(self, room_no):
        # prevent deleting occupied room
        cursor.execute("SELECT status FROM rooms WHERE room_no=?", (room_no,))
        r = cursor.fetchone()
        if r and r[0] == 'Occupied':
            messagebox.showerror("Cannot delete", "Room is occupied. Free it before deleting.")
            return
        if not messagebox.askyesno("Confirm", "Delete this room? This is permanent."):
            return
        cursor.execute("DELETE FROM rooms WHERE room_no=?", (room_no,))
        conn.commit()
        self.show_room_availability()

    # ---------------------- STAFF MANAGEMENT PAGE ----------------------
    def show_staff_page(self):
        self.clear_main()
        frame = ctk.CTkFrame(self.main_area)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.current_widgets.append(frame)

        ctk.CTkLabel(frame, text="Staff Management", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=8)

        top_frame = ctk.CTkFrame(frame)
        top_frame.pack(fill="x", padx=12, pady=6)
        self.current_widgets.append(top_frame)

        # Search
        search_var = ctk.StringVar()
        ctk.CTkEntry(top_frame, placeholder_text="Search staff by name...", textvariable=search_var).grid(row=0, column=0, padx=6, pady=6, sticky="ew")
        top_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(top_frame, text="Add Doctor", command=self.add_doctor_dialog).grid(row=0, column=1, padx=6, pady=6)
        ctk.CTkButton(top_frame, text="Add Nurse", command=self.add_nurse_dialog).grid(row=0, column=2, padx=6, pady=6)

        # Staff list area
        list_area = ctk.CTkFrame(frame)
        list_area.pack(fill="both", expand=True, padx=12, pady=8)
        self.current_widgets.append(list_area)

        # populate
        def refresh_list(filter_text=""):
            for w in list_area.winfo_children():
                w.destroy()

            # Doctors
            ctk.CTkLabel(list_area, text="Doctors:", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=8, pady=(6, 2))
            cursor.execute("SELECT id, name, specialization, contact, shift, photo_path FROM doctors WHERE name LIKE ? ORDER BY name", ('%'+filter_text+'%',))
            docs = cursor.fetchall()

            if not docs:
                ctk.CTkLabel(list_area, text="No doctors found.").pack(anchor="w", padx=20)
            else:
                for d in docs:
                    did, name, spec, contact, shift, photo = d
                    row = ctk.CTkFrame(list_area)
                    row.pack(fill="x", padx=12, pady=4)
                    ctk.CTkLabel(row, text=f"{name} ({spec})   |   Shift: {shift}   |   Contact: {contact}").pack(side="left", padx=6)
                    ctk.CTkButton(row, text="Edit", width=80, command=lambda id=did: self.edit_doctor_dialog(id)).pack(side="right", padx=6)
                    ctk.CTkButton(row, text="Delete", width=80, fg_color="#ff4444", command=lambda id=did: self.delete_doctor(id)).pack(side="right", padx=6)

            # Nurses
            ctk.CTkLabel(list_area, text="Nurses:", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=8, pady=(12, 2))
            cursor.execute("SELECT id, name, contact, shift, photo_path FROM nurses WHERE name LIKE ? ORDER BY name", ('%'+filter_text+'%',))
            nurs = cursor.fetchall()

            if not nurs:
                ctk.CTkLabel(list_area, text="No nurses found.").pack(anchor="w", padx=20)
            else:
                for n in nurs:
                    nid, name, contact, shift, photo = n
                    row = ctk.CTkFrame(list_area)
                    row.pack(fill="x", padx=12, pady=4)
                    ctk.CTkLabel(row, text=f"{name}   |   Shift: {shift}   |   Contact: {contact}").pack(side="left", padx=6)
                    ctk.CTkButton(row, text="Edit", width=80, command=lambda id=nid: self.edit_nurse_dialog(id)).pack(side="right", padx=6)
                    ctk.CTkButton(row, text="Delete", width=80, fg_color="#ff4444", command=lambda id=nid: self.delete_nurse(id)).pack(side="right", padx=6)

        # wire search
        def on_search_change(var, index, mode):
            refresh_list(search_var.get().strip())
        search_var.trace_add('write', on_search_change)

        refresh_list("")

    # ---------------------- Doctor CRUD ----------------------
    def add_doctor_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Doctor")
        dialog.geometry("420x380")

        ctk.CTkLabel(dialog, text="Doctor Details", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, padx=12, pady=12)

        labels = ["Name", "Specialization", "Contact", "Shift"]
        entries = {}
        for i, lab in enumerate(labels):
            ctk.CTkLabel(dialog, text=lab).grid(row=i+1, column=0, sticky="w", padx=12, pady=6)
            e = ctk.CTkEntry(dialog)
            e.grid(row=i+1, column=1, padx=12, pady=6, sticky="ew")
            entries[lab] = e

        photo_path = ctk.StringVar(value="")
        def choose_photo():
            p = filedialog.askopenfilename(title="Select Photo", filetypes=[("Image files","*.png;*.jpg;*.jpeg;*.gif" )])
            if p:
                photo_path.set(p)
        ctk.CTkButton(dialog, text="Choose Photo", command=choose_photo).grid(row=5, column=0, padx=12, pady=8)
        ctk.CTkLabel(dialog, textvariable=photo_path).grid(row=5, column=1, padx=12, pady=8)

        def save():
            name = entries['Name'].get().strip()
            spec = entries['Specialization'].get().strip()
            contact = entries['Contact'].get().strip()
            shift = entries['Shift'].get().strip()
            p = photo_path.get()
            if not name:
                messagebox.showerror("Validation", "Doctor name is required.")
                return
            cursor.execute("INSERT INTO doctors (name, specialization, contact, shift, photo_path) VALUES (?, ?, ?, ?, ?)",
                           (name, spec, contact, shift, p))
            conn.commit()
            dialog.destroy()
            self.show_staff_page()

        ctk.CTkButton(dialog, text="Save Doctor", command=save, fg_color="#00cc66").grid(row=6, column=1, padx=12, pady=12, sticky="e")

    def edit_doctor_dialog(self, doctor_id):
        cursor.execute("SELECT name, specialization, contact, shift, photo_path FROM doctors WHERE id=?", (doctor_id,))
        rec = cursor.fetchone()
        if not rec:
            self.show_message("Not found", "Doctor not found.")
            return
        name0, spec0, contact0, shift0, photo0 = rec

        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Doctor")
        dialog.geometry("420x380")

        ctk.CTkLabel(dialog, text=f"Edit: {name0}", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, padx=12, pady=12)

        labels = ["Name", "Specialization", "Contact", "Shift"]
        entries = {}
        values = [name0, spec0, contact0, shift0]
        for i, lab in enumerate(labels):
            ctk.CTkLabel(dialog, text=lab).grid(row=i+1, column=0, sticky="w", padx=12, pady=6)
            e = ctk.CTkEntry(dialog)
            e.insert(0, values[i] if values[i] is not None else "")
            e.grid(row=i+1, column=1, padx=12, pady=6, sticky="ew")
            entries[lab] = e

        photo_path = ctk.StringVar(value=photo0 or "")
        def choose_photo():
            p = filedialog.askopenfilename(title="Select Photo", filetypes=[("Image files","*.png;*.jpg;*.jpeg;*.gif" )])
            if p:
                photo_path.set(p)
        ctk.CTkButton(dialog, text="Choose Photo", command=choose_photo).grid(row=5, column=0, padx=12, pady=8)
        ctk.CTkLabel(dialog, textvariable=photo_path).grid(row=5, column=1, padx=12, pady=8)

        def save():
            name = entries['Name'].get().strip()
            spec = entries['Specialization'].get().strip()
            contact = entries['Contact'].get().strip()
            shift = entries['Shift'].get().strip()
            p = photo_path.get()
            if not name:
                messagebox.showerror("Validation", "Doctor name is required.")
                return
            cursor.execute("UPDATE doctors SET name=?, specialization=?, contact=?, shift=?, photo_path=? WHERE id=?",
                           (name, spec, contact, shift, p, doctor_id))
            conn.commit()
            dialog.destroy()
            self.show_staff_page()

        ctk.CTkButton(dialog, text="Save Changes", command=save, fg_color="#00cc66").grid(row=6, column=1, padx=12, pady=12, sticky="e")

    def delete_doctor(self, doctor_id):
        if not messagebox.askyesno("Confirm", "Delete this doctor? This action cannot be undone."):
            return
        # Optional: prevent deleting if doctor assigned to admissions. For now we delete but you can add a check.
        cursor.execute("DELETE FROM doctors WHERE id=?", (doctor_id,))
        conn.commit()
        self.show_staff_page()

    # ---------------------- Nurse CRUD ----------------------
    def add_nurse_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Nurse")
        dialog.geometry("420x320")

        ctk.CTkLabel(dialog, text="Nurse Details", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, padx=12, pady=12)

        labels = ["Name", "Contact", "Shift"]
        entries = {}
        for i, lab in enumerate(labels):
            ctk.CTkLabel(dialog, text=lab).grid(row=i+1, column=0, sticky="w", padx=12, pady=6)
            e = ctk.CTkEntry(dialog)
            e.grid(row=i+1, column=1, padx=12, pady=6, sticky="ew")
            entries[lab] = e

        photo_path = ctk.StringVar(value="")
        def choose_photo():
            p = filedialog.askopenfilename(title="Select Photo", filetypes=[("Image files","*.png;*.jpg;*.jpeg;*.gif" )])
            if p:
                photo_path.set(p)
        ctk.CTkButton(dialog, text="Choose Photo", command=choose_photo).grid(row=4, column=0, padx=12, pady=8)
        ctk.CTkLabel(dialog, textvariable=photo_path).grid(row=4, column=1, padx=12, pady=8)

        def save():
            name = entries['Name'].get().strip()
            contact = entries['Contact'].get().strip()
            shift = entries['Shift'].get().strip()
            p = photo_path.get()
            if not name:
                messagebox.showerror("Validation", "Nurse name is required.")
                return
            cursor.execute("INSERT INTO nurses (name, contact, shift, photo_path) VALUES (?, ?, ?, ?)",
                           (name, contact, shift, p))
            conn.commit()
            dialog.destroy()
            self.show_staff_page()

        ctk.CTkButton(dialog, text="Save Nurse", command=save, fg_color="#00cc66").grid(row=5, column=1, padx=12, pady=12, sticky="e")

    def edit_nurse_dialog(self, nurse_id):
        cursor.execute("SELECT name, contact, shift, photo_path FROM nurses WHERE id=?", (nurse_id,))
        rec = cursor.fetchone()
        if not rec:
            self.show_message("Not found", "Nurse not found.")
            return
        name0, contact0, shift0, photo0 = rec

        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Nurse")
        dialog.geometry("420x320")

        ctk.CTkLabel(dialog, text=f"Edit: {name0}", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, padx=12, pady=12)

        labels = ["Name", "Contact", "Shift"]
        entries = {}
        values = [name0, contact0, shift0]
        for i, lab in enumerate(labels):
            ctk.CTkLabel(dialog, text=lab).grid(row=i+1, column=0, sticky="w", padx=12, pady=6)
            e = ctk.CTkEntry(dialog)
            e.insert(0, values[i] if values[i] is not None else "")
            e.grid(row=i+1, column=1, padx=12, pady=6, sticky="ew")
            entries[lab] = e

        photo_path = ctk.StringVar(value=photo0 or "")
        def choose_photo():
            p = filedialog.askopenfilename(title="Select Photo", filetypes=[("Image files","*.png;*.jpg;*.jpeg;*.gif" )])
            if p:
                photo_path.set(p)
        ctk.CTkButton(dialog, text="Choose Photo", command=choose_photo).grid(row=4, column=0, padx=12, pady=8)
        ctk.CTkLabel(dialog, textvariable=photo_path).grid(row=4, column=1, padx=12, pady=8)

        def save():
            name = entries['Name'].get().strip()
            contact = entries['Contact'].get().strip()
            shift = entries['Shift'].get().strip()
            p = photo_path.get()
            if not name:
                messagebox.showerror("Validation", "Nurse name is required.")
                return
            cursor.execute("UPDATE nurses SET name=?, contact=?, shift=?, photo_path=? WHERE id=?",
                           (name, contact, shift, p, nurse_id))
            conn.commit()
            dialog.destroy()
            self.show_staff_page()

        ctk.CTkButton(dialog, text="Save Changes", command=save, fg_color="#00cc66").grid(row=5, column=1, padx=12, pady=12, sticky="e")

    def delete_nurse(self, nurse_id):
        if not messagebox.askyesno("Confirm", "Delete this nurse? This action cannot be undone."):
            return
        cursor.execute("DELETE FROM nurses WHERE id=?", (nurse_id,))
        conn.commit()
        self.show_staff_page()

    # ---------------------- BILLING PAGE ----------------------
    def show_billing_page(self):
        self.clear_main()

        frame = ctk.CTkFrame(self.main_area)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.current_widgets.append(frame)

        ctk.CTkLabel(frame, text="Billing System",font=ctk.CTkFont(size=22, weight="bold")).pack(pady=10)

        # Patient ID input
        id_frame = ctk.CTkFrame(frame)
        id_frame.pack(pady=10)
        ctk.CTkLabel(id_frame, text="Enter Patient ID: ").pack(side="left", padx=5)

        self.bill_pid = ctk.CTkEntry(id_frame, width=200)
        self.bill_pid.pack(side="left", padx=5)

        ctk.CTkButton(id_frame, text="Load Details", 
                  command=self.load_billing_details).pack(side="left", padx=5)

        # Bill output area
        self.bill_box = ctk.CTkTextbox(frame, width=700, height=400)
        self.bill_box.pack(pady=20)

        # Extra charges section
        extra_frame = ctk.CTkFrame(frame)
        extra_frame.pack(pady=10)

        ctk.CTkLabel(extra_frame, text="Extra Charges (optional): ").grid(row=0, column=0, padx=5)
        self.extra_charges = ctk.CTkEntry(extra_frame, width=120)
        self.extra_charges.grid(row=0, column=1, padx=5)

        ctk.CTkButton(extra_frame, text="Update Total",command=self.update_bill_total).grid(row=0, column=2, padx=10)


    def load_billing_details(self):
        pid = self.bill_pid.get().strip()
        if not pid:
            messagebox.showerror("Error", "Enter Patient ID")
            return

        cursor.execute("""
            SELECT patient_name, disease, admit_date, doctor_name, room_no 
            FROM admission WHERE patient_id=?
        """, (pid,))
        data = cursor.fetchone()

        if not data:
            messagebox.showerror("Error", "No patient found.")
            return

        name, disease, admit, doctor, roomno = data

        # Fetch room type for pricing
        cursor.execute("SELECT type FROM rooms WHERE room_no=?", (roomno,))
        room_type_result = cursor.fetchone()
    
        room_type = room_type_result[0] if room_type_result else "General"

        # Room charges by type
        pricing = {
            "Private": 2500,
            "Shared": 1500,
            "ICU": 5000,
            "General": 1000
        }
        room_cost = pricing.get(room_type, 1200)

        doctor_fee = 700
        nursing_fee = 400
        service_fee = 200

        total = room_cost + doctor_fee + nursing_fee + service_fee

        self.current_bill = {
            "pid": pid,
            "name": name,
            "disease": disease,
            "admit": admit,
            "doctor": doctor,
            "roomno": roomno,
            "room_cost": room_cost,
            "doctor_fee": doctor_fee,
            "nursing_fee": nursing_fee,
            "service_fee": service_fee,
            "total": total
        }

        self.show_bill()


    def show_bill(self):
        b = self.current_bill

        text = f"""
    ------------------- SAGAR CARE HOSPITAL -------------------

    Patient ID     : {b['pid']}
    Patient Name   : {b['name']}
    Disease        : {b['disease']}
    Doctor         : {b['doctor']}
    Room Number    : {b['roomno']}
    Admit Date     : {b['admit']}

    ----------------------- CHARGES ---------------------------
    Room Charge    : Rs {b['room_cost']}
    Doctor Fee     : Rs {b['doctor_fee']}
    Nursing Fee    : Rs {b['nursing_fee']}
    Service Fee    : Rs {b['service_fee']}
    -----------------------------------------------------------

    Total Amount   : Rs {b['total']}

    -----------------------------------------------------------
        """

        self.bill_box.delete("1.0", "end")
        self.bill_box.insert("end", text)


    def update_bill_total(self):
        """Add extra charges."""
        extra = self.extra_charges.get().strip()
        if not extra:
            extra_val = 0
        else:
            try:
                extra_val = int(extra)
            except:
                messagebox.showerror("Error", "Extra charges must be a number")
                return

        self.current_bill["total"] += extra_val
        self.show_bill()



# ---------------------- START APP ----------------------
if __name__ == "__main__":
    app = HospitalApp()
    app.mainloop()
