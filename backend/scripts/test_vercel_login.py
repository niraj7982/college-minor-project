import requests

url = "https://digital-campus-project-chi.vercel.app/login/"
client = requests.Session()

# 1. Get the CSRF token
response = client.get(url)
csrftoken = client.cookies.get('csrftoken')

if not csrftoken:
    print("No CSRF token found in cookies!")
    # Django might not set csrftoken on GET unless @ensure_csrf_cookie is used, 
    # but the form creates an input hidden field with csrfmiddlewaretoken
    import re
    m = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
    if m:
        csrftoken = m.group(1)
    else:
        print("No CSRF token in HTML either. Using dummy token.")
        csrftoken = 'dummy'

print(f"CSRF Token: {csrftoken}")

# 2. Login
data = {
    'username': 'admin',
    'password': '123',
    'csrfmiddlewaretoken': csrftoken
}

headers = {
    'Referer': url
}

res = client.post(url, data=data, headers=headers)
print(f"Status Code: {res.status_code}")
if res.status_code == 500:
    print("500 Error Occurred!")
    # Try to parse the traceback from Django's debug page
    import re
    title = re.search(r'<title>(.*?)</title>', res.text)
    if title:
        print(f"Error Title: {title.group(1)}")
    
    # Save output to examine
    with open("debug_vercel_500.html", "w", encoding='utf-8') as f:
        f.write(res.text)
    print("Saved 500 page to debug_vercel_500.html")
else:
    print("No 500 error!")
