__author__ = 'Yossi'
# 2.6  client server October 2021

import socket, sys,traceback
import argparse
from tcp_with_size import send_with_size, recv_by_size, logtcp



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


def main(host='127.0.0.1', port=1233):
    """
    main client - handle socket and main loop
    """
    connected = False

    sock= socket.socket()
    try:
        sock.connect((host,port))
        print (f'Connect succeeded {host}:{port}')
        connected = True
    except:
        print(f'Error while trying to connect.  Check ip or port -- {host}:{port}')

    while connected:
        from_user = menu()
        to_send = protocol_build_request(from_user)
        if to_send =='':
            print("Selection error try again")
            continue
        try :
            # send_data(sock,to_send.encode())
            send_with_size(sock, to_send.encode())
            logtcp("Client", 'sent', to_send.encode())

            length_data, payload = recv_by_size(sock)
            logtcp("Client", 'recieved', length_data + payload)
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
    logtcp("Client", 'sent', all_requests)
    

    # Now receive replies
    while True:
        try:
            length_data, payload = recv_by_size(sock)
            logtcp("Client", 'recieved', length_data + payload)
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

def send_single_message():
    if not args.send:
        print('Send mode requires --send message')
        sys.exit(2)
    sock= socket.socket()
    try:
        sock.connect((args.host,args.port))
        print (f'Connect succeeded {args.host}:{args.port}')
    except:
        print(f'Error while trying to connect.  Check ip or port -- {args.host}:{args.port}')
        sys.exit(1)
    try:
        send_with_size(sock, args.send.encode())
        logtcp("Client", 'sent', args.send.encode())
        length_data, payload = recv_by_size(sock)
        logtcp("Client", 'recieved', length_data + payload)
        handle_reply(payload)
    except Exception as err:
        print(f'Error during send: {err}')
    sock.close()

def _parse_args():
    p = argparse.ArgumentParser(description='Simple TCP client')
    p.add_argument('-H', '--host', default='127.0.0.1', help='Server host (default: 127.0.0.1)')
    p.add_argument('-p', '--port', type=int, default=1233, help='Server port (default: 1233)')
    p.add_argument('-m', '--mode', choices=['interactive','test','send'], default='interactive', help='Mode: interactive, test (multiple messages), send (single message)')
    p.add_argument('-s', '--send', help='Message to send in send mode (e.g. TIME, RAND, WHOU, EXIT, or custom)')
    return p.parse_args()


if __name__ == '__main__':
    args = _parse_args()
    if args.mode == 'test':
        test_multiple_messages()
    elif args.mode == 'send':
        send_single_message()
    else:
        # interactive mode
        main(args.host, args.port)
