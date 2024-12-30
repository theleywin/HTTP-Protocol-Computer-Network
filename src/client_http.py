import socket
import base64
from http import cookies

class HTTP_client:
    
   def __init__(self, host, port=80, use_https=False):
       
        self.host = host
        self.port = port
        self.use_https = use_https
        self.last_response_headers = None
        
        
   def send_request(self, method, path, headers=None, body=None, username=None, password=None):
        try:
            
            # socket.AF_INET se refiere a la familia de ipv4
            # socket.SOCK_STREAM representa el tipo de conexion, en este caso TCP

            sock = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
            sock.settimeout(10.0)
            sock.connect((self.host, self.port))

            if headers is None:
                headers = {}

            if username is not None and password is not None:
                credentials = f'{username}:{password}'
                base64_credentials = base64.b64encode(credentials.encode()).decode()
                headers['Authorization'] = f'Basic {base64_credentials}'

            if self.cookies:
                cookie_header = '; '.join(f'{k}={v}' for k, v in self.cookies.items())
                headers['Cookie'] = cookie_header

            if 'Host' not in headers:
                headers['Host'] = self.host

            if 'User-Agent' not in headers:
                headers['User-Agent'] = 'MyHttpClient'

            if 'Accept' not in headers:
                headers['Accept'] = '*/*'

            # Construye la solicitud HTTP
            request = '{} {} HTTP/1.1\r\n'.format(method, path)
            request += ''.join('{}: {}\r\n'.format(k, v) for k, v in headers.items())
            request += '\r\n'

            if body is not None:
                request += '\r\n' + body

            sock.send(request.encode())

            # Recibe la respuesta del servidor
            # TODO implementar el metodo receive_response
            headers, body = self.receive_response(sock)
            self.last_response_headers = headers

            # Si la respuesta es una redirección, sigue la redirección resuelve recursivo
            if headers['Status'].startswith(('301', '302', '303', '307', '308')):
                new_url = headers['Location']
                sock.close()
                new_client = HTTP_client(new_url, use_https=self.use_https)
                return new_client.send_request(method, new_url, headers, body)

            for header, value in headers.items():
                if header.lower() == 'set-cookie':
                    cookie = cookies.SimpleCookie()
                    cookie.load(value)
                    
                    for morsel in cookie.values():
                        self.cookies[morsel.key] = {
                            'value': morsel.value,
                            'expires': morsel['expires'],
                            'domain': morsel['domain'],
                            'path': morsel['path'],
                        }

            sock.close()

            return headers, body
        
        except socket.timeout:
            raise Exception("La solicitud se agotó.")
        except socket.error as e:
            raise Exception(f"No se pudo conectar al servidor. {e}")
        except Exception as e:
            raise Exception(f"Ocurrió un error inesperado. {e}")