from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Literal

Fmt = Literal["bitmap0", "range1024", "range512", "range256", "range128", "varbitmap"]

@dataclass(frozen=True)
class NCDDecoded:
    arfcn: List[int]
    ba_ind: int
    ext_ind: int
    fmt: Fmt


def _bit_lsb(octet: int, bit_no: int) -> int:
    """GSM bit numbering: bit 1 = LSB, bit 8 = MSB."""
    return (octet >> (bit_no - 1)) & 1


class BitReaderMSB:
    """
    Read bits MSB->LSB within each octet, then next octet.
    Useful because the spec diagrams are written bit8..bit1.
    """
    def __init__(self, data: bytes, byte_i: int = 0, bit_in_byte: int = 8):
        self.data = data
        self.byte_i = byte_i
        self.bit_in_byte = bit_in_byte  # 8..1 (MSB..LSB)

    def bits_left(self) -> int:
        if self.byte_i >= len(self.data):
            return 0
        # bits remaining in current byte + full remaining bytes
        return (self.bit_in_byte) + (len(self.data) - self.byte_i - 1) * 8

    def read_bits(self, n: int) -> int:
        if n <= 0:
            return 0
        if self.bits_left() < n:
            raise ValueError("Not enough bits left to read")

        val = 0
        for _ in range(n):
            b = self.data[self.byte_i]
            # bit_in_byte: 8..1, convert to shift 7..0
            shift = self.bit_in_byte - 1
            bit = (b >> shift) & 1
            val = (val << 1) | bit

            self.bit_in_byte -= 1
            if self.bit_in_byte == 0:
                self.byte_i += 1
                self.bit_in_byte = 8

        return val


def _format_id(o0: int) -> Fmt:
    # FORMAT-ID is determined by bits 8,7,4,3,2 of octet2 (here: first byte of the 16-byte value). :contentReference[oaicite:4]{index=4}
    b8 = _bit_lsb(o0, 8)
    b7 = _bit_lsb(o0, 7)
    b4 = _bit_lsb(o0, 4)
    b3 = _bit_lsb(o0, 3)
    b2 = _bit_lsb(o0, 2)

    if b8 == 0 and b7 == 0:
        return "bitmap0"
    if b8 == 1 and b7 == 0 and b4 == 0:
        return "range1024"   # 1 0 0 X X
    if b8 == 1 and b7 == 0 and b4 == 1 and b3 == 0 and b2 == 0:
        return "range512"
    if b8 == 1 and b7 == 0 and b4 == 1 and b3 == 0 and b2 == 1:
        return "range256"
    if b8 == 1 and b7 == 0 and b4 == 1 and b3 == 1 and b2 == 0:
        return "range128"
    if b8 == 1 and b7 == 0 and b4 == 1 and b3 == 1 and b2 == 1:
        return "varbitmap"
    raise ValueError("Unknown/unsupported FORMAT-ID in Neighbour Cell Description")


def _decode_bitmap0(ncd_16: bytes) -> List[int]:
    # Classic ARFCN 1..124 bitmap (bit map 0).
    o2 = ncd_16[0]

    arfcn: List[int] = []

    # ARFCN 1..8 in last byte
    last = ncd_16[15]
    for n in range(1, 9):
        if _bit_lsb(last, n):
            arfcn.append(n)

    # ARFCN 9..120 in bytes 14..1
    for byte_index in range(14, 0, -1):
        o = ncd_16[byte_index]
        base = 1 + (15 - byte_index) * 8  # 9,17,...,113
        for k in range(1, 9):
            if _bit_lsb(o, k):
                arfcn.append(base + (k - 1))

    # ARFCN 121..124 in first byte bits1..4
    for n in range(121, 125):
        if _bit_lsb(o2, n - 120):
            arfcn.append(n)

    return sorted(set(arfcn))


def _decode_orig_arfcn(ncd_16: bytes) -> int:
    """
    ORIG-ARFCN spans octet2,3,4 in the range/variable formats (Cell Channel Description family).
    In these formats, octet2 bit1 is ARFCN high, octet3 is middle 8 bits, octet4 bit8 is ARFCN low.
    This matches the spec layout where ORIG-ARFCN has high/middle/low parts across those octets. :contentReference[oaicite:5]{index=5}
    """
    high = _bit_lsb(ncd_16[0], 1)          # 1 bit
    mid = ncd_16[1]                        # 8 bits
    low = _bit_lsb(ncd_16[2], 8)           # 1 bit (MSB)
    return (high << 9) | (mid << 1) | low  # 10-bit ARFCN


def _highest_power_of_2_leq(x: int) -> int:
    return 1 << (x.bit_length() - 1)


def _compute_N_range_k(W: List[int], k: int, rng: int) -> int:
    """
    Generic “range” tree decode (for rng = 512/256/128).
    Based on the spec pseudocode structure and constants. :contentReference[oaicite:6]{index=6}
    W is 1-indexed (W[0] unused here).
    """
    index = k
    j = _highest_power_of_2_leq(index)
    n = W[index]

    while index > 1:
        if 2 * index < 3 * j:
            # left child
            index = index - (j // 2)
            modulus = (rng // j) - 1
            add = (rng // 2) // j
            n = ((n + W[index] + add - 2) % modulus) + 1
        else:
            # right child
            index = index - j
            modulus = (rng // j) - 1
            add = (rng // j)
            n = ((n + W[index] + add - 2) % modulus) + 1
        j //= 2

    return n


def _read_W_list(reader: BitReaderMSB, max_k: int, bits_for_k) -> List[int]:
    """
    Read W(1)..W(max_k) until W(k)==0 then stop (rest should be 0).
    bits_for_k(k) gives bit-length for W(k).
    """
    W = [0] * (max_k + 1)  # 1-indexed
    for k in range(1, max_k + 1):
        bl = bits_for_k(k)
        if bl <= 0:
            break
        if reader.bits_left() < bl:
            break
        W[k] = reader.read_bits(bl)
        if W[k] == 0:
            # per spec: if W(k) null, subsequent W are null
            break
    return W


def decode_ncd(ncd_16: bytes) -> NCDDecoded:
    if len(ncd_16) != 16:
        raise ValueError("Neighbour Cell Description value must be 16 bytes")

    o0 = ncd_16[0]
    ext_ind = _bit_lsb(o0, 6)  # EXT-IND bit (octet2 bit6) :contentReference[oaicite:7]{index=7}
    ba_ind = _bit_lsb(o0, 5)   # BA-IND bit (octet2 bit5) :contentReference[oaicite:8]{index=8}

    fmt = _format_id(o0)

    if fmt == "bitmap0":
        arfcn = _decode_bitmap0(ncd_16)
        return NCDDecoded(arfcn=arfcn, ba_ind=ba_ind, ext_ind=ext_ind, fmt=fmt)

    if fmt == "varbitmap":
        orig = _decode_orig_arfcn(ncd_16)
        # RRFCN bits start immediately after ORIG-ARFCN low bit (octet4 bit8), i.e. at octet4 bit7.
        r = BitReaderMSB(ncd_16, byte_i=2, bit_in_byte=7)

        arfcn = {orig}
        # RRFCN N => ARFCN = (orig + N) mod 1024 :contentReference[oaicite:9]{index=9}
        n = 1
        while r.bits_left() > 0:
            bit = r.read_bits(1)
            if bit:
                arfcn.add((orig + n) % 1024)
            n += 1

        return NCDDecoded(arfcn=sorted(arfcn), ba_ind=ba_ind, ext_ind=ext_ind, fmt=fmt)

    # Range formats (512/256/128)
    if fmt in ("range512", "range256", "range128"):
        orig = _decode_orig_arfcn(ncd_16)
        rng = {"range512": 512, "range256": 256, "range128": 128}[fmt]

        # W(1) starts at octet4 bit7 (after ORIG low bit at octet4 bit8).
        reader = BitReaderMSB(ncd_16, byte_i=2, bit_in_byte=7)

        # W bit-length rules from the range family:
        # range512: W(1)=9 bits, W(2..3)=8, W(4..7)=7, ...
        # range256: W(1)=8 bits, W(2..3)=7, W(4..7)=6, ...
        # range128: W(1)=7 bits, W(2..3)=6, W(4..7)=5, ...
        base = {"range512": 9, "range256": 8, "range128": 7}[fmt]

        def bits_for_k(k: int) -> int:
            # k in [2^m .. 2^(m+1)-1] => base - m bits
            m = k.bit_length() - 1
            return base - m

        # Max W count in 16-byte NCD is bounded; these match the spec maxes for CCDD: 17/21/28. :contentReference[oaicite:10]{index=10}
        max_k = {"range512": 17, "range256": 21, "range128": 28}[fmt]
        W = _read_W_list(reader, max_k, bits_for_k)

        arfcn = {orig}
        for k in range(1, max_k + 1):
            if W[k] == 0:
                break
            N = _compute_N_range_k(W, k, rng)
            arfcn.add((orig + N) % 1024)

        return NCDDecoded(arfcn=sorted(arfcn), ba_ind=ba_ind, ext_ind=ext_ind, fmt=fmt)

    # Optional: range1024 exists but is rarer for BA lists; implement if you actually hit it.
    # (Kept as a hard error so you notice rather than silently lying.)
    if fmt == "range1024":
        raise NotImplementedError("range1024 seen in NCD: implement if your data actually uses it")

    raise ValueError("Unreachable")


# In your parse_si2(), replace:
# neighbors = decode_ncd_bitmap0(ncd_16)
# with:
# ncd = decode_ncd(ncd_16)
# return SI2Neighbors(arfcn=ncd.arfcn, ba_ind=ncd.ba_ind, ext_ind=ncd.ext_ind, ncc_permitted=ncc_perm, rach_control=rach)


# def decode_ncd_bitmap0(ncd_16: bytes) -> SI2Neighbors:
#     """
#     Decode Neighbour Cell Description (value part only) when using bit map 0.

#     In SI2, Neighbour Cell Description is carried as V(16) = octets 2..17 of the IE
#     (i.e., the IEI octet is NOT present). See 3GPP TS 44.018.

#     Layout (octet 2 is ncd_16[0]):
#       - octet2 bit6 = EXT-IND
#       - octet2 bit5 = BA-IND
#       - ARFCN bits cover N=1..124:
#           ARFCN 1..8   -> octet17 bits1..8  (ncd_16[15])
#           ARFCN 9..16  -> octet16 bits1..8  (ncd_16[14])
#           ...
#           ARFCN 113..120 -> octet3 bits1..8 (ncd_16[1])
#           ARFCN 121..124 -> octet2 bits1..4 (ncd_16[0])
#     """
#     if len(ncd_16) != 16:
#         raise ValueError(f"Expected 16 bytes for SI2 Neighbour Cell Description value, got {len(ncd_16)}")

#     oct2 = ncd_16[0]
#     ext_ind = _bit(oct2, 6)
#     ba_ind = _bit(oct2, 5)

#     # Decide format: in practice SI2 commonly uses bitmap0 for the classic 1..124 set.
#     # If the network uses range/variable formats to represent other bands, you’ll need SI2bis/SI2ter
#     # (or implement those formats).
#     # A crude sanity check: if bit8 (labeled "Bit128" in figures) is set, you likely aren't in bitmap0.
#     if _bit(oct2, 8) == 1:
#         raise NotImplementedError(
#             "Neighbour Cell Description appears to use a non-bitmap0 format (range/variable). "
#             "Implement TS 44.018 Frequency List range/var formats or parse SI2bis/SI2ter as well."
#         )

#     arfcn: List[int] = []

#     # ARFCN 1..8 are in last byte (octet 17)
#     last = ncd_16[15]
#     for n in range(1, 9):
#         if _bit(last, n):
#             arfcn.append(n)

#     # ARFCN 9..120 live in bytes 14..1 (octets 16..3)
#     # byte_index 14 corresponds to ARFCN 9..16, ..., byte_index 1 corresponds to ARFCN 113..120
#     for byte_index in range(14, 0, -1):
#         o = ncd_16[byte_index]
#         base = 1 + (15 - byte_index) * 8  # 9,17,25,...,113
#         for k in range(1, 9):  # bit1..bit8 => base..base+7
#             if _bit(o, k):
#                 arfcn.append(base + (k - 1))

#     # ARFCN 121..124 are octet2 bits1..4
#     for n in range(121, 125):
#         if _bit(oct2, n - 120):  # 121->bit1, 124->bit4
#             arfcn.append(n)

#     arfcn = sorted(set(arfcn))
#     return SI2Neighbors(arfcn=arfcn, ba_ind=ba_ind, ext_ind=ext_ind)


# def parse_si2(payload: bytes, *, includes_l2_pseudo_length: bool = True) -> SI2Neighbors:
#     """
#     Parse a GSM RR 'System Information Type 2' message and return neighbor ARFCNs.

#     Expected ordering per TS 44.018:
#       [optional L2 pseudo length: 1]
#       PD/Skip (1), Message Type (1),
#       Neighbour Cell Description (16),
#       NCC Permitted (1),
#       RACH Control Parameters (3)

#     Note: Some capture stacks give you the RR message starting at PD (no L2 pseudo length).
#     """
#     if includes_l2_pseudo_length:
#         if len(payload) < 1 + 1 + 1 + 16 + 1 + 3:
#             raise ValueError("Payload too short for SI2 with L2 pseudo length")
#         off = 1  # skip L2 pseudo length
#     else:
#         if len(payload) < 1 + 1 + 16 + 1 + 3:
#             raise ValueError("Payload too short for SI2 without L2 pseudo length")
#         off = 0

#     pd_skip = payload[off]
#     msg_type = payload[off + 1]
#     ncd_16 = payload[off + 2 : off + 2 + 16]
#     ncc_perm = payload[off + 2 + 16]
#     rach = payload[off + 2 + 16 + 1 : off + 2 + 16 + 1 + 3]

#     print(pd_skip, msg_type, ncd_16, ncc_perm, rach)
#     # We don't hard-fail on msg_type because different stacks sometimes mask/pack it,
#     # but you can assert it if your capture is clean.
#     # Typical RR SI2 message type is 0x1A in GSM.
#     neighbors = decode_ncd_bitmap0(ncd_16)
#     return SI2Neighbors(
#         arfcn=neighbors.arfcn,
#         ba_ind=neighbors.ba_ind,
#         ext_ind=neighbors.ext_ind,
#         ncc_permitted=ncc_perm,
#         rach_control=rach,
#     )

from bitarray import bitarray


# --- tiny example ---
if __name__ == "__main__":
    payload = bytes.fromhex("59061a9fe7d00000000007800000000000000088a80000")  # fill with your SI2 RR bytes
    # Example field extraction
    bits = bitarray()
    bits.frombytes(payload)
    l2len = bits[0:6]
    l2len_val = int(l2len.to01(), 2)  # 22

    pd = bits[12:16]
    pd_val = int(pd.to01(), 2)  # 22
    
    mt = bits[16:24]
    mt_val = int(mt.to01(), 2)  # 22
    
    bcc = bits[24:152]
    ncc_permitted = bits[152:160]  # or wherever it sits in SI2
    ncc_permitted_val = int(ncc_permitted.to01(), 2)  # 22
    print(l2len_val, pd_val, mt_val, bcc, ncc_permitted, ncc_permitted_val)
    rezults= decode_ncd(bytes.fromhex("9fe7d000000000078000000000000000"))
    print(rezults)
    #print(bits)
    #print(parse_si2(payload, includes_l2_pseudo_length=False))
    pass
