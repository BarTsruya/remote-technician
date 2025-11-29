# Remote Technician

A TCP client-server application for remote system administration and file management.

## Server Services

The server supports the following commands:

| Service | Request Format | Response | Description |
|---------|----------------|----------|-------------|
| **Time** | `TIME` | `TIMR~HH:MM:SS:ffffff` | Get server's current time |
| **Random** | `RAND` | `RNDR~<1-10>` | Get random number (1-10) |
| **Server Name** | `WHOU` | `WHOR~<name>` | Get server computer name |
| **Execute Command** | `EXEC~<command>` | `EXCR~<result>` | Execute system command (e.g., calc, notepad, dir) |
| **List Directory** | `LIST~<path>` | `LISR~<files>` | List files in directory |
| **Delete File** | `DELF~<path>` | `DELR~<result>` | Delete a file |
| **Copy File** | `COPY~<src>~<dest>` | `COPR~<result>` | Copy file from source to destination |
| **Download File** | `DWNL~<path>` | `DWNR~<total>~<index>~<data>` | Download file in chunks |
| **Exit** | `EXIT` | `EXTR` | Close connection |

## Usage

### Start Server
```bash
python server2_7.py
```
Server listens on `0.0.0.0:1233`

### Start Client
```bash
python client2_7.py -H 127.0.0.1 -p 1233
```
Options:
- `-H, --host`: Server IP (default: 127.0.0.1)
- `-p, --port`: Server port (default: 1233)

## Protocol Format

**Request:** `<size>|<code>~<parameters>`  
**Response:** `<size>|<code>~<data>`

- Size is 8 digits indicating message length
- All messages use `~` as delimiter

## Example Interactions

1. **Get Time:**
   - Client: `0000004|TIME`
   - Server: `0000018|TIMR~14:32:45:123456`

2. **Download File:**
   - Client: `0000026|DWNL~/path/to/file.txt`
   - Server: `DWNR~5~1~<data>` (chunk 1 of 5)
   - Server: `DWNR~5~2~<data>` (chunk 2 of 5)
   - ... (continues for all chunks)

## Error Handling

Errors return format: `ERRR~<code>~<message>`

- `001`: General error
- `002`: Code not supported
- `003`: Bad format
- `004`: File not found