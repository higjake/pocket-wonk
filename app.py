import requests

# Replace with the correct URL
url = "https://api.propublica.org/congress/v1/115/senate/members.json"
headers = {
    'X-API-KEY': 'kuJPmTSeZ8Qt7dXn1yIzJbXCkSHI6E5FXNB4tRMM'
}
# It is a good practice not to hardcode the credentials. So ask the user to enter credentials at runtime
myResponse = requests.get(url,headers=headers)
print (myResponse.status_code)
