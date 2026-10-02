import pytest
from backend.app import create_app, validate

@pytest.fixture
def payload():
    return dict(title='AI Research',description='Study machine learning.',research_area='AI',faculty_name='Dr. Example',department='CS',required_skills='Python',available_positions=2,application_deadline='2027-01-31',status='Open')

def test_valid(payload):
    assert validate(payload)==(payload,{})

@pytest.mark.parametrize('value',[None, [], 'text', 3])
def test_object(value):
    assert validate(value)[1]

@pytest.mark.parametrize('value',[0,-1,True,1.5,'2',2147483648])
def test_positions(payload,value):
    payload['available_positions']=value
    assert 'available_positions' in validate(payload)[1]

@pytest.mark.parametrize('value',['2027-02-30','20270131','',None,'2027-1-31'])
def test_dates(payload,value):
    payload['application_deadline']=value
    assert 'application_deadline' in validate(payload)[1]

def test_text(payload):
    payload['title']='  Valid  '
    assert validate(payload)[0]['title']=='Valid'
    for value in ['   ','x'*201]:
        payload['title']=value
        assert 'title' in validate(payload)[1]

def test_unknown_and_status(payload):
    payload.update(id=3,status='open')
    assert {'body','status'} <= validate(payload)[1].keys()

def test_api_errors():
    def unavailable():raise RuntimeError('Private database detail')
    client=create_app(unavailable).test_client()
    for kwargs in [dict(json={}),dict(data='{broken',content_type='application/json'),dict(data='hello')]:
        assert client.post('/api/opportunities',**kwargs).status_code==400
    for id in ['0','-1','abc','4294967296','9'*4500]:
        assert client.get('/api/opportunities/'+id).status_code==400
    assert client.get('/assets/../../.env').status_code==404
    assert client.get('/').status_code==200
    response=client.get('/api/opportunities')
    assert response.status_code==500 and 'Private database detail' not in response.get_data(as_text=True)
