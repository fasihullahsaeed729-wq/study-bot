import socket
import sys

def check_port(host, port):
    print(f"Testing connection to {host}:{port}...")
    
    # Test DNS resolution first
    try:
        ip = socket.gethostbyname(host)
        print(f"✅ DNS resolved: {host} -> {ip}")
    except socket.gaierror:
        print(f"❌ DNS resolution failed for {host}")
        return False
    
    # Test port connection
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((ip, port))
        sock.close()
        
        if result == 0:
            print(f"✅ Port {port} is OPEN and accessible")
            return True
        else:
            print(f"❌ Port {port} is CLOSED or FILTERED (error code: {result})")
            print(f"   This usually means a firewall is blocking the connection")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    host = "cluster0.9ploiib.mongodb.net"
    port = 27017
    check_port(host, port)
    
    print("\n" + "="*50)
    print("Next steps if connection fails:")
    print("1. Check if you're on a corporate/school network that blocks MongoDB ports")
    print("2. Try connecting from a different network (mobile hotspot)")
    print("3. Temporarily disable Windows Firewall for testing")
    print("4. Check if antivirus is blocking Python")