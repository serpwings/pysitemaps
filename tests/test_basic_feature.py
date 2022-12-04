import pytest
from pysitemaps import Sitemap, Url


def test_script_url():
    ut = Url("b.html", "2021", ["c.png", "b.png"])
    assert ut.loc == "b.html", "test passed"


def test_script_sitemap():
    smp = Sitemap()
    smp.add_url(Url("a.html", "2022", ["abc.png"]))
    smp.add_url(Url("b.html", "2022", ["debc.png"]))

    assert len(smp.list_of_urls) == 2, "test passed"
