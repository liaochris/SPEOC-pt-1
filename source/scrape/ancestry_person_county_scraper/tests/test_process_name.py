import pytest
import ancestry_scraper.worker as worker

class DummyException(Exception):
    pass

@pytest.fixture(autouse=True)
def isolation(monkeypatch):
    """Automatically isolate storage/search/parser side-effects."""
    # Ensure clean monkeypatch for each test
    return monkeypatch

def test_process_name_skips_done(monkeypatch):
    # load_progress returns name already done
    called = {'append': False, 'save': False}

    # Stub load_progress(state) → {'Alice':'done'}
    monkeypatch.setattr(worker, 'load_progress',
                        lambda state: {'Alice': 'done'})

    # Stub append_result(row, state)
    monkeypatch.setattr(worker, 'append_result',
                        lambda row, state: called.__setitem__('append', True))

    # Stub save_progress(prog, state)
    monkeypatch.setattr(worker, 'save_progress',
                        lambda prog, state: called.__setitem__('save', True))

    # invoke
    result = worker.process_name('Alice', "DE", event_year=1800, event_x=5)
    # should skip entirely: no append, no save
    assert called['append'] is False
    assert called['save'] is False
    assert result is None

def test_process_name_success(monkeypatch):
    # initial empty progress
    prog = {}
    monkeypatch.setattr(worker, 'load_progress', lambda state: prog)
    # stub fetch and parse
    monkeypatch.setattr(worker, 'fetch_search_page',
                        # accept state + keywords
                        lambda name, state, **kwargs:
                            ('<html>', f'http://example.com/?name={name}'))

    monkeypatch.setattr(worker, 'parse_residence_county',
                        lambda html: 'SomeCounty')


    # capture append and save
    appended = []
    monkeypatch.setattr(worker, 'append_result', lambda args, state: appended.append(args))

    saved = []
    monkeypatch.setattr(worker, 'save_progress', lambda p, state: saved.append(p.copy()))

    # run
    worker.process_name('Bob', "DE", event_year=1777, event_x=10)

    # verify append called once with correct values
    assert appended == [['Bob', 'http://example.com/?name=Bob', 'SomeCounty']]
    # progress dict should have been updated
    assert prog['Bob'] == 'done'
    # save_progress should have been called with updated prog
    assert saved == [ {'Bob': 'done'} ]

def test_process_name_error(monkeypatch):
    state = "DE"
    # initial empty progress
    prog = {}
    monkeypatch.setattr(worker, 'load_progress', lambda state: prog)
    # simulate fetch throwing
    def bad_fetch(name, event_year, event_x):
        raise DummyException("failed fetch")
    monkeypatch.setattr(worker, 'fetch_search_page', bad_fetch)
    # capture append and save
    appended = []
    monkeypatch.setattr(worker, 'append_result', lambda args, state: appended.append(args))
    saved = []
    monkeypatch.setattr(worker, 'save_progress', lambda p, state: saved.append(p.copy()))

    # run
    worker.process_name('Carol', state, event_year=1780, event_x=0)

    # append should never be called
    assert appended == []
    # progress for Carol should record error message
    assert 'Carol' in prog and prog['Carol'].startswith('error:')
    # save_progress should have been called with error in prog
    assert saved == [prog.copy()]
