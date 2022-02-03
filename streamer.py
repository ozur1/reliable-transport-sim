# do not import anything else from loss_socket besides LossyUDP
from lossy_socket import LossyUDP
# do not import anything else from socket except INADDR_ANY
from socket import INADDR_ANY
import struct


class Streamer:
    def __init__(self, dst_ip, dst_port,
                 src_ip=INADDR_ANY, src_port=0):
        """Default values listen on all network interfaces, chooses a random source port,
           and does not introduce any simulated packet loss."""
        self.socket = LossyUDP()
        self.socket.bind((src_ip, src_port))
        self.dst_ip = dst_ip
        self.dst_port = dst_port

    def send(self, data_bytes: bytes) -> None:
        """Note that data_bytes can be larger than one packet."""
        chunks = []
        print('LENGTH BYTES: ' + str(len(data_bytes)))
        seq_num = 0
        # for b in data_bytes:
        #     value = (seq_num, b)
        #     arg = 'I ' + str(len(b)) + 's'
        #     s = struct.Struct(arg)
        #     b = s.pack(*value)
        #     seq_num += 1

        while len(data_bytes) > 0:
            if len(data_bytes) > 1472:
                chunks.append(data_bytes[:1472])
                data_bytes = data_bytes[1472:]
            else:
                chunks.append(data_bytes)
                data_bytes = []

        sequenced_chunks = []
        seq_num = 0

        for c in chunks:
            value = (seq_num, c)
            arg = 'I ' + str(len(c)) + 's'
            s = struct.Struct(arg)
            sequenced_chunks.append(s.pack(*value))
            seq_num += 1

        for c in sequenced_chunks:
            # print('SENDING: ' + str(c))
            self.socket.sendto(c, (self.dst_ip, self.dst_port))

    def recv(self) -> bytes:
        """Blocks (waits) if no data is ready to be read from the connection."""

        data, addr = self.socket.recvfrom()
        # print('RECEIVING: ' + str(data))
        # for i in range(len(data)):
        #     print(data[i])
        arg = 'I ' + str(len(data) - 4) + 's'
        data = struct.unpack(arg, data)
        seq_number = data[0]
        # print('SEQ NUM: ' + str(seq_number))
        data = data[1]
        # print('DATA: ' + str(data))

        recv_base = 0

        # For now, I'll just pass the full UDP payload to the app
        return data

    def close(self) -> None:
        """Cleans up. It should block (wait) until the Streamer is done with all
           the necessary ACKs and retransmissions"""
        # your code goes here, especially after you add ACKs and retransmissions.
        pass
