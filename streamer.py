# do not import anything else from loss_socket besides LossyUDP
from lossy_socket import LossyUDP
# do not import anything else from socket except INADDR_ANY
from socket import INADDR_ANY
import struct
from concurrent.futures.thread import ThreadPoolExecutor
import time
import hashlib


class Streamer:
    #implement 1 single absolute timer
    #Change ACK_log to be a List
    #input timeout value
    def __init__(self, dst_ip, dst_port,
                 src_ip=INADDR_ANY, src_port=0):
        """Default values listen on all network interfaces, chooses a random source port,
           and does not introduce any simulated packet loss."""
        self.socket = LossyUDP()
        self.socket.bind((src_ip, src_port))
        self.dst_ip = dst_ip
        self.dst_port = dst_port
        self.seq_num = 0
        self.expected_seq_num = 0
        self.recv_buffer = {}
        self.ACK_log = {}
        self.received_FIN = False
        self.received_FINACK = False
        self.closed = False
        executor = ThreadPoolExecutor(max_workers=1)
        executor.submit(self.listener)

    '''
    Packet Format: (seq_num, ACK, FIN, checksum payload)
    '''
    #remove ack from ack_log once received
    #clear ack_log and set sequence number to ack_log[0][0] if timer - ack_log[0][1] > timeout
    def listener(self):
        while not self.closed:
            try:
                data, addr = self.socket.recvfrom()
                arg = 'I ' + '? ' + '? ' + '16s' + str(len(data) - 22) + 's'
                data = struct.unpack(arg, data)
                '''
                data[0] = seq_num
                data[1] = ACK bit
                data[2] = FIN bit
                data[3] = checksum
                data[4] = Payload
                '''
                newHash = self.hashify(data[0], data[1], data[2], data[4])
                if newHash != data[3]:
                    continue
                elif data[1] and not data[2]:
                    self.ACK_log[data[0]] = True
                elif data[2] and not data[1]:
                    self.received_FIN = True
                    sendHash = self.hashify(data[0], True, True, b'')
                    value = (data[0], True, True, sendHash, b'')
                    s = struct.Struct('I ? ? 16s 0s')
                    response = s.pack(*value)
                    self.socket.sendto(response, (self.dst_ip, self.dst_port))
                elif data[1] and data[2]:
                    self.received_FINACK = True
                else:  # no ACK or FIN, just data
                    sendHash = self.hashify(data[0], True, False, b'')
                    value = (data[0], True, False, sendHash,  b'')
                    s = struct.Struct('I ? ? 16s 0s')
                    response = s.pack(*value)
                    self.socket.sendto(response, (self.dst_ip, self.dst_port))
                    self.recv_buffer[data[0]] = (data[1], data[2], data[4])
            except Exception as e:
                print("listener died!")
                print(e)
    
    #Change send to continue sending incremented packets regardless of recieving an ACK
    #Change second loop to a while loop, accessing the chunks list via sequence number
    def send(self, data_bytes: bytes) -> None:
        """Note that data_bytes can be larger than one packet."""
        chunks = []
        while len(data_bytes) > 0:
            if len(data_bytes) > 1400:
                chunks.append(data_bytes[:1400])
                data_bytes = data_bytes[1400:]
            else:
                chunks.append(data_bytes)
                data_bytes = []

        for c in chunks:
            outHash = self.hashify(self.seq_num, False, False, c)
            value = (self.seq_num, False, False, outHash, c)
            arg = 'I ' + '? ' + '? ' + '16s' + str(len(c)) + 's'
            s = struct.Struct(arg)
            packet = s.pack(*value)

            self.ACK_log[self.seq_num] = False

            while not self.ACK_log[self.seq_num]:
                self.socket.sendto(packet, (self.dst_ip, self.dst_port))
                time.sleep(0.25)

            self.seq_num += 1

    def recv(self) -> bytes:
        """Blocks (waits) if no data is ready to be read from the connection."""
        output = b''

        while self.expected_seq_num in self.recv_buffer:
            payload = self.recv_buffer[self.expected_seq_num][2]
            output += payload
            del self.recv_buffer[self.expected_seq_num]
            self.expected_seq_num += 1

        return output

    def close(self) -> None:
        """Cleans up. It should block (wait) until the Streamer is done with all
           the necessary ACKs and retransmissions"""
        # your code goes here, especially after you add ACKs and retransmissions.

        # Part 5 code will go here

        # Send FIN Packet
        outHash = self.hashify(self.seq_num, False, True , b'')
        value = (self.seq_num, False, True, outHash , b'')
        arg = 'I ? ? 16s 0s'
        s = struct.Struct(arg)
        packet = s.pack(*value)

        while not self.received_FIN or not self.received_FINACK:
            self.socket.sendto(packet, (self.dst_ip, self.dst_port))
            time.sleep(0.25)

        time.sleep(2)

        self.closed = True
        self.socket.stoprecv()
    
    def hashify(self, a1, a2, a3, a4):
        m = hashlib.md5()
        temparg = 'I ' + '? ' + '? ' + str(len(a4)) + 's'
        tempV = (a1, a2, a3, a4)
        
        m.update(struct.pack(temparg, *tempV))
        return m.digest()
