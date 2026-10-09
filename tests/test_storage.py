import pytest
from kkbsecu.storage import Repository, User


def test_empty_repository(tmp_path):
    repo = Repository(tmp_path / 'events.sqlite3')
    assert repo.list_users() == []
    assert repo.statistics()['total'] == 0


def test_users_events_and_alert_review(tmp_path):
    repo = Repository(tmp_path / 'events.sqlite3')
    repo.add_user(User('001', 'Profil de test', 'Employé'))
    assert repo.list_users('profil')[0].user_id == '001'
    with pytest.raises(Exception):
        repo.add_user(User('001', 'Dupliqué', 'Employé'))
    repo.log('Visage non associé', None, None, 'unknown')
    event = repo.list_events(1)[0]
    assert event.status == 'unknown'
    assert repo.statistics()['unknown'] == 1
    repo.mark_alert(event.event_id)
    assert repo.statistics()['alert'] == 1
    repo.delete_user('001')
    assert repo.list_users() == []


def test_csv_protects_formula_injection(tmp_path):
    repo = Repository(tmp_path / 'events.sqlite3')
    repo.log('=SUM(A1:A2)', None, None, 'unknown')
    target = tmp_path / 'audit.csv'
    repo.export_csv(target)
    assert "'=SUM(A1:A2)" in target.read_text(encoding='utf-8-sig')
