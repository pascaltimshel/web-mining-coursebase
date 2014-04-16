# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.conch.scripts.ckeygen}.
"""

import getpass
import sys
from StringIO import StringIO

try:
    import Crypto
    import pyasn1
except ImportError:
    skip = "PyCrypto and pyasn1 required for twisted.conch.scripts.ckeygen."
else:
    from twisted.conch.ssh.keys import Key, BadKeyError
    from twisted.conch.scripts.ckeygen import (
        displayPublicKey, printFingerprint, _saveKey)

from twisted.python.filepath import FilePath
from twisted.trial.unittest import TestCase
from twisted.conch.test.keydata import (
    publicRSA_openssh, privateRSA_openssh, privateRSA_openssh_encrypted)



class KeyGenTests(TestCase):
    """
    Tests for various functions used to implement the I{ckeygen} script.
    """
    def setUp(self):
        """
        Patch C{sys.stdout} with a L{StringIO} instance to tests can make
        assertions about what's printed.
        """
        self.stdout = StringIO()
        self.patch(sys, 'stdout', self.stdout)


    def test_printFingerprint(self):
        """
        L{printFingerprint} writes a line to standard out giving the number of
        bits of the key, its fingerprint, and the basename of the file from it
        was read.
        """
        filename = self.mktemp()
        FilePath(filename).setContent(publicRSA_openssh)
        printFingerprint({'filename': filename})
        self.assertEqual(
            self.stdout.getvalue(),
            '768 3d:13:5f:cb:c9:79:8a:93:06:27:65:bc:3d:0b:8f:af temp\n')


    def test_saveKey(self):
        """
        L{_saveKey} writes the private and public parts of a key to two
        different files and writes a report of this to standard out.
        """
        base = FilePath(self.mktemp())
        base.makedirs()
        filename = base.child('id_rsa').path
        key = Key.fromString(privateRSA_openssh)
        _saveKey(
            key.keyObject,
            {'filename': filename, 'pass': 'passphrase'})
        self.assertEqual(
            self.stdout.getvalue(),
            "Your identification has been saved in %s\n"
            "Your public key has been saved in %s.pub\n"
            "The key fingerprint is:\n"
            "3d:13:5f:cb:c9:79:8a:93:06:27:65:bc:3d:0b:8f:af\n" % (
                filename,
                filename))
        self.assertEqual(
            key.fromString(
                base.child('id_rsa').getContent(), None, 'passphrase'),
            key)
        self.assertEqual(
            Key.fromString(base.child('id_rsa.pub').getContent()),
            key.public())


    def test_displayPublicKey(self):
        """
        L{displayPublicKey} prints out the public key associated with a given
        private key.
        """
        filename = self.mktemp()
        pubKey = Key.fromString(publicRSA_openssh)
        FilePath(filename).setContent(privateRSA_openssh)
        displayPublicKey({'filename': filename})
        self.assertEqual(
            self.stdout.getvalue().strip('\n'),
            pubKey.toString('openssh'))


    def test_displayPublicKeyEncrypted(self):
        """
        L{displayPublicKey} prints out the public key associated with a given
        private key using the given passphrase when it's encrypted.
        """
        filename = self.mktemp()
        pubKey = Key.fromString(publicRSA_openssh)
        FilePath(filename).setContent(privateRSA_openssh_encrypted)
        displayPublicKey({'filename': filename, 'pass': 'encrypted'})
        self.assertEqual(
            self.stdout.getvalue().strip('\n'),
            pubKey.toString('openssh'))


    def test_displayPublicKeyEncryptedPassphrasePrompt(self):
        """
        L{displayPublicKey} prints out the public key associated with a given
        private key, asking for the passphrase when it's encrypted.
        """
        filename = self.mktemp()
        pubKey = Key.fromString(publicRSA_openssh)
        FilePath(filename).setContent(privateRSA_openssh_encrypted)
        self.patch(getpass, 'getpass', lambda x: 'encrypted')
        displayPublicKey({'filename': filename})
        self.assertEqual(
            self.stdout.getvalue().strip('\n'),
            pubKey.toString('openssh'))


    def test_displayPublicKeyWrongPassphrase(self):
        """
        L{displayPublicKey} fails with a L{BadKeyError} when trying to decrypt
        an encrypted key with the wrong password.
        """
        filename = self.mktemp()
        FilePath(filename).setContent(privateRSA_openssh_encrypted)
        self.assertRaises(
            BadKeyError, displayPublicKey,
            {'filename': filename, 'pass': 'wrong'})
