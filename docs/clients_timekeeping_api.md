# There are only 2 APIs to be used in client side.

## Authentication

Credentials:
    Host: 192.168.9.125
    username: system
    password: admin1234567

Authentication Request:
POST: http://{{host}}/brms/api/v1.0/accounts/authorize
Body:
{
    "userName": "{{username}}",
    "ipAddress": "",
    "clientType": "WINPC_V2"
}

Response:
200 ok

{
    loginToken: "5fad3e259cbc497fa3e2ece67676469c"
}

1. Store the loginToken in the database
2. Use the loginToken to make the other requests


## Pull API

6.2.10.2 Search Attendance Reports in Pages
Brief Description
• Search attendance reports in pages

Request URL
GET
• /brms/api/v1.0/attendance/record-inforeport/page?startTime={startTime}&endTime={endTime}&personId={personId}&perso
nName={personName}&deptId={deptId}&page={page}&pageSize={pageSize}

Headers:
• X-Subject-Token: {token} 

Parameter | Type | Description
startTime | string | Required. The start time in format of yyyy-MM-dd HH:mm:ss
endTime | string | Required. The end time in format of yyyy-MM-dd HH:mm:ss
personId | string | Person ID keyword, exact matching, optional
personName | string | Name keyword, fuzzy matching, optional
deptId | string | Department ID, such as: 001001,the orgCode field of the corresponding 
personnel group
page | string | Page number
pageSize | string | Number of items displayed per page
token | string | Token obtained when logging in

Request Sample:
GET /brms/api/v1.0/attendance/record-info-report/page?startTime=2023-07-12%2000%3A00%
3A00&endTime=2023-07-12%2023%3A59%3A59&personName=&personId=&deptId=001&p
age=1&pageSize=20 HTTP/1.1
Host: {{host}}
Connection: close
Content-Type: application/json;charset=UTF-8 
X-Subject-Token: 5fad3e259cbc497fa3e2ece67676469c
Return Example
{
 "code": 1000, 
 "desc": "Success",
 "data": {
 "totalCount": "-121", 
 "pageData": [
 { 
 "id": "1",
 "attendanceDate": "2023-07-12", 
 "code": "123", 
 "name": "test",
 "deptName": "Root",
 "orgInfos": [ 
 { 
 "orgCode": "001", 
 "orgName": "All Persons and Vehicles" 
 } 
 ],
 "orderName": "",
 "signInTime": "12:10",
 "signOutTime": "13:10", 
 "week": "0",
 "outTime": "1 hour and 10 minutes", 
 "workTime": "12",
 "workOverTime": "13" 
 } 
 ] 
 } 
}


Return Parameter
Parameter Type Description
code int Error code
desc string Result description
data object None
- totalCount string
Record the total number. Negative numbers indicate no total number of 
pages to be paginated. They are used to predict the total number of the 
next 7 pages and assist in displaying paginated controls. Cannot be used 
for data statistics.
- pageData object None
- - id string Attendance information ID
- -
attendanceDate string Date, such as 2018-09-20 
- - code string Person ID
- - name string Person name
- - deptName string Department name
- - orgInfos array Personnel multi organization infomation
- - - orgCode string Person group code
- - - orgName string Person group name
- - signOutTime string Check-out time, such as 13:10
- - week string Week: 0: Sunday, 1: Monday,..., 6: Saturday
- - outTime string Outing duration, such as 1 hour and 10 minutes, 10 minutes, 1 hour or 0 
minute
- - workTime string Working duration (minutes)
- -
workOverTime string Overtime duration (minutes) 
