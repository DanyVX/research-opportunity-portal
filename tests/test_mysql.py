"""Real database tests, explicitly enabled with a dedicated TEST_DB_NAME."""
import os
from pathlib import Path
import pymysql
import pytest
from backend.app import create_app

@pytest.fixture(scope='module')
def client():
    name=os.getenv('TEST_DB_NAME')
    if not name:pytest.skip('Set TEST_DB_NAME for real MySQL integration tests.')
    if not name.startswith('research_portal_test') or not name.replace('_','').isalnum():
        raise ValueError('Use a dedicated research_portal_test database; test rows are deleted.')
    options=dict(host=os.getenv('DB_HOST','127.0.0.1'),port=int(os.getenv('DB_PORT','3306')),user=os.getenv('DB_USER','portal_user'),password=os.getenv('DB_PASSWORD',''),charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
    def factory():return pymysql.connect(**options,database=name)
    sql=(Path(__file__).resolve().parents[1]/'database/schema.sql').read_text()
    with factory() as db:
        with db.cursor() as cur:
            cur.execute(sql[sql.index('CREATE TABLE'):].strip().rstrip(';'))
            cur.execute('DELETE FROM opportunities')
        db.commit()
    yield create_app(factory).test_client()
    with factory() as db:
        with db.cursor() as cur:cur.execute('DELETE FROM opportunities')
        db.commit()

def data(title='Vision Lab'):
    return dict(title=title,description='Computer vision research.',research_area='Vision',faculty_name='Dr. Example',department='CS',required_skills='Python',available_positions=2,application_deadline='2027-02-28',status='Open')

def test_crud(client):
    ids=[]
    for title in ['Vision','Networks','AI']:
        r=client.post('/api/opportunities',json=data(title));assert r.status_code==201
        ids.append(r.json['id']);assert r.headers['Location'].endswith(str(ids[-1]))
    assert len(client.get('/api/opportunities').json)==3
    path='/api/opportunities/'+str(ids[0])
    assert client.get(path).json['title']=='Vision'
    updated=data('Updated');updated['available_positions']=4
    assert client.put(path,json=updated).status_code==200
    assert client.put(path,json=updated).status_code==200
    updated['status']='Closed'
    assert client.put(path,json=updated).json['status']=='Closed'
    assert client.get(path).json['available_positions']==4
    assert client.delete(path).status_code==200
    assert client.get(path).status_code==404
    assert client.delete(path).status_code==404
    assert client.put(path,json=updated).status_code==404
    assert client.post('/api/opportunities',json={}).status_code==400

def test_all_rows_and_sql_literal(client):
    text="Robert'); DROP TABLE opportunities; --"
    for i in range(12):
        assert client.post('/api/opportunities',json=data(text if i==0 else f'Test {i}')).status_code==201
    rows=client.get('/api/opportunities').json
    assert len(rows)>=12 and any(r['title']==text for r in rows)
