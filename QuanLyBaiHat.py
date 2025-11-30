import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc
from tkcalendar import DateEntry
from datetime import date, datetime

# =========================================================================
# PHẦN 1: CẤU HÌNH DATABASE
# =========================================================================

def connect_db():
    try:
        conn = pyodbc.connect(
            'Driver={SQL Server};'
            'Server=LAPTOP-AI2HQFS7\SQLEXPRESS;'       
            'Database=QuanLyBaiHat;'
            'Trusted_Connection=yes;'
        )
        return conn
    except Exception as e:
        messagebox.showerror("Lỗi kết nối", f"Không kết nối được SQL Server:\n{e}")
        return None

# Hàm lấy dữ liệu dạng {Ten: Ma} để đổ vào Combobox
def get_map_data(table, id_col, name_col):
    data_map = {}
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT {id_col}, {name_col} FROM {table}")
            for row in cursor.fetchall():
                # Key là Tên (để hiện thị), Value là Mã (để lưu DB)
                data_map[row[1]] = row[0] 
        except: 
            pass
        conn.close()
    return data_map

# =========================================================================
# PHẦN 2: FORM QUẢN LÝ CA SĨ 
# =========================================================================

def open_frmCaSi(current_user_id, role, root_menu):
    # 1. KHỞI TẠO CỬA SỔ
    root = tk.Toplevel()
    role_text = "ADMIN" if role == 1 else "USER"
    root.title(f"Quản Lý Ca Sĩ - {role_text}")
    
    w, h = 1100, 750
    ws = root.winfo_screenwidth(); hs = root.winfo_screenheight()
    x = (ws//2) - (w//2); y = (hs//2) - (h//2)
    root.geometry(f"{w}x{h}+{x}+{y}")
    
    def on_close():
        root.destroy()
        root_menu.deiconify()
    root.protocol("WM_DELETE_WINDOW", on_close)

    # --- GIAO DIỆN ---
    tk.Label(root, text="QUẢN LÝ CA SĨ", font=("Times New Roman", 22, "bold"), fg="OrangeRed").pack(pady=15)
    
    frame_info = tk.LabelFrame(root, text="Thông tin ca sĩ", padx=20, pady=20, font=("Times New Roman", 11, "bold"))
    frame_info.pack(padx=20, fill="x")
    frame_info.grid_columnconfigure(1, weight=1)
    frame_info.grid_columnconfigure(3, weight=1)

    font_style = ("Times New Roman", 10)
    lbl_grid = {"sticky": "w", "pady": 10}
    ent_grid = {"sticky": "ew", "padx": (5, 30)}

    # Hàng 1
    tk.Label(frame_info, text="Mã Ca Sĩ:", font=font_style).grid(row=0, column=0, **lbl_grid)
    entry_ma = tk.Entry(frame_info, font=font_style); entry_ma.grid(row=0, column=1, **ent_grid)
    
    tk.Label(frame_info, text="Tên Ca Sĩ:", font=font_style).grid(row=0, column=2, **lbl_grid)
    entry_ten = tk.Entry(frame_info, font=font_style); entry_ten.grid(row=0, column=3, **ent_grid)

    # Hàng 2
    tk.Label(frame_info, text="Ngày Sinh:", font=font_style).grid(row=1, column=0, **lbl_grid)
    date_entry = DateEntry(frame_info, date_pattern='yyyy-mm-dd', background='darkblue', font=font_style)
    date_entry.grid(row=1, column=1, **ent_grid)

    tk.Label(frame_info, text="Quốc Tịch:", font=font_style).grid(row=1, column=2, **lbl_grid)
    entry_qt = tk.Entry(frame_info, font=font_style)
    entry_qt.grid(row=1, column=3, **ent_grid)

    # KHUNG TÌM KIẾM
    frame_search = tk.Frame(root, pady=5)
    frame_search.pack(padx=20, fill="x")
    tk.Label(frame_search, text="Tìm kiếm ca sĩ:", font=("Times New Roman", 10, "bold")).pack(side="left")
    entry_search = tk.Entry(frame_search, width=40, font=("Times New Roman", 10))
    entry_search.pack(side="left", padx=10)
    
    def search_data(): load_data(entry_search.get()) 
    def reset_search(): entry_search.delete(0, tk.END); load_data() 

    tk.Button(frame_search, text="Tìm", command=search_data, bg="Teal", fg="white", font=("Times New Roman", 9, "bold"), width=8).pack(side="left")
    tk.Button(frame_search, text="Reset", command=reset_search, bg="DarkGray", fg="white", font=("Times New Roman", 9, "bold"), width=8).pack(side="left", padx=5)

    # TREEVIEW
    frame_list = tk.Frame(root)
    frame_list.pack(padx=20, pady=5, fill="both", expand=True)
    cols = ("ma", "ten", "ngay", "qt")
    tree = ttk.Treeview(frame_list, columns=cols, show="headings")
    scroll = ttk.Scrollbar(frame_list, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scroll.set)
    tree.pack(side="left", fill="both", expand=True); scroll.pack(side="right", fill="y")
    
    tree.heading("ma", text="Mã CS"); tree.column("ma", width=120, anchor="center")
    tree.heading("ten", text="Tên Ca Sĩ"); tree.column("ten", width=350, anchor="center")
    tree.heading("ngay", text="Ngày Sinh"); tree.column("ngay", width=150, anchor="center")
    tree.heading("qt", text="Quốc Tịch"); tree.column("qt", width=200, anchor="center")

    # LOGIC
    def load_data(keyword=None):
        try:
            for i in tree.get_children(): tree.delete(i)
            conn = connect_db()
            if not conn: return
            cur = conn.cursor()
            sql = "SELECT MaCaSi, TenCaSi, NgaySinh, QuocTich FROM CaSi"
            params = ()
            if keyword:
                sql += " WHERE TenCaSi LIKE ?"
                params = (f"%{keyword}%",)
            cur.execute(sql, params)
            for r in cur.fetchall():
                ngay = str(r[2]) if r[2] else ""
                tree.insert("", tk.END, values=(r[0], r[1], ngay, r[3]))
            conn.close()
        except Exception as e: messagebox.showerror("Lỗi Load", str(e))

    def clear_input():
        entry_ma.config(state="normal")
        entry_ma.delete(0, tk.END); entry_ten.delete(0, tk.END); entry_qt.delete(0, tk.END)
        date_entry.set_date("1990-01-01")
        entry_search.delete(0, tk.END)
        load_data()

    def them_cs():
        ma = entry_ma.get().strip()
        ten = entry_ten.get().strip()
        qt = entry_qt.get().strip()
        ngay_sinh = date_entry.get_date()
        if ngay_sinh >= date.today():
            return messagebox.showwarning("Lỗi Ngày Tháng", "Ngày sinh phải nhỏ hơn ngày hiện tại!")
        if not ma or not ten or not qt:
            return messagebox.showwarning("Lỗi Dữ Liệu", "Vui lòng nhập đầy đủ Mã, Tên và Quốc tịch.")
        try:
            conn = connect_db()
            sql = "INSERT INTO CaSi (MaCaSi, TenCaSi, NgaySinh, QuocTich) VALUES (?,?,?,?)"
            conn.cursor().execute(sql, (ma, ten, date_entry.get(), qt))
            conn.commit(); conn.close()
            load_data(); clear_input(); messagebox.showinfo("Thành công", "Đã thêm ca sĩ mới!")
        except Exception as e:
            if "PRIMARY KEY" in str(e) or "duplicate" in str(e): messagebox.showerror("Lỗi Trùng Mã", "Mã Ca Sĩ này đã tồn tại.")
            else: messagebox.showerror("Lỗi SQL", f"Lỗi không xác định:\n{e}")

    def sua_cs():
        try:
            sel = tree.selection()
            if not sel: return messagebox.showwarning("Chú ý", "Chọn dòng cần sửa!")
            v = tree.item(sel)["values"]
            entry_ma.delete(0, tk.END); entry_ma.insert(0, v[0])
            entry_ma.config(state="readonly", background="Gainsboro")
            entry_ten.delete(0, tk.END); entry_ten.insert(0, v[1])
            try: date_entry.set_date(v[2])
            except: pass
            entry_qt.delete(0, tk.END); entry_qt.insert(0, v[3])
        except Exception as e: messagebox.showerror("Lỗi Sửa", str(e))

    def luu_cs():
        ma = entry_ma.get().strip()
        ten = entry_ten.get().strip()
        qt = entry_qt.get().strip()
        ngay_sinh = date_entry.get_date()
        if ngay_sinh >= date.today():
             return messagebox.showwarning("Lỗi Ngày Tháng", "Ngày sinh phải nhỏ hơn ngày hiện tại!")
        if not ma or not ten or not qt: return messagebox.showwarning("Lỗi Dữ Liệu", "Vui lòng nhập đầy đủ Mã, Tên và Quốc tịch để lưu.")
        try:
            conn = connect_db()
            sql = "UPDATE CaSi SET TenCaSi=?, NgaySinh=?, QuocTich=? WHERE MaCaSi=?"
            conn.cursor().execute(sql, (ten, date_entry.get(), qt, ma))
            conn.commit(); conn.close()
            load_data(); clear_input(); messagebox.showinfo("Thành công", "Đã lưu cập nhật!")
        except Exception as e: messagebox.showerror("Lỗi Lưu", str(e))

    def xoa_cs():
        ma = entry_ma.get()
        if not ma: return messagebox.showwarning("Lỗi", "Hãy chọn Ca Sĩ (bấm Sửa) để xóa!")
        if messagebox.askyesno("Xác nhận", "Xóa ca sĩ này sẽ xóa cả Bài hát liên quan?"):
            try:
                conn = connect_db()
                conn.cursor().execute("DELETE FROM CaSi WHERE MaCaSi=?", (ma,))
                conn.commit(); conn.close()
                load_data(); clear_input(); messagebox.showinfo("Thành công", "Đã xóa!")
            except Exception as e:
                error_message = str(e).lower()
                if "foreign key" in error_message or "reference" in error_message:
                    messagebox.showerror("Lỗi Ràng Buộc (FK)", "Không thể xóa. Ca sĩ này đang được sử dụng trong bảng Bài Hát hoặc Album.")
                else: messagebox.showerror("Lỗi Xóa", str(e))

    # BUTTONS
    f_btn = tk.Frame(root, pady=15); f_btn.pack(side="bottom", fill="x")
    btn_style = { "font": ("Times New Roman", 10, "bold"), "width": 14, "height": 2, "bd": 3, "relief": "raised" }
    center_frame = tk.Frame(f_btn); center_frame.pack()

    btn_them = tk.Button(center_frame, text="THÊM", command=them_cs, bg="LimeGreen", fg="white", **btn_style)
    btn_luu = tk.Button(center_frame, text="LƯU", command=luu_cs, bg="SteelBlue", fg="white", **btn_style)
    btn_sua = tk.Button(center_frame, text="SỬA", command=sua_cs, bg="Gold", fg="black", **btn_style)
    btn_huy = tk.Button(center_frame, text="HỦY", command=clear_input, bg="DarkGray", fg="white", **btn_style)
    btn_xoa = tk.Button(center_frame, text="XÓA", command=xoa_cs, bg="Red", fg="white", **btn_style)
    btn_thoat = tk.Button(center_frame, text="THOÁT", command=on_close, bg="DarkSlateGray", fg="white", **btn_style)

    if role == 1: # ADMIN
        btn_them.grid(row=0, column=0, padx=10)
        btn_sua.grid(row=0, column=1, padx=10)
        btn_luu.grid(row=0, column=2, padx=10)
        btn_xoa.grid(row=0, column=3, padx=10)
        btn_huy.grid(row=0, column=4, padx=10)
        btn_thoat.grid(row=0, column=5, padx=10)
    else: # USER
        tk.Label(center_frame, text="(User chỉ được xem)", font=("Times New Roman", 10, "italic"), fg="gray").grid(row=0, column=0, padx=10)
        btn_thoat.grid(row=0, column=1, padx=10)
        for child in frame_info.winfo_children(): child.configure(state='disabled')

    tree.bind("<<TreeviewSelect>>", lambda e: None)
    load_data()

# =========================================================================
# PHẦN 3: FORM QUẢN LÝ NHẠC SĨ 
# =========================================================================

def open_frmNhacSi(current_user_id, role, root_menu):
    root = tk.Toplevel()
    role_text = "ADMIN" if role == 1 else "USER"
    root.title(f"Quản Lý Nhạc Sĩ - {role_text}")
    
    w, h = 1100, 750
    ws = root.winfo_screenwidth(); hs = root.winfo_screenheight()
    x = (ws//2) - (w//2); y = (hs//2) - (h//2)
    root.geometry(f"{w}x{h}+{x}+{y}")
    
    def on_close():
        root.destroy()
        root_menu.deiconify()
    root.protocol("WM_DELETE_WINDOW", on_close)

    tk.Label(root, text="QUẢN LÝ NHẠC SĨ", font=("Times New Roman", 22, "bold"), fg="RoyalBlue").pack(pady=15)
    
    frame_info = tk.LabelFrame(root, text="Thông tin nhạc sĩ", padx=20, pady=20, font=("Times New Roman", 11, "bold"))
    frame_info.pack(padx=20, fill="x")
    frame_info.grid_columnconfigure(1, weight=1)
    frame_info.grid_columnconfigure(3, weight=1)

    font_style = ("Times New Roman", 10)
    lbl_grid = {"sticky": "w", "pady": 10}
    ent_grid = {"sticky": "ew", "padx": (5, 30)}

    tk.Label(frame_info, text="Mã Nhạc Sĩ:", font=font_style).grid(row=0, column=0, **lbl_grid)
    entry_ma = tk.Entry(frame_info, font=font_style); entry_ma.grid(row=0, column=1, **ent_grid)
    
    tk.Label(frame_info, text="Tên Nhạc Sĩ:", font=font_style).grid(row=0, column=2, **lbl_grid)
    entry_ten = tk.Entry(frame_info, font=font_style); entry_ten.grid(row=0, column=3, **ent_grid)

    tk.Label(frame_info, text="Ngày Sinh:", font=font_style).grid(row=1, column=0, **lbl_grid)
    date_entry = DateEntry(frame_info, date_pattern='yyyy-mm-dd', background='darkblue', font=font_style)
    date_entry.grid(row=1, column=1, **ent_grid)

    tk.Label(frame_info, text="Quốc Tịch:", font=font_style).grid(row=1, column=2, **lbl_grid)
    entry_qt = tk.Entry(frame_info, font=font_style); entry_qt.grid(row=1, column=3, **ent_grid)

    # KHUNG TÌM KIẾM
    frame_search = tk.Frame(root, pady=5); frame_search.pack(padx=20, fill="x")
    tk.Label(frame_search, text="Tìm kiếm nhạc sĩ:", font=("Times New Roman", 10, "bold")).pack(side="left")
    entry_search = tk.Entry(frame_search, width=40, font=("Times New Roman", 10)); entry_search.pack(side="left", padx=10)
    
    def search_data(): load_data(entry_search.get()) 
    def reset_search(): entry_search.delete(0, tk.END); load_data() 

    tk.Button(frame_search, text="Tìm", command=search_data, bg="Teal", fg="white", font=("Times New Roman", 9, "bold"), width=8).pack(side="left")
    tk.Button(frame_search, text="Reset", command=reset_search, bg="DarkGray", fg="white", font=("Times New Roman", 9, "bold"), width=8).pack(side="left", padx=5)

    # TREEVIEW
    frame_list = tk.Frame(root); frame_list.pack(padx=20, pady=5, fill="both", expand=True)
    cols = ("ma", "ten", "ngay", "qt")
    tree = ttk.Treeview(frame_list, columns=cols, show="headings")
    scroll = ttk.Scrollbar(frame_list, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scroll.set)
    tree.pack(side="left", fill="both", expand=True); scroll.pack(side="right", fill="y")
    
    tree.heading("ma", text="Mã NS"); tree.column("ma", width=120, anchor="center")
    tree.heading("ten", text="Tên Nhạc Sĩ"); tree.column("ten", width=350, anchor="center")
    tree.heading("ngay", text="Ngày Sinh"); tree.column("ngay", width=150, anchor="center")
    tree.heading("qt", text="Quốc Tịch"); tree.column("qt", width=200, anchor="center")

    # LOGIC
    def load_data(keyword=None):
        try:
            for i in tree.get_children(): tree.delete(i)
            conn = connect_db()
            if not conn: return
            cur = conn.cursor()
            sql = "SELECT MaNhacSi, TenNhacSi, NgaySinh, QuocTich FROM NhacSi"
            params = ()
            if keyword:
                sql += " WHERE TenNhacSi LIKE ?"
                params = (f"%{keyword}%",)
            cur.execute(sql, params)
            for r in cur.fetchall():
                ngay = str(r[2]) if r[2] else ""
                tree.insert("", tk.END, values=(r[0], r[1], ngay, r[3]))
            conn.close()
        except Exception as e: messagebox.showerror("Lỗi Load", str(e))

    def clear_input():
        entry_ma.config(state="normal")
        entry_ma.delete(0, tk.END); entry_ten.delete(0, tk.END); entry_qt.delete(0, tk.END)
        date_entry.set_date("1990-01-01")
        entry_search.delete(0, tk.END)
        load_data()

    def them_ns():
        ma = entry_ma.get().strip()
        ten = entry_ten.get().strip()
        qt = entry_qt.get().strip()
        ngay_sinh = date_entry.get_date()
        if ngay_sinh >= date.today():
            return messagebox.showwarning("Lỗi Ngày Tháng", "Ngày sinh phải nhỏ hơn ngày hiện tại!")
        if not ma or not ten or not qt: return messagebox.showwarning("Lỗi Dữ Liệu", "Vui lòng nhập đầy đủ Mã, Tên và Quốc tịch.")
        try:
            conn = connect_db()
            sql = "INSERT INTO NhacSi (MaNhacSi, TenNhacSi, NgaySinh, QuocTich) VALUES (?,?,?,?)"
            conn.cursor().execute(sql, (ma, ten, date_entry.get(), qt))
            conn.commit(); conn.close()
            load_data(); clear_input(); messagebox.showinfo("Thành công", "Đã thêm nhạc sĩ mới!")
        except Exception as e:
            if "PRIMARY KEY" in str(e) or "duplicate" in str(e): messagebox.showerror("Lỗi Trùng Mã", "Mã Nhạc Sĩ này đã tồn tại.")
            else: messagebox.showerror("Lỗi SQL", f"Lỗi không xác định:\n{e}")

    def sua_ns():
        try:
            sel = tree.selection()
            if not sel: return messagebox.showwarning("Chú ý", "Chọn dòng cần sửa!")
            v = tree.item(sel)["values"]
            entry_ma.delete(0, tk.END); entry_ma.insert(0, v[0])
            entry_ma.config(state="readonly")
            entry_ten.delete(0, tk.END); entry_ten.insert(0, v[1])
            try: date_entry.set_date(v[2])
            except: pass
            entry_qt.delete(0, tk.END); entry_qt.insert(0, v[3])
        except Exception as e: messagebox.showerror("Lỗi Sửa", str(e))

    def luu_ns():
        ma = entry_ma.get().strip()
        ten = entry_ten.get().strip()
        qt = entry_qt.get().strip()
        ngay_sinh = date_entry.get_date()
        if ngay_sinh >= date.today():
             return messagebox.showwarning("Lỗi Ngày Tháng", "Ngày sinh phải nhỏ hơn ngày hiện tại!")
        if not ma or not ten or not qt: return messagebox.showwarning("Lỗi Dữ Liệu", "Vui lòng nhập đầy đủ Mã, Tên và Quốc tịch để lưu.")
        try:
            conn = connect_db()
            sql = "UPDATE NhacSi SET TenNhacSi=?, NgaySinh=?, QuocTich=? WHERE MaNhacSi=?"
            conn.cursor().execute(sql, (ten, date_entry.get(), qt, ma))
            conn.commit(); conn.close()
            load_data(); clear_input(); messagebox.showinfo("Thành công", "Đã lưu cập nhật!")
        except Exception as e: messagebox.showerror("Lỗi Lưu", str(e))

    def xoa_ns():
        ma = entry_ma.get()
        if not ma: return messagebox.showwarning("Lỗi", "Hãy chọn Nhạc Sĩ (bấm Sửa) để xóa!")
        if messagebox.askyesno("Xác nhận", "Xóa nhạc sĩ này sẽ xóa cả Bài hát liên quan?"):
            try:
                conn = connect_db()
                conn.cursor().execute("DELETE FROM NhacSi WHERE MaNhacSi=?", (ma,))
                conn.commit(); conn.close()
                load_data(); clear_input(); messagebox.showinfo("Thành công", "Đã xóa!")
            except Exception as e:
                error_message = str(e).lower()
                if "foreign key" in error_message or "reference" in error_message:
                    messagebox.showerror("Lỗi Ràng Buộc (FK)", "Không thể xóa. Nhạc sĩ này đang được sử dụng trong bảng Bài Hát.")
                else: messagebox.showerror("Lỗi Xóa", str(e))

    # BUTTONS
    f_btn = tk.Frame(root, pady=15); f_btn.pack(side="bottom", fill="x")
    btn_style = { "font": ("Times New Roman", 10, "bold"), "width": 14, "height": 2, "bd": 3, "relief": "raised" }
    center_frame = tk.Frame(f_btn); center_frame.pack()

    btn_them = tk.Button(center_frame, text="THÊM", command=them_ns, bg="LimeGreen", fg="white", **btn_style)
    btn_luu = tk.Button(center_frame, text="LƯU", command=luu_ns, bg="SteelBlue", fg="white", **btn_style)
    btn_sua = tk.Button(center_frame, text="SỬA", command=sua_ns, bg="Gold", fg="black", **btn_style)
    btn_huy = tk.Button(center_frame, text="HỦY", command=clear_input, bg="DarkGray", fg="white", **btn_style)
    btn_xoa = tk.Button(center_frame, text="XÓA", command=xoa_ns, bg="Red", fg="white", **btn_style)
    btn_thoat = tk.Button(center_frame, text="THOÁT", command=on_close, bg="DarkSlateGray", fg="white", **btn_style)

    if role == 1:
        btn_them.grid(row=0, column=0, padx=10)
        btn_sua.grid(row=0, column=1, padx=10)
        btn_luu.grid(row=0, column=2, padx=10)
        btn_xoa.grid(row=0, column=3, padx=10)
        btn_huy.grid(row=0, column=4, padx=10)
        btn_thoat.grid(row=0, column=5, padx=10)
    else:
        tk.Label(center_frame, text="(User chỉ được xem)", font=("Times New Roman", 10, "italic"), fg="gray").grid(row=0, column=0, padx=10)
        btn_thoat.grid(row=0, column=1, padx=10)
        for child in frame_info.winfo_children(): child.configure(state='disabled')

    tree.bind("<<TreeviewSelect>>", lambda e: None)
    load_data()

# =========================================================================
# PHẦN 4: FORM QUẢN LÝ ALBUM 
# =========================================================================

def open_frmAlbum(current_user_id, role, root_menu):
    root = tk.Toplevel()
    role_text = "ADMIN" if role == 1 else "USER"
    root.title(f"Quản Lý Album - {role_text}")
    
    w, h = 1100, 750
    ws = root.winfo_screenwidth(); hs = root.winfo_screenheight()
    x = (ws//2) - (w//2); y = (hs//2) - (h//2)
    root.geometry(f"{w}x{h}+{x}+{y}")
    
    def on_close():
        root.destroy()
        root_menu.deiconify()
    root.protocol("WM_DELETE_WINDOW", on_close)

    # --- LOAD DỮ LIỆU CA SĨ 
    try:
        casi_map = get_map_data("CaSi", "MaCaSi", "TenCaSi")
    except:
        casi_map = {}

    tk.Label(root, text="QUẢN LÝ ALBUM", font=("Times New Roman", 22, "bold"), fg="RoyalBlue").pack(pady=15)
    
    frame_info = tk.LabelFrame(root, text="Thông tin Album", padx=20, pady=20, font=("Times New Roman", 11, "bold"))
    frame_info.pack(padx=20, fill="x")
    frame_info.grid_columnconfigure(1, weight=1)
    frame_info.grid_columnconfigure(3, weight=1)

    font_style = ("Times New Roman", 10)
    lbl_grid = {"sticky": "w", "pady": 10}
    ent_grid = {"sticky": "ew", "padx": (5, 30)}

    # Hàng 1
    tk.Label(frame_info, text="Mã Album:", font=font_style).grid(row=0, column=0, **lbl_grid)
    entry_ma = tk.Entry(frame_info, font=font_style); entry_ma.grid(row=0, column=1, **ent_grid)
    
    tk.Label(frame_info, text="Tên Album:", font=font_style).grid(row=0, column=2, **lbl_grid)
    entry_ten = tk.Entry(frame_info, font=font_style); entry_ten.grid(row=0, column=3, **ent_grid)

    # Hàng 2
    tk.Label(frame_info, text="Năm Phát Hành:", font=font_style).grid(row=1, column=0, **lbl_grid)
    entry_nam = tk.Entry(frame_info, font=font_style); entry_nam.grid(row=1, column=1, **ent_grid)

    tk.Label(frame_info, text="Ca Sĩ Phát Hành:", font=font_style).grid(row=1, column=2, **lbl_grid)
    cbb_cs = ttk.Combobox(frame_info, values=list(casi_map.keys()), state="readonly", font=font_style)
    cbb_cs.grid(row=1, column=3, **ent_grid)

    # KHUNG TÌM KIẾM
    frame_search = tk.Frame(root, pady=5); frame_search.pack(padx=20, fill="x")
    tk.Label(frame_search, text="Tìm kiếm Album:", font=("Times New Roman", 10, "bold")).pack(side="left")
    entry_search = tk.Entry(frame_search, width=40, font=("Times New Roman", 10)); entry_search.pack(side="left", padx=10)
    
    def search_data(): load_data(entry_search.get()) 
    def reset_search(): entry_search.delete(0, tk.END); load_data() 

    tk.Button(frame_search, text="Tìm", command=search_data, bg="Teal", fg="white", font=("Times New Roman", 9, "bold"), width=8).pack(side="left")
    tk.Button(frame_search, text="Reset", command=reset_search, bg="DarkGray", fg="white", font=("Times New Roman", 9, "bold"), width=8).pack(side="left", padx=5)

    # TREEVIEW
    frame_list = tk.Frame(root); frame_list.pack(padx=20, pady=5, fill="both", expand=True)
    cols = ("ma", "ten", "nam", "casi")
    tree = ttk.Treeview(frame_list, columns=cols, show="headings")
    scroll = ttk.Scrollbar(frame_list, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scroll.set)
    tree.pack(side="left", fill="both", expand=True); scroll.pack(side="right", fill="y")
    
    tree.heading("ma", text="Mã Album"); tree.column("ma", width=100, anchor="center")
    tree.heading("ten", text="Tên Album"); tree.column("ten", width=350, anchor="center")
    tree.heading("nam", text="Năm PH"); tree.column("nam", width=100, anchor="center")
    tree.heading("casi", text="Ca Sĩ"); tree.column("casi", width=200, anchor="center")

    # LOGIC
    def load_data(keyword=None):
        try:
            for i in tree.get_children(): tree.delete(i)
            conn = connect_db()
            if not conn: return
            cur = conn.cursor()
            sql = """SELECT a.MaAlbum, a.TenAlbum, a.NamPhatHanh, c.TenCaSi 
                     FROM Album a LEFT JOIN CaSi c ON a.MaCaSi = c.MaCaSi"""
            params = ()
            if keyword:
                sql += " WHERE a.TenAlbum LIKE ?"
                params = (f"%{keyword}%",)
            cur.execute(sql, params)
            for r in cur.fetchall():
                tree.insert("", tk.END, values=(r[0], r[1], r[2], r[3]))
            conn.close()
        except Exception as e: messagebox.showerror("Lỗi Load", str(e))

    def clear_input():
        entry_ma.config(state="normal")
        entry_ma.delete(0, tk.END); entry_ten.delete(0, tk.END)
        entry_nam.delete(0, tk.END); cbb_cs.set("")
        entry_search.delete(0, tk.END)
        load_data()

    def them_ab():
        ma = entry_ma.get().strip()
        ten = entry_ten.get().strip()
        nam = entry_nam.get().strip()
        val_cs = casi_map.get(cbb_cs.get())
        if not ma or not ten or not nam or not val_cs: return messagebox.showwarning("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
        if not nam.isdigit():
            return messagebox.showwarning("Lỗi", "Năm phát hành phải là số!")
        if nam > date.today().year:
            return messagebox.showwarning("Lỗi", f"Năm phát hành không hợp lệ")
        try:
            conn = connect_db()
            sql = "INSERT INTO Album (MaAlbum, TenAlbum, NamPhatHanh, MaCaSi) VALUES (?,?,?,?)"
            conn.cursor().execute(sql, (ma, ten, nam, val_cs))
            conn.commit(); conn.close()
            load_data(); clear_input(); messagebox.showinfo("Thành công", "Đã thêm Album!")
        except Exception as e: 
            if "PRIMARY KEY" in str(e) or "duplicate" in str(e): messagebox.showerror("Lỗi Trùng Mã", "Mã Album này đã tồn tại.")
            elif "foreign key" in str(e).lower(): messagebox.showerror("Lỗi Ràng Buộc", "Mã Ca Sĩ không hợp lệ.")
            else: messagebox.showerror("Lỗi SQL", f"Lỗi không xác định:\n{e}")

    def sua_ab():
        try:
            sel = tree.selection()
            if not sel: return messagebox.showwarning("Chú ý", "Chọn Album cần sửa!")
            v = tree.item(sel)["values"]
            entry_ma.delete(0, tk.END); entry_ma.insert(0, v[0])
            entry_ma.config(state="readonly")
            entry_ten.delete(0, tk.END); entry_ten.insert(0, v[1])
            entry_nam.delete(0, tk.END); entry_nam.insert(0, v[2])
            if v[3]: cbb_cs.set(v[3])
        except Exception as e: messagebox.showerror("Lỗi Sửa", str(e))

    def luu_ab():
        ma = entry_ma.get().strip()
        ten = entry_ten.get().strip()
        nam = entry_nam.get().strip()
        val_cs = casi_map.get(cbb_cs.get())
        if not ma or not ten or not nam or not val_cs: return messagebox.showwarning("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
        try:
            conn = connect_db()
            sql = "UPDATE Album SET TenAlbum=?, NamPhatHanh=?, MaCaSi=? WHERE MaAlbum=?"
            conn.cursor().execute(sql, (ten, nam, val_cs, ma))
            conn.commit(); conn.close()
            load_data(); clear_input(); messagebox.showinfo("Thành công", "Đã lưu cập nhật!")
        except Exception as e: messagebox.showerror("Lỗi Lưu", str(e))

    def xoa_ab():
        ma = entry_ma.get()
        if not ma: return messagebox.showwarning("Lỗi", "Hãy chọn Album (bấm Sửa) để xóa!")
        if messagebox.askyesno("Xác nhận", "Xóa Album này? Các bài hát trong Album cũng có thể bị ảnh hưởng."):
            try:
                conn = connect_db()
                conn.cursor().execute("DELETE FROM Album WHERE MaAlbum=?", (ma,))
                conn.commit(); conn.close()
                load_data(); clear_input(); messagebox.showinfo("Thành công", "Đã xóa!")
            except Exception as e:
                error_message = str(e).lower()
                if "foreign key" in error_message or "reference" in error_message:
                    messagebox.showerror("Lỗi Ràng Buộc (FK)", "Không thể xóa. Album này đang có Bài hát ràng buộc với nó.")
                else: messagebox.showerror("Lỗi Xóa", str(e))

    # BUTTONS
    f_btn = tk.Frame(root, pady=15); f_btn.pack(side="bottom", fill="x")
    btn_style = { "font": ("Times New Roman", 10, "bold"), "width": 14, "height": 2, "bd": 3, "relief": "raised" }
    center_frame = tk.Frame(f_btn); center_frame.pack()

    btn_them = tk.Button(center_frame, text="THÊM", command=them_ab, bg="LimeGreen", fg="white", **btn_style)
    btn_luu = tk.Button(center_frame, text="LƯU", command=luu_ab, bg="SteelBlue", fg="white", **btn_style)
    btn_sua = tk.Button(center_frame, text="SỬA", command=sua_ab, bg="Gold", fg="black", **btn_style)
    btn_huy = tk.Button(center_frame, text="HỦY", command=clear_input, bg="DarkGray", fg="white", **btn_style)
    btn_xoa = tk.Button(center_frame, text="XÓA", command=xoa_ab, bg="Red", fg="white", **btn_style)
    btn_thoat = tk.Button(center_frame, text="THOÁT", command=on_close, bg="DarkSlateGray", fg="white", **btn_style)

    if role == 1:
        btn_them.grid(row=0, column=0, padx=10)
        btn_sua.grid(row=0, column=1, padx=10)
        btn_luu.grid(row=0, column=2, padx=10)
        btn_xoa.grid(row=0, column=3, padx=10)
        btn_huy.grid(row=0, column=4, padx=10)
        btn_thoat.grid(row=0, column=5, padx=10)
    else:
        tk.Label(center_frame, text="(User chỉ được xem)", font=("Times New Roman", 10, "italic"), fg="gray").grid(row=0, column=0, padx=10)
        btn_thoat.grid(row=0, column=1, padx=10)
        for child in frame_info.winfo_children(): child.configure(state='disabled')

    tree.bind("<<TreeviewSelect>>", lambda e: None)
    load_data()

# =========================================================================
# PHẦN 5: FORM QUẢN LÝ BÀI HÁT 
# =========================================================================

def open_frmBaiHat(current_user_id, role, root_menu):
    root = tk.Toplevel()
    role_text = "ADMIN" if role == 1 else "USER"
    root.title(f"Quản Lý Bài Hát - {role_text}")
    
    w, h = 1100, 750
    ws = root.winfo_screenwidth(); hs = root.winfo_screenheight()
    x = (ws//2) - (w//2); y = (hs//2) - (h//2)
    root.geometry(f"{w}x{h}+{x}+{y}")
    
    def on_close():
        root.destroy()
        root_menu.deiconify()
    root.protocol("WM_DELETE_WINDOW", on_close)

    try:
        tl_map = get_map_data("TheLoai", "MaTheLoai", "TenTheLoai")
        album_map = get_map_data("Album", "MaAlbum", "TenAlbum")
        casi_map = get_map_data("CaSi", "MaCaSi", "TenCaSi")
        nhacsi_map = get_map_data("NhacSi", "MaNhacSi", "TenNhacSi")
    except: return

    tk.Label(root, text="QUẢN LÝ BÀI HÁT", font=("Times New Roman", 22, "bold"), fg="RoyalBlue").pack(pady=10)
    
    frame_info = tk.LabelFrame(root, text="Thông tin chi tiết", padx=20, pady=15, font=("Times New Roman", 11, "bold"))
    frame_info.pack(padx=20, fill="x")
    frame_info.grid_columnconfigure(1, weight=1); frame_info.grid_columnconfigure(3, weight=1); frame_info.grid_columnconfigure(5, weight=1)

    font_style = ("Times New Roman", 10)
    lbl_grid = {"sticky": "w", "pady": 8}; ent_grid = {"sticky": "ew", "padx": (5, 20)}

    # Hàng 1
    tk.Label(frame_info, text="Mã Bài:", font=font_style).grid(row=0, column=0, **lbl_grid)
    entry_ma = tk.Entry(frame_info, font=font_style); entry_ma.grid(row=0, column=1, **ent_grid)
    
    tk.Label(frame_info, text="Tên Bài Hát:", font=font_style).grid(row=0, column=2, **lbl_grid)
    entry_ten = tk.Entry(frame_info, font=font_style); entry_ten.grid(row=0, column=3, **ent_grid)
    
    tk.Label(frame_info, text="Ngày PH:", font=font_style).grid(row=0, column=4, **lbl_grid)
    date_entry = DateEntry(frame_info, date_pattern='yyyy-mm-dd', background='darkblue', font=font_style); date_entry.grid(row=0, column=5, **ent_grid)

    # Hàng 2
    tk.Label(frame_info, text="Ca Sĩ:", font=font_style).grid(row=1, column=0, **lbl_grid)
    cbb_cs = ttk.Combobox(frame_info, values=list(casi_map.keys()), state="readonly", font=font_style); cbb_cs.grid(row=1, column=1, **ent_grid)

    tk.Label(frame_info, text="Nhạc Sĩ:", font=font_style).grid(row=1, column=2, **lbl_grid)
    cbb_ns = ttk.Combobox(frame_info, values=list(nhacsi_map.keys()), state="readonly", font=font_style); cbb_ns.grid(row=1, column=3, **ent_grid)
    
    tk.Label(frame_info, text="Thể Loại:", font=font_style).grid(row=1, column=4, **lbl_grid)
    cbb_tl = ttk.Combobox(frame_info, values=list(tl_map.keys()), state="readonly", font=font_style); cbb_tl.grid(row=1, column=5, **ent_grid)

    # Hàng 3
    tk.Label(frame_info, text="Album:", font=font_style).grid(row=2, column=0, **lbl_grid)
    cbb_ab = ttk.Combobox(frame_info, values=list(album_map.keys()), state="readonly", font=font_style); cbb_ab.grid(row=2, column=1, **ent_grid)
    
    tk.Label(frame_info, text="Thời Lượng:", font=font_style).grid(row=2, column=2, **lbl_grid)
    entry_time = tk.Entry(frame_info, font=font_style); entry_time.grid(row=2, column=3, **ent_grid); entry_time.insert(0, "00:00:00")
    
    tk.Label(frame_info, text="Lượt Nghe:", font=font_style).grid(row=2, column=4, **lbl_grid)
    entry_luot = tk.Entry(frame_info, font=font_style); entry_luot.grid(row=2, column=5, **ent_grid); entry_luot.insert(0, "0")

    # SEARCH
    frame_search = tk.Frame(root, pady=5); frame_search.pack(padx=20, fill="x")
    tk.Label(frame_search, text="Tìm kiếm bài hát:", font=("Times New Roman", 10, "bold")).pack(side="left")
    entry_search = tk.Entry(frame_search, width=40, font=("Times New Roman", 10)); entry_search.pack(side="left", padx=10)
    
    def search_data(): load_data(entry_search.get())
    def reset_search(): entry_search.delete(0, tk.END); load_data()

    tk.Button(frame_search, text="Tìm", command=search_data, bg="Teal", fg="white", font=("Times New Roman", 9, "bold"), width=8).pack(side="left")
    tk.Button(frame_search, text="Reset", command=reset_search, bg="DarkGray", fg="white", font=("Times New Roman", 9, "bold"), width=8).pack(side="left", padx=5)

    frame_list = tk.Frame(root); frame_list.pack(padx=20, pady=5, fill="both", expand=True)
    cols = ("ma", "ten", "casi", "nhacsi", "theloai", "album", "ngay", "time", "luot")
    tree = ttk.Treeview(frame_list, columns=cols, show="headings")
    scroll = ttk.Scrollbar(frame_list, orient="vertical", command=tree.yview); tree.configure(yscroll=scroll.set)
    tree.pack(side="left", fill="both", expand=True); scroll.pack(side="right", fill="y")
    
    headers = ["Mã BH", "Tên Bài", "Ca Sĩ", "Nhạc Sĩ", "Thể Loại", "Album", "Ngày", "Time", "View"]
    widths = [60, 180, 120, 120, 90, 120, 90, 80, 70]
    for c, h, w in zip(cols, headers, widths):
        tree.heading(c, text=h); tree.column(c, width=w, anchor="center")

    # LOGIC
    def load_data(keyword=None):
        try:
            for i in tree.get_children(): tree.delete(i)
            conn = connect_db()
            if not conn: return
            cur = conn.cursor()
            sql = """SELECT b.MaBaiHat, b.TenBaiHat, c.TenCaSi, n.TenNhacSi, t.TenTheLoai, a.TenAlbum, b.NgayPhatHanh, b.ThoiLuong, b.LuotNghe
                     FROM BaiHat b LEFT JOIN CaSi c ON b.MaCaSi = c.MaCaSi
                     LEFT JOIN NhacSi n ON b.MaNhacSi = n.MaNhacSi
                     LEFT JOIN TheLoai t ON b.MaTheLoai = t.MaTheLoai
                     LEFT JOIN Album a ON b.MaAlbum = a.MaAlbum"""
            params = ()
            if keyword:
                sql += " WHERE b.TenBaiHat LIKE ?"; params = (f"%{keyword}%",)
            cur.execute(sql, params)
            for r in cur.fetchall():
                ngay = str(r[6]) if r[6] else ""; gio = str(r[7]).split('.')[0] if r[7] else ""
                tree.insert("", tk.END, values=(r[0], r[1], r[2], r[3], r[4], r[5], ngay, gio, r[8]))
            conn.close()
        except Exception as e: messagebox.showerror("Lỗi Load", str(e))

    def clear_input():
        try:
            entry_ma.config(state="normal"); entry_ma.delete(0, tk.END); entry_ten.delete(0, tk.END)
            cbb_cs.set(""); cbb_ns.set(""); cbb_tl.set(""); cbb_ab.set("")
            entry_time.delete(0, tk.END); entry_time.insert(0, "00:00:00")
            entry_luot.delete(0, tk.END); entry_luot.insert(0, "0")
            date_entry.set_date("2024-01-01")
            entry_search.delete(0, tk.END)
            load_data()
        except Exception as e: messagebox.showerror("Lỗi", str(e))

    def them_bh():
        ma = entry_ma.get().strip()
        ten = entry_ten.get().strip()
        ngay = date_entry.get_date()
        thoi_luong = entry_time.get().strip()
        luot_nghe = entry_luot.get().strip() 
        cbb_casi_val = cbb_cs.get().strip()
        cbb_nhacsi_val = cbb_ns.get().strip()
        cbb_theloai_val = cbb_tl.get().strip()
        cbb_album_val = cbb_ab.get().strip()
        if ngay > date.today():
            return messagebox.showwarning("Lỗi Ngày Tháng", "Ngày phát hành không được lớn hơn ngày hôm nay!")
        
        if not ma or not ten or not thoi_luong or not ngay or \
           not cbb_casi_val or not cbb_nhacsi_val or not cbb_theloai_val or not cbb_album_val:
            return messagebox.showwarning("Lỗi Dữ Liệu", "Vui lòng nhập đầy đủ thông tin.")
        try:
            datetime.strptime(thoi_luong, '%H:%M:%S')
        except ValueError:
            return messagebox.showwarning("Lỗi Định Dạng", "Thời lượng phải đúng định dạng HH:MM:SS\nVí dụ: 00:04:30")
        try:
            conn = connect_db()
            vals = (ma, ten, casi_map.get(cbb_casi_val), nhacsi_map.get(cbb_nhacsi_val),
                    tl_map.get(cbb_theloai_val), album_map.get(cbb_album_val), ngay, thoi_luong, luot_nghe)
            sql = "INSERT INTO BaiHat (MaBaiHat, TenBaiHat, MaCaSi, MaNhacSi, MaTheLoai, MaAlbum, NgayPhatHanh, ThoiLuong, LuotNghe) VALUES (?,?,?,?,?,?,?,?,?)"
            conn.cursor().execute(sql, vals)
            conn.commit(); conn.close()
            load_data(); clear_input(); messagebox.showinfo("Thành công", "Đã thêm bài hát mới!")
        except Exception as e: 
            if "PRIMARY KEY" in str(e) or "duplicate" in str(e): messagebox.showerror("Lỗi Trùng Mã", "Mã Bài Hát này đã tồn tại.")
            else: messagebox.showerror("Lỗi SQL", f"Lỗi không xác định:\n{e}")

    def sua_bh():
        try:
            sel = tree.selection()
            if not sel: return messagebox.showwarning("Chú ý", "Hãy chọn một bài hát để sửa!")
            v = tree.item(sel)["values"]
            entry_ma.delete(0, tk.END); entry_ma.insert(0, v[0])
            entry_ma.config(state="readonly")
            entry_ten.delete(0, tk.END); entry_ten.insert(0, v[1])
            if v[2]: cbb_cs.set(v[2])
            if v[3]: cbb_ns.set(v[3])
            if v[4]: cbb_tl.set(v[4])
            if v[5]: cbb_ab.set(v[5])
            try: date_entry.set_date(v[6])
            except: pass
            entry_time.delete(0, tk.END); entry_time.insert(0, v[7])
            entry_luot.delete(0, tk.END); entry_luot.insert(0, v[8])
        except Exception as e: messagebox.showerror("Lỗi Sửa", str(e))

    def luu_bh():
        ma = entry_ma.get().strip()
        ten = entry_ten.get().strip()
        ngay = date_entry.get_date()
        thoi_luong = entry_time.get().strip()
        luot_nghe = entry_luot.get().strip()
        cbb_casi_val = cbb_cs.get().strip()
        cbb_nhacsi_val = cbb_ns.get().strip()
        cbb_theloai_val = cbb_tl.get().strip()
        cbb_album_val = cbb_ab.get().strip()
        if ngay > date.today():
            return messagebox.showwarning("Lỗi Ngày Tháng", "Ngày phát hành không được lớn hơn ngày hôm nay!")
        if not ma or not ten or not thoi_luong or not luot_nghe or not ngay or \
           not cbb_casi_val or not cbb_nhacsi_val or not cbb_theloai_val or not cbb_album_val:
            return messagebox.showwarning("Lỗi Dữ Liệu", "Vui lòng nhập đầy đủ thông tin để lưu.")
        try:
            datetime.strptime(thoi_luong, '%H:%M:%S')
        except ValueError:
            return messagebox.showwarning("Lỗi Định Dạng", "Thời lượng phải đúng định dạng HH:MM:SS\nVí dụ: 00:04:30")
        try:
            conn = connect_db()
            val_cs = casi_map.get(cbb_casi_val)
            val_ns = nhacsi_map.get(cbb_nhacsi_val)
            val_tl = tl_map.get(cbb_theloai_val)
            val_ab = album_map.get(cbb_album_val)

            sql = "UPDATE BaiHat SET TenBaiHat=?, MaCaSi=?, MaNhacSi=?, MaTheLoai=?, MaAlbum=?, NgayPhatHanh=?, ThoiLuong=?, LuotNghe=? WHERE MaBaiHat=?"
            vals = (ten, val_cs, val_ns, val_tl, val_ab, ngay, thoi_luong, luot_nghe, ma)
            
            conn.cursor().execute(sql, vals)
            conn.commit(); conn.close()
            load_data(); clear_input(); messagebox.showinfo("Thành công", "Đã lưu cập nhật!")
        except Exception as e: 
            if "foreign key" in str(e).lower(): messagebox.showerror("Lỗi Ràng Buộc", "Mã Album/Ca Sĩ/Nhạc Sĩ không hợp lệ.")
            else: messagebox.showerror("Lỗi Lưu", str(e))

    def xoa_bh():
        ma = entry_ma.get()
        if not ma: return messagebox.showwarning("Lỗi", "Chọn bài hát cần xóa!")
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa?"):
            try:
                conn = connect_db()
                conn.cursor().execute("DELETE FROM BaiHat WHERE MaBaiHat=?", (ma,))
                conn.commit(); conn.close(); load_data(); clear_input(); messagebox.showinfo("Thành công", "Đã xóa!")
            except Exception as e: messagebox.showerror("Lỗi Xóa", str(e))

    def add_to_favorite():
        sel = tree.selection()
        if not sel: return messagebox.showwarning("Chú ý", "Hãy chọn một bài hát để thả tim!")
        ma_bai = tree.item(sel)['values'][0]
        try:
            conn = connect_db()
            sql = "INSERT INTO DanhSachYeuThich (UserID, MaBaiHat) VALUES (?, ?)"
            conn.cursor().execute(sql, (current_user_id, str(ma_bai)))
            conn.commit(); conn.close()
            messagebox.showinfo("Tuyệt vời", "Đã thêm vào danh sách yêu thích! ❤️")
        except Exception as e:
            if "PRIMARY KEY" in str(e) or "duplicate" in str(e): messagebox.showinfo("Thông báo", "Bạn đã thích bài này rồi!")
            else: messagebox.showerror("Lỗi", str(e))

    # BUTTONS
    f_btn = tk.Frame(root, pady=15); f_btn.pack(side="bottom", fill="x")
    btn_style = { "font": ("Times New Roman", 10, "bold"), "width": 14, "height": 2, "bd": 3, "relief": "raised" }
    center_frame = tk.Frame(f_btn); center_frame.pack()

    btn_them = tk.Button(center_frame, text="THÊM", command=them_bh, bg="LimeGreen", fg="white", **btn_style)
    btn_luu = tk.Button(center_frame, text="LƯU", command=luu_bh, bg="SteelBlue", fg="white", **btn_style)
    btn_sua = tk.Button(center_frame, text="SỬA", command=sua_bh, bg="Gold", fg="black", **btn_style)
    btn_huy = tk.Button(center_frame, text="HỦY", command=clear_input, bg="DarkGray", fg="white", **btn_style)
    btn_xoa = tk.Button(center_frame, text="XÓA", command=xoa_bh, bg="Red", fg="white", **btn_style)
    btn_thoat = tk.Button(center_frame, text="THOÁT", command=on_close, bg="DarkSlateGray", fg="white", **btn_style)
    btn_like = tk.Button(center_frame, text="YÊU THÍCH", width=14, height=2, bg="DeepPink", fg="white", font=("Times New Roman", 10, "bold"), relief="raised",
                         command=add_to_favorite)

    if role == 1: # ADMIN
        btn_them.grid(row=0, column=0, padx=10)
        btn_sua.grid(row=0, column=1, padx=10)
        btn_luu.grid(row=0, column=2, padx=10)
        btn_xoa.grid(row=0, column=3, padx=10)
        btn_huy.grid(row=0, column=4, padx=10)
        btn_thoat.grid(row=0, column=5, padx=10)
        btn_like.grid(row=1, column=0, columnspan=6, pady=(10, 0))
    else: # USER
        btn_like.grid(row=0, column=0, padx=20)
        btn_thoat.grid(row=0, column=1, padx=20)
        for child in frame_info.winfo_children():
            try: child.configure(state='disabled')
            except: pass

    tree.bind("<<TreeviewSelect>>", lambda e: None)
    load_data()

# =========================================================================
# PHẦN 6: FORM DANH SÁCH YÊU THÍCH
# =========================================================================

def open_frmYeuThich(current_user_id, role, root_menu):
    root = tk.Toplevel()
    root.title("Danh Sách Yêu Thích Của Tôi")
    
    w, h = 900, 600
    ws = root.winfo_screenwidth(); hs = root.winfo_screenheight()
    x = (ws//2) - (w//2); y = (hs//2) - (h//2)
    root.geometry(f"{w}x{h}+{x}+{y}")
    
    def on_close():
        root.destroy()
        root_menu.deiconify()
    root.protocol("WM_DELETE_WINDOW", on_close)

    tk.Label(root, text="BÀI HÁT YÊU THÍCH", font=("Times New Roman", 22, "bold"), fg="DeepPink").pack(pady=20)

    # DANH SÁCH
    frame_list = tk.Frame(root)
    frame_list.pack(padx=20, pady=10, fill="both", expand=True)
    cols = ("ma", "ten", "casi", "ngaythem")
    tree = ttk.Treeview(frame_list, columns=cols, show="headings")
    scroll = ttk.Scrollbar(frame_list, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scroll.set)
    tree.pack(side="left", fill="both", expand=True); scroll.pack(side="right", fill="y")
    
    tree.heading("ma", text="Mã BH"); tree.column("ma", width=100, anchor="center")
    tree.heading("ten", text="Tên Bài Hát"); tree.column("ten", width=300, anchor="center")
    tree.heading("casi", text="Ca Sĩ Trình Bày"); tree.column("casi", width=200, anchor="center")
    tree.heading("ngaythem", text="Ngày Thêm"); tree.column("ngaythem", width=150, anchor="center")

    # LOGIC
    def load_favorites():
        for i in tree.get_children(): tree.delete(i)
        conn = connect_db()
        if not conn: return
        try:
            cur = conn.cursor()
            sql = """
                SELECT b.MaBaiHat, b.TenBaiHat, c.TenCaSi, yt.NgayThem
                FROM DanhSachYeuThich yt
                JOIN BaiHat b ON yt.MaBaiHat = b.MaBaiHat
                LEFT JOIN CaSi c ON b.MaCaSi = c.MaCaSi
                WHERE yt.UserID = ?
                ORDER BY yt.NgayThem DESC
            """
            cur.execute(sql, (current_user_id,))
            for r in cur.fetchall():
                ngay = str(r[3]).split('.')[0] if r[3] else ""
                tree.insert("", tk.END, values=(r[0], r[1], r[2], ngay))
            conn.close()
        except Exception as e: messagebox.showerror("Lỗi", str(e))

    def remove_favorite():
        sel = tree.selection()
        if not sel: return messagebox.showwarning("Chú ý", "Chọn bài hát muốn bỏ tim!")
        item = tree.item(sel)
        ma_bai_hat = item['values'][0]
        ten_bai = item['values'][1]

        if messagebox.askyesno("Xác nhận", f"Bỏ thích bài '{ten_bai}'?"):
            conn = connect_db()
            try:
                sql = "DELETE FROM DanhSachYeuThich WHERE UserID=? AND MaBaiHat=?"
                conn.cursor().execute(sql, (current_user_id, str(ma_bai_hat)))
                conn.commit(); conn.close()
                load_favorites()
                messagebox.showinfo("Thành công", "Đã xóa khỏi danh sách yêu thích!")
            except Exception as e: messagebox.showerror("Lỗi", str(e))

    # BUTTONS
    f_btn = tk.Frame(root, pady=20); f_btn.pack(side="bottom", fill="x")
    center_frame = tk.Frame(f_btn); center_frame.pack()
    btn_style = {"font": ("Times New Roman", 10, "bold"), "width": 18, "height": 2, "bd": 3, "relief": "raised"}

    tk.Button(center_frame, text="BỎ THÍCH", command=remove_favorite, bg="Red", fg="white", **btn_style).grid(row=0, column=0, padx=20)
    tk.Button(center_frame, text="LÀM MỚI", command=load_favorites, bg="DarkGray", fg="white", **btn_style).grid(row=0, column=1, padx=20)
    tk.Button(center_frame, text="THOÁT", command=on_close, bg="DarkSlateGray", fg="white", **btn_style).grid(row=0, column=2, padx=20)

    load_favorites()

# =========================================================================
# PHẦN 7: FORM MENU CHÍNH 
# =========================================================================

def logout(root, login_callback):
    if messagebox.askyesno("Đăng xuất", "Bạn có muốn đăng xuất không?"):
        root.destroy()
        login_callback()

def open_frmMenu(user_id, role, login_callback):
    menu_win = tk.Tk()
    menu_win.title("HỆ THỐNG QUẢN LÝ ÂM NHẠC")
    
    w, h = 900, 550
    ws = menu_win.winfo_screenwidth(); hs = menu_win.winfo_screenheight()
    x = (ws//2) - (w//2); y = (hs//2) - (h//2)
    menu_win.geometry(f"{w}x{h}+{x}+{y}")

    role_text = "QUẢN TRỊ VIÊN" if role == 1 else "NGƯỜI DÙNG"
    tk.Label(menu_win, text=f"XIN CHÀO, {role_text}", font=("Times New Roman", 18, "bold"), fg="DarkGreen").pack(pady=25)
    
    frame_menu = tk.Frame(menu_win); frame_menu.pack(pady=10)
    btn_style = {"font": ("Times New Roman", 11, "bold"), "width": 22, "height": 2, "bd": 3, "relief": "raised"}

    def go_to_baihat(): menu_win.withdraw(); open_frmBaiHat(user_id, role, menu_win) 
    def go_to_album(): menu_win.withdraw(); open_frmAlbum(user_id, role, menu_win)
    def go_to_casi(): menu_win.withdraw(); open_frmCaSi(user_id, role, menu_win)
    def go_to_nhacsi(): menu_win.withdraw(); open_frmNhacSi(user_id, role, menu_win) 
    def go_to_yeuthich(): menu_win.withdraw(); open_frmYeuThich(user_id, role, menu_win)
    def exit():
        if messagebox.askyesno("Xác nhận","Bạn có muốn thoát chương trình không?"):
            menu_win.destroy()

    # HÀNG 0
    tk.Button(frame_menu, text="QUẢN LÝ BÀI HÁT", bg="DodgerBlue", fg="white", **btn_style, command=go_to_baihat).grid(row=0, column=0, columnspan=2, padx=20, pady=15)

    # HÀNG 1
    tk.Button(frame_menu, text="QUẢN LÝ CA SĨ", bg="MediumPurple", fg="white", **btn_style, command=go_to_casi).grid(row=1, column=0, padx=20, pady=15)
    tk.Button(frame_menu, text="QUẢN LÝ NHẠC SĨ", bg="OrangeRed", fg="white", **btn_style, command=go_to_nhacsi).grid(row=1, column=1, padx=20, pady=15)

    # HÀNG 2
    tk.Button(frame_menu, text="QUẢN LÝ ALBUM", bg="Gold", fg="black", **btn_style, command=go_to_album).grid(row=2, column=0, padx=20, pady=15)
    tk.Button(frame_menu, text="DANH SÁCH YÊU THÍCH", bg="DeepPink", fg="white", **btn_style, command=go_to_yeuthich).grid(row=2, column=1, padx=20, pady=30) 

    tk.Button(frame_menu, text="ĐĂNG XUẤT", bg="SaddleBrown", fg="white", **btn_style, command=lambda: logout(menu_win, login_callback)).grid(row=3, column=0, padx=20, pady=15)
    tk.Button(frame_menu, text="THOÁT", bg="red", fg="white", **btn_style, command=exit).grid(row=3, column=1, padx=20, pady=15)
    menu_win.mainloop()

# =========================================================================
# PHẦN 8: MÀN HÌNH ĐĂNG NHẬP & MAIN 
# =========================================================================

def show_login():
    login_win = tk.Tk()
    login_win.title("Đăng nhập hệ thống")
    
    w, h = 450, 350
    ws = login_win.winfo_screenwidth(); hs = login_win.winfo_screenheight()
    x = (ws//2) - (w//2); y = (hs//2) - (h//2)
    login_win.geometry(f"{w}x{h}+{x}+{y}")
    login_win.configure(bg="white")

    def handle_login(event=None):
        u = entry_user.get()
        p = entry_pass.get()
        conn = connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                sql = "SELECT UserID, Quyen FROM NguoiDung WHERE UserName=? AND MatKhau=?"
                cursor.execute(sql, (u, p))
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    user_id = row[0]
                    role = row[1]
                    login_win.destroy() 
                    open_frmMenu(user_id, role, show_login) 
                else:
                    messagebox.showerror("Thất bại", "Sai tên tài khoản hoặc mật khẩu!")
            except Exception as e:
                messagebox.showerror("Lỗi SQL", str(e))

    def handle_exit():
        if messagebox.askyesno("Xác nhận", "Bạn có muốn thoát chương trình không?"):
            login_win.destroy()

    # GIAO DIỆN
    tk.Label(login_win, text="ĐĂNG NHẬP HỆ THỐNG", font=("Times New Roman", 20, "bold"), bg="white", fg="RoyalBlue").pack(pady=(30, 20))
    
    f_content = tk.Frame(login_win, bg="white"); f_content.pack()
    lbl_font = ("Times New Roman", 11); entry_font = ("Times New Roman", 11)
    
    tk.Label(f_content, text="Tài khoản:", font=lbl_font, bg="white").grid(row=0, column=0, sticky="w", pady=10)
    entry_user = tk.Entry(f_content, font=entry_font, width=25, relief="solid", bd=1)
    entry_user.grid(row=0, column=1, ipady=3, padx=10)
    
    tk.Label(f_content, text="Mật khẩu:", font=lbl_font, bg="white").grid(row=1, column=0, sticky="w", pady=10)
    entry_pass = tk.Entry(f_content, show="*", font=entry_font, width=25, relief="solid", bd=1)
    entry_pass.grid(row=1, column=1, ipady=3, padx=10)
    
    f_btn = tk.Frame(login_win, bg="white"); f_btn.pack(pady=30)
    btn_style = { "font": ("Times New Roman", 11, "bold"), "width": 12, "height": 1, "cursor": "hand2", "relief": "raised", "bd": 2 }

    tk.Button(f_btn, text="ĐĂNG NHẬP", command=handle_login, bg="Green", fg="white", **btn_style).grid(row=0, column=0, padx=10)
    tk.Button(f_btn, text="THOÁT", command=handle_exit, bg="Red", fg="white", **btn_style).grid(row=0, column=1, padx=10)

    login_win.bind('<Return>', handle_login)
    login_win.mainloop()

if __name__ == "__main__":
    show_login()