import http.server
import socketserver
import webbrowser
from pathlib import Path

PORT = 8080
DIRECTORY = Path(__file__).parent

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

def start_server():
    print("=" * 70)
    print(" DISCOVERY-DRIVEN WEB MINING DASHBOARD SERVER")
    print(f" URL: http://localhost:{PORT}/web/dashboard.html")
    print(" Press Ctrl+C in this terminal to stop the server anytime.")
    print("=" * 70)
    
    webbrowser.open(f"http://localhost:{PORT}/web/dashboard.html")
    
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nDashboard server stopped.")

if __name__ == "__main__":
    start_server()

