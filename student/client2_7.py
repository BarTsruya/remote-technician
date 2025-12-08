__author__ = 'Yossi'
# 2.6  client server October 2021

import socket, sys,traceback


from tcp_by_size import recv_by_size,send_with_size


dest_path = 'null'


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
    print('\n  8. copy file ')
    print('\n  9. take screenshot')
    print('\n  10. to downlode file')
    return input('Input 1 - 11 > ' )


def protocol_build_request(from_user):
    """
    build the request according to user selection and protocol
    return: string - msg code
    """
    global dest_path
    if from_user == '1':
        return 'TIME'
    elif from_user == '2':
        return 'RAND'
    elif from_user == '3':
        return 'WHOU'
    elif from_user == '4':
        return 'EXIT'
    elif from_user == '5':
        cmd=input('enter command: ')
        return f'EXEC|{cmd}'
    elif from_user == '6':
        path=input('enter full or absulot path')
        return f'LIST|{path}'
    elif from_user == '7':
        delfile=input('what file you want to delete')
        return f'DELF|{delfile}'
    elif from_user=='8':
        file_to_copy=input('what file you want to copy')
        dest=input('wher you want to copy it')
        return f'COPY|{file_to_copy}|{dest}'
    elif from_user =='9':
        dest = input ('wher you want to save the screenshot')
        return f'SCRN|{dest}'
    elif from_user =='10':
        src_path=input('file path to downlode')
        dest_path= input('wher to save the file')
        return f'DWNL|{src_path}'
    else:
        return ''


def protocol_parse_reply(reply,sock):
    """
    parse the server reply and prepare it to user
    return: answer from server string
    """

    to_show = 'Invalid reply from server'
    try:
        if reply.startswith(b'DWNR') == True:
            cunter=1
            while True:
                
                fields = reply.split(b'~',3)

                chunk_index=int(fields[1])
                chunk_total=int(fields[2])
                data_info=fields[3]
                with open(dest_path,'ab') as f :
                    f.write(data_info)
                if  chunk_index == chunk_total:
                    break
                reply =recv_by_size(sock)
            to_show = f'recivd all chunks'
            protocol_parse_reply(recv_by_size(sock),sock)
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
                to_show='command execution result ' +fields[1]
            elif code == 'LISR':
                # print (type(fields[1]))     
                files = '\n'.join(fields[1].split('|'))

                to_show = 'directory files : \n' +  files
            elif code == 'DELR':
                to_show = 'delete result ' + fields[1]
            elif code == 'COPR':
                to_show = 'copy result ' + fields[1]
            elif code == 'SCRR':
                to_show = 'screenshot result ' + fields[1]
            elif code == 'DONE':
                to_show = 'downlode result '

    except Exception as e:
        print (f'Server replay bad format  {e}')

    return to_show


def handle_reply(reply,sock):
    """
    get the tcp upcoming message and show reply information
    return: void
    """
    to_show = protocol_parse_reply(reply,sock)
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
            send_with_size(sock,to_send)
            byte_data= recv_by_size(sock)
            handle_reply(byte_data,sock)

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


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main('127.0.0.1')