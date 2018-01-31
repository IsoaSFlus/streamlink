import re

from streamlink.plugin import Plugin
from streamlink.plugin.api import http, validate
from streamlink.stream import HLSStream
from streamlink.plugin.api import useragents
from streamlink.utils import update_scheme

#YY_URL = "http://interface.yy.com/hls/new/get/{0}/{0}/1200?source=wapyy&callback=jsonp2"
YY_URL = 'http://interface.yy.com/hls/get/0/{0}/{0}?appid=0&excid=1200&type=m3u8&isHttps=0&callback=jsonp2'

_url_re = re.compile(r'http(s)?://(www\.)?yy.com/(?P<channel>[^/]+)', re.VERBOSE)
_hls_re = re.compile(r'^[\S\s]*"hls":"(?P<url>[^"]+)"', re.VERBOSE)

_hls_schema = validate.Schema(
    validate.all(
        validate.transform(_hls_re.search),
        validate.any(
            None,
            validate.all(
                validate.get('url'),
                validate.transform(str)
            )
        )
    )
)


class Yy(Plugin):
    @classmethod
    def can_handle_url(self, url):
        return _url_re.match(url)

    def _get_streams(self):
        match = _url_re.match(self.url)
        channel = match.group("channel")
        http.headers.update({"User-Agent": useragents.IPAD,
                             'Referer': 'http://wap.yy.com/mobileweb/{0}/{0}'.format(channel)})

        hls_json = http.get(YY_URL.format(channel))
        hls_json = hls_json.content.decode('ascii')
        hls_match = _hls_re.match(hls_json)
        if not hls_match:
            return
        hls_url = hls_match.group("url")
        yield "live", HLSStream(self.session, hls_url)


__plugin__ = Yy
