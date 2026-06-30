import pytest
from python.load_balancer.balancer import LoadBalancer

@pytest.fixture
def lb():
    return LoadBalancer()

def test_round_robin(lb):
    lb.strategy = "round_robin"
    s1 = lb._select_server()
    s2 = lb._select_server()
    s3 = lb._select_server()
    s4 = lb._select_server()
    assert {s1, s2, s3} == {"server1", "server2", "server3"}
    assert s1 == s4

def test_least_load(lb):
    lb.strategy = "least_load"
    lb.server_stats["server1"]["requests"] = 100
    lb.server_stats["server2"]["requests"] = 10
    lb.server_stats["server3"]["requests"] = 100
    assert lb._select_server() == "server2"

def test_ai_guided_drains_high_prob(lb):
    lb.strategy = "ai_guided"
    lb.server_stats["server1"]["fault_prob"] = 0.95
    lb.server_stats["server2"]["fault_prob"] = 0.05
    lb.server_stats["server3"]["fault_prob"] = 0.05
    selections = [lb._select_server() for _ in range(100)]
    assert selections.count("server1") < 20

def test_excluded_states(lb):
    lb.strategy = "round_robin"
    lb.server_stats["server1"]["status"] = "draining"
    lb.server_stats["server2"]["status"] = "restarting"
    lb.server_stats["server3"]["status"] = "ok"
    for _ in range(10):
        assert lb._select_server() == "server3"
