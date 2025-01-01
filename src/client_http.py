import socket
import base64
from http import cookies

class HTTP_client:
    
   def __init__(self, host, port=80, use_https=False):
       
        self.host = host
        self.port = port
        self.use_https = use_https
        self.last_response_headers = None
        self.cookies = {}

        
        
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
        
   def receive_response(self, sock):
        # Lee los encabezados
        headers = ''
        while True:
            data = sock.recv(1)
            if not data:
                break
            headers += data.decode()
            if headers.endswith('\r\n\r\n'):
                break

        # Separa los encabezados del cuerpo de la respuesta
        headers, body = headers.split('\r\n\r\n', 1)
        headers = headers.split('\r\n')

        # Convierte los encabezados en un diccionario
        header_dict = {}
        for i, header in enumerate(headers):
            if i == 0:
                header_dict['Status'] = header
            else:
                name, value = header.split(': ', 1)
                header_dict[name] = value

        # Comprueba el código de estado
        status_code = int(header_dict['Status'].split()[1])

        if 100 <= status_code < 200:
            if status_code == 100:
                print("Continuar con la solicitud.")
        elif 200 <= status_code < 300:
            if status_code == 204:
                print("La solicitud fue exitosa, pero no hay contenido para devolver.")
        elif 400 <= status_code < 600:
            raise Exception(f"El servidor respondió con un código de estado de error: {status_code}")

        # Procesa los encabezados
        for name, value in header_dict.items():
            if name.lower() == 'set-cookie':
                # Si hay cookie, la almacena
                cookie = cookies.SimpleCookie()
                cookie.load(value)
                for morsel in cookie.values():
                    self.cookies[morsel.key] = {
                        'value': morsel.value,
                        'expires': morsel['expires'],
                        'domain': morsel['domain'],
                        'path': morsel['path'],
                    }
            elif name.lower() == 'content-encoding':
                print(f"El contenido está codificado con: {value}")
            elif name.lower() == 'last-modified':
                print(f"El contenido fue modificado por última vez en: {value}")

        # Si está chunkeada, armamos el cuerpo
        if 'Transfer-Encoding' in header_dict and header_dict['Transfer-Encoding'] == 'chunked':
            chunks = []
            while True:
                line = ''
                while not line.endswith('\r\n'):
                    line += sock.recv(1).decode()
                chunk_length = int(line[:-2], 16)

                if chunk_length == 0:
                    break

                chunk = ''
                while len(chunk) < chunk_length:
                    chunk += sock.recv(min(chunk_length - len(chunk), 1024)).decode()
                chunks.append(chunk)

                sock.recv(2)
            body = ''.join(chunks)  
        elif 'Content-Length' in header_dict:
            # S es un  'Content-Length', lee el cuerpo de la respuesta hasta que se haya leído la cantidad de datos especificada
            remaining = int(header_dict['Content-Length']) - len(body)
            while remaining > 0:
                data = sock.recv(min(remaining, 1024))
                if not data:
                    break
                body += data.decode()
                remaining -= len(data)

        return header_dict, body