import http.server
import socketserver
import os
import mimetypes
import re
import urllib.parse

PORT = 3000
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class VideoStreamingHandler(http.server.BaseHTTPRequestHandler):
    def do_HEAD(self):
        self._serve(head_only=True)

    def do_GET(self):
        self._serve(head_only=False)

    def _serve(self, head_only=False):
        # Parse path
        url_parts = urllib.parse.urlsplit(self.path)
        rel_path = urllib.parse.unquote(url_parts.path.lstrip('/'))
        if not rel_path or rel_path == '':
            rel_path = 'index.html'

        file_path = os.path.normpath(os.path.join(BASE_DIR, rel_path))

        # Security check: must stay within BASE_DIR
        if not file_path.startswith(BASE_DIR):
            self.send_error(403, "Access denied")
            return

        if os.path.isdir(file_path):
            index_path = os.path.join(file_path, 'index.html')
            if os.path.exists(index_path):
                file_path = index_path
            else:
                self.send_error(403, "Directory listing disabled")
                return

        if not os.path.exists(file_path):
            self.send_error(404, "File not found")
            return

        ctype, _ = mimetypes.guess_type(file_path)
        if not ctype:
            if file_path.endswith('.css'): ctype = 'text/css'
            elif file_path.endswith('.js'): ctype = 'application/javascript'
            elif file_path.endswith('.mp4'): ctype = 'video/mp4'
            elif file_path.endswith('.svg'): ctype = 'image/svg+xml'
            elif file_path.endswith('.woff2'): ctype = 'font/woff2'
            elif file_path.endswith('.png'): ctype = 'image/png'
            elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'): ctype = 'image/jpeg'
            elif file_path.endswith('.ico'): ctype = 'image/x-icon'
            else: ctype = 'application/octet-stream'

        file_size = os.path.getsize(file_path)
        range_header = self.headers.get('Range')

        if range_header and not head_only:
            match = re.match(r'bytes=(\d+)-(\d*)', range_header)
            if match:
                start = int(match.group(1))
                end = int(match.group(2)) if match.group(2) else file_size - 1
                if start >= file_size:
                    self.send_error(416, "Requested Range Not Satisfiable")
                    return

                end = min(end, file_size - 1)
                chunk_size = end - start + 1

                self.send_response(206)
                self.send_header('Content-Type', ctype)
                self.send_header('Content-Range', f'bytes {start}-{end}/{file_size}')
                self.send_header('Content-Length', str(chunk_size))
                self.send_header('Accept-Ranges', 'bytes')
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()

                with open(file_path, 'rb') as f:
                    f.seek(start)
                    self.wfile.write(f.read(chunk_size))
                return

        self.send_response(200)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(file_size))
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()

        if not head_only:
            with open(file_path, 'rb') as f:
                while chunk := f.read(65536):
                    self.wfile.write(chunk)

    def log_message(self, format, *args):
        pass  # quiet logging for high-throughput tests

if __name__ == '__main__':
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("127.0.0.1", PORT), VideoStreamingHandler) as httpd:
        print(f"Nutrifresh Eggs Server running at http://127.0.0.1:{PORT}/")
        httpd.serve_forever()
