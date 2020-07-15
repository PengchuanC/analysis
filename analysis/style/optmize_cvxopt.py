"""
min(Y-Yt)^2, Yt=w1*X1+w2*X2+w3*X3+w4*X4+w5*X5+w6*X6+w7*X7
s.t.: sum(wi)=1, i=1,2,...,7
      wi > 0

利用cvxopt求解
"""


import numpy as np
import cvxopt as opt


def optimize(change):
    """优化求解"""
    x = np.array(change.iloc[:, 1:])
    y = np.array(change.iloc[:, 0])
    length = len(x.T)

    opt.solvers.options['show_progress'] = False
    opt.solvers.options['abstol'] = 1e-10

    p = opt.matrix(np.dot(x.T, x))
    q = -opt.matrix(np.dot(x.T, y))
    g = opt.matrix(-np.eye(length))
    h = opt.matrix([0.]*length)
    a = opt.matrix([1.]*length, (1, length))
    b = opt.matrix(1.)

    model = opt.solvers.qp(P=p, q=q, G=g, h=h, A=a, b=b)

    ret = model.get("x")
    return list(ret)


def optimize_and_r(change):
    """计算R方
    R^2 = 1 - Σ(y - y_hat)^2/Σ(y - y_mean)^2
    """
    coef = optimize(change)
    _data = change.copy()
    _data['y_hat'] = 0
    for i in range(1, len(change.columns)):
        _data['y_hat'] += _data[change.columns[i]] * coef[i - 1]
    _data['y_mean'] = _data[change.columns[0]].mean()

    r2 = 1 - ((_data[change.columns[0]] - _data.y_hat) ** 2).sum() / ((_data[change.columns[0]] - _data.y_mean) ** 2).sum()
    coef.append(r2)
    return coef
