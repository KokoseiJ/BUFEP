import struct

MAGIC_BYTES = b"\x11\x03\x70"
BYTEORDER = "little"


class UnsupportedVersion(Exception):
    pass


class ChecksumMismatch(Exception):
    pass


def btoi(byte):
    return int.from_bytes(byte, BYTEORDER)


def byte_split(data, size):
    for i in range(0, len(data), size):
        yield data[i:i+size]


def fletcher(datas, bit=16):
    bytelen = int(bit / 16)
    threshold = int(2 ** (bit / 2) - 1)
    #
    sum1 = 0
    sum2 = 0
    #
    for data in datas:
        assert len(data) == bytelen
        sum1 = (sum1 + btoi(data)) % threshold
        sum2 = (sum2 + sum1) % threshold
    #
    return (sum2 << (bit / 2)) | sum1


def check_version(fp):
    magic = fp.read(4)
    if magic[:3] != MAGIC_BYTES:
        return False

    version = btoi(magic[3])

    return version


class ParserV1:
    HEADER_STRUCT = struct.Struct("<16sBH4s")

    @classmethod
    def parse_header(cls, fp):
        header = fp.read(23)

        uuid, type_, size, checksum = cls.HEADER_STRUCT.unpack(header)

        data = fp.read(size)

        if fletcher(byte_split(data, 16), 32) != checksum:
            raise ChecksumMismatch

        return uuid, type_, data
