Step1 First authentication For specific parameters, see the [API Reference > API Interface > 
Login Authentication > The First Login] interface 
• For the first authentication request, carry the userName. The platform then returns Error 
Code 401 (meaning no permission), and contains encrypted information (including realm, 
randomKey, encryptType and publickey) in the message body. Currently, MD5 is the 
only supported encryption type. The platform public key is not the parameter for second 
authentication.
• The request process is as shown below:
POST /brms/api/v1.0/accounts/authorize HTTP/1.1
Host: 192.168.1.1
Connection: keep-alive
Accept-Language: en
Time-Zone: Asia/Shanghai
Content-Type: application/json;charset=UTF-8 
Content-Length: 70
{ 
 "userName": "system",
 "ipAddress": "",
 "clientType": "WINPC_V2"
}HTTP/1.1 401 
Server: nginx
Date: Thu, 17 Dec 2020 00:39:03 GMT
Content-Type: application/json;charset=utf-8 
Content-Length: 502
Connection: keep-alive
X-Frame-Options: SAMEORIGIN
{"realm":"f689ed8c43530d68bf7d6e95a62f7f87","randomKey":"dec91d61f68d4f24","encryptTy
pe":"MD5","publickey":"MIIBIj...MywIDAQAB"}
Dahua HTTP API For DSS V8.4_EN for ITBS
62
Note: Always load WINPC_V2 for clientType.
Step 2 Second authentication For specific parameters, see the [API Reference > API Interface > 
Login Authentication > The Second Login] interface. 
• The second authentication request shall carry the RSA public key of the requester, 
converse the byte array, and use BASE64 code. The public key is in x.509 format, that is, 
parameter publicKey = string (encode (RSAPublicKey)). See [Overview > Interface 
Protocol > Encryption Mode Examples for Interface]. The RSA public key is used to 
encrypt the AES secretkey and secretVector returned to the requester.
• In the second authentication, common user requests shall carry the signature. The 
signature is calculated with the userName, password, realm, randomKey, and 
encryptType (MD5 encryption) in the following way: Pseudocode examples:

temp1 = md5(password)
temp2 = md5(userName + temp1)
temp3 = md5(temp2)
temp4 = md5(userName + ":" + realm + ":" + temp3)
signature = md5(temp4 + ":" + randomKey)
• As shown in the aforementioned pseudocodes, a total of 5 times of MD5 encryption is 
needed. The parameter values and results values are all character strings. The result value 
of MD5 encryption are all in lower case, and the length of MD5 encryption is 32 digits. 
The assumed values are as follows:
Parameter Value
userName "system"
password "admin123"
realm "VMS"
randomKey "9c2b603650f54bcb"
• Calculated values at each stage are as follows:
Times of 
encryption Parameter/Result Value
1 Parameter "admin123"
1 Result "0192023a7bbd73250516f069df18b500"
2 Parameter "system0192023a7bbd73250516f069df18b500"
2 Result "5a0fdbe44b86807b5e5e127918bbc475"
3 Parameter "5a0fdbe44b86807b5e5e127918bbc475"
3 Result "1e27fadce9af09e120ab5142a83a679e"
4 Parameter "system:VMS:1e27fadce9af09e120ab5142a83a679e"
4 Result "4b923d65cbbfd724285a164c3178b055"
5 Parameter "4b923d65cbbfd724285a164c3178b055:9c2b603650f54bcb"
5 Result "024a3dc397a3844bb31d24f22b4d6035"

POST /brms/api/v1.0/accounts/authorize HTTP/1.1
Host: 192.168.1.1
Connection: keep-alive
Accept-Language: en
Time-Zone: Asia/Shanghai
Content-Type: application/json;charset=UTF-8 
Content-Length: 634
{ 
 "mac": "C8:D9:D2:0B:81:22",
 "signature": "6720dd8c9017e8cb1e1171c0a5b43cb9",
 "userName": "system",
 "randomKey": "9d47f3b120174541",
 "publicKey": "MIIBIjANBgkq...AQAB",
 "encryptType": "MD5",
 "ipAddress": "",
 "clientType": "WINPC_V2",
 "userType": "0"
}HTTP/1.1 200 
Server: nginx
Date: Tue, 15 Dec 2020 01:38:17 GMT
Content-Type: application/json;charset=UTF-8 
Transfer-Encoding: chunked
Connection: keep-alive
X-Frame-Options: SAMEORIGIN
Set-Cookie: JSESSIONID=745EAF17E510F06C3AC9A932A9E782B1; Path=/brms; HttpOnl
y 
{"duration":30,"token":"47e5edb9cb5e44dfa3caeea54340c3e9","userId":"1","serviceAbilty":nul
l,"versionInfo":{"lastVersion":"1981402","updateUrl":"/client/x86/Client_Win32_IS_V8.000.00
00001.0.R.20201212.exe;/client/x64/Client_Win64_IS_V8.000.0000001.0.R.20201212.exe"},"e
mapUrl":null,"sipNum":"8888881000","tokenRate":1800,"secretKey":"R8Y1NF8HEEljQP/H...8
6wq0Xg==","secretVector":"...CcQ==","reused":"1","userLevel":"1"}
After a successful second authentication, the meanings of returned fields by the platform are 
shown below:
Parameter Type Description
duration int Keep-alive lasting time (second): The heartbeat keeping interface shall be 
called for keep-alive during this period
token string Token: In subsequent requests, the token shall be placed into the request 
head. The field name is X-Subject-Token
userId string User ID
versionInfo object Version information
Dahua HTTP API For DSS V8.4_EN for ITBS
64
Parameter Type Description
-
lastVersion string Latest version on client
- updateUrl string Client update path
tokenRate int
Token update frequency (second) The valid time of the token is 30 minutes 
by default. Before the token value becomes invalid, call the update token 
interface to get a new token value.
secretKey string
Secretkey ciphertext = Encryption (secret key, public key of terminal), AES 
secret key encrypted by the RSA public key of the requester; all sensitive 
information subsequently needs to be encrypted by AES
secretVector string
Vector ciphertext = Encryption (vector, public key of terminal). AES vector 
encrypted by the RSA public key of the requester; all sensitive information 
subsequently needs to be encrypted by AES
reused string
Whether Multiple Points of Presence (MPOP) is supported for the user 
account, that is whether a single user account can log in to multiple devices 
at the same time; 0: No; 1: Yes
userLevel string User level: 1: Super administrator; 2: Administrator; 3: Custom role
Keep heartbeat
For specific parameters, see the [API Reference > API Interface > Login Authentication > 
Heartbeat Keep-alive] interface.
• After successful authentication, the heartbeat keeping interface shall be called for keepalive during keep-alive period. The keep-alive interval is recommended to be 3/4 of the 
keep-alive lasting period (every 22 seconds). 
The keep-alive request needs to bring the current valid authentication token. The token value is 
put in the X-Subject-Token parameter of the request head, and null is passed to the request 
message body.

The request process is as shown below:
PUT /brms/api/v1.0/accounts/keepalive HTTP/1.1
Host: 192.168.1.1
Connection: close
Content-Type: application/json;charset=UTF-8 
X-Subject-Token: eded084348c9404da6dc80c6a73bb967
Content-Length: 3
{ 
}HTTP/1.1 200 
Set-Cookie: JSESSIONID=93E265F25CD64693CC245189A7D7452D; Path=/brms; HttpOnly
X-Frame-Options: SAMEORIGIN
Content-Type: application/json
Transfer-Encoding: chunked
Date: Thu, 19 Mar 2020 06:27:26 GMT
Connection: close
{"code":1000,"desc":"Success","data":{"token":"eded084348c9404da6dc80c6a73bb967","durati
on":30}}


Update token
For specific parameters, see the [API Reference > API Interface > Login Authentication > Update 
Token] interface. After successful authentication, although the token starts keeping alive, it 
remains invalid after tokenRate. Therefore, you need to call the update token interface to get a 
new token, and keep alive with it. It is recommended that the interval for updating token is 3/4 of 
tokenRate. If the tokenRate is 1,800, it means that the period of validity is 30 minutes, and the 
token update frequency is about 22 minutes. After token update, to ensure consistent request 
authentication, the old token will be deleted in one minute. 
In the token update request, the signature value needs to be carried in the message body. The 
signature value here needs MD5 calculation based on the fourth calculation result for the second 
authentication and the latest token value. The first token value is the returned token in the second 
authentication. Subsequent token values are the returned ones from token updates. The 
pseudocodes are as follows: 
signature = md5(temp4 + ":" + token)
• The assumed values are as follows:
Parameter Value
temp "675ae42820b189caa27d63b4b3264232"
token "a0e5844699db4cf8a2f9afaae11becd4"
• Calculated values are as follows:
Times of 
encryption Parameter/Result Value
1 Parameter "675ae42820b189caa27d63b4b3264232:a0e5844699db4cf8
a2f9afaae11becd4"
1 Result "5bce0dc0059363e251a706a8b1b281a9"
• The request process is as shown below:
POST /brms/api/v1.0/accounts/updateToken HTTP/1.1
Host: 192.168.1.1
Connection: close
Content-Type: application/json;charset=UTF-8 
X-Subject-Token: a0e5844699db4cf8a2f9afaae11becd4
Content-Length: 52
{ 
 "signature": "5bce0dc0059363e251a706a8b1b281a9"
}HTTP/1.1 200 OK
Server: Apache-Coyote/1.1

Set-Cookie: JSESSIONID=C778CC5FC4302D4C71DB10F7FF34391B; Path=/brms; HttpOnl
y 
Content-Type: application/json;charset=UTF-8 
Transfer-Encoding: chunked
Date: Wed, 19 Dec 2018 08:43:04 GMT
Connection: close
{"code":1000,"desc":"Success","data":{"token":"6c2b745658834416b670ed76cfb652d9","durati
on":30}}
The client needs to update the local token values wit