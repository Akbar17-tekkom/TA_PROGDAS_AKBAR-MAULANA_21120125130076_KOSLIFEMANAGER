import tkinter as tk
from tkinter import messagebox
import json
import os

DATA_FILE = "koslife_data.json"

# --- Load data ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"todos": [], "money": []}

# --- Save data ---
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

root = tk.Tk()
root.title("Koslife Manager")
root.geometry("400x550")

# --- To Do List ---
def add_todo():
    text = todo_entry.get()
    if text:
        data["todos"].append(text)
        todo_list.insert(tk.END, text)
        save_data()
        todo_entry.delete(0, tk.END)

def delete_todo():
    try:
        index = todo_list.curselection()[0]
        todo_list.delete(index)
        del data["todos"][index]
        save_data()
    except:
        messagebox.showwarning("Pilih item", "Pilih tugas yang mau dihapus")

tk.Label(root, text="To-Do List", font=("Arial", 14)).pack()
todo_entry = tk.Entry(root, width=30)
todo_entry.pack()

tk.Button(root, text="Tambah", command=add_todo).pack(pady=3)

todo_list = tk.Listbox(root, width=40, height=10)
todo_list.pack()

tk.Button(root, text="Hapus", command=delete_todo).pack(pady=3)

# --- Keuangan ---
def add_money():
    try:
        nominal = int(money_entry.get())
        kategori = money_var.get()
        data["money"].append({"jenis": kategori, "nominal": nominal})
        save_data()
        update_balance()
        money_entry.delete(0, tk.END)
    except:
        messagebox.showerror("Error", "Masukkan angka!")

def update_balance():
    total = 0
    for m in data["money"]:
        if m["jenis"] == "Pengeluaran":
            total -= m["nominal"]
        else:
            total += m["nominal"]
    saldo_label.config(text=f"Saldo: Rp {total}")

tk.Label(root, text="\nPencatat Keuangan", font=("Arial", 14)).pack()

money_var = tk.StringVar(value="Pengeluaran")
tk.OptionMenu(root, money_var, "Pengeluaran", "Pemasukan").pack()

money_entry = tk.Entry(root)
money_entry.pack()
tk.Button(root, text="Input", command=add_money).pack(pady=4)

saldo_label = tk.Label(root, text="Saldo: Rp 0", font=("Arial", 12))
saldo_label.pack()

update_balance()
root.mainloop()