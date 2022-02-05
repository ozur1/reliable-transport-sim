# do not import anything else from loss_socket besides LossyUDP
from lossy_socket import LossyUDP
# do not import anything else from socket except INADDR_ANY
from socket import INADDR_ANY
import struct
from concurrent.futures.thread import ThreadPoolExecutor
import time


class Streamer:
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
        self.expected_ack_num = 0
        self.recv_buffer = {}
        self.ACK_log = {}
        self.closed = False
        executor = ThreadPoolExecutor(max_workers=1)
        executor.submit(self.listener)

    def listener(self):
        while not self.closed:
            try:
                data, addr = self.socket.recvfrom()
                arg = 'I ' + '? ' + str(len(data) - 5) + 's'
                data = struct.unpack(arg, data)
                self.recv_buffer[data[0]] = (data[1], data[2])

                if self.seq_num in self.recv_buffer:
                    if self.recv_buffer[self.seq_num][0]:
                        self.ACK_log[self.seq_num] = True
                        del self.recv_buffer[self.seq_num]

            except Exception as e:
                print("listener died!")
                print(e)

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
            value = (self.seq_num, False, c)
            arg = 'I ' + '? ' + str(len(c)) + 's'
            s = struct.Struct(arg)
            sequenced_c = s.pack(*value)
            self.ACK_log[self.seq_num] = False

            self.socket.sendto(sequenced_c, (self.dst_ip, self.dst_port))
            while not self.ACK_log[self.seq_num]:
                # print("ACK_LOG: " + str(self.ACK_log))
                time.sleep(0.01)

            self.seq_num += 1

    def recv(self) -> bytes:
        """Blocks (waits) if no data is ready to be read from the connection."""
        output = b''


        '''
        seq_num = expected_seq_num
        ACK = self.recv_buffer[self.expected_seq_num][0]
        payload = self.recv_buffer[self.expected_seq_num][1]
        
        if expected_seq_num in recv_buffer
            if ACK = False
                send reply with same seq num, ACK = True, payload = b''
                append to output
                delete from recv buffer
                expected ++
            if ACK = True
                flip ACK log at seq num
                delete from recv buffer
            
        '''

        while self.expected_seq_num in self.recv_buffer:
            ack = self.recv_buffer[self.expected_seq_num][0]
            if ack:
                print("ACK BIT TRUE")
                # self.ACK_log[self.expected_seq_num] = True
                # del self.recv_buffer[self.expected_seq_num]
            else:
                payload = self.recv_buffer[self.expected_seq_num][1]
                output += payload
                del self.recv_buffer[self.expected_seq_num]

                value = (self.expected_seq_num, True, b'')
                s = struct.Struct('I ? 1s')
                response = s.pack(*value)
                self.socket.sendto(response, (self.dst_ip, self.dst_port))

                self.expected_seq_num += 1

        return output

    def close(self) -> None:
        """Cleans up. It should block (wait) until the Streamer is done with all
           the necessary ACKs and retransmissions"""
        # your code goes here, especially after you add ACKs and retransmissions.
        self.closed = True
        self.socket.stoprecv()
