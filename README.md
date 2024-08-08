# TCPTorConnect
A simple Python script for connecting remotely to TOR network and onion sites. That are two things to be said tough,
first its designed to be isolated and does not require f.i. systemwide tor install, second thing to know is that its
only client side, currently you cant use it to host a service(and also please never do).

# Setup
1. Clone the repository: `git clone https://github.com/Polskiecus/TCPTorConnect/`
2. Optional(tough very recommended) start by setting up Control Port password(can be done
using `tor --hash-password "passwd"` and editing torrc(in this case inside the Components Directory
by adding a line like so: `HashedControlPassword YOURHASHHERE`, you will get warned if you dont do this.
3. Also optional but recommended: recompile/get tor binary by yourself and place it under the path `Components/Binaries/tor`

# Usage
The program does not have a wiki yet, but all the functionality you may need is put in an example inside it :)

# Support
As its GNU/GPL project I will try to resolve issues, but I wont promise anything(this program does not come with any 
law applicable warranty), aside from that it should be working on all platforms, but I am only going to maintain it 
for LINUX based operating systems
