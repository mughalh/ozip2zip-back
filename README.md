# ozip2zip-back
###(help needed!)
![Alt text](/image.png)

compiled using pyinstaller --onefile --windowed aop.py


(BETA) OZIP tool for Custom ROM for devices without fastboot, No SP Flash tool,  for Oppo, Oneplus, Xiaomi, Realme

Fork https://github.com/bkerler/oppo_ozip_decrypt & https://github.com/chiragkrishna/system.new.dat-extractor

Here's a comprehensive GitHub README for your OPPO ROM Converter:

```markdown
# OPPO ROM Converter

A powerful GUI application for converting custom ROMs to OPPO's OZIP format, enabling flashing of custom firmware on OPPO/Realme devices using the official recovery system.

![OPPO ROM Converter](https://img.shields.io/badge/Platform-Windows-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8%2B-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

## ✨ Features

- **OZIP Decryption/Encryption**: Supports multiple AES encryption keys for various OPPO/Realme devices
- **HiDPI Support**: Fully compatible with high-resolution displays
- **User-Friendly GUI**: Intuitive interface with progress tracking
- **Batch Processing**: Convert system images while preserving original OTA structure
- **Cross-Platform**: Works on Windows with proper HiDPI scaling
- **Comprehensive Logging**: Detailed conversion logs for debugging

## 📋 Supported Devices

The tool supports a wide range of OPPO and Realme devices including:
- OPPO R9s, R11, R11s, R17 Pro, Find X
- Realme 1, 2 Pro, 3 Pro, 5, X, X2, XT
- Realme 5 Pro, Q, X2 Pro
- OPPO A series (A1, A3s, A5s, A7, A9, A77)
- Reno series (Reno, Reno 2, Reno 10x Zoom, Reno Ace)
- And many more...

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Windows 10/11 (recommended) or Linux/macOS
- 4GB+ RAM recommended for large ROM conversions
- Sufficient disk space (3x the system image size)

### Quick Install

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/oppo-rom-converter.git
   cd oppo-rom-converter
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python oppo_converter.py
   ```

### Requirements

The `requirements.txt` file includes:
```
pycryptodome>=3.10.1
brotli>=1.0.9
```

## 🎯 Usage

### Basic Conversion

1. **Select Original OZIP**: Choose the official OPPO firmware file (.ozip)
2. **Select Custom system.img**: Choose your custom system image
3. **Choose Output Directory**: Select where to save the converted file
4. **Click Compile**: Start the conversion process

### Conversion Process

The tool performs the following steps automatically:

1. **Decryption**: Decrypts the original OZIP using the appropriate AES key
2. **Extraction**: Extracts the decrypted ZIP contents
3. **Decompression**: Decompresses system.new.dat.br to system.new.dat
4. **Conversion**: Converts system.new.dat to system.img for analysis
5. **Replacement**: Replaces the system image with your custom version
6. **Compression**: Compresses the new system image back to .br format
7. **Re-encryption**: Creates a new OZIP file with your custom ROM

### Command Line Usage

For advanced users, the tool can also be used via command line:

```bash
# Analyze an OZIP file
python analyze_ozip.py firmware.ozip

# Convert with specific key
python oppo_converter.py --input firmware.ozip --system custom_system.img --output output_dir --key YOUR_AES_KEY
```

## 🔑 Supported AES Keys

The tool includes an extensive database of AES keys for various devices:

```python
KEYS = [
    "d6eecf0ae5acd4e0e9fe522de7ce381e",  # mnkey
    "d6eccf0ae5acd4e0e92e522de7c1381e",  # mkey
    "d6dccf0ad5acd4e0292e522db7c1381e",  # realkey
    # ... over 40 supported keys
]
```

## 🛠️ Technical Details

### File Structure

```
oppo-rom-converter/
├── oppo_converter.py      # Main GUI application
├── analyze_ozip.py        # OZIP analysis tool
├── requirements.txt       # Python dependencies
├── oppo_converter.log     # Generated log file
└── README.md             # This file
```

### OZIP Format

OPPO uses a custom encrypted ZIP format (.ozip) with:
- AES-ECB encryption with device-specific keys
- 0x1050 byte header with "OPPOENCRYPT!" magic
- 0x4000 byte encrypted blocks
- Brotli-compressed system images

### Recovery Mode Flashing

After conversion:
1. Transfer the .ozip file to your phone's storage
2. Shutdown the phone completely
3. Press Power + Volume Down to enter recovery mode
4. Select "Firmware restore from device"
5. Choose your converted .ozip file

## 🐛 Troubleshooting

### Common Issues

1. **"OPPOENCRYPT! header not found"**
   - Ensure you're using a valid OPPO OZIP file
   - Try the analysis tool first: `python analyze_ozip.py your_file.ozip`

2. **File access errors on Windows**
   - Run as Administrator if needed
   - Check antivirus software isn't blocking file operations
   - Ensure sufficient disk space

3. **Conversion fails at decryption**
   - Your device might use a key not in the database
   - Contact developers to add support for your device

4. **HiDPI display issues**
   - Application automatically detects and scales for HiDPI
   - Manual scaling can be adjusted in the code

### Logs

Check `oppo_converter.log` for detailed error information and conversion progress.

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Add new device keys**: If you have a device not currently supported
2. **Improve GUI**: Enhance the user interface or add new features
3. **Documentation**: Improve this README or add usage examples
4. **Testing**: Test on different devices and report issues

### Adding New Keys

To add support for a new device:

1. Extract the AES key from your device's recovery
2. Add it to the `KEYS` list in the code
3. Test with your device's OZIP files
4. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is provided for educational and development purposes only. Use at your own risk. The developers are not responsible for any damage to devices or data loss resulting from the use of this software.

Always backup your data before flashing any firmware.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/oppo-rom-converter/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/oppo-rom-converter/discussions)
- **Email**: your-email@example.com

## 🙏 Acknowledgments

- Based on original work by B. Kerler
- Crypto functions using pycryptodome
- Brotli compression support
- Open-source community contributions

---

**Note**: This tool is not affiliated with or endorsed by OPPO or Realme. All trademarks are property of their respective owners.
```

This README includes:

1. **Comprehensive feature list** showcasing the tool's capabilities
2. **Installation instructions** for different scenarios
3. **Detailed usage guide** with step-by-step instructions
4. **Technical specifications** about the OZIP format
5. **Troubleshooting section** for common issues
6. **Contribution guidelines** for developers
7. **Legal disclaimers** and license information
8. **Support channels** for users needing help

You can customize the GitHub links, email address, and other specific details for your repository. The README is structured to be both user-friendly and technically comprehensive.
