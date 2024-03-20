import os
import time
import py7zr
import rarfile
from zipfile import ZipFile
import gzip

def compress_to_7z(file_path):
    start_time = time.time()
    with py7zr.SevenZipFile('compressed.7z', 'w') as archive:
        archive.write(file_path)
    return time.time() - start_time
import patoolib

def compress_to_rar(file_path):
    start_time = time.time()
    patoolib.create_archive('compressed.rar', [file_path])
    return time.time() - start_time

def compress_to_zip(file_path):
    start_time = time.time()
    with ZipFile('compressed.zip', 'w') as archive:
        archive.write(file_path, os.path.basename(file_path))
    return time.time() - start_time

def compress_to_gz(file_path):
    start_time = time.time()
    with open(file_path, 'rb') as f_in, gzip.open('compressed.txt.gz', 'wb') as f_out:
        f_out.writelines(f_in)
    return time.time() - start_time

def main():
    file_path = 'temp.txt'
    # Create a sample text file (replace this with your own file)
    # with open(file_path, 'w') as f:
    #     f.write('This is a sample text file for compression benchmarking.')

    compression_methods = {
        # '7z': compress_to_7z,
        'rar': compress_to_rar,
        'zip': compress_to_zip,
        'gz': compress_to_gz
    }

    # Benchmark each compression method
    for method, compress_func in compression_methods.items():
        print(f"Compressing to {method}...")
        time_taken = compress_func(file_path)
        print(f"Time taken: {time_taken:.2f} seconds")
        print()

    # Clean up the sample text file
    os.remove(file_path)

if __name__ == "__main__":
    main()
