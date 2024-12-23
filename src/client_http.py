

class HTTP_client:
    
   def __init__(self, host, port=80, use_https=False):
       
        self.host = host
        self.port = port
        self.use_https = use_https