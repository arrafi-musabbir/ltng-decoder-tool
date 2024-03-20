import streamlit as st
import os
import shutil
import subprocess
from datetime import datetime
import pytz
import gzip

def current_time_gmt_plus_6():
    # Get current UTC time
    utc_now = datetime.utcnow()

    # Define GMT+6 timezone
    gmt_plus_6 = pytz.timezone('Asia/Dhaka')

    # Convert UTC time to GMT+6 time
    gmt_plus_6_now = utc_now.replace(tzinfo=pytz.utc).astimezone(gmt_plus_6)

    return gmt_plus_6_now.strftime("%Y-%m-%d %H:%M:%S %Z%z")

os.makedirs('output', exist_ok=True)
os.makedirs('temp', exist_ok=True)

def clean_directory(directory_path):
    if os.path.exists(directory_path):
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

def compress_to_gz(file_path):
    with open(file_path, 'rb') as f_in, gzip.open('output/compressed-output.gz', 'wb') as f_out:
        f_out.writelines(f_in)

def LTNG_Processing (CTR_Path, Linux_LTNG_Path):
    OUT_PATH = 'output/output.txt'
    command = Linux_LTNG_Path + '/./ltng-decoder -f ' + CTR_Path + ' > ' + f'{OUT_PATH}'
    print("\n")
    print("Current time in GMT+6:", current_time_gmt_plus_6())
    print("running: \n", command)
    # print(CTR_Path)
    process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # Handle output and error
    # output = process.stdout.strip()
    # error = process.stderr.strip()

    # if process.returncode != 0:
    #     print("Error:", error)
    #     return error
    # else:
    #     print("Output:", output)
    #     return True

def saveUpload(fpath, tfile):
    clean_directory('output')
    clean_directory('temp')
    with open(fpath,"wb") as f:
        f.write(tfile.getbuffer())
    return True

clean_directory('output')
clean_directory('temp')

st.title("LTNG decoder tool ♾")

def read_first_n_lines(file_path, n=100):
    lines = []
    with open(file_path, 'r') as file:
        for _ in range(n):
            line = file.readline().strip()
            if not line:
                break
            lines.append(line)
    return lines


# File uploader
uploaded_file = st.file_uploader("Upload File Compressed file in .gz format", type='.gz')

col1, col2 = st.columns(2)

with col1:
    if uploaded_file is not None:
        fpath1 = os.path.join("temp", 'temp.gz')
        fpath = os.path.join(os.getcwd(), fpath1)
        saveUpload(fpath, uploaded_file)
        st.success("File uploaded successfully!")
        
        # Display file details
        file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, 
                        "Uploaded FileSize(MB)": round((float(uploaded_file.size)/(1024*1024)), 2), "UploadPath": fpath1}
        st.write(file_details)
        with st.spinner('LTNG-Decoding in progress.....'):
            LTNG_Processing (fpath, "ltng-284.7.45/ltng/bin")
        # st.success("Done!")
        # if os.path.exists("output/output.txt"):
        #     compress_to_gz("output/output.txt")
        # Read first 100 lines


with col2:
    if uploaded_file is not None:
        # File path
        file_path = "output/output.txt"  # Update with the actual file path

        if os.path.exists(file_path):
            st.balloons()
            # compress_to_gz("output/output.txt")
            st.success("LTNG decoding successful!")

            # Get file size in megabytes
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

            # File details
            file_details = {
                "File Name": os.path.basename(file_path),
                "FileType": ".txt file", 
                "Decoded File Size (MB)": round(file_size_mb, 2),
                "File Path": file_path
            }

            # Display file details in a container
            with st.container():
                st.write(file_details)

            obj_file_bytes = open('output/output.txt', 'rb').read()
            st.download_button(
                label="Download Decoded Text",
                data=obj_file_bytes,
                file_name=os.path.basename('output/output.txt'),
                key="download_button_1",
                mime="text/plain",
            )   
        else:
            st.error("File not found! LTNG-decoding failed!!!")




