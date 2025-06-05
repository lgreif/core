def plugin(version: str):
    from mypy.plugin import Plugin
    class StubPlugin(Plugin):
        pass
    return StubPlugin
