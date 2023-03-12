#!/usr/bin/env python
# -*- coding: utf-8 -*- #

"""
pysitemaps: A Python Package for Website Sitemaps

MIT License
Copyright (c) 2023 SERP Wings www.serpwings.com
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORTS Standard Library
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

from datetime import datetime
from xml.dom import minidom
from unittest.mock import Mock

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORTS 3rd Party Libraries
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

import requests
from requests.adapters import HTTPAdapter
from requests.models import Response
from bs4 import BeautifulSoup

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# DATABASE/CONSTANTS LIST
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

XSL_ATTR_LIST = {
    "xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9",
    "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "xmlns:image": "http://www.google.com/schemas/sitemap-image/1.1",
}

HEADER = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0",
}

SITEMAP_SEARCH_PATHS = [
    "wp-sitemap.xml",
    "sitemap_index.xml",
    "sitemap.xml",
    "sitemapindex.xml",
    "sitemap-index.xml",
    "sitemap1.xml",
    "sitemap.php",
    "sitemap/",
    "sitemas/",
    "sitemas.xml",
    "sitemap.txt",
    "sitemap.xml.gz",
    "post-sitemap.xml",
    "page-sitemap.xml",
    "news-sitemap.xml",
]

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# Utility Functions
# +++++++++++++++++++++++++++++++++++++++++++++++++++++


def mock_requests_object(url: str) -> Response:
    """generate moked request objet

    Args:
        url (str): url needed to be fetched

    Returns:
        Response: request response object.
    """
    response = Mock(spec=Response)
    response.text = ""
    response.status_code = 9999
    response.url = url
    return response


def get_remote_content(url: str, max_retires: int = 5) -> Response:
    """get remote content using request library

    Args:
        url (str): url needed to be fetched
        max_retires (int, optional): maximum tries to fetch the content. Defaults to 5.

    Returns:
        Response: request response object.
    """
    try:
        s = requests.Session()
        s.mount(url, HTTPAdapter(max_retries=max_retires))
        return s.get(url, headers=HEADER)
    except:
        return mock_requests_object(url)


def get_corrected_url(url: str, fix_slash: str = "/") -> str:
    """correct url for missing slash and scheme

    Args:
        url (str): input url
        fix_slash (str, optional): text to append at the end of url. Defaults to "/".

    Returns:
        str: corrected url
    """
    if not url.startswith("http://") and not url.startswith("https://"):
        url = f"http://{url}"

    if not url.endswith(fix_slash):
        url = f"{url}{fix_slash}"

    return url


def extract_url_set(xml_as_text: str) -> list:
    """Extract Url Set

    Args:
        xml_as_text (str): xml as text data

    Returns:
        list: list of urls in a xml text.
    """
    soup = BeautifulSoup(xml_as_text, "xml")

    return [
        Url(
            loc=url.findNext("loc").text if url.findNext("loc") else "",
            lastmod=url.findNext("lastmod").text if url.findNext("lastmod") else "",
            images_loc=[
                img_loc.findNext("image:loc").text
                for img_loc in url.find_all("image:image")
            ],
        )
        for url in soup.find_all("url")
    ]


def extract_xsl_file(xml_as_text: str) -> str:
    """extract xsl file from text

    Args:
        xml_as_text (str): xml as text data

    Returns:
        str: location of xsl file
    """
    xsl_item = [item.strip() for item in xml_as_text.split("\n") if ".xsl" in item]
    if xsl_item:
        try:
            return xsl_item[0].split('href="')[-1].split('"?>')[0]
        except:
            return ""

    return ""


def extract_sub_sitemaps(xml_as_text: str, include_urls: bool = False) -> list:
    """extract sub-sitemaps from text (xml string)

    Args:
        xml_as_text (str): xml as text data
        include_urls (bool, optional): If set to ture, then all urls present in the text will be included in the retunr list. Defaults to False.

    Returns:
        list: list of sub-sitemaps
    """
    soup = BeautifulSoup(xml_as_text, features="xml")

    if len(soup.find_all("sitemapindex")) > 0:
        return [
            XmlDocument(sitemap.findNext("loc").text, include_urls=include_urls)
            for sitemap in soup.find_all("sitemap")
        ]

    return []


def search_sitemap(url: str) -> list:
    """search/locate sitemap of any url:str

    Args:
        url (str): url for which searching/locating a sitemap is required.

    Returns:
        list: list of sitemaps found.
    """
    for sitemap_path in SITEMAP_SEARCH_PATHS:
        sitemap_url = f"{url}{sitemap_path}"
        response = get_remote_content(sitemap_url)
        if response.status_code < 400:
            if response.url.endswith(".xml"):
                return [response.url]

    # extract sitemap from robots.txt
    robots_txt = f"{url}robots.txt"
    response = get_remote_content(robots_txt)
    if response:
        return list(
            set(
                [
                    item.split("Sitemap:")[-1].strip()
                    for item in response.text.split("\n")
                    if item.startswith("Sitemap:")
                ]
            )
        )

    # check home page for link rel=sitemap
    response = get_remote_content(url)
    if response:
        soup = BeautifulSoup(response.text, features="xml")
        return list(
            set(
                [
                    link["href"]
                    for link in soup.find_all("link")
                    if link.has_attr("sitemap")
                ]
            )
        )
    return []


def write_index_sitemap(
    sub_sitemaps_set: list,
    website_name: str,
    xsl_file: str = "",
    path: str = "",
    file_name: str = "sitemap_index.xml",
) -> None:
    """write index sitemap

    Args:
        sub_sitemaps_set (list): list of sub-sitemaps
        website_name (str): name of the website
        xsl_file (str, optional): location of xsl file. Defaults to "".
        path (str, optional): path/folder output location of index-sitema. Defaults to "".
        file_name (str, optional): file name of index sitemap. Defaults to "sitemap_index.xml".
    """
    dom_sitemap = minidom.Document()
    dom_sitemap.appendChild(
        dom_sitemap.createComment(f"sitemap avialble at {website_name}{file_name} ")
    )

    if xsl_file:
        node_sitemap_stylesheet = dom_sitemap.createProcessingInstruction(
            "xml-stylesheet", f'type="text/xsl" href="{xsl_file}"'
        )
        dom_sitemap.insertBefore(node_sitemap_stylesheet, dom_sitemap.firstChild)

    node_sitemapindex = dom_sitemap.createElement("sitemapindex")
    xsl_attributes = ["xmlns"]
    for xsl_attribute in xsl_attributes:
        node_sitemapindex.setAttribute(xsl_attribute, XSL_ATTR_LIST[xsl_attribute])

    dom_sitemap.appendChild(node_sitemapindex)

    for current_url in sub_sitemaps_set:
        node_sitemap = dom_sitemap.createElement("sitemap")

        node_sitemap_loc = dom_sitemap.createElement("loc")
        node_sitemap_loc.appendChild(dom_sitemap.createTextNode(current_url["loc"]))

        node_sitemap.appendChild(node_sitemap_loc)

        node_lastmod = dom_sitemap.createElement("lastmod")
        node_lastmod.appendChild(dom_sitemap.createTextNode(current_url["lastmod"]))

        node_sitemap.appendChild(node_lastmod)

        node_sitemapindex.appendChild(node_sitemap)

    dom_sitemap.appendChild(
        dom_sitemap.createComment("XML Index Sitemap generated by pysitemaps")
    )

    with open(f"{path}{file_name}", "w") as fp:
        dom_sitemap.writexml(fp, indent="", addindent="\t", newl="\n", encoding="utf-8")


def write_sub_sitemap(
    url_set: list,
    website_name: str,
    xsl_file: str = "",
    path: str = "",
    file_name: str = "sitemap.xml",
) -> None:
    """write sub sitemap

    Args:
        url_set (list): list of Urls also known as url_set
        website_name (str): name of the website
        xsl_file (str, optional): path of xsl file. Defaults to "".
        path (str, optional): path/folder location of sub-sitemap. Defaults to "".
        file_name (str, optional): output file name e.g. sitemap.xml or categories-sitemap.xml. Defaults to "sitemap.xml".
    """
    dom_sitemap = minidom.Document()
    dom_sitemap.appendChild(
        dom_sitemap.createComment(f"sitemap avialble at {website_name}{file_name} ")
    )

    if xsl_file:
        node_sitemap_stylesheet = dom_sitemap.createProcessingInstruction(
            "xml-stylesheet", f'type="text/xsl" href="{xsl_file}"'
        )
        dom_sitemap.insertBefore(node_sitemap_stylesheet, dom_sitemap.firstChild)

    node_urlset = dom_sitemap.createElement("urlset")
    xsl_attributes = ["xmlns:xsi", "xmlns:image", "xmlns"]
    for xsl_attribute in xsl_attributes:
        node_urlset.setAttribute(xsl_attribute, XSL_ATTR_LIST[xsl_attribute])

    dom_sitemap.appendChild(node_urlset)

    for current_url in url_set:
        node_url = dom_sitemap.createElement("url")

        node_url_loc = dom_sitemap.createElement("loc")
        node_url_loc.appendChild(dom_sitemap.createTextNode(current_url["loc"]))

        node_url.appendChild(node_url_loc)

        node_lastmod = dom_sitemap.createElement("lastmod")
        node_lastmod.appendChild(dom_sitemap.createTextNode(current_url["lastmod"]))

        node_url.appendChild(node_lastmod)

        for image_location in current_url["images"]:
            node_image_image = dom_sitemap.createElement("image:image")

            node_image_loc = dom_sitemap.createElement("image:loc")
            node_image_loc.appendChild(dom_sitemap.createTextNode(image_location))

            node_image_image.appendChild(node_image_loc)
            node_url.appendChild(node_image_image)

        node_urlset.appendChild(node_url)

    dom_sitemap.appendChild(
        dom_sitemap.createComment("XML Sitemap generated by pysitemaps")
    )

    with open(f"{path}{file_name}", "w") as fp:
        dom_sitemap.writexml(fp, indent="", addindent="\t", newl="\n", encoding="utf-8")


# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASSES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++


class Url:
    """
    A class to store a URL Object.

    This class contains several function/methods to handle sitemap urls.
    """

    def __init__(
        self,
        loc: str,
        lastmod: str = datetime.now().strftime("%Y-%m-%d"),
        images_loc: list = [],
    ) -> None:
        """Intialize Url Object

        Args:
            loc (str): location of Url (full path with scheme)
            lastmod (str, optional): last modification date of Url. Defaults to datetime.now().strftime("%Y-%m-%d").
            images_loc (list, optional): List of Images included in the Url. Defaults to [].
        """
        self.loc = loc
        self.lastmod = lastmod
        self.image_locations = images_loc

    def add_images(self, images_loc: list = []) -> None:
        """append images to current Url

        Args:
            images_loc (list, optional): list of images location. Defaults to [].
        """
        self.image_locations += images_loc

    def as_dict(self) -> dict:
        """return Url as dict object

        Returns:
            dict: contains loc, lastmod and images keys.
        """
        return {
            "loc": self.loc,
            "lastmod": self.lastmod,
            "images": self.image_locations,
        }


class XmlDocument:
    """
    A class to store an XML Sitemap (index, sub-sitemaps, or main-sitemap) Document.

    This class contains several function methods to handle XML Sitemaps.
    It includes convenient functions e.g. add_url and add_url_set.

    """

    def __init__(
        self,
        loc: str,
        lastmod: str = datetime.now().strftime("%Y-%m-%d"),
        include_urls: bool = False,
    ) -> None:
        """Initialize XmlDocument

        Args:
            loc (str): loc of XmlDocument
            lastmod (str, optional): lastmod of XmlDocument. Defaults to datetime.now().strftime("%Y-%m-%d").
            include_urls (bool, optional): If true then XmlDocument will also include (aviaalble) Urls otherwise ignored. Defaults to False.
        """

        self.loc = loc
        self.lastmod = lastmod
        self.urls = []

        if include_urls:
            file_url = get_corrected_url(loc, fix_slash="")
            response = get_remote_content(file_url)
            if response.status_code == 200:
                self.add_from_text(response.text)

    def add_object(self, url_object: Url):
        """add Url Object to current XmlDocument

        Args:
            url_object (Url): Url Object.
        """
        if url_object:
            self.urls.append(url_object)

    def add_url(
        self,
        loc: str,
        lastmod: str = datetime.now().strftime("%Y-%m-%d"),
        images_loc: list = [],
    ) -> None:
        """add url to current sitemap by specifiyig loc, lastmod and list of images.

        Args:
            loc (str): _description_
            lastmod (str, optional): _description_. Defaults to datetime.now().strftime("%Y-%m-%d").
            images_loc (list, optional): _description_. Defaults to [].
        """
        if loc:
            self.urls.append(Url(loc=loc, lastmod=lastmod, images_loc=images_loc))

    def add_from_text(self, xml_as_text: str) -> None:
        """ """
        self.urls += extract_url_set(xml_as_text=xml_as_text)

    def as_dict(self) -> dict:
        """return XmlDocument as dit

        Returns:
            dict: contains loc, lastmod of XML Document. It also include urls key containing list of Url(s).
        """
        return {
            "loc": self.loc,
            "lastmod": self.lastmod,
            "urls": [url.as_dict() for url in self.urls],
        }


class Sitemap:
    """Sitemap: A class to represent a Sitemap.

    This class contains several function methods to  read and fetch the website sitemap from a local or a remote file location.
    You can use write function to save the file to any file location.
    """

    def __init__(
        self,
        website_name: str = None,
        file_path: str = "",
        xsl_file: str = "",
    ) -> None:
        """Initlaize Sitemap Object

        Args:
            website_name (str, optional): Webiste Name. Defaults to None.
            file_path (str, optional): Path of Sitemap.xml. Defaults to "".
            xsl_file (str, optional): Path of xsl_file. Defaults to "".
        """
        if website_name:
            self.website_name = website_name
        else:
            raise "Cannot Create Sitemap object. Please add sitename to the argument"

        self.xsl_file = xsl_file
        self.file_path = file_path

        self.content = {
            "parent": XmlDocument(file_path),
            "sub_sitemaps": [],
        }

    def read(self, file_path: str = "") -> None:
        """Read sitemap from local file_path
        
        If not specified then file_path specified at the time creation of Sitemap objet.
        Args:
            file_path (str, optional): Sitemap file path. Defaults to "".
        """
        if not file_path:
            file_path = self.file_path

        if file_path.endswith("xml"):
            with open(file_path, "r") as f:
                xml_as_text = f.read()
            self.xsl_file = extract_xsl_file(xml_as_text=xml_as_text)
            self.content["parent"] = XmlDocument(file_path)
            self.content["parent"].add_from_text(xml_as_text)
            self.content["sub_sitemaps"] += extract_sub_sitemaps(xml_as_text)

    def fetch(self, file_path: str = "", include_urls: bool = False) -> None:
        """fetch remote sitemap.

        If File name is not specified then function will locate is by browsing the website.

        Args:
            file_path (str, optional): Url Path of sitemap. Defaults to "".
            include_urls (bool, optional): If true then Urls present in the sitemap will be included. Defaults to False.
        """
        sitemaps = [file_path]
        if not file_path.endswith("xml"):
            sitemaps = search_sitemap(self.website_name)

        for sitemap in sitemaps:
            if sitemap.endswith("xml"):
                self.content["parent"] = XmlDocument(
                    sitemap, include_urls=include_urls
                )
                response = get_remote_content(sitemap)
                if response.status_code < 400:
                    self.xsl_file = extract_xsl_file(xml_as_text=response.text)
                    self.content["sub_sitemaps"] += extract_sub_sitemaps(
                        response.text, include_urls=include_urls
                    )

    def append(self, object_to_append) -> None:
        """Append any of XmlDocument, Url, dict Object

        Args:
            object_to_append (XmlDocument | Url | dict): append Url to current Sitemap
        """

        if isinstance(object_to_append, XmlDocument):
            self.content["sub_sitemaps"].append(object_to_append)
        elif isinstance(object_to_append, Url):
            self.content["parent"].add_object(object_to_append)
        elif isinstance(object_to_append, dict):
            self.content["parent"].add_url(
                object_to_append["loc"],
                lastmod=object_to_append["lastmod"],
                images_loc=object_to_append["images_loc"],
            )

    def as_dict(self) -> dict:
        """return Stimeap object as dict.

        Returns:
            dict: contains 'parent', 'xsl-file' and 'sub_sitemaps'
        """
        return {
            "parent": self.content["parent"].as_dict(),
            "xsl-file": self.xsl_file,
            "sub_sitemaps": [
                sub_sitemap.as_dict() for sub_sitemap in self.content["sub_sitemaps"]
            ],
        }

    def write(
        self,
        path: str = "",
    ) -> None:
        """write Sitemap to xml file

        Args:
            path (str, optional): specify output path/folder location (without file name). Defaults to "".
        """
        parent_sitemap = self.content["parent"]
        sub_sitemaps = self.content["sub_sitemaps"]

        for sub_sitemap in sub_sitemaps:
            sitemap_name = sub_sitemap.as_dict()["loc"].split("/")[-1]
            url_set = sub_sitemap.as_dict()["urls"]
            if url_set:
                write_sub_sitemap(
                    url_set,
                    self.website_name,
                    self.xsl_file,
                    path=path,
                    file_name=sitemap_name,
                )

        if sub_sitemaps and parent_sitemap:
            sitemap_name = parent_sitemap.as_dict()["loc"].split("/")[-1]
            sub_sitemaps_set = [
                {"loc": item.as_dict()["loc"], "lastmod": item.as_dict()["lastmod"]}
                for item in self.content["sub_sitemaps"]
            ]
            if sub_sitemaps_set:
                write_index_sitemap(
                    sub_sitemaps_set,
                    self.website_name,
                    self.xsl_file,
                    path=path,
                    file_name=sitemap_name,
                )
        elif parent_sitemap:
            sitemap_name = parent_sitemap.as_dict()["loc"].split("/")[-1]
            url_set = parent_sitemap.as_dict()["urls"]
            if url_set:
                write_sub_sitemap(
                    url_set,
                    self.website_name,
                    self.xsl_file,
                    path=path,
                    file_name=sitemap_name,
                )
