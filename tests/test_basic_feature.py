import pytest
from pysitemaps import Sitemap, Url


def test_script_url():
    ut = Url("b.html", "2021", ["c.png", "b.png"])
    assert ut.loc == "b.html", "test passed"
