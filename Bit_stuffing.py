"""
hdlc_demo.py

Demo script that:
 - Shows bit-stuffing (sender -> transmitted frame -> receiver un-stuff)
 - Shows character (byte) stuffing (sender -> transmitted bytes -> receiver un-stuff)

Prints intermediate values so you can see exactly what happens.
"""

FLAG_BITS = '01111110'   # HDLC flag (bit-level)
FLAG = 0x7E              # byte-level flag
ESC  = 0x7D              # escape byte
ESC_MASK = 0x20          # XOR mask used for escaping

# ---------- Helpers ----------
def to_bits(s: str) -> str:
    """Convert text to a contiguous bit string (8 bits per char)."""
    return ''.join(f'{ord(c):08b}' for c in s)

def from_bits(b: str) -> str:
    """Convert a contiguous bit string (length multiple of 8) to a Python string."""
    if len(b) % 8 != 0:
        raise ValueError("Bit string length must be multiple of 8")
    chars = [b[i:i+8] for i in range(0, len(b), 8)]
    return ''.join(chr(int(byte, 2)) for byte in chars)

def bits_pretty(bits: str) -> str:
    """Return bits grouped by bytes for readability: '01000001 01111101 ...'"""
    return ' '.join(bits[i:i+8] for i in range(0, len(bits), 8))


# ---------------------------
# Bit stuffing (sender)
# ---------------------------
def bit_stuff(data_str: str) -> str:
    bits = to_bits(data_str)
    stuffed_bits = []
    count_ones = 0
    for bit in bits:
        stuffed_bits.append(bit)
        if bit == '1':
            count_ones += 1
            if count_ones == 5:
                # insert a '0' immediately after five consecutive '1's
                stuffed_bits.append('0')
                count_ones = 0
        else:
            count_ones = 0
    frame = FLAG_BITS + ''.join(stuffed_bits) + FLAG_BITS
    return frame

# ---------------------------
# Bit un-stuffing (receiver)
# ---------------------------
def bit_unstuff(frame_bits: str) -> str:
    if not (frame_bits.startswith(FLAG_BITS) and frame_bits.endswith(FLAG_BITS)):
        raise ValueError("Frame missing start/end FLAG_BITS")
    inner = frame_bits[len(FLAG_BITS):-len(FLAG_BITS)]
    out_bits = []
    count_ones = 0
    i = 0
    while i < len(inner):
        b = inner[i]
        out_bits.append(b)
        if b == '1':
            count_ones += 1
            if count_ones == 5:
                # skip the stuffed '0'
                i += 1
                count_ones = 0
        else:
            count_ones = 0
        i += 1
    # verify length is multiple of 8 before converting
    if len(out_bits) % 8 != 0:
        # This indicates an error (corrupted frame) — we still try to convert but warn
        print("WARNING: Recovered bit length is not multiple of 8:", len(out_bits))
    return from_bits(''.join(out_bits))

# ---------------------------
# Character (byte) stuffing (sender)
# ---------------------------
def char_stuff(data_bytes: bytes) -> bytes:
    out = bytearray()
    out.append(FLAG)
    for b in data_bytes:
        if b == FLAG or b == ESC:
            out.append(ESC)
            out.append(b ^ ESC_MASK)
        else:
            out.append(b)
    out.append(FLAG)
    return bytes(out)

# ---------------------------
# Character (byte) un-stuffing (receiver)
# ---------------------------
def char_unstuff(frame: bytes) -> bytes:
    if len(frame) < 2 or frame[0] != FLAG or frame[-1] != FLAG:
        raise ValueError("Frame missing start/end FLAG byte")
    inner = frame[1:-1]
    out = bytearray()
    i = 0
    while i < len(inner):
        if inner[i] == ESC:
            if i+1 >= len(inner):
                raise ValueError("Malformed frame: ESC at end")
            out.append(inner[i+1] ^ ESC_MASK)
            i += 2
        else:
            out.append(inner[i])
            i += 1
    return bytes(out)


# ---------------------------
# Demo runner
# ---------------------------
def demo_bit_stuffing(message: str):
    print("=== BIT STUFFING DEMO ===")
    print("Original message:", repr(message))
    bits = to_bits(message)
    print("Original bits     :", bits_pretty(bits))
    stuffed_frame = bit_stuff(message)
    # Show inner stuffed bits (without flags) and full frame
    inner = stuffed_frame[len(FLAG_BITS):-len(FLAG_BITS)]
    print("Stuffed inner bits:", bits_pretty(inner))
    print("Transmitted frame  :", bits_pretty(stuffed_frame))
    recovered = bit_unstuff(stuffed_frame)
    print("Recovered message :", repr(recovered))
    print()

def demo_char_stuffing(message: str):
    print("=== CHARACTER (BYTE) STUFFING DEMO ===")
    print("Original message:", repr(message))
    mbytes = message.encode('utf-8')
    print("Original bytes (hex):", ' '.join(f'{b:02X}' for b in mbytes))
    framed = char_stuff(mbytes)
    print("Transmitted frame (hex):", ' '.join(f'{b:02X}' for b in framed))
    # Show printable representation where possible
    printable = []
    for b in framed:
        if b == FLAG:
            printable.append("[FLAG]")
        elif b == ESC:
            printable.append("[ESC]")
        elif 32 <= b <= 126:
            printable.append(chr(b))
        else:
            printable.append(f"0x{b:02X}")
    print("Transmitted (printable):", ' '.join(printable))
    recovered_bytes = char_unstuff(framed)
    print("Recovered bytes (hex) :", ' '.join(f'{b:02X}' for b in recovered_bytes))
    print("Recovered message      :", repr(recovered_bytes.decode('utf-8')))
    print()

def run_demos():
    # Choose messages that show the special cases
    messages = [
        "A~}B",          # contains FLAG (0x7E '~') and ESC (0x7D '}') for char stuffing demo
        "A}B",           # contains '}' which has five consecutive 1s in its binary -> good for bit stuffing
        "Hello",         # normal message
    ]
    # Run bit-stuff demo on the message that will show inserted 0s clearly
    demo_bit_stuffing("A}B")
    # Run char-stuff demo on the message containing FLAG and ESC
    demo_char_stuffing("A~}B")
    # Also show a normal case
    demo_bit_stuffing("Hello")
    demo_char_stuffing("Hello")

if __name__ == "__main__":
    run_demos()
