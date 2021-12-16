import urllib3
# import urllib3



while True:
    http = urllib3.PoolManager()
    inputstr=input("Enter String:")
    rq =  inputstr
    # inputstr=urllib3.quote(inputstr)
    # sending a post request to bot engine
    url1 = 'http://localhost:5000/bot/hello?message=%s&session=sdjknc'%inputstr
    r = http.request('POST', url1)
    print (r.status)
    r1= r.data

    print (r1)
