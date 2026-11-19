# AI Usage Log

| No. | Tujuan | Prompt ringkas | Hasil AI | Revisi manual |
|---|---|---|---|---|
| 1 | Class diagram | Rancang UML sistem akademik berbasis SOLID | Menghasilkan class inti | Menambah KRSDetail dan kardinalitas |
| 2 | Relasi class | Audit inheritance, composition, dan aggregation | Memberi relasi awal | Mengubah KRS-KRSDetail menjadi composition |
| 3 | Use case | Buat use case aktor mahasiswa, dosen, admin | Use case dasar tersedia | Menambah include validasi KRS |
| 4 | Sequence PMB | Rancang alur daftar hingga NIM | Alur normal tersedia | Menambah validasi dan error 400/409 |
| 5 | Sequence KRS | Validasi prasyarat, SKS, jadwal | Alur validasi tersedia | Menambah alternate flow penolakan |
| 6 | Audit SOLID | Temukan potensi god object pada desain | Rekomendasi pemisahan layanan | Menggunakan KRS Manager dan validator terpisah |

## Bukti iterasi

AI dipakai sebagai asisten rancangan, bukan sebagai hasil akhir. Semua hubungan, kardinalitas, aturan SKS maksimal 24, dan alur gagal validasi diperiksa serta disesuaikan kembali secara manual.

