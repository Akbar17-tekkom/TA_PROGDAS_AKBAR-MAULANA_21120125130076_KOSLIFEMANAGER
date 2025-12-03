import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import json
import os
from datetime import datetime, date
from playsound3 import playsound3

class KosLifeManager:
    DATA_FILE = "data_file.json"

    def __init__(self, root):
        self.root = root
        self.root.title("KOS LIFE MANAGER")
        self.root.geometry("380x560")

        self.played_alarms = set()

        self.data = self.load_data()
        if "history" not in self.data:
            self.data["history"] = []

        self.todos_gui = []

        self.page_home()
        self.page_todo()
        self.page_uang()

        self.check_waktu()

    def load_data(self):
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                return {"todo": [], "uang": [], "history": []}
        return {"todo": [], "uang": [], "history": []}

    def simpan_data(self):
        with open(self.DATA_FILE, "w") as f:
            json.dump(self.data, f, indent=4)

    def tambah_history(self, teks):
        now = datetime.now().strftime("%H:%M")
        entry = f"[{now}] {teks}"

        if "history" not in self.data:
            self.data["history"] = []
        self.data["history"].insert(0, entry)
        self.data["history"] = self.data["history"][:50]

        self.simpan_data()
        try:
            self.update_history_home()
        except Exception:
            pass

    def update_history_home(self):
        for w in self.history_frame.winfo_children():
            w.destroy()

        for item in self.data.get("history", [])[:5]:
            tk.Label(self.history_frame, text="- " + item, anchor="w", justify="left").pack(anchor="w")

    def check_waktu(self):
        waktu_sekarang = datetime.now().strftime("%H:%M")
        today_str = date.today().isoformat()

        for idx, item in enumerate(self.data.get("todo", [])):
            waktu = item.get("waktu", "-")
            if not waktu or waktu == "-" or waktu.strip() == "":
                continue

            key = (idx, item.get("tugas", ""), waktu, today_str)

            if waktu == waktu_sekarang and key not in self.played_alarms:
                try:
                    playsound3.playsound("alarm.mp3")
                except Exception:
                    pass

                self.played_alarms.add(key)

                tugas = item.get("tugas", "Tugas")
                self.tambah_history(f"Alarm: {tugas} ({waktu})")

        self.root.after(1000, self.check_waktu)

    def hitung_total_uang(self):
        return sum(item.get("nominal", 0) for item in self.data.get("uang", []))


    def add_placeholder(self, entry, placeholder):
        entry.insert(0, placeholder)
        entry.config(fg="gray")

        def on_focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg="black")

        def on_focus_out(event):
            if entry.get() == "":
                entry.insert(0, placeholder)
                entry.config(fg="gray")

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    def page_home(self):
        self.label1 = tk.Frame(self.root)
        self.label1.pack(fill="both", expand=True)

        tk.Label(self.label1, text="Beranda", font=("Segoe UI", 16)).pack(anchor="w", padx=10, pady=10)

        frame_tombol = tk.Frame(self.label1)
        frame_tombol.pack(anchor="w", padx=20, pady=10)

        try:
            icontodo = Image.open("todo.jpeg").resize((56, 56))
            self.icon_todo = ImageTk.PhotoImage(icontodo)
            btn1 = tk.Button(frame_tombol, image=self.icon_todo, command=self.tampil_todo)
        except Exception:
            btn1 = tk.Button(frame_tombol, text="To-Do", command=self.tampil_todo, width=8)
        btn1.pack(side="left", padx=8)

        try:
            iconcuang = Image.open("uang.jpeg").resize((56, 56))
            self.icon_uang = ImageTk.PhotoImage(iconcuang)
            btn2 = tk.Button(frame_tombol, image=self.icon_uang, command=self.tampil_uang)
        except Exception:
            btn2 = tk.Button(frame_tombol, text="Keuangan", command=self.tampil_uang, width=8)
        btn2.pack(side="left", padx=8)

        tk.Label(self.label1, text="Aktivitas Terbaru:", font=("Segoe UI", 12)).pack(anchor="w", padx=10, pady=(10, 0))
        self.history_frame = tk.Frame(self.label1)
        self.history_frame.pack(anchor="w", padx=20, pady=5)
        self.update_history_home()

    def page_todo(self):
        self.label3 = tk.Frame(self.root)

        tk.Label(self.label3, text="To-Do List", font=("Segoe UI", 16)).pack(anchor="w", padx=10, pady=10)

        frame_input = tk.Frame(self.label3)
        frame_input.pack(pady=8, anchor="w", padx=10)

        self.todo_entry = tk.Entry(frame_input, width=25)
        self.todo_entry.grid(row=0, column=0, padx=5)

        frame_jam = tk.Frame(frame_input)
        frame_jam.grid(row=1, column=0, pady=6, sticky="w")

        self.masuk_jam = tk.Entry(frame_jam,textvariable="jam", width=5)
        self.masuk_jam.grid(row=0, column=0, padx=5)
        tk.Label(frame_jam, text=":").grid(row=0, column=1, padx=1)
        self.masuk_menit = tk.Entry(frame_jam, width=5)
        self.masuk_menit.grid(row=0, column=2)

        tk.Button(frame_input, text="Tambah", command=self.tambah_todo).grid(row=0, column=1, padx=8)

        tk.Button(frame_input, text="Hapus Terpilih", bg="#E53935", fg="white",
                  command=self.hapus_todo).grid(row=0, column=2, padx=5)

        scroll_container = tk.Frame(self.label3)
        scroll_container.pack(fill="both", expand=True, padx=10, pady=5)

        self.canvas = tk.Canvas(scroll_container, height=330)
        self.scrollbar = tk.Scrollbar(scroll_container, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas)

        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        frame_back_todo = tk.Frame(self.label3)
        frame_back_todo.pack(side="bottom", fill="x")
        tk.Button(frame_back_todo, text="⟵ Kembali",
                  command=lambda: self.kembali(self.label3),
                  bg="#129AD4", fg="white").pack(side="left", padx=10, pady=10)

        self.load_todo_gui()
        self.add_placeholder(self.todo_entry, "masukkan tugas...")

    def tampil_todo(self):
        self.label1.pack_forget()
        self.label3.pack(fill="both", expand=True)

    def tambah_todo(self):
        text = self.todo_entry.get().strip()
        jam = self.masuk_jam.get().strip()
        menit = self.masuk_menit.get().strip()

        if not text:
            messagebox.showwarning("Kosong", "Tulis dulu tugasnya")
            return

        if jam == "" and menit == "":
            waktu = "-"
        else:
            if not (jam.isdigit() and menit.isdigit()):
                messagebox.showwarning("Waktu salah", "Jam & menit harus angka (atau kosong)")
                return
            hh = int(jam)
            mm = int(menit)
            if not (0 <= hh <= 23 and 0 <= mm <= 59):
                messagebox.showwarning("Waktu salah", "Jam harus 0-23 dan menit 0-59")
                return
            waktu = f"{jam.zfill(2)}:{menit.zfill(2)}"

        self.data.setdefault("todo", []).append({"tugas": text, "waktu": waktu, "done": False})
        self.simpan_data()

        self.buat_checkbutton(len(self.data["todo"]) - 1)

        self.tambah_history(f"Tambah To-Do: {text} ({waktu})")

        self.todo_entry.delete(0, tk.END)
        self.masuk_jam.delete(0, tk.END)
        self.masuk_menit.delete(0, tk.END)

    def hapus_todo(self):
        removed_any = False
        to_remove = [i for i, it in enumerate(self.data.get("todo", [])) if it.get("done", False)]
        if not to_remove:
            
            sel = messagebox.askyesno("Hapus tugas", "Tidak ada tugas tercentang. Mau hapus tugas terakhir?")
            if sel:
                if self.data.get("todo"):
                    removed = self.data["todo"].pop()
                    self.tambah_history(f"Hapus To-Do: {removed.get('tugas','')}")
                    removed_any = True
            else:
                return
        else:
            for idx in sorted(to_remove, reverse=True):
                removed = self.data["todo"].pop(idx)
                self.tambah_history(f"Hapus To-Do: {removed.get('tugas','')}")
                removed_any = True

        if removed_any:
            self.simpan_data()
            self.played_alarms.clear()
            self.load_todo_gui()

    def buat_checkbutton(self, index):
        item = self.data["todo"][index]
        var = tk.BooleanVar(value=item.get("done", False))

        cb = tk.Checkbutton(
            self.scroll_frame,
            text=f"{item['tugas']}  ({item['waktu']})",
            variable=var,
            anchor="w",
            width=34,
            command=lambda v=var, cb_widget=None, idx=index: self.on_check(v, None, idx)
        )
        cb.pack(anchor="w", pady=2)

        cb.configure(command=lambda v=var, cb_widget=cb, idx=index: self.on_check(v, cb_widget, idx))

        if item.get("done", False):
            cb.config(fg="gray", font=("Arial", 12, "overstrike"))
        else:
            cb.config(fg="black", font=("Arial", 12, "normal"))

        self.todos_gui.append((var, cb, index))

    def on_check(self, var, checkbutton, index):
        try:
            tugas = self.data["todo"][index].get("tugas", "Tugas")
        except Exception:
            self.load_todo_gui()
            return

        prev = self.data["todo"][index].get("done", False)

        if var.get():
            self.data["todo"][index]["done"] = True
            self.simpan_data()
            if checkbutton:
                checkbutton.config(fg="gray", font=("Arial", 12, "overstrike"))

            if not prev:
                try:
                    playsound3.playsound("ting.mp3")
                except Exception:
                    pass
                messagebox.showinfo("Selamat!", "Tugas selesai!")
                self.tambah_history(f"Selesai To-Do: {tugas}")
        else:
            self.data["todo"][index]["done"] = False
            self.simpan_data()
            if checkbutton:
                checkbutton.config(fg="black", font=("Arial", 12, "normal"))
            self.tambah_history(f"Batalkan To-Do: {tugas}")

    def load_todo_gui(self):
        for w in self.scroll_frame.winfo_children():
            w.destroy()
        self.todos_gui.clear()
        for i in range(len(self.data.get("todo", []))):
            self.buat_checkbutton(i)

    def page_uang(self):
        self.label4 = tk.Frame(self.root)
        tk.Label(self.label4, text="Catat Keuangan", font=("Segoe UI", 16)).pack(anchor="w", padx=10, pady=10)

        frame_back_uang = tk.Frame(self.label4)
        frame_back_uang.pack(side="bottom", fill="x")
        tk.Button(frame_back_uang, text="⟵ Kembali",
                  command=lambda: self.kembali(self.label4),
                  bg="#129AD4", fg="white").pack(side="left", padx=10, pady=10)

        frame_masuk = tk.Frame(self.label4)
        frame_masuk.pack(pady=10, anchor="w", padx=10)

        self.masukkan_uang = tk.Entry(frame_masuk, width=15)
        self.masukkan_uang.grid(row=0, column=0, padx=5)

        tk.Button(frame_masuk, text="+ Pemasukan", bg="#4CAF50", fg="white",
                  command=lambda: self.add_money("masuk")).grid(row=0, column=3, padx=5)

        tk.Button(frame_masuk, text="- Pengeluaran", bg="#E53935", fg="white",
                  command=lambda: self.add_money("keluar")).grid(row=0, column=4, padx=5)

        tk.Label(self.label4, text="Riwayat Keuangan (terbaru):", font=("Segoe UI", 10)).pack(anchor="w", padx=10)
        self.riwayat_uang_frame = tk.Frame(self.label4)
        self.riwayat_uang_frame.pack(anchor="w", padx=20, pady=5)
        self.update_riwayat_uang()

        self.label_total_saldo = tk.Label(self.label4, text="Total Saldo: 0", font=("Segoe UI", 12, "bold"))
        self.label_total_saldo.pack(anchor="w", padx=10, pady=(0, 10))
        total = self.hitung_total_uang()
        self.label_total_saldo.config(text=f"Total Saldo: {total}")

    def tampil_uang(self):
        self.label1.pack_forget()
        self.label4.pack(fill="both", expand=True)

    def update_riwayat_uang(self):
        for w in self.riwayat_uang_frame.winfo_children():
            w.destroy()

        for item in self.data.get("uang", [])[:5]:
            nominal = item.get("nominal", 0)
            tipe = item.get("tipe", "")

            if tipe == "masuk":
                txt = f"+{abs(nominal)} (Pemasukan)"
            else:
                txt = f"-{abs(nominal)} (Pengeluaran)"

            tk.Label(self.riwayat_uang_frame, text=txt).pack(anchor="w")

    def add_money(self, tipe):
        try:
            uang = int(self.masukkan_uang.get())
            if tipe == "keluar":
                uang = -abs(uang)

            self.data.setdefault("uang", []).insert(0, {"nominal": uang, "tipe": tipe})
            self.simpan_data()
            self.update_riwayat_uang()

            if tipe == "masuk":
                self.tambah_history(f"Pemasukan: +{abs(uang)}")
            else:
                self.tambah_history(f"Pengeluaran: -{abs(uang)}")

            self.masukkan_uang.delete(0, tk.END)

        except Exception:
            messagebox.showerror("ERROR", "Masukkan angka yang valid")

    def kembali(self, page):
        page.pack_forget()
        try:
            self.update_history_home()
            self.update_riwayat_uang()
        except Exception:
            pass
        self.label1.pack(fill="both", expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = KosLifeManager(root)
    root.mainloop()