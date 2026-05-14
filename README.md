# Steganography Tool

A simple command-line tool to **hide secret messages** inside images and audio files using LSB (Least Significant Bit) steganography.

Made by **Villian** | [github.com/VillianIR](https://github.com/VillianIR)

---

## Features

- Hide text inside **PNG / BMP** images
- Hide text inside **WAV** audio files
- Extract hidden messages with optional **password protection**
- **Analyze** any file for suspicious hidden data (LSB bias detection)
- Interactive **menu** — no command-line arguments needed
- Clean, human-readable code

---

## Requirements

- Python 3.7+
- Pillow

```bash
pip install pillow
```

---

## Installation

```bash
git clone https://github.com/VillianIR/steganography-tool.git
cd steganography-tool
pip install -r requirements.txt
python stego.py
```

---

## Usage

Run the script and follow the menu:

```bash
python stego.py
```

```
    +------------------------------------------+
    |       STEGANOGRAPHY TOOL v1.0            |
    |       Made by Villian                    |
    |    github.com/VillianIR                  |
    +------------------------------------------+
    |  1. Hide message in image                |
    |  2. Hide message in audio                |
    |  3. Extract from image                   |
    |  4. Extract from audio                   |
    |  5. Scan file for hidden data            |
    |  6. Exit                                 |
    +------------------------------------------+
```

### Hide message in image

```
>> 1
  Image path: photo.png
  Secret message: My secret text
  Password: 1234
  [+] Message hidden successfully!
  [+] Output: photo_stego.png
```

### Hide message in audio

```
>> 2
  Audio path: audio.wav
  Secret message: My secret text
  Password: 1234
  [+] Message hidden successfully!
  [+] Output: audio_stego.wav
```

### Extract from image

```
>> 3
  Image path: photo_stego.png
  Password: 1234
  [+] Hidden message: My secret text
```

### Extract from audio

```
>> 4
  Audio path: audio_stego.wav
  Password: 1234
  [+] Hidden message: My secret text
```

### Scan for hidden data

```
>> 5
  File path: suspicious.png
  [*] File: suspicious.png
  [*] Size: 245,632 bytes
  [*] LSB Statistical Analysis:
      Ones:  2347 (52.1%)
      Zeros: 2153 (47.9%)
      Bias:  194 bits
  [!] Significant bias — hidden data likely!
```

---

## How It Works

LSB steganography replaces the **least significant bit** of each pixel (or audio sample) with one bit of the secret message. The change is invisible to the human eye/ear but can be statistically detected.

Password protection uses **SHA-256** hashing — the password hash is embedded alongside the message.

---

## File Structure

```
steganography-tool/
├── stego.py          # Main script
├── requirements.txt  # Python dependencies
├── README.md         # This file
├── LICENSE           # MIT License
└── .gitignore        # Git ignore rules
```

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## Author

**Villian**  
GitHub: [github.com/VillianIR](https://github.com/VillianIR)
