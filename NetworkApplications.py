#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import argparse
import socket
import os
import sys
import struct
import time
import random
import traceback # useful for exception handling
import threading

def setupArgumentParser() -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            description='A collection of Network Applications developed for SCC.203.')
        parser.set_defaults(func=ICMPPing, hostname='lancaster.ac.uk')
        subparsers = parser.add_subparsers(help='sub-command help')
        
        parser_p = subparsers.add_parser('ping', aliases=['p'], help='run ping')
        parser_p.set_defaults(timeout=2, count=10)
        parser_p.add_argument('hostname', type=str, help='host to ping towards')
        parser_p.add_argument('--count', '-c', nargs='?', type=int,
                              help='number of times to ping the host before stopping')
        parser_p.add_argument('--timeout', '-t', nargs='?',
                              type=int,
                              help='maximum timeout before considering request lost')
        parser_p.set_defaults(func=ICMPPing)

        parser_t = subparsers.add_parser('traceroute', aliases=['t'],
                                         help='run traceroute')
        parser_t.set_defaults(timeout=2, protocol='icmp')
        parser_t.add_argument('hostname', type=str, help='host to traceroute towards')
        parser_t.add_argument('--timeout', '-t', nargs='?', type=int,
                              help='maximum timeout before considering request lost')
        parser_t.add_argument('--protocol', '-p', nargs='?', type=str,
                              help='protocol to send request with (UDP/ICMP)')
        parser_t.set_defaults(func=Traceroute)
        
        parser_w = subparsers.add_parser('web', aliases=['w'], help='run web server')
        parser_w.set_defaults(port=8080)
        parser_w.add_argument('--port', '-p', type=int, nargs='?',
                              help='port number to start web server listening on')
        parser_w.set_defaults(func=WebServer)

        parser_x = subparsers.add_parser('proxy', aliases=['x'], help='run proxy')
        parser_x.set_defaults(port=8000)
        parser_x.add_argument('--port', '-p', type=int, nargs='?',
                              help='port number to start web server listening on')
        parser_x.set_defaults(func=Proxy)

        args = parser.parse_args()
        return args


class NetworkApplication:

    def checksum(self, dataToChecksum: bytes) -> int:
        csum = 0
        countTo = (len(dataToChecksum) // 2) * 2
        count = 0

        while count < countTo:
            thisVal = dataToChecksum[count+1] * 256 + dataToChecksum[count]
            csum = csum + thisVal
            csum = csum & 0xffffffff
            count = count + 2

        if countTo < len(dataToChecksum):
            csum = csum + dataToChecksum[len(dataToChecksum) - 1]
            csum = csum & 0xffffffff

        csum = (csum >> 16) + (csum & 0xffff)
        csum = csum + (csum >> 16)
        answer = ~csum
        answer = answer & 0xffff
        answer = answer >> 8 | (answer << 8 & 0xff00)

        answer = socket.htons(answer)

        return answer

    def printOneResult(self, destinationAddress: str, packetLength: int, time: float, seq: int, ttl: int, destinationHostname=''):
        if destinationHostname:
            print("%d bytes from %s (%s): icmp_seq=%d ttl=%d time=%.3f ms" % (packetLength, destinationHostname, destinationAddress, seq, ttl, time))
        else:
            print("%d bytes from %s: icmp_seq=%d ttl=%d time=%.3f ms" % (packetLength, destinationAddress, seq, ttl, time))

    def printAdditionalDetails(self, packetLoss=0.0, minimumDelay=0.0, averageDelay=0.0, maximumDelay=0.0):
        print("%.2f%% packet loss" % (packetLoss))
        if minimumDelay > 0 and averageDelay > 0 and maximumDelay > 0:
            print("rtt min/avg/max = %.2f/%.2f/%.2f ms" % (minimumDelay, averageDelay, maximumDelay))

    def printOneTraceRouteIteration(self, ttl: int, destinationAddress: str, measurements: list, destinationHostname=''):
        latencies = ''
        noResponse = True
        for rtt in measurements:
            if rtt is not None:
                latencies += str(round(rtt, 3))
                latencies += ' ms  '
                noResponse = False
            else:
                latencies += '* ' 

        if noResponse is False:
            print("%d %s (%s) %s" % (ttl, destinationHostname, destinationAddress, latencies))
        else:
            print("%d %s" % (ttl, latencies))

class ICMPPing(NetworkApplication):

    def receiveOnePing(self, icmpSocket, destinationAddress, ID, timeout):
        try:
        # 1. Wait for the socket to receive a reply
            packet = icmpSocket.recv(1024)
            timeRecieved = time.time()
        except timeout:
            print("TIMEOUT\n")
        # 2. If reply received, record time of receipt, otherwise, handle timeout
        
        # 3. Unpack the imcp and ip headers for useful information, including Identifier, TTL, sequence number 
        icmpHeader = packet[20:28]
        type, code, checksum, identifier, seqNumber = struct.unpack('BBHHH', packet[20:28])

        packetSize = len(packet)
        ttl = packet[8]

        # 5. Check that the Identifier (ID) matches between the request and reply
        if identifier == ID:
            # 6. Return time of receipt, TTL, packetSize, sequence number
            return timeRecieved, ttl, packetSize, seqNumber
            
        
        pass

    def sendOnePing(self, icmpSocket, destinationAddress, ID, seq_num):
        type = 8 #type number 8 is used for echo requests
        code = 0 #code number 0 is used for echo requests
        checksumVar = 0 #temporary variable before doing the actual checksum algorithim

        unusedID = 10 #temporary
        unusedSequenceNumber= 132234 #temporary

        # 1. Build ICMP header
        icmpHeader = struct.pack('BBHHH', type,code,checksumVar, ID,seq_num)

        # 2. Checksum ICMP packet using given function
        actualChecksum = self.checksum(self, icmpHeader)
        
        # 3. Insert checksum into packet
        icmpHeaderAfterChecksum = struct.pack('BBHHH', type,code, actualChecksum, ID,seq_num)
        
        # 4. Send packet using socket
        icmpSocket.sendto(icmpHeaderAfterChecksum, (destinationAddress,1))

        # 5. Return time of sending
        return time.time()


        pass

    def doOnePing(self, destinationAddress, packetID, seq_num, timeout):

        # 1. Create ICMP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

        # 2. Call sendOnePing function
        timeSneding = ICMPPing.sendOnePing(ICMPPing, s, destinationAddress, packetID, seq_num) #this returns time of sending
        
        
        # 3. Call receiveOnePing function
        recieving = ICMPPing.receiveOnePing(ICMPPing, s, destinationAddress, packetID, timeout) #this returns time of recieving
        # print(time_received, ttl, packetSize, seqNumber)

        # 4. Close ICMP socket
        s.close()

        # 5. Print out the delay (and other relevant details) using the printOneResult method, below is just an example.
        if recieving is not None:
            time_received, ttl, packetSize, seqNumber = recieving
            timeTaken = (time_received - timeSneding) * 1000  #done to get timetaken in milliseconds
            self.printOneResult(destinationAddress, packetSize, timeTaken, seqNumber, ttl)
        else:
            print("ERROR: nothing is recieved.")
        pass

        

    def __init__(self, args):
        print('Ping to: %s...' % (args.hostname))
        # 1. Look up hostname, resolving it to an IP address
        destinationAddress = socket.gethostbyname(args.hostname)

        # 2. Repeat below args.count times
        for seq_num in range(args.count):
            # 3. Call doOnePing function, approximately every second
            self.doOnePing(destinationAddress, 1, seq_num, args.timeout)
            time.sleep(1)
        
class Traceroute(NetworkApplication):
    def sendICMP(self, icmpSocket, destinationAddress):
        type = 8 #type number 8 is used for echo requests
        code = 0 #code number 0 is used for echo requests
        checksumVar = 0 #temporary variable before doing the actual checksum algorithim

        unusedID = 1 #temporary
        unusedSequenceNumber= 1 #temporary

        # 1. Build ICMP header
        icmpHeader = struct.pack('!BBHHH', type,code,checksumVar, unusedID,unusedSequenceNumber)

        # 2. Checksum ICMP packet using given function
        actualChecksum = self.checksum(self, icmpHeader)
        
        # 3. Insert checksum into packet
        icmpHeaderAfterChecksum = struct.pack('!BBHHH', type,code, actualChecksum, unusedID,unusedSequenceNumber)
        
        # 4. Send packet using socket
        icmpSocket.sendto(icmpHeaderAfterChecksum, (destinationAddress,8000))
    
    def tracerouteFunction(self, protocol, ttl, destinationAddress, timeout):
        identifier = 1
        seqNum = 1
        
        if protocol == 'icmp':
            icmpSocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            icmpSocket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
            icmpSocket.settimeout(timeout)

            Traceroute.sendICMP(Traceroute, icmpSocket, destinationAddress)

            try:
                recieving, address = icmpSocket.recvfrom(1024)
                type, code, checksum, identifier, seqNumber = struct.unpack('BBHHH', recieving[20:28])
                packetSize  = len(recieving)
                return address[0], type, code, packetSize, seqNumber
                
            except socket.timeout:
                #print("TIMEOUT\n")
                return '*', -1, -1, 1, 1
            finally:
                icmpSocket.close()

        elif protocol == 'udp':
            icmpSocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            udpSocket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
            icmpSocket.settimeout(timeout)
 
            udpSocket.sendto(b'', (destinationAddress, 33434))

            try:
                recieving, address = icmpSocket.recvfrom(1024)
                type, code, checksum, identifier, seqNumber = struct.unpack('BBHHH', recieving[20:28])
                packetSize  = len(recieving)
                return address[0], type, code, packetSize, seqNumber
            except socket.timeout:
                return '*', -1, -1, 1, 1
            finally:
                udpSocket.close()
        else:
            print("ERROR: Protocol not detected")
            

    def doTraceroute(self, protocol, destinationAddress, timeout):
        maxHops = 30
        

        for ttl in range(1, maxHops+1):
            address, type, code, packetSize, seqNum = self.tracerouteFunction(protocol, ttl, destinationAddress, timeout)

            measurementsList = []
            for i in range(3):
                startTime = time.time()
                self.tracerouteFunction(protocol, ttl, destinationAddress, timeout)
                endTime = time.time()
                roundTime = (endTime - startTime) * 1000
                measurementsList.append(roundTime) 

            if address == '*':
                print (ttl, "* * *")
            else:
                try:                    
                    hostname = socket.gethostbyaddr(address)[0]

                except socket.herror:
                    hostname = address

                finally:    
                    try:
                        self.printOneTraceRouteIteration(ttl, address, measurementsList, hostname)
                    except socket.timeout:
                        print("TIMED OUT - ERROR")
                        break
                
                if address == destinationAddress:
                    break

  
    def __init__(self, args):
        print('Traceroute to: %s...' % (args.hostname))
        destinationAddress = socket.gethostbyname(args.hostname)
        self.doTraceroute(args.protocol, destinationAddress, args.timeout)

class WebServer(NetworkApplication):

    def handleRequest(self, tcpSocket):
        # 1. Receive request message from the client on connection socket
        requestMessage = tcpSocket.recv(4096).decode()
        
        # 2. Extract the path of the requested object from the message (second part of the HTTP header)
        filePath = requestMessage.split()[1]

        if filePath == '/': 
            filePath = os.path.join(os.getcwd(), 'index.html')
        else:
            filePath = os.path.join(os.getcwd(), filePath[1:])  # Skip the leading '/' in the path

        # 3. Read the corresponding file from disk
        try:
            
            file = open(filePath, 'r')
            fileContentBuffer = file.read()
            status = "200 OK"

        except FileNotFoundError:
            fileContentBuffer = "<h1>404 NOT FOUND</h1>"
            status = "404 Not Found"

        
        # 5. Send the correct HTTP response error
        HTTPresponse = "HTTP/1.1 " + status + "\nContent-Length: " + str(len(fileContentBuffer)) + "\n\n" + fileContentBuffer
    
        # 6. Send the content of the file to the socket
        tcpSocket.send(HTTPresponse.encode())

        # 7. Close the connection socket
        tcpSocket.shutdown()
        tcpSocket.close()
        pass

    def __init__(self, args):
        true = True
        print('Web Server starting on port: %i...' % (args.port))
        # 1. Create server socket
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 2. Bind the server socket to server address and server port
        serverSocket.bind(('127.0.0.1', args.port))

        # 3. Continuously listen for connections to server socket
        serverSocket.listen(1)

        # 4. When a connection is accepted, call handleRequest function, passing new connection socket
        while true:
            connectionSocket, accepting = serverSocket.accept()
            self.handleRequest(connectionSocket)
        # 5. Close server socket
        serverSocket.close()


class Proxy(NetworkApplication):

    def handleRequest(self, tcpSocket, cache):
        
        self.cacheDirectory = "cache" 
        self.cacheFile = os.path.join(self.cacheDirectory, 'cache.txt')
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        request = tcpSocket.recv(4096).decode()
        filePath = request.split()[1]
        host = request.split()[4]

        if ':' in host:
            hostName, port = host.split(':')
        else:
            hostName = host
            port = 80

        clientSocket.connect((hostName, port))

        #Checks if the cache folder and file are already created, if yes then it is read
        if os.path.exists(self.cacheDirectory):
            file = open(self.cacheFile, 'r')
            responseCaching = file.read()
            tcpSocket.send(responseCaching.encode())
        
        #Checks if cache is stored in the dictionary, if yes then it is loaded
        if  filePath in cache.keys():
            responseCaching = self.cache[filePath]
            tcpSocket.send(responseCaching)

        #else, cache not found in disk or memory
        else:
            clientSocket.sendall(request.encode())
            serverResponse = b""
            while True:
                data = clientSocket.recv(4096)
                if not data:
                    break
                serverResponse += data

            cache[filePath] = serverResponse #caching response in memory

            #the following code creates a text file in a folder and stores the data.
            if not os.path.exists(self.cacheDirectory): 
                os.makedirs(self.cacheDirectory)

            file = open(self.cacheFile, 'w')
            file.write(serverResponse.decode('utf-8'))
            
            tcpSocket.send(serverResponse)

        #clientSocket.shutdown()
        clientSocket.close()
        tcpSocket.close()

    def __init__(self, args):
        self.cache = {}
        
        self.proxyPort = args.port
        print('Web Proxy starting on port: %i...' % (self.proxyPort))

        #creating server socket
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #binding server socket to the correct port and address
        serverSocket.bind(('127.0.0.1', self.proxyPort))


        true = True
        
        #Listening to for connections
        while true:
            serverSocket.listen(1)
            connectionSocket, address = serverSocket.accept()
            self.handleRequest(connectionSocket, self.cache)
        
        serverSocket.close()
    

if __name__ == "__main__":
    args = setupArgumentParser()
    args.func(args)
