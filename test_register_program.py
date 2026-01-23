import requests
url = 'http://127.0.0.1:5000/register_program_modal'
data = {
    'program_name': 'Test Program',
    'full_name': 'Unit Tester',
    'phone': '9990001112',
    'email': 'test@example.com'
}
try:
    r = requests.post(url, data=data, timeout=5)
    print('Status:', r.status_code)
    print('Response:', r.text)
except Exception as e:
    print('Error:', e)
