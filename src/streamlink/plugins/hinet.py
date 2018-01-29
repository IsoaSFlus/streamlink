import re

from streamlink.plugin import Plugin
from streamlink.plugin.api import http, validate
from streamlink.stream import HLSStream
from streamlink.plugin.api import useragents
from streamlink.utils import update_scheme

HINET_URL = "http://hichannel.hinet.net/radio/index.do"

_url_re = re.compile(r'http://hichannel.hinet.net/(?P<room>[^/]+)', re.VERBOSE)
_hls_re = re.compile(r'^[\S\s]*"hls":"(?P<url>[^"]+)"', re.MULTILINE)
#  _chn_re = re.compile(r'^[\s\S]*<li class="no6">[\s\S]*?onclick="uiControl.playRank\(\'(?P<channel>[^\']+)\'\)">', re.MULTILINE)
_chn_re_str = r'^[\s\S]*<li class="{0}">[\s\S]*?onclick="uiControl.playRank\(\'(?P<channel>[^\']+)\'\)">'
#  _chn_re = re.compile(r'^[\s\S]*onclick="uiControl.playRank\(\'(?P<channel>[\w]+)\'\)">Classical Taiwan愛樂電台</a>', re.MULTILINE)

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


class Hinet(Plugin):
    @classmethod
    def can_handle_url(self, url):
        return _url_re.match(url)

    def _get_streams(self):
        http.headers.update({"User-Agent": useragents.CHROME,
                             'Referer': 'http://hichannel.hinet.net/radio/index.do'})
        match = _url_re.match(self.url)
        room = match.group('room')
        _chn_re = re.compile(_chn_re_str.format(room), re.MULTILINE)

        channel = http.get(HINET_URL)
        match = _chn_re.match(channel.content.decode('utf-8'))
        channel = match.group("channel")

        hls_json = http.get('http://hichannel.hinet.net/radio/cp.do?id={0}'.format(channel))
        #hls_json = hls_json.content.decode('utf-8')
        hls_dict = http.json(hls_json)
        hls_dict = HLSStream.parse_variant_playlist(self.session, hls_dict['_adc'])
        if not hls_dict:
            return
        yield "live", hls_dict['135k']


__plugin__ = Hinet
