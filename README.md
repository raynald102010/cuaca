# Cuaca — aplikasi prakiraan cuaca Android (Python)

Aplikasi Kivy sederhana dengan pencarian kota, cuaca saat ini, dan prakiraan 7 hari.
Data diambil dari layanan Open-Meteo; tidak membutuhkan API key.

## Isi proyek
- `main.py` — kode aplikasi.
- `buildozer.spec` — konfigurasi untuk membangun APK Android.
- `requirements.txt` — dependensi Python.

## Menjalankan di komputer untuk uji awal
Disarankan Python 3.10 atau 3.11.

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

## Membuat APK (disarankan Ubuntu Linux atau WSL2 Ubuntu)
Buildozer paling mudah dijalankan di Linux. Di Windows, gunakan WSL2 Ubuntu dan simpan
proyek di filesystem Linux (misalnya `~/aplikasi_cuaca`), bukan `/mnt/c`.

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv git zip unzip openjdk-17-jdk \
  build-essential autoconf libtool pkg-config zlib1g-dev libncurses5-dev \
  libncursesw5-dev libtinfo6 cmake libffi-dev libssl-dev
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install buildozer
buildozer android debug
```

Build pertama mengunduh Android SDK/NDK dan dapat memerlukan waktu serta ruang disk.
Jika berhasil, APK debug berada di folder `bin/`.
Salin APK ke HP Android, lalu instal. Android mungkin meminta izin instalasi dari
sumber tersebut. Untuk rilis publik, buat APK/AAB release dan tanda tangani dengan
keystore milik sendiri.

## Catatan
- Perangkat membutuhkan koneksi internet untuk mengambil prakiraan.
- Lokasi awal diatur ke Pematangsiantar; ubah kolom pencarian untuk kota lain.
- Aplikasi belum meminta izin GPS. Versi awal menggunakan pencarian nama kota agar
  sederhana dan tidak meminta akses lokasi.
- Prakiraan adalah estimasi model cuaca, bukan kepastian. Untuk keputusan keselamatan,
  ikuti peringatan resmi BMKG.
- Open-Meteo: https://open-meteo.com/ dan https://open-meteo.com/en/docs


## Alternatif build APK melalui GitHub Actions
Jika tidak memiliki Linux/WSL2, proyek ini sudah menyertakan workflow otomatis:
`.github/workflows/build-apk.yml`.

1. Buat repository baru di GitHub.
2. Unggah seluruh isi folder proyek ini ke repository (termasuk folder `.github`).
3. Buka tab **Actions** pada repository.
4. Pilih workflow **Build Android APK**, lalu tekan **Run workflow**.
5. Tunggu proses build selesai. Buka hasil run dan unduh artifact **Cuaca-Android-APK**.
6. Ekstrak ZIP artifact untuk mendapatkan file APK.

Build pertama dapat memerlukan waktu cukup lama karena Android SDK/NDK diunduh.
Workflow membuat APK debug untuk pengujian, bukan APK release untuk Play Store.
