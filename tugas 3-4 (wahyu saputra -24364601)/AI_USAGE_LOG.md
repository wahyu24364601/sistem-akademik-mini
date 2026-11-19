# AI Usage Log - Modul PMB

| Area | Bantuan AI | Verifikasi dan revisi manual |
|---|---|---|
| Skema database | Draft tabel calon_mahasiswa, program_studi, dan NIM counter | Memastikan email/NIM unik serta foreign key program studi |
| Validasi | Draft validasi email dan nomor telepon | Nomor dinormalisasi ke format 08xxxxxxxxxx dan diuji data tidak valid |
| NIM generator | Draft format NIM dan counter per tahun/prodi | Menetapkan format `YYYYPPP-NNNN`, idempotent, serta unique constraint |
| REST API | Draft endpoint register, status, approve, dan stats | Menambahkan HTTP 201, 404, 409 serta dokumentasi Swagger |
| Testing | Draft test API | Menjalankan pytest untuk registrasi, duplikasi email, nomor invalid, dan approve idempotent |

AI digunakan sebagai asisten. Logika bisnis, format NIM, respons error, dan hasil pengujian ditinjau kembali secara manual.

