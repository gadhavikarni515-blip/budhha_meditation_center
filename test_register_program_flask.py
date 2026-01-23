from app import app
with app.test_client() as c:
    resp = c.post('/register_program_modal', data={'program_name':'Test Program','full_name':'Unit Tester','phone':'9990001112','email':'test@example.com'})
    print('status:', resp.status_code)
    try:
        print('json:', resp.get_json())
    except Exception as e:
        print('resp data:', resp.data)
