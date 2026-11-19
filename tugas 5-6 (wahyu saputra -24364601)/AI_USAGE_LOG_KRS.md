# AI Usage Log - Modul KRS

| Area | Bantuan AI | Verifikasi manual |
|---|---|---|
| Struktur KRS | Draft tabel KRS, KRSDetail, MataKuliah, Prerequisite | Relasi dan unique constraint diperiksa ulang |
| Validator | Draft Chain of Responsibility | Menetapkan urutan duplicate, prasyarat, SKS, lalu bentrok |
| State machine | Draft status DRAFT, SUBMITTED, APPROVED, REVISION | Melarang langsung DRAFT ke APPROVED |
| API | Draft endpoint tambah/hapus/submit/approve | Menambah respons error yang jelas |
| Testing | Draft kasus KRS | Menjalankan unit dan property-based test |

AI hanya menjadi asisten. Aturan akademik, relasi data, dan hasil pengujian divalidasi secara manual.
