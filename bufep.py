import struct
from uuid import UUID, uuid1

BYTEORDER = "little"


def btoi(byte, order=BYTEORDER):
    return int.from_bytes(byte, order)


def itob(num, leng=1, order=BYTEORDER):
    return int.to_bytes(num, leng, order)


def split_bytes(data, size):
    for i in range(0, len(data), size):
        yield data[i:i+size]


def fletcher(data, bit=32):
    chunk_size = int(bit / 16)
    mask = int(2 ** (bit / 2)) - 1

    sum1 = 0
    sum2 = 0

    for chunk in split_bytes(data, chunk_size):
        sum1 = (sum1 + btoi(chunk)) % mask
        sum2 = (sum2 + sum1) % mask

    return (sum2 << (chunk_size * 8)) | sum1


class BUFEPError(Exception):
    pass


class BUFEPPacketVAlpha3:
    version = 0
    magic = b"\x11\x03\x70"
    header_struct = "<16sBHI"

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

        uuid, type_, size, checksum = struct.unpack(cls.header_struct, header)

        data = packet.read(size)
        if len(data) != size:
            raise BUFEPError("Size Mismatch- Payload is smaller than expected")
        elif len(packet.read(-1)) != 0:
            raise BUFEPError("Size Mismatch- Payload is bigger than expected")

        checksum_data = header[:-4] + data

        checksum_calc = fletcher(checksum_data, 32)

        if checksum != checksum_calc:
            raise BUFEPError("Checksum Mismatch")

        return cls(uuid, type_, size, data)

    def to_packet(self):
        header = struct.pack(
            self.header_struct, self.uuid.bytes_le, self.type, self.size, 0)
        checksum = fletcher(header[:-4] + self.data)
        header = struct.pack(
            self.header_struct, self.uuid.bytes_le, self.type, self.size,
            checksum)
        return self.magic + itob(self.version) + header + self.data


if __name__ == "__main__":
    with open("testpacket", "wb") as f:
        uuid = uuid1()
        print(uuid)
        packet = BUFEPPacketVAlpha3(uuid.bytes_le, 69, 6, b"zotgay")
        packetbytes = packet.to_packet()
        f.write(packetbytes)
        print('0x' + "".join([hex(x)[2:] for x in packetbytes]))

        from io import BytesIO

        newpacket = BUFEPPacketVAlpha3.from_packetstream(BytesIO(packetbytes))
        print(newpacket.data)
