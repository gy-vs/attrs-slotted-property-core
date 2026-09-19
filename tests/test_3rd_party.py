# SPDX-License-Identifier: MIT

"""
Tests for compatibility against other Python modules.
"""

import functools

import pytest

from hypothesis import given

import attr

from attr._compat import PY_3_8_PLUS

from .strategies import simple_classes


cloudpickle = pytest.importorskip("cloudpickle")


class TestCloudpickleCompat:
    """
    Tests for compatibility with ``cloudpickle``.
    """

    @given(simple_classes(cached_property=False))
    def test_repr(self, cls):
        """
        attrs instances can be pickled and un-pickled with cloudpickle.
        """
        inst = cls()
        # Exact values aren't a concern so long as neither direction
        # raises an exception.
        pkl = cloudpickle.dumps(inst)
        cloudpickle.loads(pkl)

    @pytest.mark.skipif(not PY_3_8_PLUS, reason="cached_property is 3.8+")
    def test_cached_property(self):
        """
        Slotted classes with cached properties stay cloudpickle-able: the
        generated __getattr__ holds no unpicklable state and the cache is
        recomputed after unpickling.
        """

        @attr.s(slots=True)
        class A:
            x = attr.ib()

            @functools.cached_property
            def f(self):
                return self.x * 2

        a = A(21)
        assert a.f == 42

        a2 = cloudpickle.loads(cloudpickle.dumps(a))
        assert a2.f == 42
        assert not hasattr(a2, "__dict__")

        cls = cloudpickle.loads(cloudpickle.dumps(A))
        assert cls(1).f == 2
