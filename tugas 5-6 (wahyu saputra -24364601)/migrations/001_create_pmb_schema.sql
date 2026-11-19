-- Migration UP: skema awal Modul PMB
CREATE TABLE program_studi (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  kode VARCHAR(3) NOT NULL UNIQUE,
  nama VARCHAR(100) NOT NULL,
  fakultas VARCHAR(100) NOT NULL
);

CREATE TABLE calon_mahasiswa (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nama_lengkap VARCHAR(150) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  phone VARCHAR(16) NOT NULL,
  tanggal_lahir DATE NOT NULL,
  alamat VARCHAR(255) NOT NULL,
  program_studi_id INTEGER NOT NULL REFERENCES program_studi(id),
  jalur_masuk VARCHAR(20) NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'pending',
  nim VARCHAR(20) UNIQUE,
  created_at DATETIME NOT NULL,
  approved_at DATETIME
);

CREATE TABLE nim_counter (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tahun INTEGER NOT NULL,
  kode_prodi VARCHAR(3) NOT NULL,
  nomor_terakhir INTEGER NOT NULL DEFAULT 0,
  CONSTRAINT uq_nim_counter UNIQUE (tahun, kode_prodi)
);

