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
    @pytest.mark.parametrize("frozen", [False, True])
    def test_cached_property(self, frozen):
        """
        Slotted classes whose cached properties are transformed by attrs can
        be pickled and un-pickled with cloudpickle.
        """

        @attr.s(slots=True, frozen=frozen)
        class A:
            x = attr.ib()

            @functools.cached_property
            def f(self):
                return self.x * 2

        inst = A(1)
        assert inst.f == 2

        pkl = cloudpickle.dumps(inst)
        new_inst = cloudpickle.loads(pkl)

        assert new_inst.x == 1
        assert new_inst.f == 2
