from pysitemaps import Sitemap, Url, XmlDocument
from pprint import pprint


def demo_read_sitemap():
    smp = Sitemap(
        website_name="seowings.org",
    )
    smp.read("sitemap.xml")
    pprint(smp.as_dict())


def demo_create_sitemap():
    smp = Sitemap(
        website_name="https://www.seowings.org/",
        file_path="sitemap.xml",
        xsl_file="https://www.seowings.org/main-sitemap.xsl",
    )
    smp.append(
        Url(
            loc="https://www.seowings.org/a.html",
            lastmod="2022-12-25",
            images_loc=["https://www.seowings.org/a1.png"],
        )
    )
    smp.append(
        {
            "loc": "https://www.seowings.org/b.html",
            "lastmod": "2023-05-01",
            "images_loc": [
                "https://www.seowings.org/b1.png",
                "https://www.seowings.org/b2.png",
            ],
        }
    )
    smp.write()
    pprint(smp.as_dict())


def demo_locate_sitemap():
    smp = Sitemap(website_name="https://www.seowings.org/")
    smp.fetch(include_urls=False)
    print(smp.as_dict())


def demo_fetch_sitemap():
    smp = Sitemap(website_name="https://www.seowings.org/")
    smp.fetch(include_urls=True)
    print(smp.as_dict())


def demo_fetch_index_sitemap():
    smp = Sitemap(website_name="https://www.dw.com/")
    smp.fetch(include_urls=False)
    print(smp.as_dict())


def demo_create_xml_doc():
    from datetime import datetime

    news_sitemap = XmlDocument(
        "sitemap-news.xml",
        lastmod=datetime.now().strftime("%Y-%m-%d"),
        include_urls=False,
    )
    news_sitemap.add_object(Url("b.html", "2023-05-02", ["img1.png", "img2.png"]))
    news_sitemap.add_url(
        loc="c.html", lastmod="2023-01-02", images_loc=["img4.png", "img5.png"]
    )
    news_sitemap.add_from_text(
        """
        <urlset xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1" xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>z.html</loc>
                <lastmod>2022</lastmod>
                <image:image>
                    <image:loc>z.png</image:loc>
                </image:image>
            </url>
            <url>
                <loc>dz.html</loc>
                <lastmod>2022</lastmod>
                <image:image>
                    <image:loc>z.png</image:loc>
                </image:image>
                <image:image>
                    <image:loc>a.png</image:loc>
                </image:image>
            </url>
        </urlset>
        """
    )

    print(news_sitemap.as_dict())


if __name__ == "__main__":
    demo_create_sitemap()
    demo_read_sitemap()
    demo_locate_sitemap()
    demo_fetch_sitemap()
    demo_fetch_index_sitemap()
    demo_create_xml_doc()
