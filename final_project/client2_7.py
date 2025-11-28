__author__ = 'Yossi'
# 2.6  client server October 2021

import socket, sys,traceback
import argparse
from tcp_by_size import send_with_size, recv_by_size



def menu():
    """
    show client menu
    return: string with selection
    """
    print('\n  1. ask for time')
    print('\n  2. ask for random')
    print('\n  3. ask for name')
    print('\n  4. notify exit')
    print('\n  5. execute command')
    return input('Input 1 - 5 > ' )


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
        cmd = input("enter command to execute> ")
        return 'EXEC~' + cmd
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
            to_show = 'Server acknowledged the exit message'
        elif code == 'EXCR':
            to_show = 'Command execution result: ' + fields[1]
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
            send_with_size(sock, to_send, name="Client")

            payload = recv_by_size(sock, name="Client")
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


def _parse_args():
    p = argparse.ArgumentParser(description='Simple TCP client')
    p.add_argument('-H', '--host', default='127.0.0.1', help='Server host (default: 127.0.0.1)')
    p.add_argument('-p', '--port', type=int, default=1233, help='Server port (default: 1233)')
    return p.parse_args()


if __name__ == '__main__':
    args = _parse_args()
    main(args.host, args.port)
