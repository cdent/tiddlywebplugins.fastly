
def test_compile():
    try:
        import tiddlywebplugins.fastly
        assert True
    except ImportError, exc:
        assert False, exc
