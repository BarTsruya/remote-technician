__author__ = 'Yossi'
# 2.6  client server October 2021

import socket, sys,traceback
from tcp_with_size import send_with_size, recv_by_size

def logtcp(dir, byte_data):
    """
    log direction and all TCP byte array data
    return: void
    """
    if dir == 'sent':
        print(f'C LOG:Sent     >>>{byte_data}')
    else:
        print(f'C LOG:Recieved <<<{byte_data}')


def send_data(sock, bdata):
    """
    send to client byte array data
    will add 8 bytes message length as first field
    e.g. from 'abcd' will send  b'00000004~abcd'
    return: void
    """
    bytearray_data = str(len(bdata)).zfill(8).encode() + b'~' + bdata
    sock.send(bytearray_data)
    logtcp('sent', bytearray_data)


def menu():
    """
    show client menu
    return: string with selection
    """
    print('\n  1. ask for time')
    print('\n  2. ask for random')
    print('\n  3. ask for name')
    print('\n  4. notify exit')
    print('\n  (5. some invalid data for testing)')
    return input('Input 1 - 4 > ' )


def protocol_build_request(from_user):
    """
    build the request according to user selection and protocol
    return: string - msg code
    """
    if from_user == '1':
        return 'TIME'
    elif from_user == '2':
        return 'RAND'
    elif from_user == '3':
        return 'WHOU'
    elif from_user == '4':
        return 'EXIT'
    elif from_user == '5':
        return input("enter free text data to send> ")
    else:
        return ''


def protocol_parse_reply(reply):
    """
    parse the server reply and prepare it to user
    return: answer from server string
    """

    to_show = 'Invalid reply from server'
    try:
        reply = reply.decode()
        if '~' in reply:
            fields = reply.split('~')
        code = reply[:4]
        if code == 'TIMR':
            to_show = 'The Server time is: ' + fields[1]
        elif code == 'RNDR':
            to_show = 'Server draw the number: ' +  fields[1]
        elif code == 'WHOR':
            to_show = 'Server name is: ' +  fields[1]
        elif code == 'ERRR':
            to_show = 'Server return an error: ' + fields[1] + ' ' + fields[2]
        elif code == 'EXTR':
            to_show = 'Server acknowledged the exit message';
    except:
        print ('Server replay bad format')
    return to_show


def handle_reply(reply):
    """
    get the tcp upcoming message and show reply information
    return: void
    """
    to_show = protocol_parse_reply(reply)
    if to_show != '':
        print('\n==========================================================')
        print (f'  SERVER Reply: {to_show}   |')
        print(  '==========================================================')


def main(ip):
    """
    main client - handle socket and main loop
    """
    connected = False

    sock= socket.socket()

    port = 1233
    try:
        sock.connect((ip,port))
        print (f'Connect succeeded {ip}:{port}')
        connected = True
    except:
        print(f'Error while trying to connect.  Check ip or port -- {ip}:{port}')

    while connected:
        from_user = menu()
        to_send = protocol_build_request(from_user)
        if to_send =='':
            print("Selection error try again")
            continue
        try :
            # send_data(sock,to_send.encode())
            send_with_size(sock, to_send.encode())
            # byte_data = sock.recv(1000)   # todo improve it to recv by message size
            payload = recv_by_size(sock)
            handle_reply(payload)

            if from_user == '4':
                print('Will exit ...')
                connected = False
                break
        except socket.error as err:
            print(f'Got socket error: {err}')
            break
        except Exception as err:
            print(f'General error: {err}')
            print(traceback.format_exc())
            break
    print ('Bye')
    sock.close()


def test_multiple_messages():
    """
    test sending multiple messages in a row without waiting for reply
    """
    sock= socket.socket()
    ip = "127.0.0.1"
    port = 1233
    try:
        sock.connect((ip,port))
        print (f'Connect succeeded {ip}:{port}')
    except:
        print(f'Error while trying to connect.  Check ip or port -- {ip}:{port}')
    messages = ['TIME', 'RAND', 'WHOU', 'EXIT']
    all_requests = b''
    for msg in messages:
        bdata = msg.encode()
        length_prefix = str(len(bdata)).zfill(8).encode() + b'~'
        bytearray_data = length_prefix + bdata
        all_requests += bytearray_data
    
    # Send all messages at once
    sock.sendall(all_requests)
    logtcp('sent', all_requests)
    print("")
    

    # bdata1 = messages[0].encode()
    # bdata2 = messages[1].encode()
    # length_prefix1 = str(len(bdata1)).zfill(8).encode() + b'~'
    # bytearray_data1 = length_prefix1 + bdata1
    # length_prefix2 = str(len(bdata2)).zfill(8).encode() + b'~'
    # bytearray_data2 = length_prefix2 + bdata2
    # sock.sendall(bytearray_data1 + bytearray_data2)
    # logtcp('sent', bytearray_data1 + bytearray_data2)
    # print("")
    # Now receive replies
    while True:
        try:
            payload = recv_by_size(sock)
            handle_reply(payload)
            if payload.startswith(b'EXTR'):
                print('Will exit ...')
                break
        except socket.error as err:
            print(f'Got socket error: {err}')
            break
        except Exception as err:
            print(f'General error: {err}')
            print(traceback.format_exc())
            break
    
    print ('Bye')
    sock.close()


if __name__ == '__main__':
    test_multiple_messages()
    # if len(sys.argv) > 1:
    #     main(sys.argv[1])
    # else:
    #     main('127.0.0.1')