from pathlib import Path

import os

from bs4 import BeautifulSoup
from openpyxl import load_workbook

from trust_stores_observatory.certificates_repository import RootCertificatesRepository
from trust_stores_observatory.store_fetcher import MacosTrustStoreFetcher, MicrosoftTrustStoreFetcher, \
    AospTrustStoreFetcher, JavaTrustStoreFetcher, OpenJDKTrustStoreFetcher
from trust_stores_observatory.store_fetcher.mozilla_fetcher import MozillaTrustStoreFetcher, \
    _CerdataEntryServerAuthTrustEnum, _CertdataCertificateEntry, _CertdataTrustEntry


class TestMozillaTrustStoreFetcher:

    def test_scraping(self):
        # Given a Mozilla certdata file
        certdata_path = Path(os.path.abspath(os.path.dirname(__file__))) / 'bin' / 'mozilla_certdata.txt'
        with open(certdata_path) as certdata_file:
            certdata_content = certdata_file.read()

        # When scraping it
        certdata_entries = MozillaTrustStoreFetcher._scrape_certdata(certdata_content)

        # It returns the correct entries
        assert 319 == len(certdata_entries)

        certificate_entries = [entry for entry in certdata_entries if isinstance(entry, _CertdataCertificateEntry)]
        assert 157 == len(certificate_entries)

        trust_entries = [entry for entry in certdata_entries if isinstance(entry, _CertdataTrustEntry)]
        assert 162 == len(trust_entries)

        trusted_trust_entries = [entry for entry in trust_entries
                                 if entry.trust_enum == _CerdataEntryServerAuthTrustEnum.TRUSTED]
        assert 138 == len(trusted_trust_entries)

        not_trusted_trust_entries = [entry for entry in trust_entries
                                     if entry.trust_enum == _CerdataEntryServerAuthTrustEnum.NOT_TRUSTED]
        assert 7 == len(not_trusted_trust_entries)

        must_verify_trust_entries = [entry for entry in trust_entries
                                     if entry.trust_enum == _CerdataEntryServerAuthTrustEnum.MUST_VERIFY]
        assert 17 == len(must_verify_trust_entries)

    def test_online(self):
        certs_repo = RootCertificatesRepository.get_default()
        store_fetcher = MozillaTrustStoreFetcher()
        fetched_store = store_fetcher.fetch(certs_repo)
        assert fetched_store
        assert 100 < len(fetched_store.trusted_certificates)
        assert 5 < len(fetched_store.blocked_certificates)


class TestMacOsTrustStoreFetcher:

    def test_scraping(self):
        # Given a macOS trust store page
        html_path = Path(os.path.abspath(os.path.dirname(__file__))) / 'bin' / 'macOS.html'
        with open(html_path) as html_file:
            parsed_html = BeautifulSoup(html_file.read(), 'html.parser')

        # When scraping it
        trusted_entries = MacosTrustStoreFetcher._parse_root_records_in_div(parsed_html, 'trusted')
        blocked_entries = MacosTrustStoreFetcher._parse_root_records_in_div(parsed_html, 'blocked')

        # It returns the correct entries
        assert 173 == len(trusted_entries)
        assert 38 == len(blocked_entries)

    def test_online(self):
        certs_repo = RootCertificatesRepository.get_default()
        store_fetcher = MacosTrustStoreFetcher()
        fetched_store = store_fetcher.fetch(certs_repo)
        assert fetched_store
        assert 100 < len(fetched_store.trusted_certificates)
        assert 6 < len(fetched_store.blocked_certificates)


class TestMicrosoftStoreFetcher:

    def test_scraping(self):
        # Given a Microsoft root CA spreadsheet
        spreadsheet_path = Path(os.path.abspath(os.path.dirname(__file__))) / 'bin' / 'microsoft.xlsx'
        workbook = load_workbook(spreadsheet_path)

        # When parsing it
        version, trusted_records, blocked_records = MicrosoftTrustStoreFetcher._parse_spreadsheet(workbook)

        # The right data is returned
        assert 'March 29, 2018' == version
        assert 294 == len(trusted_records)
        assert 85 == len(blocked_records)

    def test_online(self):
        certs_repo = RootCertificatesRepository.get_default()
        store_fetcher = MicrosoftTrustStoreFetcher()
        fetched_store = store_fetcher.fetch(certs_repo)
        assert fetched_store
        assert 100 < len(fetched_store.trusted_certificates)
        assert 6 < len(fetched_store.blocked_certificates)


class TestAospTrustStoreFetcher:

    def test_scraping(self):
        # TODO(AD)
        pass

    def test_online(self):
        certs_repo = RootCertificatesRepository.get_default()
        store_fetcher = AospTrustStoreFetcher()
        fetched_store = store_fetcher.fetch(certs_repo)
        assert fetched_store
        assert 100 < len(fetched_store.trusted_certificates)
        assert 0 == len(fetched_store.blocked_certificates)


class TestJavaTrustStoreFetcher:

    def test_online(self):
        certs_repo = RootCertificatesRepository.get_default()
        store_fetcher = JavaTrustStoreFetcher()
        fetched_store = store_fetcher.fetch(certs_repo)
        assert fetched_store
        assert 90 < len(fetched_store.trusted_certificates)
        assert 10 < len(fetched_store.blocked_certificates)


class TestOpenJdkTrustStoreFetcher:

    def test_online(self):
        certs_repo = RootCertificatesRepository.get_default()
        store_fetcher = OpenJDKTrustStoreFetcher()
        fetched_store = store_fetcher.fetch(certs_repo)
        assert fetched_store
        assert 90 < len(fetched_store.trusted_certificates)
        assert 10 < len(fetched_store.blocked_certificates)
