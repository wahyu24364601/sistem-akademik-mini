# Sistem Akademik Mini - Modul PMB (Minggu 3-4)

Modul ini mengimplementasikan Penerimaan Mahasiswa Baru (PMB) sesuai rancangan UML sebelumnya.

## Fitur

- Registrasi calon mahasiswa.
- Validasi email dan nomor telepon Indonesia.
- Pencegahan email ganda.
- Status pendaftaran: `pending`, `approved`, `rejected`.
- Persetujuan admin serta generator NIM yang idempotent.
- NIM format `YYYYPPP-NNNN`, contoh: `2026INF-0001`.
- Swagger API otomatis di `http://127.0.0.1:8000/docs`.

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

