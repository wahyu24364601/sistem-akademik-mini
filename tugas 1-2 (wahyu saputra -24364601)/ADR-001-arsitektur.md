# ADR-001: Pemisahan Modul dan Validasi KRS

**Status:** Disetujui  
**Konteks:** Sistem akademik memiliki proses PMB, KRS, jadwal, nilai, dan pembayaran yang saling berkaitan. Bila seluruh aturan dimasukkan ke satu class, desain akan sulit diuji dan berkembang menjadi god object.

## Keputusan

1. `User` dijadikan abstract base class, lalu diturunkan menjadi `Mahasiswa`, `Dosen`, `AdminAkademik`, dan `CalonMahasiswa`.
2. `KRS` memiliki `KRSDetail` dengan composition karena detail tidak bermakna tanpa KRS induknya.
3. Validasi KRS dipisahkan menjadi validator prasyarat, batas SKS, dan bentrok jadwal dengan pola Chain of Responsibility.
4. Modul jadwal dan ruang dibuat terpisah agar dapat dipakai kembali oleh KRS serta presensi.

## Konsekuensi

Desain menjadi lebih modular, mudah diuji, dan setiap aturan bisnis dapat diubah tanpa mengganggu seluruh sistem. Konsekuensinya jumlah class lebih banyak, tetapi tanggung jawab tiap class lebih jelas dan sesuai prinsip SOLID.

## Alternatif yang ditolak

Memusatkan seluruh aturan pada class `Mahasiswa` atau `KRSManager`. Alternatif ini ditolak karena membuat class terlalu besar, sulit diuji, dan berisiko melanggar Single Responsibility Principle.

