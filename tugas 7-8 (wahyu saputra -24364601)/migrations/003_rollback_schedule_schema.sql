-- SQLite tidak mendukung DROP COLUMN pada versi lama.
-- Untuk rollback sederhana, hapus tabel ruangan dan jalankan ulang migration KRS pada database bersih.
DROP TABLE IF EXISTS ruangan;
