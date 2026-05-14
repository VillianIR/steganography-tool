import os
import sys
import hashlib
import struct
import wave
from PIL import Image

__author__  = "Villian"
__version__ = "1.0"
__github__  = "https://github.com/VillianIR"

def main_menu():
    print("""
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
    """)
    return input("  >> Choose an option: ").strip()

# ─── embed message into LSB ───
def _stuff_bits(pixels, message, passwd=None):
    if passwd:
        tag = hashlib.sha256(passwd.encode()).hexdigest()[:16]
        message = tag + ":::" + message
    
    bits = ''.join(format(ord(c), '08b') for c in message) + '11111111'
    
    if len(bits) > len(pixels) * 3:
        return None, "Message too long for this image!"
    
    out = []
    idx = 0
    for r, g, b in pixels:
        if idx < len(bits):
            r = (r & 0xFE) | int(bits[idx]); idx += 1
        if idx < len(bits):
            g = (g & 0xFE) | int(bits[idx]); idx += 1
        if idx < len(bits):
            b = (b & 0xFE) | int(bits[idx]); idx += 1
        out.append((r, g, b))
    
    return out, None

def _stuff_audio_samples(samples, message, passwd=None):
    if passwd:
        tag = hashlib.sha256(passwd.encode()).hexdigest()[:16]
        message = tag + ":::" + message
    
    bits = ''.join(format(ord(c), '08b') for c in message) + '11111111'
    
    if len(bits) > len(samples):
        return None, "Message too long for this audio file!"
    
    for i in range(len(bits)):
        samples[i] = (samples[i] & 0xFFFE) | int(bits[i])
    
    return samples, None

def _extract_bits(binary_str, passwd=None):
    end = binary_str.find('11111111')
    if end == -1:
        return None, "No hidden message found!"
    
    chars = []
    for i in range(0, end, 8):
        if i + 8 <= len(binary_str):
            chars.append(chr(int(binary_str[i:i+8], 2)))
    
    raw = ''.join(chars)
    
    if passwd:
        if ':::' not in raw:
            return None, "Wrong password or no password set!"
        tag, content = raw.split(':::', 1)
        expected = hashlib.sha256(passwd.encode()).hexdigest()[:16]
        if tag != expected:
            return None, "Wrong password!"
        return content, None
    
    return raw, None

def _analyze_lsb(bits):
    ones = bits.count('1')
    zeros = bits.count('0')
    total = len(bits)
    bias = abs(ones - zeros)
    suspicious = bias > total * 0.1
    return ones, zeros, total, bias, suspicious

# ═══════════════════════════════════════════════
#  Core functions
# ═══════════════════════════════════════════════

def hide_in_image():
    path = input("  Image path (PNG/BMP): ").strip().strip('"')
    if not os.path.exists(path):
        print("  [!] File not found!"); return
    
    msg = input("  Secret message: ").strip()
    if not msg:
        print("  [!] Message cannot be empty!"); return
    
    pwd = input("  Password (Enter to skip): ").strip()
    if not pwd: pwd = None
    
    try:
        img = Image.open(path).convert('RGB')
        pixels = list(img.getdata())
        
        new_pixels, err = _stuff_bits(pixels, msg, pwd)
        if err:
            print(f"  [!] {err}"); return
        
        new_img = Image.new('RGB', img.size)
        new_img.putdata(new_pixels)
        
        base, ext = os.path.splitext(path)
        save_path = f"{base}_stego.png"
        new_img.save(save_path, 'PNG')
        
        print(f"\n  [+] Message hidden successfully!")
        print(f"  [+] Output: {save_path}")
        print(f"  [+] Message size: {len(msg)} chars")
        
    except Exception as e:
        print(f"  [!] Error: {e}")

def hide_in_audio():
    path = input("  Audio path (WAV): ").strip().strip('"')
    if not os.path.exists(path):
        print("  [!] File not found!"); return
    
    msg = input("  Secret message: ").strip()
    if not msg:
        print("  [!] Message cannot be empty!"); return
    
    pwd = input("  Password (Enter to skip): ").strip()
    if not pwd: pwd = None
    
    try:
        with wave.open(path, 'rb') as w:
            params = w.getparams()
            frames = w.readframes(w.getnframes())
        
        samples = list(struct.unpack(f'{len(frames)//2}h', frames))
        
        new_samples, err = _stuff_audio_samples(samples, msg, pwd)
        if err:
            print(f"  [!] {err}"); return
        
        new_frames = struct.pack(f'{len(new_samples)}h', *new_samples)
        
        base, _ = os.path.splitext(path)
        save_path = f"{base}_stego.wav"
        
        with wave.open(save_path, 'wb') as w:
            w.setparams(params)
            w.writeframes(new_frames)
        
        print(f"\n  [+] Message hidden successfully!")
        print(f"  [+] Output: {save_path}")
        
    except Exception as e:
        print(f"  [!] Error: {e}")

def extract_from_image():
    path = input("  Image path: ").strip().strip('"')
    if not os.path.exists(path):
        print("  [!] File not found!"); return
    
    pwd = input("  Password (Enter to skip): ").strip()
    if not pwd: pwd = None
    
    try:
        img = Image.open(path).convert('RGB')
        pixels = list(img.getdata())
        
        bits = ''
        for p in pixels:
            for c in p[:3]:
                bits += str(c & 1)
        
        result, err = _extract_bits(bits, pwd)
        if err:
            print(f"  [!] {err}")
        else:
            print(f"\n  [+] Hidden message: {result}")
    
    except Exception as e:
        print(f"  [!] Error: {e}")

def extract_from_audio():
    path = input("  Audio path: ").strip().strip('"')
    if not os.path.exists(path):
        print("  [!] File not found!"); return
    
    pwd = input("  Password (Enter to skip): ").strip()
    if not pwd: pwd = None
    
    try:
        with wave.open(path, 'rb') as w:
            frames = w.readframes(w.getnframes())
        
        samples = list(struct.unpack(f'{len(frames)//2}h', frames))
        
        bits = ''
        for s in samples:
            bits += str(s & 1)
        
        result, err = _extract_bits(bits, pwd)
        if err:
            print(f"  [!] {err}")
        else:
            print(f"\n  [+] Hidden message: {result}")
    
    except Exception as e:
        print(f"  [!] Error: {e}")

def scan_file():
    path = input("  File path: ").strip().strip('"')
    if not os.path.exists(path):
        print("  [!] File not found!"); return
    
    size = os.path.getsize(path)
    print(f"\n  [*] File: {os.path.basename(path)}")
    print(f"  [*] Size: {size:,} bytes")
    
    ext = os.path.splitext(path)[1].lower()
    
    if ext in ('.png', '.bmp'):
        try:
            img = Image.open(path).convert('RGB')
            pixels = list(img.getdata())[:1000]
            bits = ''.join(str(c & 1) for p in pixels for c in p[:3])
            
            ones, zeros, total, bias, suspicious = _analyze_lsb(bits)
            
            print(f"\n  [*] LSB Statistical Analysis:")
            print(f"      Ones:  {ones} ({100*ones/total:.1f}%)")
            print(f"      Zeros: {zeros} ({100*zeros/total:.1f}%)")
            print(f"      Bias:  {bias} bits")
            
            if suspicious:
                print(f"  [!] Significant bias — hidden data likely!")
            else:
                print(f"  [*] Distribution looks natural.")
        except:
            print("  [!] Could not analyze image!")
    
    elif ext == '.wav':
        try:
            with wave.open(path, 'rb') as w:
                frames = w.readframes(min(1000, w.getnframes()))
            samples = list(struct.unpack(f'{len(frames)//2}h', frames))
            bits = ''.join(str(s & 1) for s in samples)
            
            ones, zeros, total, bias, suspicious = _analyze_lsb(bits)
            
            print(f"\n  [*] LSB Statistical Analysis:")
            print(f"      Ones:  {ones} ({100*ones/total:.1f}%)")
            print(f"      Zeros: {zeros} ({100*zeros/total:.1f}%)")
            
            if suspicious:
                print(f"  [!] Significant bias — hidden data likely!")
            else:
                print(f"  [*] Distribution looks natural.")
        except:
            print("  [!] Could not analyze audio file!")
    
    else:
        with open(path, 'rb') as f:
            data = f.read()
        
        if b'PK' in data[100:]:
            print("  [!] ZIP archive appended — possible hidden file!")
        
        bits = ''.join(str(b & 1) for b in data[:1000])
        ones, zeros, total, bias, suspicious = _analyze_lsb(bits)
        
        if suspicious:
            print(f"  [!] LSB bias detected — possible hidden data!")
        else:
            print(f"  [*] Nothing suspicious found.")

# ═══════════════════════════════════════════════
if __name__ == "__main__":
    while True:
        choice = main_menu()
        
        if choice == '1':
            hide_in_image()
        elif choice == '2':
            hide_in_audio()
        elif choice == '3':
            extract_from_image()
        elif choice == '4':
            extract_from_audio()
        elif choice == '5':
            scan_file()
        elif choice == '6':
            print("\n  Goodbye!\n")
            break
        else:
            print("  [!] Invalid option!")
        
        input("\n  [Enter] to continue...")
