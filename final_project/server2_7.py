__author__ = 'Yossi'

# 2.6  client server October 2021
import shutil
import socket, random, traceback
import time, threading, os, datetime
from tcp_by_size import send_with_size, recv_by_size

import subprocess
import glob
import pyautogui

all_to_die = False  # global


def check_length(message):
	"""
	check message length
	return: string - error message
	"""
	size = len(message)
	if size < 13:  # 13 is min message size
		return b'ERRR~003~Bad Format message too short'
	if int(message[:8].decode()) !=  size -9:
		return b'ERRR~003~Bad Format, incorrect message length'
	return b''


def get_time():
	"""return local time """
	return datetime.datetime.now().strftime('%H:%M:%S:%f')


def get_random():
	"""return random 1-10 """
	return str(random.randint(1, 10))


def get_server_name():
	"""return server name from os environment """
	return  os.environ['COMPUTERNAME']

def exec_command(command):
	"""
	execute command and return result 
	Examples: notepad(c:\windows\system32\notepad.exe), calc, explorer, cmd, taskmgr
	return: 'succeed' or 'failed' or error message
	"""
	try:
		ret = subprocess.call(command[0])
		return 'succeed' if ret == 0 else 'failed'
	except FileNotFoundError:
		return f"Failed, Command not found: {command[0]}"
	except Exception as e:
		return f"Failed, Error running command: {e}"
	

def list_directory(path):
	try:
		files_list = glob.glob(os.path.join(path, '*'))
		files = [os.path.basename(f) for f in files_list]
		print("files:", files)
		return 'LISR' + '~' + '|'.join(files)
	except FileNotFoundError:
		return f'ERRR~004~File not found: {path}'
	except Exception as e:
		return f'LISR~Failed to list directory: {e}'

def delete_file(path):
	try:
		os.remove(path)
		return 'DELR' + '~' + 'File deleted successfully'
	except FileNotFoundError:
		return f'ERRR~004~File not found: {path}'
	except Exception as e:
		return f'DELR~Failed to delete file: {e}'

def copy_file(src, dest):
	try:
		shutil.copy(src, dest)
		return 'COPR' + '~' + 'File copied successfully'
	except FileNotFoundError:
		return f'ERRR~004~File not found: {src}'
	except Exception as e:
		return f'COPR~Failed to copy file: {e}'

def download_file(sock, src_path):
	try:
		file_size = os.path.getsize(src_path)
		with open(src_path, "rb") as f:
			chunk_size = 1024
			total_chunks = (file_size + chunk_size - 1) // chunk_size
			chunk_index = 1
			while True:
				data = f.read(chunk_size)
				if not data:
					break
				reply = b'DWNR~' + str(total_chunks).encode() + b'~' + str(chunk_index).encode() + b'~' + data
				send_with_size(sock, reply, name=f"Server download")
				chunk_index += 1
		return 'DONE~file downloading finished successfuly'
	except Exception as e:
		error_msg = f'ERRR~004~File not found: {src_path}'
		send_with_size(sock, error_msg.encode(), name=f"Server download")
		return 'DONE~somthing went wrong in file downloading'

def screen_shot(sock, image_path):
	try:
		screenshot = pyautogui.screenshot()
		screenshot.save(image_path)
		time.sleep(10)
		# verify save
		if os.path.isfile(image_path) and os.path.getsize(image_path) > 0:
			screen_shot_reply = 'SCRR' + '~Image saved in ' + image_path + ' on server side'
			send_with_size(sock, screen_shot_reply.encode(), name=f"Server screenshot")
			return download_file(sock, image_path)
		return f'ERRR~005~Failed to take screenshot: Image not saved properly'
	except Exception as e:
		return f'ERRR~005~Failed to take screenshot: {e}'

def protocol_build_reply(sock, request):
	"""
	Application Business Logic
	function despatcher ! for each code will get to some function that handle specific request
	Handle client request and prepare the reply info
	string:return: reply
	Examples:
	rand request: b'0000005|RAND'
	rand reply: b'0000006|RNDR~4'
	exec request: b'0000013|EXEC~dir c:\\'
	exec reply: b'0000006|EXCR~succeed'
	"""
	request_code = request[:4].decode()
	request_feilds = request.decode("utf8").split('~')
	# print("request_feilds:", request_feilds)
	reply = ''
	if request_code == 'TIME':
		reply = 'TIMR' +'~' + get_time()
	elif request_code == 'RAND':
		reply ='RNDR' + '~' + get_random()
	elif request_code == 'WHOU':
		reply ='WHOR' + '~' + get_server_name()
	elif request_code == 'EXIT':
		reply= 'EXTR'
	elif request_code == 'EXEC':
		if len(request_feilds) < 2:
			reply = 'ERRR~003~Bad Format, EXEC needs command'
		else:
			reply = 'EXCR' + '~' + exec_command(request_feilds[1])
	elif request_code == 'LIST':
		if len(request_feilds) < 2: # todo with liron
			reply = 'ERRR~003~Bad Format, LIST needs directory path'
		else:
			reply = list_directory(request_feilds[1])
	elif request_code == 'DELF':
		if len(request_feilds) < 2:
			reply = 'ERRR~003~Bad Format, DELF needs file path'
		else:
			reply = delete_file(request_feilds[1])
	elif request_code == 'COPY':
		if len(request_feilds) < 3:
			reply = 'ERRR~003~Bad Format, COPY needs source and destination paths'
		else:
			reply = copy_file(request_feilds[1], request_feilds[2])
	elif request_code == 'DWNL':
		if len(request_feilds) < 2:
			reply = 'ERRR~003~Bad Format, DWNL needs file path'
		else:
			reply = download_file(sock, request_feilds[1])
	elif request_code == 'SCRN':
		if len(request_feilds) < 2:
			reply = 'ERRR~003~Bad Format, SCRN needs image path'
		else:
			reply = screen_shot(sock, request_feilds[1])
	else:
		reply = 'ERRR~002~code not supported'
	return reply.encode()


def handle_request(sock, request):
    """
    Handle client request
    tuple :return: return message to send to client and bool if to close the client socket
    """
    try:
        request_code = request[:4]

        to_send = protocol_build_reply(sock, request)
        
        if request_code == b'EXIT':
            return to_send, True
    except Exception as err:
        print(traceback.format_exc())
        to_send = b'ERRR~001~General error'
    return to_send, False


def handle_client(sock, tid, addr):
	"""
	Main client thread loop (in the server),
	:param sock: client socket
	:param tid: thread number
	:param addr: client ip + reply port
	:return: void
	"""
	global all_to_die

	finish = False
	print(f'New Client number {tid} from {addr}')
	while not finish:
		if all_to_die:
			print('will close due to main server issue')
			break
		try:
			# byte_data = sock.recv(1000)  # todo improve it to recv by message size
			payload = recv_by_size(sock, name=f"Server TID {tid}")
			to_send, finish = handle_request(sock, payload)  # pass sock here
			if to_send != b'':
				send_with_size(sock, to_send, name=f"Server TID {tid}")
			if finish:
				time.sleep(1)
				break
		except socket.error as err:
			print(f'Socket Error exit client loop: err:  {err}')
			break
		except Exception as  err:
			print(f'General Error %s exit client loop: {err}')
			print(traceback.format_exc())
			break

	print(f'Client {tid} Exit')
	sock.close()


def main ():
	global  all_to_die
	"""
	main server loop
	1. accept tcp connection
	2. create thread for each connected new client
	3. wait for all threads
	4. every X clients limit will exit
	"""
	threads = []
	srv_sock = socket.socket()
	print("0")
	srv_sock.bind(('0.0.0.0', 1233))
	print("1")
	srv_sock.listen(20)
	print("2")
	#next line release the port
	srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	i = 1
	while True:
		print('\nMain thread: before accepting ...')
		cli_sock , addr = srv_sock.accept()
		print('\n3')
		t = threading.Thread(target = handle_client, args=(cli_sock, str(i),addr))
		t.start()
		i+=1
		threads.append(t)
		if i > 100000000:     # for tests change it to 4
			print('\nMain thread: going down for maintenance')
			break

	all_to_die = True
	print('Main thread: waiting to all clints to die')
	for t in threads:
		t.join()
	srv_sock.close()
	print( 'Bye ..')


if __name__ == '__main__':
	main()
