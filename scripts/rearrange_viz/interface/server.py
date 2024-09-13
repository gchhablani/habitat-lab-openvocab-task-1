import http.server
import socketserver
import webbrowser
import threading
import time
import json
import argparse

HTML_FILE = 'interface.html'  # Replace with your HTML file name
SAVE_FILE = 'annotations.json'  # File where annotations will be saved

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/save_annotations':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                with open(SAVE_FILE, 'w') as f:
                    json.dump(data, f, indent=2)
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Annotations saved successfully')
            except Exception as e:
                print(f"Error saving annotations: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Failed to save annotations')
        else:
            self.send_error(404, "File not found")

# Start HTTP server
def start_server(port):
    handler = CustomHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving at port {port}")
        httpd.serve_forever()

# Open HTML file in default web browser
def open_browser(port):
    time.sleep(1)  # Give server a moment to start
    webbrowser.open(f'http://localhost:{port}/{HTML_FILE}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start a simple HTTP server.')
    parser.add_argument('--port', type=int, default=8888, help='Port to run the server on (default: 8888)')
    args = parser.parse_args()

    # Run server in a separate thread
    server_thread = threading.Thread(target=start_server, args=(args.port,))
    server_thread.start()

    # Open HTML file in browser
    open_browser(args.port)
