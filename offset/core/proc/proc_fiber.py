import threading

import fibers

_tls = threading.local()

def _proc_getcurrent():
    try:
        return _tls.current_proc
    except AttributeError:
        return _proc_getmain()

def _proc_getmain():
    try:
        return _tls.main_proc
    except AttributeError:
        _tls.main_proc = MainProc()
        return _tls.main_proc

class Proc(object):

    def __init__(self, func, args, kwargs):

        def _run():
            _tls.current_proc = self
            self._is_started = 1
            return func(*args, **kwargs)

        self.fiber = fibers.Fiber(_run)
        self.waiting = False
        self.sleeping = False
        self._is_started = 0

    def switch(self):
        current = _proc_getcurrent()
        try:
            self.fiber.switch()
        finally:
            _tls.current_proc = current

    def throw(self, *args):
        current = _proc_getcurrent()
        try:
            self.fiber.throw(*args)
        finally:
            _tls.current_proc = current

    def is_alive(self):
        return self._is_started < 0 or self.fiber.is_alive()

class MainProc(Proc):

    def __init__(self):
        self._is_started = -1
        self.fiber = fibers.current()

current = _proc_getcurrent
