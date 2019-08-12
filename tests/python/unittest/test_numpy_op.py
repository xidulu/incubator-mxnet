# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# pylint: skip-file
from __future__ import absolute_import
import numpy as _np
import mxnet as mx
from mxnet import np, npx
from mxnet.base import MXNetError
from mxnet.gluon import HybridBlock
from mxnet.base import MXNetError
from mxnet.test_utils import same, assert_almost_equal, rand_shape_nd, rand_ndarray
from mxnet.test_utils import check_numeric_gradient, use_np
from common import assertRaises, with_seed
import random
import collections


@with_seed()
@use_np
def test_np_sum():
    class TestSum(HybridBlock):
        def __init__(self, axis=None, dtype=None, keepdims=False):
            super(TestSum, self).__init__()
            self._axis = axis
            self._dtype = dtype
            self._keepdims = keepdims

        def hybrid_forward(self, F, a, *args, **kwargs):
            return F.np.sum(a, axis=self._axis, dtype=self._dtype, keepdims=self._keepdims)

    def is_int(dtype):
        return 'int' in dtype

    in_data_dim = random.choice([2, 3, 4])
    shape = rand_shape_nd(in_data_dim, dim=3)
    acc_type = {'float16': 'float32', 'float32': 'float64', 'float64': 'float64',
                'int8': 'int32', 'int32': 'int64', 'int64': 'int64'}
    for hybridize in [False, True]:
        for keepdims in [True, False]:
            for axis in ([i for i in range(in_data_dim)] + [(), None]):
                for itype in ['float16', 'float32', 'float64', 'int8', 'int32', 'int64']:
                    for dtype in ['float16', 'float32', 'float64', 'int8', 'int32', 'int64']:
                        if is_int(dtype) and not is_int(itype):
                            continue
                        # test gluon
                        test_sum = TestSum(axis=axis, dtype=dtype, keepdims=keepdims)
                        if hybridize:
                            test_sum.hybridize()
                        if is_int(itype):
                            x = _np.random.randint(-128, 128, shape, dtype=itype)
                            x = mx.nd.array(x)
                        else:
                            x = mx.nd.random.uniform(-1.0, 1.0, shape=shape, dtype=itype)
                        x = x.as_np_ndarray()
                        x.attach_grad()
                        expected_ret = _np.sum(x.asnumpy(), axis=axis, dtype=acc_type[itype], keepdims=keepdims)
                        expected_ret = expected_ret.astype(dtype)
                        with mx.autograd.record():
                            y = test_sum(x)
                        assert y.shape == expected_ret.shape
                        assert_almost_equal(y.asnumpy(), expected_ret, rtol=1e-3 if dtype == 'float16' else 1e-3,
                                            atol=1e-5 if dtype == 'float16' else 1e-5)

                        y.backward()
                        assert same(x.grad.asnumpy(), _np.ones(shape=x.shape, dtype=x.dtype))

                        # test numeric
                        if itype == 'float32' and dtype == 'float32':
                            x_sym = mx.sym.Variable("x").as_np_ndarray()
                            mx_sym = mx.sym.np.sum(x_sym, axis=axis, dtype=dtype, keepdims=keepdims).as_nd_ndarray()
                            check_numeric_gradient(mx_sym, [x.as_nd_ndarray()],
                                                   numeric_eps=1e-3, rtol=1e-3, atol=1e-4, dtype=_np.float32)

                        # test imperative
                        mx_out = np.sum(x, axis=axis, dtype=dtype, keepdims=keepdims)
                        np_out = _np.sum(x.asnumpy(), axis=axis, dtype=acc_type[itype], keepdims=keepdims).astype(dtype)
                        assert_almost_equal(mx_out.asnumpy(), np_out, rtol=1e-3, atol=1e-5)


@with_seed()
@use_np
def test_npx_slice():
    class TestSlice(HybridBlock):
        def __init__(self, begin, end, step):
            super(TestSlice, self).__init__()
            self._begin = begin
            self._end = end
            self._step = step

        def hybrid_forward(self, F, a):
            return F.npx.slice(a, begin=self._begin, end=self._end, step=self._step)

    shape = (8, 16, 9, 9)
    np_array = _np.arange(_np.prod(shape), dtype='int32').reshape(shape)
    configs = [
        ([], [], None),
        ([], [], []),
        ([1], [4], None),
        ([1], [10], [3]),
        ([10], [0], [-2]),
        ([None], [None], [None]),
        ([None], [None], [-1]),
        ([10], [None], [-1]),
        ([1, 0, 3], [-2, 10, -4], [None, 2, 3]),
        ([-2, -3, -5, -6], [1, 3, 4, 5], None),
        ([-2, -3, -5, -6], [1, 3, 4, 5], [-1, -2, -3, -4]),
        ([2, -3, -5, -6], [2, 3, 4, 5], None),
        ([2, -3, -5, 5], [3, 3, 4, 5], None),
    ]

    for hybridize in [True, False]:
        for config in configs:
            start, end, step = config[0], config[1], config[2]
            test_slice = TestSlice(begin=start, end=end, step=step)
            if hybridize:
                test_slice.hybridize()

            a = np.array(np_array, dtype=np_array.dtype)
            a.attach_grad()
            basic_index = tuple([
                slice(start[i], end[i], step[i]) if step is not None else slice(start[i], end[i])
                for i in range(len(start))
            ])
            expected_ret = np_array[basic_index]
            with mx.autograd.record():
                y = test_slice(a)

            assert same(y.asnumpy(), expected_ret)

            # test backward
            mx.autograd.backward(y)
            expected_grad = _np.zeros(shape)
            expected_grad[basic_index] = 1
            assert same(a.grad.asnumpy(), expected_grad)


@with_seed()
@use_np
def test_np_logaddexp():
    @use_np
    class TestLogaddexp(HybridBlock):
        def __init__(self):
            super(TestLogaddexp, self).__init__()

        def hybrid_forward(self, F, x1, x2):
            return F.np.logaddexp(x1, x2)

    shapes = [
        ((3, 1), (3, 1)),
        ((3, 1, 2), (3, 1, 2)),
        ((1, ), (1, )),
        ((3, 0), (3, 0)),  # zero-size shape
        ((0, 1), (0, 1)),  # zero-size shape
        ((2, 0, 2), (2, 0, 2)),  # zero-size shape
        ((1, ), (3, )),  # broadcast
        ((2, 3), (2, 1)),  # broadcast
        ((1, 3), (2, 3)),  # broadcast
        ((1, 3), (2, 0, 3)),  # broadcast to zero-dim shape
        ((1, 0, 1), (3, 0, 1)),  # broadcast of zero-dim shape
        ((), ()),  # zero-dim shape
    ]
    eps = 1e-3
    # Legal shape test.
    for shape_a, shape_b in shapes:
        for hybridize in [True, False]:
            test_logaddexp = TestLogaddexp()
            if hybridize:
                test_logaddexp.hybridize()
            lhs = rand_ndarray(shape_a).as_np_ndarray()
            rhs = rand_ndarray(shape_b).as_np_ndarray()
            lhs.attach_grad()
            rhs.attach_grad()
            np_out = _np.logaddexp(lhs.asnumpy(), rhs.asnumpy())
            np_backward_lhs = _np.exp(
                lhs.asnumpy()) / (_np.exp(lhs.asnumpy()) + _np.exp(rhs.asnumpy()))
            np_backward_rhs = _np.exp(
                rhs.asnumpy()) / (_np.exp(lhs.asnumpy()) + _np.exp(rhs.asnumpy()))
            with mx.autograd.record():
                mx_out = test_logaddexp(lhs, rhs)
            assert mx_out.shape == np_out.shape
            assert_almost_equal(mx_out.asnumpy(), np_out, rtol=1e-3, atol=1e-5)
            mx_out.backward()
            # For broadcast backward case,
            # reduce sum is applied on numpy result.
            for n_dim in range(len(shape_a)):
                if (shape_a[n_dim] != shape_b[n_dim]):
                    if (shape_a[n_dim] > shape_b[n_dim]):
                        np_backward_rhs = np_backward_rhs.sum(
                            axis=n_dim, keepdims=True)
                    else:
                        np_backward_lhs = np_backward_lhs.sum(
                            axis=n_dim, keepdims=True)
            assert_almost_equal(lhs.grad.asnumpy(),
                                np_backward_lhs, rtol=1e-3, atol=1e-5)
            assert_almost_equal(rhs.grad.asnumpy(),
                                np_backward_rhs, rtol=1e-3, atol=1e-5)
            # Test imperative once again
            mx_out = np.logaddexp(lhs, rhs)
            np_out = _np.logaddexp(lhs.asnumpy(), rhs.asnumpy())
            assert_almost_equal(mx_out.asnumpy(), np_out, rtol=1e-3, atol=1e-5)

        # Range case.
    x = [1000000, -1000000, 1000200, -1000200]
    y = [1000200, -1000200, 1000000, -1000000]
    z = [1000200, -1000000, 1000200, -1000000]
    for dt in ['float64']:
        logxf = np.array(x, dtype=dt)
        logyf = np.array(y, dtype=dt)
        logzf = np.array(z, dtype=dt)
        assert_almost_equal(np.logaddexp(logxf, logyf).asnumpy(),
                            logzf.asnumpy())

        # Bad shape case.
    bad_shapes = [((4, 5), (2, 3)), ((3, 4, 5), (6, ))]
    for shape_a, shape_b in bad_shapes:
        a = mx.nd.array(random.random()) if len(
            shape_a) == 0 else rand_ndarray(shape_a)
        b = mx.nd.array(random.random()) if len(
            shape_b) == 0 else rand_ndarray(shape_b)
        try:
            mx_res = np.logaddexp(a.as_np_ndarray(), b.as_np_ndarray())
        except mx.base.MXNetError:
            continue
        assert False


if __name__ == '__main__':
    import nose
    nose.runmodule()
