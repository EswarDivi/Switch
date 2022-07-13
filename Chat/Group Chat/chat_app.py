import streamlit as st
import socket
import threading
from streamlit.scriptrunner import add_script_run_ctx
nickname=st.text_input("Choose your nickname: ")

st.write("Login in to Server")
# if st.button("Login") :
ip=st.text_input("IP: ")
port=(st.text_input("Port: "))

cont=st.button("Connect")
def receive():
    while True:
        try:
            # Receive Message From Server
            # If 'NICK' Send Nickname
            message = client.recv(1024).decode("ascii")
            if message == "NICK":
                client.send(nickname.encode("ascii"))
            else:
                st.write(message)
        except Exception:
            # Close Connection When Error
            print("An error occured!")
            client.close()
            break

# Sending Messages To Server
def write():
    i=1
    while True:
        i=i+1
        message=st.text_input(f"m{i}:",key=i)
        message = f'{nickname}: {message}'
        client.send(message.encode("ascii"))

if cont==True:
    st.write("Connecting to Server")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((ip, int(port)))
        st.write("Connected to Server")
    except Exception as e:
        st.write("Couldn't connect to server")
        st.write("Try again later")
    # Starting Threads For Listening And Writing
    receive_thread = threading.Thread(target=receive)
    add_script_run_ctx(receive_thread)
    receive_thread.start()

    write_thread = threading.Thread(target=write)
    add_script_run_ctx(write_thread)
    write_thread.start()
