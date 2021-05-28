BUFEP v.alpha1 Specification

# Base format

`MMMVSSSSIIIIPPOTLLRRD-CCCC`

M: Magic header, \x11 \x03 \x70

V: Protocol Version information, 0 in this spec

S: Shard for identifying requests

I: IP address, used in UDP hole punching

P: UDP Port number, used in UDP hole punching

O: Type of the operation(a.k.a. OPcode)

T: Operation mode(ex. send/recv)

L: Length of the data

R: Reserved header space- could be used or left null depending on the operation.

D: Data, as specified in L. This does not include the length of the checksum

C: Checksum at the last 4 bytes of the data, calculated using Fletcher-32

```
                     1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|    3 bytes Magic header: \x11, \x03, \x70     | Protocol Ver. |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                             Shard                             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                          IP Address                           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         Port number           |    OP code    |    OP mode    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         Data Length           |     Reserved Header Space     |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                            Data...                            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                     Fletcher-32 Checksum                      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

IP Address and a port number doesn't get changed in the response.

in case of making simultaneous requests in a single machine, A shard will be used to identify each requests.
Shard should be unique per requests- otherwise it could cause conflicts.

Operation mode can be used to specify the type of the operation, but it can also be used to specify errors-
such as data loss, authentication request, and errors in a parameter.

Error types start from `0xA0`, and it could be defined by each OP codes.
Error types starting from `0xE0` are global(OP code independent).

`0xE0`: Data loss has been occured(Data length Mismatch/Checksum Mismatch), please send a packet again.

`0xE1`: Invalid/Bad Request. I cannot process the data.

Additionally, these modes are being used globally to imply a short reply.

`0x99`: OK

Checksum is null when the data length is 0.

If the other client doesn't reply within 10 seconds, Client should resend the request. if the client still doesn't reply within 3 tries, Client should take it as a connection lost.

# Operation codes

## `0x01`: Download

### `0x01`: Download Request

This OP mode gets sent from a client.

Requesting to download a file requires 2 informations: base64 encoded filename and its hash.

Data should be a format of `HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHS-`, where:

H: SHA256 hash of a file.

S: base64-encoded filename.

If everything goes honky dory, the server should reply with 0x12.

### `0x11`: 

This OP mode gets sent from a server.

This packet

Each packets can contain

`IIIID-`
