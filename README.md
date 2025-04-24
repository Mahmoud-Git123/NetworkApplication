# NetworkApplication
Network Application Development

A collection of networking tools including a Ping client, Traceroute utility, Web Server, and Web Proxy - all implemented in Python using raw sockets.

# Features
1. Ping Client<br/>
Implements ICMP echo requests to measure round-trip time (RTT) to a target host.<br/>
Supports configurable timeout and packet count.<br/>
Detects packet loss and unreachable hosts.<br/>
Uses raw sockets for direct ICMP packet handling.<br/>

2. Traceroute Utility<br/>
Maps the network path to a destination by incrementing TTL (Time To Live).<br/>
Supports both ICMP and UDP protocols (configurable via command line).<br/>
Measures latency for each hop along the route.<br/>
Detects intermediate routers and final destination.<br/>

3. Web Server<br/>
Basic HTTP/1.1 server that handles GET requests.<br/>
Serves files from the local directory (e.g., index.html).<br/>
Returns proper HTTP status codes (200 OK, 404 Not Found).<br/>
Configurable port binding (default: 8080).<br/>

4. Web Proxy<br/>
Acts as an intermediary for HTTP requests.<br/>
Supports caching – stores responses locally to reduce redundant fetches.<br/>
Forwards requests to the destination server if not cached.<br/>
Configurable port binding (default: 8000).<br/>

Technical Details:<br/>
Built using Python’s socket library for raw network operations.<br/>
No external dependencies – pure Python standard library.<br/>
Tested on Linux (works best with raw socket permissions).<br/>

# How To Run:<br/>
#Ping a host
python3 NetworkApplications.py ping <hostname><br/>

#Traceroute to a host (ICMP or UDP)<br/>
python3 NetworkApplications.py traceroute --protocol icmp <hostname><br/>
python3 NetworkApplications.py traceroute --protocol udp <hostname><br/>

#Start web server (default port 8080)<br/>
python3 NetworkApplications.py web --port 8080<br/>

#Start proxy server (default port 8000)<br/>
python3 NetworkApplications.py proxy --port 8000<br/>
