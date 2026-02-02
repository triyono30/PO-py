from flask import Flask, render_template, request, redirect, jsonify # type: ignore
from koneksi import koneksi
from datetime import date

app = Flask(__name__)

# ================= AUTO ID PO =================
def generate_id_po(id_supplier):
    db = koneksi()
    cur = db.cursor()
    tahun = date.today().strftime("%Y")
    bulan = date.today().strftime("%m")
    prefix = f"PO-{tahun}{bulan}-{id_supplier}-"

    cur.execute("""
        SELECT id_po FROM po
        WHERE id_po LIKE %s
        ORDER BY id_po DESC
        LIMIT 1
    """, (prefix + "%",))

    last = cur.fetchone()
    if last:
        no = int(last[0].split("-")[-1]) + 1
    else:
        no = 1

    cur.close()
    db.close()
    return f"{prefix}{no:04d}"

#===================================================================================

@app.route("/dashboard_detail/<jenis>")
def dashboard_detail(jenis):
    db = koneksi()
    cursor = db.cursor(dictionary=True)

    if jenis == "supplier":
        cursor.execute("SELECT id_supplier, nama_supplier,  alamat, telp, status FROM supplier")
        data = cursor.fetchall()
        return render_template("partials/supplier.html", data=data)
        

    elif jenis == "barang":
        cursor.execute("SELECT b.*, s.nama_supplier FROM barang b JOIN supplier s ON b.id_supplier = s.id_supplier ORDER BY b.nama_barang")
        data = cursor.fetchall()
        # Ambil data suppliers untuk dropdown
        cursor.execute("SELECT DISTINCT nama_supplier FROM supplier ORDER BY nama_supplier")
        suppliers = cursor.fetchall()
        return render_template("partials/barang.html", data=data, suppliers=suppliers)

    elif jenis == "po":
        cursor.execute("SELECT id_po, tanggal_order FROM purchase_order")
        data = cursor.fetchall()

    else:
        cursor.close()
        db.close()
        return "Data tidak ditemukan", 404

    cursor.close()
    db.close()
    return data  # atau render_template(...)


#=====================update status suplier=========================
@app.route("/supplier/toggle/<id_supplier>/<int:status>")
def toggle_supplier(id_supplier, status):
    db = koneksi()
    cur = db.cursor()

    cur.execute("""
        UPDATE supplier
        SET status = %s
        WHERE id_supplier = %s
    """, (status, id_supplier))

    db.commit()
    cur.close()
    db.close()

    return "", 204   # ⬅️ PENTING: TANPA RESPONSE BODY



@app.route("/supplier/status", methods=["POST"])
def supplier_status():
    id_supplier = request.form.get("id_supplier")
    status = request.form.get("status")

    if not id_supplier or status is None:
        return jsonify({"success": False, "message": "Data tidak lengkap"})

    db = koneksi()
    cur = db.cursor()

    cur.execute("""
        UPDATE supplier
        SET status = %s
        WHERE id_supplier = %s
    """, (status, id_supplier))

    db.commit()
    affected = cur.rowcount  # 🔥 INI KUNCI

    cur.close()
    db.close()

    if affected == 0:
        return jsonify({"success": False, "message": "Supplier tidak ditemukan"})

    return jsonify({"success": True, "status": int(status)})

#====================== DATA BARANG

@app.route("/dashboard_detail/barang")
def barang_list():
    db = koneksi()
    cur = db.cursor(dictionary=True)

    cur.execute("""
        SELECT b.*, s.nama_supplier
        FROM barang b
        JOIN supplier s ON b.id_supplier = s.id_supplier
        ORDER BY b.nama_barang
    """)

    data = cur.fetchall()
    
    # Ambil data suppliers untuk dropdown
    cur.execute("SELECT DISTINCT nama_supplier FROM supplier ORDER BY nama_supplier")
    suppliers = cur.fetchall()
    
    cur.close()
    db.close()

    return render_template("partials/barang.html", data=data, suppliers=suppliers)


# ================= DASHBOARD =================
@app.route("/")
def dashboard():
    db = koneksi()
    cur = db.cursor()
    cur.execute("SELECT COUNT(*) FROM supplier")
    total_supplier = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM barang")
    total_barang = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM po")
    total_po = cur.fetchone()[0]
    cur.execute("SELECT IFNULL(SUM(total),0) FROM po")
    total_transaksi = cur.fetchone()[0]
    cur.close()
    db.close()
    return render_template(
        "dashboard.html",
        total_supplier=total_supplier,
        total_barang=total_barang,
        total_po=total_po,
        total_transaksi=total_transaksi
    )

# ================= FORM PO =================
@app.route("/po")
def form_po():
    db = koneksi()
    cur = db.cursor()
    cur.execute("SELECT id_supplier, nama_supplier FROM supplier WHERE status = 1 ORDER BY nama_supplier")
    supplier = cur.fetchall()
    cur.close()
    db.close()
    tanggal_order = date.today().strftime("%Y-%m-%d")
    return render_template("form_po.html", supplier=supplier, tanggal_order=tanggal_order)

# ================= GET BARANG (AJAX) =================
@app.route("/get_barang/<id_supplier>")
def get_barang(id_supplier):
    db = koneksi()
    cur = db.cursor()
    cur.execute("""
        SELECT id_barang, nama_barang, harga, stok, spek
        FROM barang
        WHERE id_supplier = %s
    """, (id_supplier,))
    data = cur.fetchall()
    cur.close()
    db.close()

    return jsonify({
        "barang": [
            {
                "id": b[0],
                "nama": b[1],
                "harga": float(b[2]),
                "stok": b[3],
                "spek": b[4] or ""
            } for b in data
        ]
    })


# ================= GET PO TERBARU (AJAX) =================
@app.route("/get_po_terbaru")
def get_po_terbaru():
    db = koneksi()
    cur = db.cursor()
    cur.execute("""
        SELECT po.id_po, po.tanggal_order, supplier.nama_supplier, po.total
        FROM po
        JOIN supplier ON po.id_supplier = supplier.id_supplier
        ORDER BY po.tanggal_order DESC, po.id_po DESC
        LIMIT 10
    """)
    data = cur.fetchall()
    cur.close()
    db.close()
    result = [
        {"id_po": d[0], "tanggal_order": d[1].strftime("%Y-%m-%d"), "supplier": d[2], "total": float(d[3])}
        for d in data
    ]
    return jsonify(result)

# ================= SIMPAN PO =================
@app.route("/simpan_po", methods=["POST"])
def simpan_po():
    data = request.form
    db = koneksi()
    cur = db.cursor()

    id_supplier   = data["id_supplier"]
    tanggal_order = data.get("tanggal_order", date.today().strftime("%Y-%m-%d"))
    tanggal_kirim = data.get("tanggal_kirim")
    nama_pemesan  = data.get("nama_pemesan", "")
    alamat_kirim  = data.get("alamat_kirim", "")

    barang_ids = request.form.getlist("id_barang_list")
    qty_list   = request.form.getlist("qty_list")

    if not barang_ids:
        # ambil supplier untuk render kembali
        cur.execute("SELECT id_supplier, nama_supplier FROM supplier")
        supplier = cur.fetchall()
        cur.close()
        db.close()
        return render_template("form_po.html",
            supplier=supplier,
            tanggal_order=tanggal_order,
            form_data={
                "id_supplier": id_supplier,
                "tanggal_kirim": tanggal_kirim,
                "nama_pemesan": nama_pemesan,
                "alamat_kirim": alamat_kirim,
                "barang_ids": barang_ids,
                "qty_list": qty_list
            },
            error="Harap tambahkan minimal 1 barang!"
        )

    # AUTO ID PO
    id_po = generate_id_po(id_supplier)

    # Hitung total
    total = 0
    for i in range(len(barang_ids)):
        cur.execute("SELECT harga FROM barang WHERE id_barang=%s", (barang_ids[i],))
        harga = float(cur.fetchone()[0])
        subtotal = harga * int(qty_list[i])
        total += subtotal

    # Insert header
    cur.execute("""
        INSERT INTO po (id_po, tanggal_order, tanggal_kirim, id_supplier, nama_pemesan, alamat_kirim, total)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (id_po, tanggal_order, tanggal_kirim, id_supplier, nama_pemesan, alamat_kirim, total))

    # Insert detail dan update stok
    for i in range(len(barang_ids)):
        barang_id = barang_ids[i]
        q = int(qty_list[i])
        cur.execute("SELECT harga FROM barang WHERE id_barang=%s", (barang_id,))
        harga = float(cur.fetchone()[0])
        subtotal = harga * q
        cur.execute("""
            INSERT INTO po_detail (id_po, id_barang, qty, harga, subtotal)
            VALUES (%s,%s,%s,%s,%s)
        """, (id_po, barang_id, q, harga, subtotal))
        cur.execute("UPDATE barang SET stok = stok + %s WHERE id_barang=%s", (q, barang_id))

    db.commit()
    cur.close()
    db.close()
    return redirect("/po?success=1")
@app.route("/simpan_po_ajax", methods=["POST"])
def simpan_po_ajax():
    data = request.form
    db = koneksi()
    cur = db.cursor()

    id_supplier   = data.get("id_supplier")
    tanggal_order = date.today().strftime("%Y-%m-%d")
    tanggal_kirim = data.get("tanggal_kirim")
    nama_pemesan  = data.get("nama_pemesan")
    alamat_kirim  = data.get("alamat_kirim")

    barang_ids = request.form.getlist("id_barang_list")
    qty_list   = request.form.getlist("qty_list")

    if not barang_ids:
        cur.close()
        db.close()
        return jsonify({"status":"error","message":"Harap tambahkan minimal 1 barang!"})

    # AUTO ID PO
    id_po = generate_id_po(id_supplier)

    # Hitung total
    total = 0
    for i in range(len(barang_ids)):
        cur.execute("SELECT harga FROM barang WHERE id_barang=%s", (barang_ids[i],))
        harga = float(cur.fetchone()[0])
        subtotal = harga * int(qty_list[i])
        total += subtotal

    # Insert header
    cur.execute("""
        INSERT INTO po (id_po, tanggal_order, tanggal_kirim, id_supplier, nama_pemesan, alamat_kirim, total)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (id_po, tanggal_order, tanggal_kirim, id_supplier, nama_pemesan, alamat_kirim, total))

    # Insert detail dan update stok
    for i in range(len(barang_ids)):
        barang_id = barang_ids[i]
        q = int(qty_list[i])
        cur.execute("SELECT harga FROM barang WHERE id_barang=%s", (barang_id,))
        harga = float(cur.fetchone()[0])
        subtotal = harga * q
        cur.execute("""
            INSERT INTO po_detail (id_po, id_barang, qty, harga, subtotal)
            VALUES (%s,%s,%s,%s,%s)
        """, (id_po, barang_id, q, harga, subtotal))
        cur.execute("UPDATE barang SET stok = stok + %s WHERE id_barang=%s", (q, barang_id))

    db.commit()
    cur.close()
    db.close()

    return jsonify({"status":"success","message":"PO berhasil disimpan..!"})

if __name__ == "__main__":
    app.run(debug=True)
