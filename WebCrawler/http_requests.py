import socket
import re

class Response:

    def __init__(self, text, status_code, response_headers):
        self.text = text
        self.status_code = status_code
        self.response_headers = response_headers

    def __repr__(self):
        return str("<Response {}>".format(self.status_code))


class KeepAliveRequests:

    def __init__(self, server):
        self.sock = None
        self.server = server
        self.initiate_connection()

    def initiate_connection(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.server, 80))

    def parse_headers(self, text):
        '''
        Takes the first bit of a HTTP request and separates the headers and 
        the content.
        Returns a triple of the headers in a dict, the data as a string, 
        and the http status code.
        '''

        
        header_text, data = text.split('\r\n\r\n')[:2]

        headers_raw = header_text.split('\r\n')

        status_code = int(headers_raw[0].split(' ')[1])

        headers = {}
        for header in headers_raw[1:]:
            hd = header.split(': ')
            headers[hd[0]] = hd[1]

        return headers, data, status_code


    def receive_from_socket(self, sock=None):
        if sock is None:
            sock = self.sock

        headers = {}
        status_code = None

        buffer = ""
        parsed_headers = False
        is_chunked = False
        length = 0
        expected_length = None
        while True:
            if expected_length is None:
                data = sock.recv(1024)
            else:
                data = sock.recv(expected_length - len(buffer))

            # print "Received {} bytes".format(len(data))

            if len(data) == 0:
                return Response("", 500, {})
            elif len(data) <= 2:
                continue

            if not parsed_headers:
                parsed_headers = True
                headers, data, status_code = self.parse_headers(data)

                if status_code == 500:
                    break

                if headers.get('Transfer-Encoding', "") == "chunked":
                    is_chunked = True
                    expected_length = int(data.split('\r\n')[0], 16)
                    data = "".join(data.split('\r\n')[1:]) 
                else:
                    expected_length = int(headers['Content-Length'])

            length += len(data)

            if not data:
                break

            if length >= expected_length:
                if not is_chunked:
                    buffer += data
                    break
                else:
                    # We got the end of the chunked data, 
                    # get rid of it and break out.
                    if '\r\n\r\n' in data:
                        data = data.split('\r\n\r\n')[0].split('\r\n')[0]
                        buffer += data
                        break
                    # There still may be more...
                    # Now we have to get the next chunk length.
                    else:
                        chunked_data = ""
                        while True:
                            temp = sock.recv(1)
                            chunked_data += temp
                            if re.search('\\r\\n.+\\r\\n', chunked_data) is not None:
                                break
                        expected_length = int(chunked_data.replace('\r\n', ''), 16)
                        if expected_length == 0:
                            break

            buffer += data

        return Response(buffer, status_code, headers)


    def get(self, url, headers={}):
        '''
        Make an HTTP get request to a given url.
        An optional headers field may be passed and
        will be applied to the HTTP request.

        A header can pass in a cookie...e.g.
        {
            "Cookie": "11111"
        }

        Returns a Response object.
        '''
        # print "GET " + url
        supplied_headers = headers

        header_text = ""
        if supplied_headers != {}:
            header_text = "\n".join(["{}: {}".format(key, supplied_headers[key]) for key in supplied_headers.keys()])
        
        url = url.replace('http://','')
        hostname = url.split('/')[0]
        path     = "/".join(url.split('/')[1:])

        self.sock.send(
            "GET /{} HTTP/1.1\n".format(path) + \
            "Host: {}\n".format(hostname) + \
            "Connection: Keep-Alive\n" + \
            header_text + \
            "\n\n\n"
        )

        return self.receive_from_socket()

        

    def post(self, url, data={}, headers={}):
        '''
        Posts to a URL with the given data as
        the payload.
        Returns a Response object.
        '''
        # print "POST " + url

        supplied_headers = headers
        url = url.replace('http://','')
        hostname = url.split('/')[0]
        path     = "/".join(url.split('/')[1:])

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((hostname, 80))

        post_content = "{}".format("&".join(["{}={}".format(key, data[key]) for key in data.keys()]))
        s = "POST /{} HTTP/1.1\n".format(path) + \
            "Host: {}\n".format(hostname) + \
            "Content-Type: application/x-www-form-urlencoded\n" + \
            "Connection: Keep-Alive\n" + \
            "Content-Length: {}\n".format(len(post_content)) + \
            "\n".join(["{}: {}".format(key, supplied_headers[key]) for key in supplied_headers.keys()]) + \
            "\n\n" + \
            post_content + \
            "\n\n"
        
        sock.send(s)

        return self.receive_from_socket(sock)
