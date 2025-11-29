__author__ = 'Yossi'
# 2.6  client server October 2021

import socket, sys,traceback
import argparse
from tcp_by_size import send_with_size, recv_by_size

dest_path_global = ''  # global variable to hold destination path for download

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
    print('\n  6. list directory')
    print('\n  7. delete file')
    print('\n  8. copy file')
    print('\n  9. download file')
    return input('Input 1 - 9 > ' )


def protocol_build_request(from_user):
    """
    build the request according to user selection and protocol
    return: string - msg code
    """
    global dest_path_global
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
    elif from_user == '6':
        path = input("enter directory path to list> ")
        return 'LIST~' + path
    elif from_user == '7':
        path = input("enter file path to delete> ")
        return 'DELF~' + path
    elif from_user == '8':
        src = input("enter source file path to copy> ")
        dest = input("enter destination file path> ")
        return 'COPY~' + src + '~' + dest
    elif from_user == '9':
        src_path = input("enter file path to download> ")
        dest_path_global = input("enter destination path to save the file> ")
        return 'DWNL~' + src_path
    else:
        return ''


def protocol_parse_reply(sock, reply):
    """
    parse the server reply and prepare it to user
    return: answer from server string
    """
    global dest_path_global
    to_show = 'Invalid reply from server'
    try:
        if reply.startswith(b'DWNR'):
            # DWNR~<total_chunks>~<chunk_index>~<file_data>
            fields = reply.split(b'~', 3)
            total_chunks = int(fields[1])
            chunk_index = int(fields[2])
            
            print('\n==========================================================')
            while chunk_index <= total_chunks:
                file_data = fields[3]  # already bytes
                # file_data = fields[3].encode('latin1')  # to get original bytes
                to_show = f'Receiving chunk {chunk_index} of {total_chunks}'
                with open(dest_path_global, 'ab') as f:
                    f.write(file_data)
                
                print (f'  SERVER Reply: {to_show}   |')
                print(  '==========================================================')
                
                if chunk_index == total_chunks:
                    break
                # receive next chunk
                reply = recv_by_size(sock, name="Client")
                fields = reply.split(b'~', 3)
                chunk_index = int(fields[2])
            to_show = f'File download completed successfully to: {dest_path_global}'
            
            # C:\Users\barts\OneDrive\Documents\package.txt
            # C:\Users\barts\OneDrive\Documents\clones\remote-technician\package.txt
        else: 
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
            elif code == 'LISR':
                to_show = 'Directory listing: \n' + '\n'.join(fields[1].split('|'))
            elif code == 'DELR':
                to_show = 'Delete file result: ' + fields[1]
            elif code == 'COPR':
                to_show = 'Copy file result: ' + fields[1]
            elif code == "DONE":
                to_show = fields[1]
    except Exception as e:
        print (f'Server replay bad format: {e}')
    return to_show


def handle_reply(sock, reply):
    """
    get the tcp upcoming message and show reply information
    return: void
    """
    to_show = protocol_parse_reply(sock, reply)
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
            handle_reply(sock, payload)

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
