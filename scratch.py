import struct
import random

chunks = [b'0', b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9', b'10', b'11', b'12', b'13', b'14', b'15', b'16', b'17']
seq_num = 0


for c in chunks:
    ACK = bool(random.getrandbits(1))
    value = (seq_num, ACK, c)
    arg = 'I ' + '? ' + str(len(c)) + 's'
    s = struct.Struct(arg)
    packed_data = s.pack(*value)
    seq_num += 1

    print('Original values:', value)
    print('Format string  :', s.format)
    print('Uses           :', s.size, 'bytes')
    print('Packed Value   :', packed_data)
    print('LENGTH: ' + str(len(packed_data)))
    for i in range(len(packed_data)):
        print(packed_data[i])
    unpacked_data = s.unpack(packed_data)
    print('Unpacked Values:', unpacked_data)
    print("")


""" 
HOST 1                                  HOST 2
ACK_log = {}                            ACK_log = {}
                                        seq_num not in ACK_log, send false
                                        send(0, False, b'0')
                                        seq_num not in ACK_log, add false
                                        ACK_log = {0: False}
receive(0, False, b'0')
sqe_num not in ACK_log, add false
ACK_log = {0: False}

seq_num in ACK_log, send true
send(0, True, b'0')
seq_num in ACK_log, flip true
ACK_log = {0: True}

                                        receive(0, True, b'0')
                                        seq_num is in ACK_log, flip true
                                        ACK_log = {0: True}
                                        


"""