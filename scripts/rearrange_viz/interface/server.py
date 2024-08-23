import http.server
import socketserver
import webbrowser
import threading
import os
import time

PORT = 8000
HTML_FILE = 'interface.html'  # Replace with your HTML file name

# Start HTTP server
def start_server():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()

# Open HTML file in default web browser
def open_browser():
    time.sleep(1)  # Give server a moment to start
    webbrowser.open(f'http://localhost:{PORT}/{HTML_FILE}')

# Run server in a separate thread
server_thread = threading.Thread(target=start_server)
server_thread.start()

# Open HTML file in browser
open_browser()
