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

"""Namespace for operators used in Gluon dispatched by F=ndarray."""
from __future__ import absolute_import
import numpy as np
from ...context import current_context
from . import _internal as _npi
from ..ndarray import NDArray


__all__ = ['randint', 'uniform', 'normal', "choice", "rand", "multinomial", "multivariate_normal",
           "shuffle", 'gamma', 'exponential']


def randint(low, high=None, size=None, dtype=None, ctx=None, out=None):
    r"""Return random integers from `low` (inclusive) to `high` (exclusive).

    Return random integers from the "discrete uniform" distribution of
    the specified dtype in the "half-open" interval [`low`, `high`). If
    `high` is None (the default), then results are from [0, `low`).

    Parameters
    ----------
    low : int
        Lowest (signed) integer to be drawn from the distribution (unless
        ``high=None``, in which case this parameter is one above the
        *highest* such integer).
    high : int, optional
        If provided, one above the largest (signed) integer to be drawn
        from the distribution (see above for behavior if ``high=None``).
    size : int or tuple of ints, optional
        Output shape.  If the given shape is, e.g., ``(m, n, k)``, then
        ``m * n * k`` samples are drawn.  Default is None, in which case a
        single value is returned.
    dtype : dtype, optional
        Desired dtype of the result. All dtypes are determined by their
        name, i.e., 'int64', 'int', etc, so byteorder is not available
        and a specific precision may have different C types depending
        on the platform. The default value is 'np.int'.
    ctx : Context, optional
        Device context of output. Default is current context.
    out : ndarray, optional
        The output ndarray (default is `None`).

    Returns
    -------
    out : ndarray of ints
        `size`-shaped array of random integers from the appropriate
        distribution, or a single such random int if `size` not provided.

    Examples
    --------
    >>> np.random.randint(2, size=10)
    array([1, 0, 0, 0, 1, 1, 0, 0, 1, 0])
    >>> np.random.randint(1, size=10)
    array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    Generate a 2 x 4 array of ints between 0 and 4, inclusive:

    >>> np.random.randint(5, size=(2, 4))
    array([[4, 0, 2, 1],
        [3, 2, 2, 0]])
    """
    if dtype is None:
        dtype = 'int'
    if ctx is None:
        ctx = current_context()
    if size is None:
        size = ()
    if high is None:
        high = low
        low = 0
    return _npi.random_randint(low, high, shape=size, dtype=dtype, ctx=ctx, out=out)


def uniform(low=0.0, high=1.0, size=None, dtype=None, ctx=None, out=None):
    r"""Draw samples from a uniform distribution.

    Samples are uniformly distributed over the half-open interval
    ``[low, high)`` (includes low, but excludes high).  In other words,
    any value within the given interval is equally likely to be drawn
    by `uniform`.

    Parameters
    ----------
    low : float, ndarray, optional
        Lower boundary of the output interval.  All values generated will be
        greater than or equal to low.  The default value is 0.
    high : float, ndarray, optional
        Upper boundary of the output interval.  All values generated will be
        less than high.  The default value is 1.0.
    size : int or tuple of ints, optional
        Output shape.  If the given shape is, e.g., ``(m, n, k)``, then
        ``m * n * k`` samples are drawn.  If size is ``None`` (default),
        a scalar tensor containing a single value is returned if
        ``low`` and ``high`` are both scalars.
    dtype : {'float16', 'float32', 'float64'}, optional
        Data type of output samples. Default is 'float32'
    ctx : Context, optional
        Device context of output. Default is current context.
    out : ``ndarray``, optional
        Store output to an existing ``ndarray``.

    Returns
    -------
    out : ndarray
        Drawn samples from the parameterized uniform distribution.
    """
    from ...numpy import ndarray as np_ndarray
    input_type = (isinstance(low, np_ndarray), isinstance(high, np_ndarray))
    if dtype is None:
        dtype = 'float32'
    if ctx is None:
        ctx = current_context()
    if size == ():
        size = None
    if input_type == (True, True):
        return _npi.uniform(low, high, low=None, high=None, size=size,
                            ctx=ctx, dtype=dtype, out=out)
    elif input_type == (False, True):
        return _npi.uniform(high, low=low, high=None, size=size,
                            ctx=ctx, dtype=dtype, out=out)
    elif input_type == (True, False):
        return _npi.uniform(low, low=None, high=high, size=size,
                            ctx=ctx, dtype=dtype, out=out)
    else:
        return _npi.uniform(low=low, high=high, size=size,
                            ctx=ctx, dtype=dtype, out=out)


def normal(loc=0.0, scale=1.0, size=None, dtype=None, ctx=None, out=None):
    r"""Draw random samples from a normal (Gaussian) distribution.

    Samples are distributed according to a normal distribution parametrized
    by *loc* (mean) and *scale* (standard deviation).


    Parameters
    ----------
    loc : float, optional
        Mean (centre) of the distribution.
    scale : float, optional
        Standard deviation (spread or "width") of the distribution.
    size : int or tuple of ints, optional
        Output shape. If the given shape is, e.g., `(m, n, k)`, then `m * n * k`
        samples are drawn. If size is `None` (default), a scalar tensor containing
        a single value is returned if loc and scale are both scalars.
    dtype : {'float16', 'float32', 'float64'}, optional
        Data type of output samples. Default is 'float32'
    ctx : Context, optional
        Device context of output. Default is current context.
    out : ``ndarray``, optional
        Store output to an existing ``ndarray``.

    Returns
    -------
    out : ndarray
        Drawn samples from the parameterized normal distribution.
    """
    from ...numpy import ndarray as np_ndarray
    input_type = (isinstance(loc, np_ndarray), isinstance(scale, np_ndarray))
    if dtype is None:
        dtype = 'float32'
    if ctx is None:
        ctx = current_context()
    if size == ():
        size = None
    if input_type == (True, True):
        return _npi.normal(loc, scale, loc=None, scale=None, size=size,
                           ctx=ctx, dtype=dtype, out=out)
    elif input_type == (False, True):
        return _npi.normal(scale, loc=loc, scale=None, size=size,
                           ctx=ctx, dtype=dtype, out=out)
    elif input_type == (True, False):
        return _npi.normal(loc, loc=None, scale=scale, size=size,
                           ctx=ctx, dtype=dtype, out=out)
    else:
        return _npi.normal(loc=loc, scale=scale, size=size,
                           ctx=ctx, dtype=dtype, out=out)


def multinomial(n, pvals, size=None):
    r"""multinomial(n, pvals, size=None)

    Draw samples from a multinomial distribution.

    The multinomial distribution is a multivariate generalisation of the binomial distribution.
    Take an experiment with one of ``p`` possible outcomes. An example of such an experiment is throwing a dice,
    where the outcome can be 1 through 6. Each sample drawn from the distribution represents n such experiments.
    Its values, ``X_i = [X_0, X_1, ..., X_p]``, represent the number of times the outcome was ``i``.

    Parameters
    ----------
    n : int
        Number of experiments.
    pvals : sequence of floats, length p
        Probabilities of each of the p different outcomes. These should sum to 1.
    size : int or tuple of ints, optional
        Output shape. If the given shape is, e.g., ``(m, n, k)``, then ``m * n * k`` samples
        are drawn. Default is None, in which case a single value is returned.

    Returns
    -------
    out : ndarray
        The drawn samples, of shape size, if that was provided. If not, the shape is ``(N,)``.
        In other words, each entry ``out[i,j,...,:]`` is an N-dimensional value drawn from the distribution.

    Examples
    --------
    Throw a dice 1000 times, and 1000 times again:

    >>> np.random.multinomial(1000, [1/6.]*6, size=2)
    array([[164, 161, 179, 158, 150, 188],
           [178, 162, 177, 143, 163, 177]])

    A loaded die is more likely to land on number 6:

    >>> np.random.multinomial(100, [1/7.]*5 + [2/7.])
    array([19, 14, 12, 11, 21, 23])

    >>> np.random.multinomial(100, [1.0 / 3, 2.0 / 3])
    array([32, 68])
    """
    if isinstance(pvals, NDArray):
        return _npi.multinomial(pvals, pvals=None, n=n, size=size)
    else:
        if isinstance(pvals, np.ndarray):
            raise ValueError('numpy ndarray is not supported!')
        if any(isinstance(i, list) for i in pvals):
            raise ValueError('object too deep for desired array')
        return _npi.multinomial(n=n, pvals=pvals, size=size)


def multivariate_normal(mean, cov, size=None, check_valid=None, tol=None):
    """
    multivariate_normal(mean, cov, size=None, check_valid=None, tol=None)

    Draw random samples from a multivariate normal distribution.

    The multivariate normal, multinormal or Gaussian distribution is a
    generalization of the one-dimensional normal distribution to higher
    dimensions.  Such a distribution is specified by its mean and
    covariance matrix.  These parameters are analogous to the mean
    (average or "center") and variance (standard deviation, or "width,"
    squared) of the one-dimensional normal distribution.

    This operator is a little different from the one in official NumPy.
    The official NumPy operator only accepts 1-D ndarray as mean and 2-D ndarray as cov,
    whereas the operator in DeepNumPy supports batch operation and auto-broadcasting.

    Both `mean` and `cov` may have any number of leading dimensions, which correspond
    to a batch shape. They are not necessarily assumed to have the same batch shape,
    just ones which can be broadcasted.

    Parameters
    ----------
    mean : K-D ndarray, of shape (..., N)
        Mean of the N-dimensional distribution.
    cov : (K+1)-D ndarray, of shape (..., N, N)
        Covariance matrix of the distribution. The last two dimensions must be symmetric and
        positive-semidefinite for proper sampling.
    size : int or tuple of ints, optional
        Given a shape of, for example, ``(m,n,k)``,
        ``m*n*k`` identically distributed batchs of samples are
        generated, and packed in an `m`-by-`n`-by-`k` arrangement.
        If no shape is specified, a batch of (`N`-D) sample is returned.
    check_valid : { 'warn', 'raise', 'ignore' }, optional
        Behavior when the covariance matrix is not positive semidefinite.
        (Not supported)
    tol : float, optional
        Tolerance when checking the singular values in covariance matrix.
        cov is cast to double before the check.
        (Not supported)

    Returns
    -------
    out : ndarray
        The input shape of `mean` and `cov` should satisfy the requirements of broadcasting.
        If the parameter `size` is not provided,
        the output shape is ``np.broadcast(mean.shape, cov.shape[:-1])``.
        Otherwise, the output shape is ``size + np.broadcast(mean.shape, cov.shape[:-1])``

    Examples
    --------
    >>> mean = np.array([1, 2])
    >>> cov = np.array([[1, 0], [0, 1]])
    >>> x = np.random.multivariate_normal(mean, cov, (3, 3))
    >>> x.shape
    (3, 3, 2)

    The following is probably true, given that 0.6 is roughly twice the
    standard deviation:

    >>> list((x[0,0,:] - mean) < 0.6)
    [True, True] # random

    # Performs autobroadcasting when the batch shape of
    # `mean` and `cov` is different but compatible.

    >>> mean = np.zeros((3,2)) # shape (3, 2)
    >>> cov = np.array([[1, 0], [0, 100]]) # shape (2, 2)
    >>> x = np.random.multivariate_normal(mean, cov)
    >>> x
    array([[-1.6115597 , -8.726251  ],
           [ 2.2425299 ,  2.8104177 ],
           [ 0.36229908, -8.386591  ]])
    """
    if check_valid is not None:
        raise NotImplementedError('Parameter `check_valid` is not supported')
    if tol is not None:
        raise NotImplementedError('Parameter `tol` is not supported')
    return _npi.mvn_fallback(mean, cov, size=size)


def choice(a, size=None, replace=True, p=None, ctx=None, out=None):
    r"""Generates a random sample from a given 1-D array

    Parameters
    -----------
    a : 1-D array-like or int
        If an ndarray, a random sample is generated from its elements.
        If an int, the random sample is generated as if a were np.arange(a)
    size : int or tuple of ints, optional
        Output shape.  If the given shape is, e.g., ``(m, n, k)``, then
        ``m * n * k`` samples are drawn.  Default is None, in which case a
        single value is returned.
    replace : boolean, optional
        Whether the sample is with or without replacement
    p : 1-D array-like, optional
        The probabilities associated with each entry in a.
        If not given the sample assumes a uniform distribution over all
        entries in a.
    ctx : Context, optional
        Device context of output. Default is current context.

    Returns
    --------
    samples : ndarray
        The generated random samples

    Examples
    ---------
    Generate a uniform random sample from np.arange(5) of size 3:

    >>> np.random.choice(5, 3)
    array([0, 3, 4])
    >>> #This is equivalent to np.random.randint(0,5,3)

    Generate a non-uniform random sample from np.arange(5) of size 3:

    >>> np.random.choice(5, 3, p=[0.1, 0, 0.3, 0.6, 0])
    array([3, 3, 0])

    Generate a uniform random sample from np.arange(5) of size 3 without
    replacement:

    >>> np.random.choice(5, 3, replace=False)
    array([3,1,0])
    >>> #This is equivalent to np.random.permutation(np.arange(5))[:3]

    Generate a non-uniform random sample from np.arange(5) of size
    3 without replacement:

    >>> np.random.choice(5, 3, replace=False, p=[0.1, 0, 0.3, 0.6, 0])
    array([2, 3, 0])
    """
    from ...numpy import ndarray as np_ndarray
    if ctx is None:
        ctx = current_context()
    if size == ():
        size = None
    if isinstance(a, np_ndarray):
        ctx = None
        if p is None:
            indices = _npi.choice(a, a=None, size=size,
                                  replace=replace, ctx=ctx, weighted=False)
            return _npi.take(a, indices)
        else:
            indices = _npi.choice(a, p, a=None, size=size,
                                  replace=replace, ctx=ctx, weighted=True)
            return _npi.take(a, indices)
    else:
        if p is None:
            return _npi.choice(a=a, size=size, replace=replace, ctx=ctx, weighted=False, out=out)
        else:
            return _npi.choice(p, a=a, size=size, replace=replace, ctx=ctx, weighted=True, out=out)


def exponential(scale, size):
    r"""Draw samples from an exponential distribution.
    Parameters
    ----------
    scale : float or array_like of floats
        The scale parameter, :math:`\beta = 1/\lambda`. Must be
        non-negative.
    size : int or tuple of ints, optional
        Output shape.  If the given shape is, e.g., ``(m, n, k)``, then
        ``m * n * k`` samples are drawn.  If size is ``None`` (default),
        a single value is returned if ``scale`` is a scalar.  Otherwise,
        ``np.array(scale).size`` samples are drawn.
    Returns
    -------
    out : ndarray or scalar
        Drawn samples from the parameterized exponential distribution.
    """
    from ...numpy import ndarray as np_ndarray
    tensor_type_name = np_ndarray
    if size == ():
        size = None
    is_tensor = isinstance(scale, tensor_type_name)
    if is_tensor:
        return _npi.exponential(scale, scale=None, size=size)
    else:
        return _npi.exponential(scale=scale, size=size)


def gamma(shape, scale=1.0, size=None, dtype=None, ctx=None, out=None):
    """Draw samples from a Gamma distribution.

    Samples are drawn from a Gamma distribution with specified parameters,
    `shape` (sometimes designated "k") and `scale` (sometimes designated
    "theta"), where both parameters are > 0.

    Parameters
    ----------
    shape : float or array_like of floats
        The shape of the gamma distribution. Should be greater than zero.
    scale : float or array_like of floats, optional
        The scale of the gamma distribution. Should be greater than zero.
        Default is equal to 1.
    size : int or tuple of ints, optional
        Output shape.  If the given shape is, e.g., ``(m, n, k)``, then
        ``m * n * k`` samples are drawn.  If size is ``None`` (default),
        a single value is returned if ``shape`` and ``scale`` are both scalars.
        Otherwise, ``np.broadcast(shape, scale).size`` samples are drawn.
    ctx : Context, optional
        Device context of output. Default is current context.

    Returns
    -------
    out : ndarray or scalar
        Drawn samples from the parameterized gamma distribution.

    The Gamma distribution is often used to model the times to failure of
    electronic components, and arises naturally in processes for which the
    waiting times between Poisson distributed events are relevant.
    """
    from ...numpy import ndarray as np_ndarray
    input_type = (isinstance(shape, np_ndarray), isinstance(scale, np_ndarray))
    if dtype is None:
        dtype = 'float32'
    if ctx is None:
        ctx = current_context()
    if out is not None:
        size = out.shape
    if size == ():
        size = None
    if input_type == (True, True):
        return _npi.gamma(shape, scale, shape=None, scale=None, size=size,
                          ctx=ctx, dtype=dtype, out=out)
    elif input_type == (False, True):
        return _npi.gamma(scale, shape=shape, scale=None, size=size,
                          ctx=ctx, dtype=dtype, out=out)
    elif input_type == (True, False):
        return _npi.gamma(shape, shape=None, scale=scale, size=size,
                          ctx=ctx, dtype=dtype, out=out)
    else:
        return _npi.gamma(shape=shape, scale=scale, size=size,
                          ctx=ctx, dtype=dtype, out=out)

    raise ValueError("Distribution parameters must be either mxnet.numpy.ndarray or numbers")


def rand(*size, **kwargs):
    r"""Random values in a given shape.

    Create an array of the given shape and populate it with random
    samples from a uniform distribution over [0, 1).
    Parameters
    ----------
    d0, d1, ..., dn : int, optional
        The dimensions of the returned array, should be all positive.
        If no argument is given a single Python float is returned.
    Returns
    -------
    out : ndarray
       Random values.
    Examples
    --------
    >>> np.random.rand(3,2)
    array([[ 0.14022471,  0.96360618],  #random
           [ 0.37601032,  0.25528411],  #random
           [ 0.49313049,  0.94909878]]) #random
    """
    output_shape = ()
    for s in size:
        output_shape += (s,)
    return uniform(0, 1, size=output_shape, **kwargs)


def shuffle(x):
    """
    Modify a sequence in-place by shuffling its contents.

    This function only shuffles the array along the first axis of a
    multi-dimensional array. The order of sub-arrays is changed but
    their contents remain the same.

    Parameters
    ----------
    x: ndarray
        The array or list to be shuffled.

    Returns
    -------
    None

    Examples
    --------
    >>> arr = np.arange(10)
    >>> np.random.shuffle(arr)
    >>> arr
    array([5., 1., 0., 6., 7., 3., 9., 8., 4., 2.])  # random

    Multi-dimensional arrays are only shuffled along the first axis:

    >>> arr = np.arange(9).reshape((3, 3))
    >>> np.random.shuffle(arr)
    >>> arr
    array([[6., 7., 8.], # random
           [3., 4., 5.],
           [0., 1., 2.]])
    """
    _npi.shuffle(x, out=x)


def multivariate_normal(mean, cov, size=None):
    return _npi.mvn_fallback(mean, cov, shape=size)