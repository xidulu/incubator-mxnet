import weakref

__all__ = ["Transformation", "ExpTransform", "AffineTransform"]

class Transformation(object):
    r"""Abstract class for implementing invertible transformation
    with computable log  det jacobians
    
    Attributes
    ----------
    bijective : bool
        
    """
    bijective = False
    def __init__(self, F=None):
        self._inv = None
        self._F = F
        super(Transformation, self).__init__()

    @property
    def F(self):
        return self._F

    @F.setter
    def F(self, value):
        self._F = value

    @property
    def inv(self):
        inv = None
        if self._inv is not None:
            inv = self._inv()
        if inv is None:
            inv = _InverseTransformation(self)
            self._inv = weakref.ref(inv)
        return inv

    def __call__(self, x):
        return self._forward_compute(x)

    def _inv_call(self, y):
        return self._inverse_compute(y)

    def _forward_compute(self, x):
        raise NotImplementedError

    def _inverse_compute(self, x):
        raise NotImplementedError
    
    def log_det_jacobian(self, x, y):
        """
        Compute the value of log(|dy/dx|)
        """
        raise NotImplementedError


class _InverseTransformation(Transformation):
    """
    A private class representing the invert of `Transformation`,
    which should be accessed through `Transformation.inv` property.
    """
    def __init__(self, forward_transformation):
        super(_InverseTransformation, self).__init__()
        self._inv = forward_transformation

    @property
    def inv(self):
        return self._inv

    def __call__(self, x):
        return self._inv._inverse_compute(x)

    def log_det_jacobian(self, x, y):
        return -self._inv.log_det_jacobian(y, x)


class ExpTransform(Transformation):
    r"""
    Perform the exponential transform: y = exp{x}.
    """

    def _forward_compute(self, x):
        return self.F.np.exp(x)

    def _inverse_compute(self, y):
        return self.F.np.log(y)

    def log_det_jacobian(self, x, y):
        return x

class AffineTransform(Transformation):
    r"""
    Perform pointwise affine transform: y = loc + scale * x.
    """

    def __init__(self, loc, scale):
        super(AffineTransform, self).__init__()
        self._loc = loc
        self._scale = scale

    def _forward_compute(self, x):
        return self._loc + self._scale * x
    
    def _inverse_compute(self, y):
        return (y - self._loc) /  self._scale

    def log_det_jacobian(self, x, y):
        abs_fn = self.F.np.abs
        log_fn = self.F.np.log
        ones_fn = self.F.np.ones_like
        # FIXME: handle multivariate cases.
        return ones_fn(x) * log_fn(abs_fn(self._scale))