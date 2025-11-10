import argparse
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
host = '127.0.0.1'
port = 12432
cliEnd = "[modelLabCliEnd]"
newLine = '[NewLine]'
errorPrefix = '[Error]'
logPrefix = '[Info]'

# Each entry: (command, description, [required params (without leading dash)])
SUPPORTED_CMDS = [
    ('listModels', 'List available models (default)', []),
    ('createWorkspace', 'Create a new workspace and set the CLI path to that folder', ['path']),
    ('setCliPath', 'Set the CLI path to an existing workspace', ['path']),
    ('addModel', 'Add a model to the workspace at the current CLI path', ['modelid']),
    ('listLocalModels', 'List models added to the local workspace at the current CLI path', []),
    ('convert', 'Convert a model in the local workspace at the current CLI path', ['modelid', 'workflow', 'runtime', 'name(optional)']),
]

cmdError = False
class PrintingHandler(BaseHTTPRequestHandler):
    server_version = "HttpListener/0.1"

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8', errors='replace') if length else ''
        # Respond 200
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b'OK')

        if cliEnd == body:
            # Shutdown must be called from another thread
            threading.Thread(target=self.server.shutdown, daemon=True).start()
        elif newLine == body:
            # Split body on newLine markers and print each line with a timestamp
            print('')
        else:
            if errorPrefix in body:
                global cmdError
                cmdError = True
            # Print received body with a local timestamp prefix
            now = datetime.now()
            print(f'[{now.strftime("%Y-%m-%d %H:%M:%S")}] {body}')

    def do_GET(self):
        # Quick status page
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b'Http listener running')
        
    # Prevent BaseHTTPRequestHandler from writing request logs to stderr
    # (send_response calls self.log_request which calls log_message -> writes to
    # stderr). Override log_message to be a no-op to suppress those messages.
    def log_message(self, format, *args):
        # no-op: silence automatic request logging
        return

    # Optionally suppress error logging as well
    def log_error(self, format, *args):
        return

def run(host: str, port: int, args):
    # Build query params from args namespace: include all keys except 'cmd' and
    # omit values that are None or empty strings.
    from urllib.parse import urlencode

    params = {}
    # args may be an argparse.Namespace; vars(args) returns its dict
    for k, v in vars(args).items():
        if k == 'cmd':
            continue
        # Skip unset or empty values
        if v is None:
            continue
        if isinstance(v, str) and v.strip() == '':
            continue
        params[k] = v

    query = urlencode(params)
    uri = f"vscode://ms-windows-ai-studio.windows-ai-studio/conversion/{args.cmd}"
    if query:
        uri = uri + '?' + query

    server = HTTPServer((host, port), PrintingHandler)
    import os
    # Open the URI (this will trigger the external app to send requests to our server)
    os.startfile(uri)

    try:
        # Wait for the server thread to finish. The handler will call server.shutdown()
        # (via a separate thread) when it sees the cliEnd marker.
        server.serve_forever()
        print("\033[92mCommand run succeeded\033[0m") if not cmdError else print("\033[91mCommand run stopped with errors\033[0m")
    except KeyboardInterrupt:
        print("Keyboard interrupt received, shutting down server")
        # Ensure shutdown is called from a different thread context to avoid deadlocks
        threading.Thread(target=server.shutdown, daemon=True).start()
    finally:
        try:
            server.server_close()
        except Exception:
            pass
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # Add a -help switch (in addition to argparse -h) that prints supported cmds
    parser.add_argument('-help', action='store_true', dest='show_help_cmds',
                        help='Show supported -cmd values and exit')
    parser.add_argument('-cmd')
    parser.add_argument('-path')
    parser.add_argument('-modelid')
    parser.add_argument('-workflow')
    parser.add_argument('-runtime')
    parser.add_argument('-name')
    args = parser.parse_args()
    if not args.cmd:
        print('Supported -cmd values:')
        # Compute max command name width so we can align the columns
        max_name_len = max((len(n) for n, _, _ in SUPPORTED_CMDS), default=0)
        for name, desc, reqs in SUPPORTED_CMDS:
            req_part = f" (required: {', '.join(f'-{p}' for p in reqs)})" if reqs else ''
            print(f'  {name.ljust(max_name_len)}  - {desc}{req_part}')
        print('\nNote: the actual supported commands are provided by the Windows AI Studio extension.\n')
        raise SystemExit(0)
    run(host=host, port=port, args=args)
