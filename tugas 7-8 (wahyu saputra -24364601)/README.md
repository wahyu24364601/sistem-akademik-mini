# Sistem Akademik Mini - PMB, KRS, Jadwal & Ruangan (Minggu 3-8)

Proyek ini melanjutkan PMB dan KRS dengan modul Jadwal & Ruangan.

## Fitur

- Registrasi calon mahasiswa.
- Validasi email dan nomor telepon Indonesia.
- Pencegahan email ganda.
- Status pendaftaran: `pending`, `approved`, `rejected`.
- Persetujuan admin serta generator NIM yang idempotent.
- NIM format `YYYYPPP-NNNN`, contoh: `2026INF-0001`.
- Swagger API otomatis di `http://127.0.0.1:8000/docs`.
- Pengisian KRS dengan maksimum 24 SKS, prasyarat nilai minimal C, deteksi jadwal bentrok, dan state approval Dosen PA.
- CRUD jadwal, deteksi bentrok ruang/dosen/waktu, cek kapasitas, notifikasi Observer, serta saran jadwal alternatif.

## Menjalankan proyek

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python seed_data.py
uvicorn app.main:app --reload
```

Untuk Linux/macOS, aktivasi virtual environment memakai `source .venv/bin/activate`.

## Endpoint

| Method | Endpoint | Fungsi |
|---|---|---|
| POST | `/api/pmb/register` | Daftar calon mahasiswa |
| GET | `/api/pmb/status/{id}` | Lihat status pendaftaran |
| PUT | `/api/pmb/approve/{id}` | Approve pendaftaran dan buat NIM |
| GET | `/api/pmb/stats` | Statistik pendaftar |
| POST | `/api/krs/{nim}/{semester}/courses` | Tambah mata kuliah ke KRS |
| DELETE | `/api/krs/{nim}/{semester}/courses/{kode_mk}` | Hapus mata kuliah dari KRS |
| POST | `/api/krs/{nim}/{semester}/submit` | Validasi dan submit KRS |
| PUT | `/api/krs/{nim}/{semester}/approve/{dosen_pa_id}` | Approve KRS |
| POST | `/api/schedules` | Buat jadwal kuliah |
| PUT | `/api/schedules/{id}` | Ubah jadwal dan kirim notifikasi |
| DELETE | `/api/schedules/{id}` | Hapus jadwal |
| GET | `/api/schedules/conflicts` | Lihat semua bentrok jadwal |
| GET | `/api/schedules/{id}/alternatives` | Saran jadwal alternatif |

## Contoh data registrasi

```json
{
  "nama_lengkap": "Siti Aminah",
  "email": "siti@example.com",
  "phone": "081234567890",
  "tanggal_lahir": "2007-05-20",
  "alamat": "Jakarta Selatan",
  "program_studi_id": 1,
  "jalur_masuk": "Mandiri"
}
```

## Pengujian

```bash
pytest -v
```

## Aturan KRS

- Total SKS maksimal 24 per semester.
- Prasyarat mata kuliah wajib sudah lulus dengan nilai minimal C.
- Mata kuliah tidak boleh dipilih dua kali.
- Jadwal pada hari dan jam yang bertabrakan akan ditolak.
- Alur status: `DRAFT → SUBMITTED → APPROVED`; dosen dapat mengubah `SUBMITTED → REVISION`.

