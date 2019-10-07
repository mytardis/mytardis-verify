import os

from django.test import TransactionTestCase

from tardis import utils


class UtilsTestCase(TransactionTestCase):

    def setUp(self):
        this_folder = os.path.dirname(os.path.realpath(__file__))
        self.assets_folder = os.path.join(this_folder, 'assets')

    def testMD5Sum(self):
        fname = os.path.join(self.assets_folder, '15525119098910.pdf')
        checksum = utils.checksum(fname, 'md5')
        self.assertTrue(checksum == 'ec4e3b91d2e03fdb17db55ff46da43b2')

    def testSHA512Sum(self):
        fname = os.path.join(self.assets_folder, '15525119098910.pdf')
        checksum = utils.checksum(fname, 'sha512')
        self.assertTrue(checksum == 'bc803d8abccf18d89765d6ae9fb7d490ad07f57a'
                                    '48e4987acc173af4e65f143a4d215ffb59e9eebe'
                                    'b03849baab5a6e016e2806a2cd0e84b14c778bdb'
                                    '84afbbf4')
