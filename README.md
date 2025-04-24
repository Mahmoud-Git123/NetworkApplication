# NetworkApplication
Network Application Development

A collection of networking tools including a Ping client, Traceroute utility, Web Server, and Web Proxy - all implemented in Python using raw sockets.

# Features
1. Ping Client
Implements ICMP echo requests to measure round-trip time (RTT) to a target host.
Supports configurable timeout and packet count.
Detects packet loss and unreachable hosts.
Uses raw sockets for direct ICMP packet handling.

2. Traceroute Utility
Maps the network path to a destination by incrementing TTL (Time To Live).
Supports both ICMP and UDP protocols (configurable via command line).
Measures latency for each hop along the route.
Detects intermediate routers and final destination.

3. Web Server
Basic HTTP/1.1 server that handles GET requests.
Serves files from the local directory (e.g., index.html).
Returns proper HTTP status codes (200 OK, 404 Not Found).
Configurable port binding (default: 8080).

4. Web Proxy
Acts as an intermediary for HTTP requests.
Supports caching – stores responses locally to reduce redundant fetches.
Forwards requests to the destination server if not cached.
Configurable port binding (default: 8000).

Technical Details:
Built using Python’s socket library for raw network operations.
No external dependencies – pure Python standard library.
Tested on Linux (works best with raw socket permissions).

# How To Run:
#Ping a host
python3 NetworkApplications.py ping <hostname>

#Traceroute to a host (ICMP or UDP)
python3 NetworkApplications.py traceroute --protocol icmp <hostname>
python3 NetworkApplications.py traceroute --protocol udp <hostname>

#Start web server (default port 8080)
python3 NetworkApplications.py web --port 8080

#Start proxy server (default port 8000)
python3 NetworkApplications.py proxy --port 8000
