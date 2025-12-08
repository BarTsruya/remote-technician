__author__ = 'Yossi'

# 2.6  client server October 2021
import shutil
import socket, random, traceback
import time, threading, os, datetime
import glob 
import pyautogui
import subprocess
from tcp_by_size import recv_by_size,send_with_size
all_to_die = False  # global




def get_time():
	"""return local time """
	return datetime.datetime.now().strftime('%H:%M:%S:%f')


def get_random():
	"""return random 1-10 """
	return str(random.randint(1, 10))


def get_server_name():
	"""return server name from os environment """
	return  os.environ['COMPUTERNAME']

def exec_command(cmd):
	try:
		subprocess.call(cmd)
		return 'EXCR~succeed'
	except FileNotFoundError:
		return f'ERRR~004~File Not Found {cmd}'
	except Exception:
		return f'ERRR~001~error while runing {cmd}'

def list_dir(path):
	try:
		files=glob.glob(path+'*')
		result='|'.join(files)
		return f'LISR~{result}'
	except FileNotFoundError:
		return f'ERRR~004~File Not Found{path}'
	except Exception as e:
		return f'ERRR~001~{e}'
	
def dele(file):
	try:
		os.remove(file)
		return 'DELR~file deleted successfuly'
	except FileNotFoundError:
		return f'ERRR~004~File Not Found{file}'
	except Exception as e:
		return f'ERRR~001~{e}'

def copy(source,dest):
	try:
		shutil.copy(source,dest)
		return f'COPR~file copyed successfuly'
	except FileNotFoundError:
		return f'ERRR~004~File Not Found{source}'
	except Exception as e:
		return f'ERRR~001~{e}'
	
def screenshot(sock, dest):
	try:
		image = pyautogui.screenshot()
		image.save(dest)
		return downlowde_file(sock, dest)
		# return f'SCRR~image saved in {dest}'
	except Exception as e:
		return f'ERRR~001~{e}'

def downlowde_file(sock,src):
	try:
		
		chunk_index=1
		chunk_sise=4096
		file_size = os.path.getsize(src)
		total_chunks= (file_size+(chunk_sise-1))//chunk_sise
		with open(src,'rb') as f:
			while True:
				data = f.read(chunk_sise)
				if not data :
					break
				to_send = b'DWNR~'+str(chunk_index).encode()+b'~'+str(total_chunks).encode()+b'~'+data
				send_with_size(sock,to_send)
				chunk_index+=1

		return f'DONE~file downlode successfuly'
	except Exception as e:
		return f'ERRR~001~{e}'

def protocol_build_reply(sock,request):
	"""
	Application Business Logic
	function despatcher ! for each code will get to some function that handle specific request
	Handle client request and prepare the reply info
	string:return: reply
	"""
	request_code = request[:4].decode()
	request = request.decode("utf8")
	if request_code == 'TIME':
		reply = 'TIMR' +'~' + get_time()
	elif request_code == 'RAND':
		reply ='RNDR' + '~' + get_random()
	elif request_code == 'WHOU':
		reply ='WHOR' + '~' + get_server_name()
	elif request_code == 'EXIT':
		reply= 'EXTR'
	elif request_code == 'EXEC':
		fields=request.split('|')
		cmd=fields[1]
		reply=exec_command(cmd)
	elif request_code =='LIST':
		fields=request.split('|')
		path=fields[1]
		reply=list_dir(path)
	elif request_code =='DELF':
		fields=request.split('|')
		deletefile=fields[1]
		reply = dele(deletefile)
	elif request_code=='COPY':
		fields =request.split('|')
		source=fields[1]
		destination=fields[2]
		reply =copy(source,destination)
	elif request_code == 'SCRN':
		fields=request.split('|')
		dest = fields[1]
		reply = screenshot(sock, dest)
	elif request_code == 'DWNL':
		fields=request.split('|')
		src = fields[1]
		reply = downlowde_file(sock,src)

	else:
		reply = 'ERRR~002~code not supported'
	return reply.encode()


def handle_request(sock,request):
	"""
	Hadle client request
	tuple :return: return message to send to client and bool if to close the client socket
	"""
	try:
		request_code = request[:4]
		to_send = protocol_build_reply(sock,request)
		if request_code == b'EXIT':
			return to_send, True
	except Exception as err:
		print(traceback.format_exc())
		to_send =  b'ERRR~001~General error'
	return to_send, False


def handle_client(sock, tid , addr):
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
			byte_data = recv_by_size(sock)
			to_send , finish = handle_request(sock,byte_data)
			if to_send != '':
				send_with_size(sock,to_send)
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
	input("0")
	srv_sock.bind(('0.0.0.0', 1233))
	input("1")
	srv_sock.listen(20)
	input("2")
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
