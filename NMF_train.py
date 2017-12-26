import numpy as np
from scipy.sparse import coo_matrix, load_npz
import math

def train(R, iterations, k, alpha=0.0001, beta=0.001, target_error=None):
    """
    R is scipy.sparse.coo_matrix
    The error doesn't compute zero term in R
    R = P * Q
    (m*n) = (m*k) * (k*n)
    """
    assert isinstance(R, coo_matrix)

    def _Rij(i, j):
        for ii in range(R_indices.shape[0]):
            if (R_indices[ii, 0] == i) and (R_indices[ii, 1] == j):
                return R_data[ii]
        raise IndexError("R(%d, %d) is zero term" % (i, j))

    def _sum_kPQ(i, j):
        sum = 0
        for kk in range(k):
            sum = sum + P[i, kk] * Q[kk, j]
        return sum

    def _loss():
        loss = 0
        for c in range(R_indices.shape[0]):
            i = R_indices[c, 0]
            j = R_indices[c, 1]
            loss = loss + math.sqrt((R_data[c] - _sum_kPQ(i, j))**2)
            if (c+1) % 100000 == 0:
                print("loss iter %d in %d" % ((c+1), R_indices.shape[0]))
        return loss

    m, n = np.shape(R)
    P = np.mat(np.random.random([m, k]))
    Q = np.mat(np.random.random([k, n]))
    R_indices = np.mat([R.row, R.col]).transpose()
    R_data = R.data

    for i_count in range(iterations):
        print("iteration %d..." % (i_count+1))
        for c in range(R_indices.shape[0]):
            i = R_indices[c, 0]
            j = R_indices[c, 1]
            P_next = P
            Q_next = Q
            e = R_data[c] - _sum_kPQ(i, j)
            for kk in range(k):
                P_next[i, kk] = P[i, kk] - 2*alpha*(e*Q[kk, j] - beta*P[i, kk])
                Q_next[kk, j] = Q[kk, j] - 2*alpha*(e*P[i, kk] - beta*Q[kk, j])
                P = P_next
                Q = Q_next
            if (c+1) % 100000 == 0:
                print("point iter %d in %d" % ((c+1), R_indices.shape[0]))
        loss = _loss()
        if target_error is not None:
            if loss < target_error:
                print("finish training at iteration %d" % (i_count + 1))
                print("loss: %0.4f" % loss)
                break
        if (i_count + 1) % 1:
            print("iteration %d loss: %0.4f" % ((i_count + 1), loss))
    return P, Q


if __name__ == "__main__":
    R = load_npz("data/r.npz").tocoo()
    P, Q = train(R, 100000, k=5)
    print(P)
    print(Q)