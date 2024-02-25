import zipfile
from PIL import Image
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

from flask import Flask, render_template, request
from dokumenter import generate, delete_files
import os

app = Flask(__name__)

# Atur batas ukuran file (dalam byte)
MAX_FILE_SIZE = 10 * 1024 * 1024  # Contoh: 50 MB

@app.route('/', methods=['GET', 'POST'])
def index(msg=None):
    if request.method == 'POST':
        # Periksa apakah ada file yang diunggah
        if 'files' not in request.files:
            return 'No file part'
        elif 'title' not in request.form:
            return 'No title input'

        files = request.files.getlist('files')
        title = request.form['title']

        # Periksa apakah ada file yang dipilih
        if not files or all(file.filename == '' for file in files):
            return 'No selected file'
        
        folder = 'files/'
        output = "dokumentasi"


        # Proses setiap file yang diunggah
        for file in files:
            # # Periksa ukuran file, tolak jika lebih besar dari batas yang ditentukan
            file_path = folder + file.filename
            file.save(file_path)

            if os.path.getsize(file_path) > MAX_FILE_SIZE:
                os.remove(file_path)
                return render_template('index.html', msg=f"Ukuran file {file.filename} melebihi batas yang diizinkan")

            if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.zip')):
                files_to_delete = [folder + f for f in os.listdir(folder)]
                delete_files(files_to_delete)
                # os.remove(file_path)
                return render_template('index.html', msg=f"Format file {file.filename} tidak diizinkan")

        # verifikasi files
        if not verification_files(folder):
            return render_template('index.html', msg=f"Format file {file.filename} tidak diizinkan")
        
        pdf_output = generate(title, folder, output)

        response = send_file(path_or_file=pdf_output, as_attachment=True, download_name=pdf_output)
        
        # Gantilah 'file1.txt', 'file2.txt', dst. dengan nama file yang ingin Anda hapus
        files_to_delete = [f'{output}.aux', f'{output}.log', f'{output}.tex', f'{output}.pdf']
        # Tampilkan informasi tentang file yang diunggah
        files_to_delete += [folder + f for f in os.listdir(folder)]

        delete_files(files_to_delete)
        
        return response

    return render_template('index.html')

def unzip_file(zip_path, extract_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
        extracted_files = zip_ref.namelist()

    return extracted_files


def compress_image(file, output_path, target_size_kb=500, quality=85):
    try:
        img = Image.open(file)
        
        # Hitung faktor skala untuk mencapai ukuran file target
        current_size_kb = os.path.getsize(file) / 1024  # Ukuran file saat ini dalam KB
        scale_factor = (target_size_kb / current_size_kb) ** 0.5
        
        # Terapkan kompresi dengan faktor skala
        img = img.resize((int(img.width * scale_factor), int(img.height * scale_factor)), Image.LANCZOS)
        img.save(output_path, quality=quality)
        return True
    except Exception as e:
        print(f"Error compressing image: {e}")
        return False
    
def verification_files(folder):
    # Verifikasi file format yang diterima
    for file in os.listdir(folder):
        print(f"File -> {file}")
        file_path = folder + file

        if file.lower().endswith(('.zip')):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                extracted_files = zip_ref.namelist()
                for f in extracted_files:
                    if not f.lower().endswith(('.png', '.jpg', '.jpeg')):
                        os.remove(file_path)
                        return False
                    
                zip_ref.extractall(folder)
            # verification_files(folder)

        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            # Periksa ukuran file, misalnya, jika lebih besar dari 500 kb, kompres
            if os.path.getsize(file_path) > 500 * 1028:  # 500 kb
                print("=========MENGURANGI FILE==============")
                print(f"{file_path} : {os.path.getsize(file_path)}")
                compress_image(file_path, file_path, target_size_kb=500)
                print(f"{file_path} : {os.path.getsize(file_path)}")
    return True



    
if __name__ == '__main__':
    app.run(debug=True)


        