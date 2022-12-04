from pysitemaps import Sitemap, Url

if __name__ == "__main__":

    smp = Sitemap()
    smp.add_url(Url("a.html", "2022", ["abc.png"]))
    smp.add_url(Url("b.html", "2021", ["def.png"]))
    smp.add_url(Url("b.html", "2021", ["c.png", "b.png"]))
    smp.process()
    smp.write()
