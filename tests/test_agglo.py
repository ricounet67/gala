from __future__ import absolute_import
import os
from six.moves import map
from six.moves import range

D = os.path.dirname(os.path.abspath(__file__)) + '/'

import numpy as np
from numpy.testing import assert_equal, assert_allclose

from gala import agglo
from gala import evaluate as ev


test_idxs = list(range(6))
num_tests = len(test_idxs)
fns = [D + 'toy-data/test-%02i-probabilities.txt' % i for i in test_idxs]
probs = list(map(np.loadtxt, fns))
fns = [D + 'toy-data/test-%02i-watershed.txt' % i for i in test_idxs]
wss = [np.loadtxt(fn, dtype=np.uint32) for fn in fns]
fns = [D + 'toy-data/test-%02i-groundtruth.txt' % i for i in test_idxs]
results = list(map(np.loadtxt, fns))

landscape = np.array([1,0,1,2,1,3,2,0,2,4,1,0])

def test_8_connectivity():
    p = np.array([[0,0.5,0],[0.5,1.0,0.5],[0,0.5,0]])
    ws = np.array([[1,0,2],[0,0,0],[3,0,4]], np.uint32)
    g = agglo.Rag(ws, p, connectivity=2)
    assert_equal(agglo.boundary_mean(g, 1, 2), 0.75)
    assert_equal(agglo.boundary_mean(g, 1, 4), 1.0)

def test_empty_rag():
    g = agglo.Rag()
    assert_equal(g.nodes(), [])
    assert_equal(g.copy().nodes(), [])

def test_agglomeration():
    i = 1
    g = agglo.Rag(wss[i], probs[i], agglo.boundary_mean, 
        normalize_probabilities=True)
    g.agglomerate(0.51)
    assert_allclose(ev.vi(g.get_segmentation(), results[i]), 0.0,
                    err_msg='Mean agglomeration failed.')

def test_ladder_agglomeration():
    i = 2
    g = agglo.Rag(wss[i], probs[i], agglo.boundary_mean,
        normalize_probabilities=True)
    g.agglomerate_ladder(2)
    g.agglomerate(0.5)
    assert_allclose(ev.vi(g.get_segmentation(), results[i]), 0.0,
                    err_msg='Ladder agglomeration failed.')

def test_no_dam_agglomeration():
    i = 3
    g = agglo.Rag(wss[i], probs[i], agglo.boundary_mean, 
        normalize_probabilities=True)
    g.agglomerate(0.75)
    assert_allclose(ev.vi(g.get_segmentation(), results[i]), 0.0,
                    err_msg='No dam agglomeration failed.')


def test_mito():
    i = 5
    def frozen(g, i):
        "hardcoded frozen nodes representing mitochondria"
        return i in [3, 4]
    g = agglo.Rag(wss[i], probs[i], agglo.no_mito_merge(agglo.boundary_mean),
                  normalize_probabilities=True, isfrozennode=frozen)
    g.agglomerate(0.15)
    g.merge_priority_function = agglo.mito_merge()
    g.rebuild_merge_queue()
    g.agglomerate(1.0)
    assert_allclose(ev.vi(g.get_segmentation(), results[i]), 0.0,
                    err_msg='Mito merge failed')


if __name__ == '__main__':
    from numpy import testing
    testing.run_module_suite()

