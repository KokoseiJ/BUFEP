BUFEP v.alpha3 Specification
# Basic UDP File Exchange Protocol

---

# Spec

## Basic header format

27 Bytes Following:

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1| Byte
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|        Magic Header (0x11, 0x03, 0x70)        | Protocol Ver. |  0-3
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                  Client Identifier (UUID v1)                  |  4-7
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                              ...                              |  8-11
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                              ...                              | 12-15
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                              ...                              | 16-19
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| Req/Res Type  |           Data Size           |  Fletcher-32  | 20-23
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                      ...                      |  Payloads...  | 24-27
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### Magic Header

3-bytes sequence of `0x11, 0x03, 0x70`

### Protocol Version

Should be 0 at the moment.

### UUID

UUID should be generated per request, to prevent collision.

### Req/Res Type

8 bits fowllowing this format:

```
+------+-------+------+------+------+------+------+------+ 
| Type | Error |             Req/Error  type             |        
+------+-------+------+------+------+------+------+------+
```

Where

 * Type: 0 if request, 1 if response
 * Error: 0 if normal, 1 if error
 * Req/Error type: defined below, can have 64 types

### Data Size

Size EXCLUDING header

### Fletcher-32:

4 Bytes of Fletcher-32 checksum calculated from (header EXCLUDING first 4 bytes AND checksum + payload)

---

# Types

## `0`: Ping/Pong

Used to determine PMTUD and connectivity. No data is required in both request and response.

## `1`: GetInfo

### Request

We are using 2 factors to identify a file: Filename and Filehash.

Filehash is SHA256 hash of a file content, and Filename should match with the file that server has.

This is used to avoid accidental hash collision.

Payload format is as follows:

```
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|Filename Length|  Filename...  |      Desired Packet Size      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                      Filehash (32 bytes)                      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                      Passhash (32 bytes)                      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

where length represents the byte length of the following data.

This is used to dynamically adapt to the appropriate size, removing the theoretical limit set within protocol level.

PassHash is a hashed SHA256 password. It should be 0 if not provided.

Desired Packet Size is used to calculate expected amount of packets, ideal value is Path MTU value. You can use Type 0 Ping/Pong to figure out Path MTU from the client side using binary search.

### Response

Client might return Error 1 or Error 2.

Payload format is as follows:

```
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|Filename Length|  Filename...  |Filesize Length|  Filesize...  |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                        Pages (8 bytes)                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

Where Pages is the amount of packets required to completely transfer a file, which the client should expect to receive in full.

Pages should be calculated as `ceil(filesize / (desired_mtu - header_size))` where header_size is 35(27 + 8 for page indicator).

## `2`: GetData

### Request

It is the same as Request Type 1.

```
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|Filename Length|  Filename...  |      Desired Packet Size      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                      Filehash (32 bytes)                      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                      Passhash (32 bytes)                      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### Response

Client should expect server to send multiple packets.

First 8 bytes will be the page number counting from 0, and the rest of the data should be the fragment of file content.

Packet size including the header MUST be matching with the desired packet size unless the page is the last one.

If the checksum is mismatching or some of the packets appear to be dropped, client can send Error Type 4 to request the malformed page again.


# Errors

If no specific payload format is found, request/response can
contain the string message.

```
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| String Length |                   String...                   |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

String length must be specified as 0 if not provided.

## `1`: FileNotFound

## `2`: AuthError

## `3`: PageChecksumMismatch

Sent when a page checksum value mismatches.

Server should send a response of a corresponding page, in Response Type 2.

Payload format is as follows:

```
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|Filename Length|  Filename...  |      Desired Packet Size      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                      Filehash (32 bytes)                      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                      Passhash (32 bytes)                      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                          Page number                          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

---

# Requirements

- [x] Magic header => \x11 \x03 \x70

- [x] Protocol verson
 
- [x] Client UUID 
 
- [ ] A Way to identify the server reliably
 
- [x] Multiple types of req/res
 
- [ ] Multiple Files?
 
- [x] File name
 
- [x] File size
 
- [x] Password/authentication => sha256
 
- [ ] Encryption


# Size representation solutions

1. Fixed size
  - Using a pre-defined amount of bytes ex. uint32

  * Pros: Simple implementation
  * Cons: Less sufficient when transferring a small amount of data, theoretical limit is set

2. size then data
  - First byte represents the length of the data, and then the following data contains the actual length

  * Pros: theoretical limit is comically large, almost no additional calculation
  * Cons: could be difficult to implement in some languages

3. carry on if 0xFF
  - Read the first byte, if the byte is 255, add the next byte. rinse and repeat, until non-255 value is read.

  * Pros: Super easy implementation, no additional bytes used
  * Cons: inevitably slower

4. 3-1. maybe specify the amount of bytes with 0xFF value and thus lowering the size?