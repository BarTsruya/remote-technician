import socket

def logtcp(name, dir, byte_data):
	"""
	log direction, tid and all TCP byte array data
	return: void
	"""
	if dir == 'sent':
		print(f'{name} LOG: Sent >>> {byte_data}')
	else:
		print(f'{name} LOG: Recieved <<< {byte_data}')


def send_with_size(sock: socket.socket, bdata: bytes):
    """
    Send data with 8-byte length prefix.
    Format: b'00000012~<data>'
    """
    length_prefix = str(len(bdata)).zfill(8).encode() + b'~'
    bytearray_data = length_prefix + bdata
    sock.sendall(bytearray_data)

def recv_by_size(sock: socket.socket) -> bytes:
    """
    Receive data using length prefix.
    1. Read 8 bytes length prefix + 1 byte '~'
    2. Read exactly the payload length
    """
    # Step 1: read length prefix
    length_data = b''
    while len(length_data) < 9:  # 8 bytes length + 1 for '~'
        chunk = sock.recv(9 - len(length_data))
        if not chunk:
            raise ConnectionError("Socket closed while reading length")
        length_data += chunk

    if length_data[8:9] != b'~':
        raise ValueError("Invalid message format, missing '~' separator")

    payload_len = int(length_data[:8].decode())
    
    # Step 2: read payload
    payload = b''
    while len(payload) < payload_len:
        chunk = sock.recv(payload_len - len(payload))
        if not chunk:
            raise ConnectionError("Socket closed while reading payload")
        payload += chunk

    return length_data, payload
