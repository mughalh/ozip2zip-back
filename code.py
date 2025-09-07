#!/usr/bin/env python3
"""
OPPO ROM Converter - Single File Windows Application
Converts custom ROMs to OPPO's OZIP format with a user-friendly GUI

Refactored with:
- Better AES encryption/decryption handling
- Robust transfer list parsing
- Thread-safe UI updates
- Proper error handling and logging
- Secure temporary file management
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import zipfile
import binascii
import shutil
import threading
import subprocess
import queue
import tempfile
import struct
import logging
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# HiDPI scaling for Windows
if sys.platform == "win32":
    from ctypes import windll, byref, c_int
    windll.shcore.SetProcessDpiAwareness(1)

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='oppo_converter.log',
    filemode='w'
)
logger = logging.getLogger("OppoConverter")

# Known OPPO AES keys
KEYS = [
    "d6eecf0ae5acd4e0e9fe522de7ce381e",  # mnkey
    "d6eccf0ae5acd4e0e92e522de7c1381e",  # mkey
    "d6dccf0ad5acd4e0292e522db7c1381e",  # realkey
    "d7dcce1ad4afdce2393e5161cbdc4321",  # testkey
    "d7dbce2ad4addce1393e5521cbdc4321",  # utilkey
    "d7dbce1ad4afdce1393e5121cbdc4321",  # R11s
    "d4d2cd61d4afdce13b5e01221bd14d20",  # FindX
    "261cc7131d7c1481294e532db752381e",  # FindX
    "1ca21e12271335ae33ab81b2a7b14622",  # Realme 2 pro
    "d4d2ce11d4afdce13b3e0121cbdc4321",  # K1
    "1c4c1ea3a12531ae491b21bb31613c11",  # Realme 3 Pro
    "acaa1e12a71431ce4a1b21bba1c1c6a2", 
     "D6EECF0AE5ACD4E0E9FE522DE7CE381E",  # mnkey
        "D6ECCF0AE5ACD4E0E92E522DE7C1381E",  # mkey
        "D6DCCF0AD5ACD4E0292E522DB7C1381E",  # realkey, R9s CPH1607 MSM8953, Plus, R11, RMX1921 Realme XT, RMX1851EX Realme Android 10, RMX1992EX_11_OTA_1050
        "D7DCCE1AD4AFDCE2393E5161CBDC4321",  # testkey
        "D7DBCE2AD4ADDCE1393E5521CBDC4321",  # utilkey
        "D7DBCE1AD4AFDCE1393E5121CBDC4321",  # R11s CPH1719 MSM8976, Plus
        "D4D2CD61D4AFDCE13B5E01221BD14D20",  # FindX CPH1871 SDM845
        "261CC7131D7C1481294E532DB752381E",  # FindX
        "1CA21E12271335AE33AB81B2A7B14622",  # Realme 2 pro SDM660/MSM8976
        "D4D2CE11D4AFDCE13B3E0121CBD14D20",  # K1 SDM660/MSM8976
        "1C4C1EA3A12531AE491B21BB31613C11",  # Realme 3 Pro SDM710, X, 5 Pro, Q, RMX1921 Realme XT
        "1C4C1EA3A12531AE4A1B21BB31C13C21",  # Reno 10x zoom PCCM00 SDM855, CPH1921EX Reno 5G
        "1C4A11A3A12513AE441B23BB31513121",  # Reno 2 PCKM00 SDM730G
        "1C4A11A3A12589AE441A23BB31517733",  # Realme X2 SDM730G
        "1C4A11A3A22513AE541B53BB31513121",  # Realme 5 SDM665
        "2442CE821A4F352E33AE81B22BC1462E",  # R17 Pro SDM710
        "14C2CD6214CFDC2733AE81B22BC1462C",  # CPH1803 OppoA3s SDM450/MSM8953
        "1E38C1B72D522E29E0D4ACD50ACFDCD6",
        "12341EAAC4C123CE193556A1BBCC232D",
        "2143DCCB21513E39E1DCAFD41ACEDBD7",
        "2D23CCBBA1563519CE23C1C4AA1E3412",  # A77 CPH1715 MT6750T
        "172B3E14E46F3CE13E2B5121CBDC4321",  # Realme 1 MTK P60
        "ACAA1E12A71431CE4A1B21BBA1C1C6A2",  # Realme U1 RMX1831 MTK P70
        "ACAC1E13A72531AE4A1B22BB31C1CC22",  # Realme 3 RMX1825EX P70
        "1C4411A3A12533AE441B21BB31613C11",  # A1k CPH1923 MTK P22
        "1C4416A8A42717AE441523B336513121",  # Reno 3 PCRM00 MTK 1000L, CPH2059 OPPO A92, CPH2067 OPPO A72
        "55EEAA33112133AE441B23BB31513121",  # RenoAce SDM855Plus
        "ACAC1E13A12531AE4A1B21BB31C13C21",  # Reno, K3
        "ACAC1E13A72431AE4A1B22BBA1C1C6A2",  # A9
        "12CAC11211AAC3AEA2658690122C1E81",  # A1,A83t
        "1CA21E12271435AE331B81BBA7C14612",  # CPH1909 OppoA5s MT6765
        "D1DACF24351CE428A9CE32ED87323216",  # Realme1(reserved)
        "A1CC75115CAECB890E4A563CA1AC67C8",  # A73(reserved)
        "2132321EA2CA86621A11241ABA512722",  # Realme3(reserved)
        "22A21E821743E5EE33AE81B227B1462E" # Realme U1
]

class ThreadSafeQueue:
    """Thread-safe queue for UI updates"""
    def __init__(self):
        self.queue = queue.Queue()
        
    def put(self, message):
        self.queue.put(message)
        
    def get_all(self):
        messages = []
        while not self.queue.empty():
            try:
                messages.append(self.queue.get_nowait())
            except queue.Empty:
                break
        return messages

class OppoConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("OPPO Custom ROM Converter")
        self.root.geometry("800x650")
        self.root.resizable(True, True)
        
        # Variables to store paths
        self.ozip_path = tk.StringVar()
        self.system_img_path = tk.StringVar()
        self.output_path = tk.StringVar()
        
        # Conversion flags
        self.conversion_in_progress = False
        self.cancel_requested = False
        
        # Thread-safe message queue
        self.message_queue = ThreadSafeQueue()
        
        # Successful key storage
        self.successful_key = None
        
        # Setup the GUI
        self.setup_gui()
        
        # Start the message polling
        self.poll_messages()
        
    def setup_gui(self):
        # Header with instructions
        header_frame = ttk.Frame(self.root, padding="10")
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        instructions = (
            "Flash custom ROMs on Oppo devices using official system restore.\n"
            "After converting, transfer the converted ozip file to the phone, then shut down the phone.\n"
            "Press power and volume down to enter recovery mode and select firmware restore from device."
        )
        
        ttk.Label(header_frame, text=instructions, wraplength=700, justify=tk.LEFT).grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Main content frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))
        
        # OZIP file selection
        ttk.Label(main_frame, text="Original OZIP File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.ozip_path, width=70).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_ozip).grid(row=0, column=2, padx=5, pady=5)
        
        # System image selection
        ttk.Label(main_frame, text="Custom system.img:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.system_img_path, width=70).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_system_img).grid(row=1, column=2, padx=5, pady=5)
        
        # Output directory selection
        ttk.Label(main_frame, text="Output Directory:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_path, width=70).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_output).grid(row=2, column=2, padx=5, pady=5)
        
        # Progress bar
        ttk.Label(main_frame, text="Progress:").grid(row=3, column=0, sticky=tk.W, pady=10)
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=10)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready")
        self.status_label.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Compile button
        self.compile_btn = ttk.Button(main_frame, text="Compile", command=self.start_conversion)
        self.compile_btn.grid(row=5, column=1, pady=20)
        
        # Cancel button
        self.cancel_btn = ttk.Button(main_frame, text="Cancel", command=self.cancel_conversion, state=tk.DISABLED)
        self.cancel_btn.grid(row=5, column=2, padx=5, pady=20)
        
        # Log text area
        ttk.Label(main_frame, text="Conversion Log:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.log_text = scrolledtext.ScrolledText(main_frame, height=15, width=90)
        self.log_text.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(7, weight=1)
        
    def poll_messages(self):
        """Poll messages from the queue and update UI (runs in main thread)"""
        messages = self.message_queue.get_all()
        for message in messages:
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
            self.status_label.config(text=message)
            
        self.root.after(100, self.poll_messages)
        
    def log_message(self, message):
        """Thread-safe logging"""
        logger.info(message)
        self.message_queue.put(message)
        
    def browse_ozip(self):
        file_path = filedialog.askopenfilename(
            title="Select Original OZIP File",
            filetypes=[("OZIP files", "*.ozip"), ("All files", "*.*")]
        )
        if file_path:
            self.ozip_path.set(file_path)
            
    def browse_system_img(self):
        file_path = filedialog.askopenfilename(
            title="Select Custom system.img File",
            filetypes=[("IMG files", "*.img"), ("All files", "*.*")]
        )
        if file_path:
            # Check if the file is named system.img
            if not file_path.endswith("system.img"):
                result = messagebox.askyesno(
                    "Rename File?",
                    "For best results, the system image should be named 'system.img'. "
                    "Would you like to rename it automatically?"
                )
                if result:
                    new_path = os.path.join(os.path.dirname(file_path), "system.img")
                    try:
                        shutil.copy2(file_path, new_path)
                        file_path = new_path
                    except Exception as e:
                        self.log_message(f"Error renaming file: {str(e)}")
                        messagebox.showerror("Error", f"Failed to rename file: {str(e)}")
                        return
            self.system_img_path.set(file_path)
            
    def browse_output(self):
        dir_path = filedialog.askdirectory(title="Select Output Directory")
        if dir_path:
            self.output_path.set(dir_path)
            
    def start_conversion(self):
        if self.conversion_in_progress:
            self.log_message("Conversion already in progress. Please wait.")
            return
            
        # Validate inputs
        if not self.ozip_path.get():
            messagebox.showerror("Error", "Please select an original OZIP file")
            return
            
        if not self.system_img_path.get():
            messagebox.showerror("Error", "Please select a custom system.img file")
            return
            
        if not self.output_path.get():
            messagebox.showerror("Error", "Please select an output directory")
            return
            
        # Check if system image exists and is accessible
        if not os.path.isfile(self.system_img_path.get()):
            messagebox.showerror("Error", "System image file does not exist or is not accessible")
            return
            
        # Check free disk space
        output_dir = self.output_path.get()
        system_img_size = os.path.getsize(self.system_img_path.get())
        free_space = shutil.disk_usage(output_dir).free
        
        # We need at least 3x the system image size for temporary files
        if free_space < system_img_size * 3:
            messagebox.showerror("Error", "Not enough free disk space in output directory")
            return
            
        # Reset flags
        self.cancel_requested = False
        self.conversion_in_progress = True
        
        # Update UI
        self.compile_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.progress.start(10)
        
        # Start conversion in a separate thread to avoid freezing the GUI
        thread = threading.Thread(target=self.run_conversion)
        thread.daemon = True
        thread.start()
        
    def cancel_conversion(self):
        self.cancel_requested = True
        self.log_message("Cancellation requested...")
        
    def run_conversion(self):
        temp_dir = None
        try:
            self.log_message("Starting conversion process...")
            
            # Create temporary working directory in the output directory (not AppData)
            output_dir = self.output_path.get()
            temp_dir = os.path.join(output_dir, "temp_conversion")
            
            # Clean up any existing temp directory
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            
            os.makedirs(temp_dir, exist_ok=True)
            self.log_message(f"Using temporary directory: {temp_dir}")
            

            # Step 1: Decrypt the original OZIP
            self.log_message("Step 1: Decrypting original OZIP file...")
            decrypted_zip = os.path.join(temp_dir, "decrypted.zip")
            if self.cancel_requested:
                raise Exception("Conversion cancelled by user")
                
            if not self.decrypt_ozip(self.ozip_path.get(), decrypted_zip):
                raise Exception("Failed to decrypt OZIP file")
            
            # Step 2: Extract the decrypted ZIP
            self.log_message("Step 2: Extracting decrypted ZIP...")
            extracted_dir = os.path.join(temp_dir, "extracted")
            os.makedirs(extracted_dir, exist_ok=True)
            if self.cancel_requested:
                raise Exception("Conversion cancelled by user")
                
            self.extract_zip(decrypted_zip, extracted_dir)
            
            # Step 3: Find and decompress system.new.dat.br
            self.log_message("Step 3: Finding and decompressing system.new.dat.br...")
            if self.cancel_requested:
                raise Exception("Conversion cancelled by user")
                
            system_dat_br = self.find_file(extracted_dir, "system.new.dat.br")
            if not system_dat_br:
                raise Exception("system.new.dat.br not found in the extracted files")
                
            system_dat = os.path.join(temp_dir, "system.new.dat")
            self.decompress_br(system_dat_br, system_dat)
            
            # Step 4: Convert system.new.dat to system.img
            self.log_message("Step 4: Converting system.new.dat to system.img...")
            if self.cancel_requested:
                raise Exception("Conversion cancelled by user")
                
            transfer_list = self.find_file(extracted_dir, "system.transfer.list")
            if not transfer_list:
                raise Exception("system.transfer.list not found in the extracted files")
                
            original_system_img = os.path.join(temp_dir, "original_system.img")
            self.convert_dat_to_img(transfer_list, system_dat, original_system_img)
            
            # Step 5: Replace with custom system.img
            self.log_message("Step 5: Replacing with custom system.img...")
            if self.cancel_requested:
                raise Exception("Conversion cancelled by user")
                
            # We'll create a new system.new.dat from the custom system.img
            new_system_dat = os.path.join(temp_dir, "new_system.new.dat")
            new_transfer_list = os.path.join(temp_dir, "new_system.transfer.list")
            self.convert_img_to_dat(self.system_img_path.get(), new_transfer_list, new_system_dat)
            
            # Step 6: Compress the new system.new.dat to .br format
            self.log_message("Step 6: Compressing new system.new.dat to .br format...")
            if self.cancel_requested:
                raise Exception("Conversion cancelled by user")
                
            new_system_dat_br = os.path.join(temp_dir, "new_system.new.dat.br")
            self.compress_to_br(new_system_dat, new_system_dat_br)
            
            # Step 7: Replace the files in the extracted directory
            self.log_message("Step 7: Updating files in the extracted directory...")
            if self.cancel_requested:
                raise Exception("Conversion cancelled by user")
                
            # Remove the old files
            os.remove(system_dat_br)
            if os.path.exists(os.path.join(extracted_dir, "system.new.dat")):
                os.remove(os.path.join(extracted_dir, "system.new.dat"))
            if os.path.exists(os.path.join(extracted_dir, "system.transfer.list")):
                os.remove(os.path.join(extracted_dir, "system.transfer.list"))
                
            # Copy the new files
            shutil.copy2(new_system_dat_br, os.path.join(extracted_dir, "system.new.dat.br"))
            shutil.copy2(new_transfer_list, os.path.join(extracted_dir, "system.transfer.list"))
            
            # Step 8: Create a new ZIP file
            self.log_message("Step 8: Creating new ZIP file...")
            if self.cancel_requested:
                raise Exception("Conversion cancelled by user")
                
            new_zip_path = os.path.join(temp_dir, "new_firmware.zip")
            self.create_zip(extracted_dir, new_zip_path)
            
            # Step 9: Encrypt the new ZIP to OZIP format
            self.log_message("Step 9: Encrypting to OZIP format...")
            if self.cancel_requested:
                raise Exception("Conversion cancelled by user")
                
            output_ozip = os.path.join(self.output_path.get(), "custom_firmware.ozip")
            self.encrypt_to_ozip(new_zip_path, output_ozip)
            
            # Clean up
            self.log_message("Cleaning up temporary files...")
            shutil.rmtree(temp_dir, ignore_errors=True)
            temp_dir = None
            
            self.log_message(f"Conversion completed successfully! Output file: {output_ozip}")
            if self.successful_key:
                self.log_message(f"Used key: {self.successful_key}")
                
            # Show success message in main thread
            self.root.after(0, lambda: messagebox.showinfo("Success", 
                f"Conversion completed successfully!\nOutput file: {output_ozip}\nUsed key: {self.successful_key}"))
            
        except Exception as e:
            error_msg = f"Error during conversion: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.log_message(error_msg)
            
            # Show error message in main thread
            self.root.after(0, lambda: messagebox.showerror("Error", f"Conversion failed: {str(e)}"))
            
        finally:
        # Clean up temp directory if it exists
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except Exception as cleanup_error:
                    self.log_message(f"Warning: Could not clean up temp directory: {cleanup_error}")
                    
            # Update UI in main thread
            self.root.after(0, self.on_conversion_finished)

            
    def on_conversion_finished(self):
        """Called in main thread when conversion finishes"""
        self.compile_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.progress.stop()
        self.conversion_in_progress = False
            
    def decrypt_ozip(self, ozip_path, output_path):
        """Decrypt OZIP file using the known keys"""
        file_size = os.path.getsize(ozip_path)
        if file_size < 0x1050:
            raise Exception("OZIP file is too small to be valid")
            
        with open(ozip_path, 'rb') as f:
            magic = f.read(12)
            # if magic != b'OPPOENCRYPT!':
            #     raise Exception("Not a valid OZIP file - missing OPPOENCRYPT! header")
                
            # Calculate the encrypted data size
            encrypted_size = file_size - 0x1050
            
            # Try each key until one works
            for key_hex in KEYS:
                if self.cancel_requested:
                    return False
                    
                try:
                    key = binascii.unhexlify(key_hex)
                    cipher = AES.new(key, AES.MODE_ECB)
                    
                    # Read and decrypt the file
                    f.seek(0x1050)  # Skip the header
                    
                    # Use a temporary file for writing in the same directory as output
                    temp_dir = os.path.dirname(output_path)
                    temp_filename = os.path.join(temp_dir, f"temp_decrypt_{os.urandom(4).hex()}")
                    
                    with open(temp_filename, 'wb') as tmp_file:
                        bytes_decrypted = 0
                        
                        while bytes_decrypted < encrypted_size:
                            if self.cancel_requested:
                                break
                                
                            # Read a chunk
                            chunk_size = min(0x4000, encrypted_size - bytes_decrypted)
                            chunk = f.read(chunk_size)
                            
                            if not chunk:
                                break
                                
                            # Pad the chunk if needed for AES
                            if len(chunk) % 16 != 0:
                                chunk = pad(chunk, 16)
                                
                            decrypted = cipher.decrypt(chunk)
                            tmp_file.write(decrypted)
                            bytes_decrypted += chunk_size
                    
                    if self.cancel_requested:
                        os.unlink(temp_filename)
                        return False
                    
                    # Verify the decrypted file is a valid ZIP by checking magic bytes
                    with open(temp_filename, 'rb') as tmp:
                        magic_bytes = tmp.read(4)
                        if magic_bytes == b'PK\x03\x04':
                            # Valid ZIP, move to output path
                            if os.path.exists(output_path):
                                os.unlink(output_path)
                            shutil.move(temp_filename, output_path)
                            self.successful_key = key_hex
                            self.log_message(f"Successfully decrypted with key: {key_hex}")
                            return True
                        else:
                            # Not a valid ZIP, remove temp file
                            os.unlink(temp_filename)
                            
                except Exception as e:
                    self.log_message(f"Failed with key {key_hex}: {str(e)}")
                    # Ensure temp file is closed and deleted
                    if 'temp_filename' in locals() and os.path.exists(temp_filename):
                        try:
                            os.unlink(temp_filename)
                        except:
                            pass
                    continue
                    
            raise Exception("Failed to decrypt OZIP with any known key")

    def extract_zip(self, zip_path, output_dir):
        """Extract ZIP file"""
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
        self.log_message("ZIP extraction completed")
        
    def find_file(self, directory, filename):
        """Find a file in a directory recursively"""
        for root, dirs, files in os.walk(directory):
            if filename in files:
                return os.path.join(root, filename)
        return None
        
    def decompress_br(self, br_path, output_path):
        """Decompress .br file using brotli"""
        try:
            # Try using Python brotli module first
            import brotli
            with open(br_path, 'rb') as f:
                compressed_data = f.read()
            decompressed_data = brotli.decompress(compressed_data)
            with open(output_path, 'wb') as f:
                f.write(decompressed_data)
            self.log_message("Brotli decompression completed (Python module)")
        except ImportError:
            # Fallback to brotli command line tool
            self.log_message("Python brotli module not found, using CLI tool")
            try:
                result = subprocess.run(['brotli', '-d', br_path, '-o', output_path], 
                                      capture_output=True, text=True, check=True)
                self.log_message("Brotli decompression completed (CLI tool)")
            except (subprocess.CalledProcessError, FileNotFoundError):
                raise Exception("Brotli decompression requires either brotli tool or Python brotli module")
                
    def convert_dat_to_img(self, transfer_list_path, dat_path, output_img_path):
        """Convert system.new.dat to system.img using transfer list"""
        # Parse transfer list file with robust parsing
        commands = self.parse_transfer_list(transfer_list_path)
        if not commands:
            raise Exception("No valid commands found in transfer list")
            
        block_size = 4096
        
        # Calculate total blocks needed
        max_block = 0
        for cmd, ranges in commands:
            if cmd in ['new', 'erase', 'zero']:
                for start, end in ranges:
                    if end > max_block:
                        max_block = end
        
        # Create output image file
        with open(dat_path, 'rb') as dat_file, open(output_img_path, 'wb') as img_file:
            # Pre-allocate the file with zeros
            img_file.truncate(max_block * block_size)
            
            for cmd, ranges in commands:
                if self.cancel_requested:
                    raise Exception("Conversion cancelled by user")
                    
                if cmd == 'new':
                    for start, end in ranges:
                        block_count = end - start
                        img_file.seek(start * block_size)
                        
                        # Read and write blocks
                        for _ in range(block_count):
                            block = dat_file.read(block_size)
                            if len(block) < block_size:
                                # Pad with zeros if block is incomplete
                                block += b'\x00' * (block_size - len(block))
                            img_file.write(block)
                elif cmd in ['erase', 'zero']:
                    for start, end in ranges:
                        img_file.seek(start * block_size)
                        zero_block = b'\x00' * ((end - start) * block_size)
                        img_file.write(zero_block)
        
        self.log_message("DAT to IMG conversion completed")
        
    def parse_transfer_list(self, transfer_list_path):
        """Robust transfer list parser that handles different versions"""
        commands = []
        
        with open(transfer_list_path, 'r') as f:
            lines = f.readlines()
            
        if not lines:
            return commands
            
        # Parse version (could be string or integer)
        version_line = lines[0].strip()
        try:
            version = int(version_line)
        except ValueError:
            # Handle string versions
            if version_line.isdigit():
                version = int(version_line)
            else:
                version = 1  # Default to version 1
                
        # Parse based on version
        line_index = 1
        
        # Skip lines based on version
        if version >= 2:
            # Next line is new_blocks
            if line_index < len(lines):
                line_index += 1
            # Next line is stash_entries
            if line_index < len(lines):
                line_index += 1
            # Next line is max_blocks
            if line_index < len(lines):
                line_index += 1
                
        # Parse commands
        for i in range(line_index, len(lines)):
            line = lines[i].strip()
            if not line or line.startswith('#'):
                continue
                
            parts = line.split(' ')
            if len(parts) < 2:
                continue
                
            cmd = parts[0]
            if cmd in ['erase', 'new', 'zero']:
                ranges_str = parts[1]
                ranges = ranges_str.split(',')
                
                # Ranges should be in pairs
                if len(ranges) % 2 != 0:
                    self.log_message(f"Warning: Invalid range format in line: {line}")
                    continue
                    
                range_set = []
                for j in range(0, len(ranges), 2):
                    try:
                        start = int(ranges[j])
                        end = int(ranges[j+1])
                        range_set.append((start, end))
                    except ValueError:
                        self.log_message(f"Warning: Invalid range values in line: {line}")
                        continue
                        
                commands.append((cmd, range_set))
                
        return commands
        
    def convert_img_to_dat(self, img_path, output_transfer_list, output_dat_path):
        """Convert system.img to system.new.dat"""
        block_size = 4096
        
        # Get image size and calculate blocks
        img_size = os.path.getsize(img_path)
        total_blocks = (img_size + block_size - 1) // block_size
        
        # Try to detect transfer list version from original if available
        # For now, we'll use version 4 which is common
        version = 4
        
        # Create transfer list
        with open(output_transfer_list, 'w') as f:
            f.write(f'{version}\n')  # Version
            f.write(f'{total_blocks}\n')  # Total blocks
            f.write('0\n')  # Stash entries
            f.write('0\n')  # Max blocks
            
            # Write new command for all blocks
            f.write(f'new 0,{total_blocks}\n')
            
        # Copy the image to dat file using efficient method
        with open(img_path, 'rb') as img_file, open(output_dat_path, 'wb') as dat_file:
            shutil.copyfileobj(img_file, dat_file)
            
        self.log_message("IMG to DAT conversion completed")
        
    def compress_to_br(self, dat_path, output_br_path):
        """Compress .dat file to .br format"""
        try:
            # Try using Python brotli module first
            import brotli
            with open(dat_path, 'rb') as f:
                data = f.read()
            compressed_data = brotli.compress(data, quality=11)
            with open(output_br_path, 'wb') as f:
                f.write(compressed_data)
            self.log_message("Brotli compression completed (Python module)")
        except ImportError:
            # Fallback to brotli command line tool
            self.log_message("Python brotli module not found, using CLI tool")
            try:
                result = subprocess.run(['brotli', '-q', '11', dat_path, '-o', output_br_path], 
                                      capture_output=True, text=True, check=True)
                self.log_message("Brotli compression completed (CLI tool)")
            except (subprocess.CalledProcessError, FileNotFoundError):
                raise Exception("Brotli compression requires either brotli tool or Python brotli module")
                
    def create_zip(self, source_dir, output_zip):
        """Create a ZIP file from directory contents"""
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    if self.cancel_requested:
                        raise Exception("Conversion cancelled by user")
                        
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, arcname)
                    
        self.log_message("ZIP creation completed")
        
    def encrypt_to_ozip(self, zip_path, output_ozip_path):
        """Encrypt ZIP file to OZIP format"""
        if not self.successful_key:
            raise Exception("No successful key found for encryption")
            
        try:
            key = binascii.unhexlify(self.successful_key)
            cipher = AES.new(key, AES.MODE_ECB)
            
            # Create OZIP header
            header = b'OPPOENCRYPT!' + b'\x00' * (0x1050 - 12)
            
            # Read the ZIP file
            zip_size = os.path.getsize(zip_path)
            
            # Write the encrypted file
            with open(zip_path, 'rb') as zip_file, open(output_ozip_path, 'wb') as ozip_file:
                # Write header
                ozip_file.write(header)
                
                # Encrypt and write data in blocks
                bytes_processed = 0
                block_size = 0x4000
                
                while bytes_processed < zip_size:
                    if self.cancel_requested:
                        raise Exception("Conversion cancelled by user")
                        
                    # Read a block
                    read_size = min(block_size, zip_size - bytes_processed)
                    block = zip_file.read(read_size)
                    
                    # Pad the block if needed for AES
                    if len(block) % 16 != 0:
                        block = pad(block, 16)
                    
                    # Encrypt the block
                    encrypted_block = cipher.encrypt(block)
                    ozip_file.write(encrypted_block)
                    bytes_processed += read_size
            
            self.log_message(f"OZIP encryption completed with key: {self.successful_key}")
            return True
            
        except Exception as e:
            self.log_message(f"Encryption failed with key {self.successful_key}: {str(e)}")
            raise

def main():
    root = tk.Tk()
    app = OppoConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()