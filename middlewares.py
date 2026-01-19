from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time


async def simple_midlleware(request:Request, call_next):
    response = await call_next(request)
    return response

async def process_time_per_request(request:Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    end_time = time.time()
    response.headers["X-Process-Time"] = str(end_time - start_time)
    return response

async def is_authenticated_middleware(request:Request, call_next):
    if not request.method in ["GET", "HEAD", "OPTION"]:
        if not request.headers.get("Authorization"):
            return Response(content="Not authorized 1111", status_code=403)
    response = await call_next(request)
    return response


class AdvancedMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.limit_per_sc = {}
    
    async def dispatch(self, request, call_next):
        current_time = time.time()
        ip_address = request.client.host
        
        if self.limit_per_sc.get(ip_address):
            last_time = self.limit_per_sc[ip_address]["start_time"]
            if  current_time - last_time <= 20:
                number_of_request = len(self.limit_per_sc[ip_address]["requests"])+1
                if number_of_request == 10:
                    return Response(content="You send too many requests", status_code=429)
                else:
                    print("number of request:", number_of_request)
            elif current_time - last_time > 20:
                print("update datas")
                self.limit_per_sc[ip_address] = {
                    "start_time" : current_time,
                    "requests": []
            }
        else:
            print("step 1 init dict ")
            self.limit_per_sc[ip_address] = {
                "start_time" : current_time,
                "requests": []
            }
        
        self.limit_per_sc[ip_address]["requests"].append(request.method)
        print(self.limit_per_sc[ip_address])
        
        response = await call_next(request)
        
        return response
        
            