# ozip2zip-back
## (help needed! willing to work with anyone)
A powerful GUI application for converting custom ROMs to OPPO's OZIP format, enabling flashing of custom firmware on OPPO/Realme devices using the official recovery system.
(BETA) OZIP tool for Custom ROM for devices without fastboot, No SP Flash tool,  for Oppo, Oneplus, Xiaomi, Realme
![Alt text](/image.png)

compiled using pyinstaller --onefile --windowed aop.py
MUST HAVE PYTHON!

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
   - 
## 🤝 Contributing
want to see this as a application the world can use to flash custom roms for devices with a locked down fastboot, using OEM recovery mode where allowed from device

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
- **Email**: mughal641@outlook.com
