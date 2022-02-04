import struct
import heapq

b = b'\x01\x02\x03\x04\x05\x06\x07\x08'
b = bytearray(b)

# chunks = [b'0', b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9', b'10', b'11', b'12', b'13', b'14', b'15', b'16', b'17']
# seq_num = 0
#
# for c in chunks:
#     value = (seq_num, c)
#     print(len(c))
#     arg = 'I ' + str(len(c)) + 's'
#     s = struct.Struct(arg)
#     packed_data = s.pack(*value)
#     seq_num += 1
#
#     print('Original values:', value)
#     print('Format string  :', s.format)
#     print('Uses           :', s.size, 'bytes')
#     print('Packed Value   :', packed_data)
#     print('LENGTH: ' + str(len(packed_data)))
#     for i in range(len(packed_data)):
#         print(packed_data[i])
#     unpacked_data = s.unpack(packed_data)
#     print('Unpacked Values:', unpacked_data)
#     print("")


'''
buffer = {}
expected =  0
output = ''

0 arrives
buffer = {0}
expected in buffer
output = 0
buffer = {}
expected = 1
expected not in buffer
return 0

2 arrives
buffer = {2}
expected not in buffer
return ''

3 arrives
buffer = {2, 3}
expected not in buffer
return ''

5 arrives
buffer = {2, 3, 5}
expected not in buffer
return ''

6 arrives
buffer = {2, 3, 5, 6}
expected not in buffer
return ''

1 arrives
buffer = {2, 3, 5, 6, 1}
expected in buffer
output = 1
buffer = {2, 3, 5, 6}
expected = 2
expected in buffer
output = 1, 2
buffer = {3, 5, 6}
expected = 3
expected in buffer
output = 1, 2, 3
buffer = {5, 6}
expected = 4
expected not in buffer
return 1, 2, 3

4 arrives
buffer = {5, 6, 4}
expected in buffer
output = 4
buffer = {5, 6}
expected = 5
expected in buffer
output = 4, 5
buffer = {6}
expected = 6
expected in buffer
output = 4, 5, 6
buffer = {}
expected = 7
expected not in buffer
return 4, 5, 6

'''