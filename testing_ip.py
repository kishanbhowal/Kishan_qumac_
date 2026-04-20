# import socket
#
# s = socket.socket()
# s.settimeout(2)
# s.connect(("192.168.0.27", 5025))
# s.send(b"*IDN?\n")
# print(s.recv(1024))
import pyvisa
rm = pyvisa.ResourceManager()
print(rm.list_resources())  # VNA should appear again
kna = rm.open_resource("TCPIP0::192.168.0.117::hislip0::INSTR")
#
# print(kna.query("*IDN?"))

#CALC1:MEAS1:DATA:FDAT?
#kna = rm.open_resource("TCPIP0::192.168.0.27::5025::SOCKET")
#kna.write("SYST:REBOOT")


