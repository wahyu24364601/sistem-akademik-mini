-- Migration UP: Modul Jadwal dan Ruangan
CREATE TABLE ruangan (id INTEGER PRIMARY KEY AUTOINCREMENT, kode_ruang VARCHAR(20) NOT NULL UNIQUE, kapasitas INTEGER NOT NULL);
ALTER TABLE jadwal_kuliah ADD COLUMN ruangan_id INTEGER REFERENCES ruangan(id);
ALTER TABLE jadwal_kuliah ADD COLUMN dosen_id VARCHAR(30);
ALTER TABLE jadwal_kuliah ADD COLUMN jumlah_mahasiswa INTEGER NOT NULL DEFAULT 0;
