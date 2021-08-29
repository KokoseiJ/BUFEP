# Memo

## Broadcasting station

Servers should contact Broadcasting station first, with requested datas. This includes the name of the server, supported protocol version, etc

Broadcasting station then should act as a searching server of some sort. When the client requests to search the file, The station should contact each servers to check if the file is present in each server. then the station should send the list of servers that have the file. 

If the client wants to contact to a server, Broadcasting station then should act as a public node to perform UDP hole punching.

We could also try to connect each broadcasting stations- to further expand the network, or just make each servers to be able to communicate with eachother.

## Server

Server should be able to check if the file presents for clients.

Maybe packet encryption?

