import struct
from uuid import UUID

BYTEORDER = "little"


def btoi(byte, order=BYTEORDER):
    return int.from_bytes(byte, order)


def split_bytes(data, size):
    for i in range(0, len(data), size):
        yield data[i:i+size]


def fletcher(data, bit=32):
    chunk_size = int(bit / 16)
    mask = int(2 ** (bit / 2)) - 1

    sum1 = 0
    sum2 = 0

    for chunk in split_bytes(data, chunk_size):
        print(chunk)
        print(btoi(chunk))
        sum1 = (sum1 + btoi(chunk)) % mask
        sum2 = (sum2 + sum1) % mask
        print(sum1, sum2)
        print(mask)

    return (sum2 << (chunk_size * 8)) | sum1


class BUFEPError(Exception):
    pass


class BUFEPPacketVAlpha3:
    version = 0
    magic = b"\x11\x03\x70"
    packet_struct = "<16sBHI"

    def __init__(self, client_uuid, type_, size, data):
        self.uuid = UUID(bytes_le=client_uuid)
        self.type = type_
        self.size = size
        self.data = data

    @classmethod
    def from_packetstream(cls, packet):
        magic = packet.read(3)
        if magic != cls.magic:
            raise BUFEPError("Magic Mismatch")

        version = btoi(packet.read(1))
        if version != cls.version:
            raise BUFEPError("Version Mismatch")

        header = packet.read(23)

        uuid, type_, size, checksum = struct.unpack(header)

        data = packet.read(size)
        if len(data) != size:
            raise BUFEPError("Size Mismatch- Payload is smaller than expected")
        elif packet.read(-1) != 0:
            raise BUFEPError("Size Mismatch- Payload is bigger than expected")

        checksum_data = header[:-4] + data

        checksum_calc = fletcher(checksum_data, 32)

        if checksum != checksum_calc:
            raise BUFEPError("Checksum Mismatch")

        return cls(uuid, type_, size, data)


print(hex(fletcher(b"abcdef")))
