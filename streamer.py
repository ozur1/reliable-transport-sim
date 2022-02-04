# do not import anything else from loss_socket besides LossyUDP
from lossy_socket import LossyUDP
# do not import anything else from socket except INADDR_ANY
from socket import INADDR_ANY
import struct
from concurrent.futures.thread import ThreadPoolExecutor


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
        self.recv_buffer = {}
        self.ACK = False
        self.ACK_log = {}
        self.closed = False
        executor = ThreadPoolExecutor(max_workers=1)
        executor.submit(self.listener)

    def listener(self):
        while not self.closed:
            try:
                data, addr = self.socket.recvfrom()
                # store the data in the receive buffer
                arg = 'I ' + '? ' + str(len(data) - 5) + 's'
                data = struct.unpack(arg, data)
                self.recv_buffer[data[0]] = data[2]
                self.ACK_log[data[0]] = data[1]
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

        sequenced_chunks = []
        for c in chunks:
            value = (self.seq_num, self.ACK, c)
            arg = 'I ' + '? ' + str(len(c)) + 's'
            s = struct.Struct(arg)
            sequenced_chunks.append(s.pack(*value))
            self.seq_num += 1

        for c in sequenced_chunks:
            self.socket.sendto(c, (self.dst_ip, self.dst_port))

    def recv(self) -> bytes:
        """Blocks (waits) if no data is ready to be read from the connection."""
        output = b''

        while self.expected_seq_num in self.recv_buffer:
            output += self.recv_buffer[self.expected_seq_num]
            del self.recv_buffer[self.expected_seq_num]
            self.expected_seq_num += 1

        return output

    def close(self) -> None:
        """Cleans up. It should block (wait) until the Streamer is done with all
           the necessary ACKs and retransmissions"""
        # your code goes here, especially after you add ACKs and retransmissions.
        self.closed = True
        self.socket.stoprecv()
