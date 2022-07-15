import socket, cv2, pickle, struct
import pyshine as ps


# create socket
def Auido(ip,port):
    mode = "get"
    name = "CLIENT RECEIVING AUDIO"
    audio, context = ps.audioCapture(mode=mode)
    ps.showPlot(context, name)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_ip = ip
    port = int(port)
    socket_address = (host_ip, port)
    client_socket.connect(socket_address)
    print("CLIENT CONNECTED TO", socket_address)
    data = b""
    payload_size = struct.calcsize("Q")  # Q is for 64 bit unsigned long size of 8 bytes
    while True:
        while len(data) < payload_size:
            packet = client_socket.recv(4 * 1024)  # 4K
            if not packet:
                break
            data += packet
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q", packed_msg_size)[0]

        while len(data) < msg_size:
            data += client_socket.recv(4 * 1024)
        frame_data = data[:msg_size]
        data = data[msg_size:]
        frame = pickle.loads(frame_data)
        audio.put(frame)

    client_socket.close()
