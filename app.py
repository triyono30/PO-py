from flask import Flask, render_template, request, redirect, jsonify # type: ignore
from koneksi import koneksi
from datetime import date

app = Flask(__name__)


def update_status(id_po, from_status, to_status):
    db = koneksi()
    cur = db.cursor()
    cur.execute("""
        UPDATE po
        SET status_order=%s
        WHERE id_po=%s AND status_order=%s
    """, (to_status, id_po, from_status))
    ok = cur.rowcount
    db.commit()
    return ok
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
        cursor.execute("SELECT b.*, s.nama_suppliers.status AS status_supplier FROM barang b JOIN supplier s ON b.id_supplier = s.id_supplier ORDER BY b.nama_barang""")
        data = cursor.fetchall()
        # Ambil data suppliers untuk dropdown
        cursor.execute("SELECT DISTINCT nama_supplier FROM supplier ORDER BY nama_supplier")
        suppliers = cursor.fetchall()
        return render_template("partials/barang.html", data=data, suppliers=suppliers)

    elif jenis == "po":
        # Detail PO: pakai desain seperti supplier (partials/po_status.html)
        cursor.execute("""
            SELECT po.id_po,
                   po.tanggal_order,
                    po.tanggal_kirim,
                   supplier.nama_supplier AS supplier,
                   po.total,
                   po.status_order AS status_terakhir
            FROM po
                
            JOIN supplier ON po.id_supplier = supplier.id_supplier
            ORDER BY po.tanggal_order DESC, po.id_po DESC
        """)
        data = cursor.fetchall()

        
        today = date.today()

        for p in data:
            if p["status_terakhir"] == "SELESAI":
                p["sisa_hari"] = "Selesai"
                p["sisa_class"] = "sisa-selesai"

            elif p["tanggal_kirim"]:
                delta = (p["tanggal_kirim"] - today).days

                if delta > 0:
                    p["sisa_hari"] = f"{delta} hari lagi"
                    p["sisa_class"] = "sisa-aman"
                elif delta == 0:
                    p["sisa_hari"] = "Hari ini"
                    p["sisa_class"] = "sisa-warning"
                else:
                    p["sisa_hari"] = f"Terlambat {abs(delta)} hari"
                    p["sisa_class"] = "sisa-danger"
            else:
                p["sisa_hari"] = "-"


        # hitung ringkasan untuk ditampilkan di atas tabel
        total_po = len(data)
        total_nilai = sum([float(row["total"] or 0) for row in data]) if data else 0.0
        cursor.close()
        db.close()
        return render_template(
            "partials/po_status.html",
            data=data,
            total_po=total_po,
            total_nilai=total_nilai,
        )

    else:
        cursor.close()
        db.close()
        return "Data tidak ditemukan", 404

    cursor.close()
    db.close()
    return data  # fallback untuk jenis lain jika ditambah nanti


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
    SELECT 
        b.*,
        s.nama_supplier,
        s.status AS status_supplier
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
        SELECT id_barang, nama_barang, harga, stok, spek, satuan
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
                "spek": b[4] or "",
                "satuan": b[5]
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


# ================= FORM TOTAL PO + STATUS TERAKHIR =================
@app.route("/po_status")
def po_status():
    db = koneksi()
    cur = db.cursor(dictionary=True)

    # Ambil semua PO dengan status terakhir (menggunakan kolom status_order)
    cur.execute("""
        SELECT po.id_po,
            po.tanggal_order,
            po.tanggal_kirim,
            supplier.nama_supplier AS supplier,
            po.total,
            po.status_order AS status_terakhir
        FROM po
        JOIN supplier ON po.id_supplier = supplier.id_supplier
        ORDER BY po.tanggal_order DESC, po.id_po DESC
    """)

    data = cur.fetchall()
    today = date.today()

    for p in data:
        tgl_kirim = p.get("tanggal_kirim")
        if tgl_kirim:
            delta = (tgl_kirim - today).days
            if delta > 0:
                p["sisa_hari"] = f"{delta} hari lagi"
            elif delta == 0:
                p["sisa_hari"] = "Hari ini"
            else:
                p["sisa_hari"] = f"Terlambat {abs(delta)} hari"
        else:
            p["sisa_hari"] = "-"

    # Hitung ringkasan
    cur.execute("SELECT COUNT(*), IFNULL(SUM(total),0) FROM po")
    row = cur.fetchone()
    total_po = row[0]
    total_nilai = float(row[1] or 0)

    cur.close()
    db.close()

    return render_template(
        "partials/po_status.html",
        data=data,
        total_po=total_po,
        total_nilai=total_nilai,
    )

# ================= SIMPAN PO =================
@app.route("/simpan_po_ajax", methods=["POST"])
def simpan_po_ajax():
    data = request.form
    db = koneksi()
    cur = db.cursor()

    try:
        id_supplier        = data.get("id_supplier")
        tanggal_order      = date.today().strftime("%Y-%m-%d")
        tanggal_kirim      = data.get("tanggal_kirim")
        nama_pemesan       = data.get("nama_pemesan")
        alamat_kirim       = data.get("alamat_kirim")
        jenis_pembayaran   = data.get("jenis_pembayaran")

        barang_ids = request.form.getlist("id_barang_list")
        qty_list   = request.form.getlist("qty_list")
        note_list  = request.form.getlist("note_list")   # ✅ PENTING

        if not barang_ids:
            return jsonify({"status":"error","message":"Harap tambahkan minimal 1 barang!"})

        id_po = generate_id_po(id_supplier)

        total = 0
        harga_cache = []

        for i in range(len(barang_ids)):
            cur.execute("SELECT harga FROM barang WHERE id_barang=%s", (barang_ids[i],))
            harga = float(cur.fetchone()[0])
            harga_cache.append(harga)
            total += harga * int(qty_list[i])

        status_order = "DRAF"

        # ✅ INSERT PO (HEADER)
        cur.execute("""
            INSERT INTO po
            (id_po, tanggal_order, tanggal_kirim, id_supplier,
             nama_pemesan, alamat_kirim, jenis_pembayaran,
             total, status_order)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            id_po, tanggal_order, tanggal_kirim,
            id_supplier, nama_pemesan,
            alamat_kirim, jenis_pembayaran,
            total, status_order
        ))

        # ✅ INSERT DETAIL + KET
        for i in range(len(barang_ids)):
            barang_id = barang_ids[i]
            q = int(qty_list[i])
            harga = harga_cache[i]
            subtotal = harga * q
            ket = note_list[i] if i < len(note_list) else ""

            cur.execute("""
                INSERT INTO po_detail
                (id_po, id_barang, qty, harga, subtotal, ket)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (
                id_po, barang_id, q, harga, subtotal, ket
            ))

           # cur.execute("""
            #    UPDATE barang
             #   SET stok = stok - %s
              #  WHERE id_barang=%s AND stok >= %s
            #""", (q, barang_id, q))

            if cur.rowcount == 0:
                db.rollback()
                return jsonify({
                    "status":"error",
                    "message":f"Stok tidak cukup untuk barang {barang_id}"
                })

        db.commit()
        return jsonify({"status":"success","message":"PO berhasil disimpan!"})

    except Exception as e:
        db.rollback()
        return jsonify({"status":"error","message":str(e)})

    finally:
        cur.close()
        db.close()

@app.route("/po_detail_ajax/<id_po>")
def po_detail_ajax(id_po):
    db = koneksi()
    cur = db.cursor(dictionary=True)

    # HEADER PO
    cur.execute("""
        SELECT 
            p.id_po,
            p.tanggal_order,
            p.tanggal_kirim,
            p.nama_pemesan,
            p.alamat_kirim,
            p.jenis_pembayaran,
            p.status_order,
            p.total,
            s.nama_supplier
        FROM po p
        LEFT JOIN supplier s ON p.id_supplier = s.id_supplier
        WHERE p.id_po = %s
    """, (id_po,))
    po = cur.fetchone()

    if not po:
        return "<p>❌ PO tidak ditemukan</p>"

    # DETAIL BARANG
    cur.execute("""
        SELECT 
            b.nama_barang,
            d.qty,
            b.satuan,
            d.harga,
            d.subtotal,
            d.ket
        FROM po_detail d
        JOIN barang b ON d.id_barang = b.id_barang
        WHERE d.id_po = %s
    """, (id_po,))
    detail = cur.fetchall()

    return render_template(
        "po_detail.html",
        po=po,
        detail=detail
    )



@app.route("/po/order/<id_po>", methods=["POST"])
def order_po(id_po):
    db = koneksi()
    cur = db.cursor()

    # ambil detail
    cur.execute("""
        SELECT id_barang, qty FROM po_detail WHERE id_po=%s
    """, (id_po,))
    items = cur.fetchall()

    # kurangi stok
    for barang_id, qty in items:
        cur.execute("""
            UPDATE barang
            SET stok = stok - %s
            WHERE id_barang=%s AND stok >= %s
        """, (qty, barang_id, qty))
        if cur.rowcount == 0:
            db.rollback()
            return jsonify({
                "status":"error",
                "message":f"Stok tidak cukup untuk barang {barang_id}"
            })

    # update status
    cur.execute("""
        UPDATE po
        SET status_order='ORDER'
        WHERE id_po=%s AND status_order='APPROVED'
    """, (id_po,))

    db.commit()
    return jsonify({"status":"success","message":"PO di-order ke supplier"})

@app.route("/po/approve/<id_po>", methods=["POST"])
def approve_po(id_po):
    db = koneksi()
    cur = db.cursor()

    cur.execute("""
        UPDATE po
        SET status_order='APPROVED'
        WHERE id_po=%s AND status_order='AWAITING_APPROVAL'
    """, (id_po,))

    if cur.rowcount == 0:
        return jsonify({"status":"error","message":"PO tidak bisa di-approve"})

    db.commit()
    return jsonify({"status":"success","message":"PO disetujui"})

@app.route("/po/submit/<id_po>", methods=["POST"])
def submit_po(id_po):
    db = koneksi()
    cur = db.cursor()

    cur.execute("""
        UPDATE po
        SET status_order = 'AWAITING_APPROVAL'
        WHERE id_po=%s AND status_order='DRAF'
    """, (id_po,))

    if cur.rowcount == 0:
        return jsonify({"status":"error","message":"PO tidak bisa diajukan"})

    db.commit()
    return jsonify({"status":"success","message":"PO diajukan ke approval"})



if __name__ == "__main__":
    app.run(debug=True)
