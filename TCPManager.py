import subprocess
import socks
import socket
from stem import Signal
from stem.control import Controller

class TorConnector:
    def __init__(self, tor_binary_path, tor_data_dir, control_port=9051, control_password=None):
        self.tor_binary_path = tor_binary_path
        self.tor_data_dir = tor_data_dir
        self.control_port = control_port
        self.control_password = control_password
        self.tor_process = None
        self.control_connection = None
        self.tcp_socket = None

    def start_tor(self):
        if self.tor_process is not None:
            raise RuntimeError("[ERROR] Tor process is already running")

        self.tor_process = subprocess.Popen(
            [self.tor_binary_path, '--DataDirectory', self.tor_data_dir, '--ControlPort', str(self.control_port), '--torrc-file', self.tor_data_dir+"torrc"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

        # Wait until Tor has established a circuit and is ready
        while True:
            line = self.tor_process.stdout.readline()
            print("[TOR BINARY PIPE] "+line, end="")

            if "Bootstrapped 100%" in line:
                print("[INFO] Tor is ready.")
                break

            if line == "" and self.tor_process.poll() is not None:
                raise RuntimeError("[ERROR] Tor process failed to start")

        # Connect to the Tor control port
        self.control_connection = Controller.from_port(port=self.control_port)
        if self.control_password:
            self.control_connection.authenticate(password=self.control_password)
            print("[INFO] logged into the control port")
        else:
            self.control_connection.authenticate()
            print("[WARN] authenticated without password, you better set one up, as you are vulnerable to config changes at port 9051")

    def stop_tor(self):
        if self.tor_process is not None:
            self.tor_process.terminate()
            self.tor_process.wait()
            self.tor_process = None
            print("[INFO] Tor process terminated.")

    def reset_circuit(self):
        if self.control_connection is None:
            raise RuntimeError("[ERROR] Control connection is not established")

		# Close the existing TCP connection if open
        self.close_tcp_connection()

        # Send the NEWNYM signal to Tor to reset the circuit
        self.control_connection.signal(Signal.NEWNYM)
        print("[INFO] Tor circuit reset. Waiting for new circuit...")

        # Wait for the new circuit to be established
        while True:
            line = self.tor_process.stdout.readline()
            if "New control connection opened" in line or "New circuit" in line:
                print("[INFO] New Tor circuit established.")
                break

    def establish_tcp_connection(self, onion_address, port):
        if self.tcp_socket:
            print("[INFO] TCP connection already established.")
            return

        # Connect via Tor SOCKS proxy
        socks.set_default_proxy(socks.SOCKS5, "localhost", 9050)
        socket.socket = socks.socksocket
        print("[INFO] Proxy Settings Applied")

        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("[INFO] Ready to Establish TCP connection")

        self.tcp_socket.connect((onion_address, port))
        print("[INFO] TCP connected")

    def send_data(self, data):
        if self.tcp_socket is None:
            raise RuntimeError("[ERROR] No TCP connection established")

        self.tcp_socket.sendall(data)
        print("[INFO] Data Sent")

    def receive_data(self, buffer_size=4096):
        if self.tcp_socket is None:
            raise RuntimeError("[ERROR] No TCP connection established")

        response = self.tcp_socket.recv(buffer_size)
        return response.decode()

    def close_tcp_connection(self):
        if self.tcp_socket is not None:
            self.tcp_socket.close()
            self.tcp_socket = None
            print("[INFO] TCP connection closed")

    def __del__(self):
        self.close_tcp_connection()
        self.stop_tor()

# Usage example:

if __name__ == "__main__":
    tor_connector = TorConnector(tor_binary_path='Components/Binaries/tor', tor_data_dir='Components/', control_password="passwd")

    try:
        # Start the Tor process and establish a circuit
        tor_connector.start_tor()

        # Example: Establish a persistent TCP connection
        tor_connector.establish_tcp_connection('phgn6b3cbn2tazyx3s76eo23aqhqxyswj66af6c4omcpo67rkp7yt2qd.onion', 5001)
        
        # Send data through the persistent TCP connection
        tor_connector.send_data(b"Hello Onion!")
        
        # Receive data from the persistent TCP connection
        tcp_response = tor_connector.receive_data()
        print("[OUT] Data received: " + str(tcp_response))

        # Optionally, reset Tor circuit if needed
        tor_connector.reset_circuit()

        # Close the TCP connection when done
        tor_connector.close_tcp_connection()

    finally:
        # Ensure that Tor is properly stopped
        tor_connector.stop_tor()

