# -*- coding: utf-8 -*-

"""Util module for using password-encrypted files
.. module:: utils.crypto
   :platform: Unix, Windows
   :synopsis: Simple password-encrypted fileIO

Note
----
The following module is based on the `simple-crypt package<https://github.com/andrewcooke/simple-crypt>`_ which is a high-level implementation of the `pycrypto library<https://www.dlitz.net/software/pycrypto>`_

Warning
-------
This package provides _sufficiently good_ password-encryption for the purpose of the slack-pack project. This is __not a serious cryptographic implementation__ !!

Attributes
----------
PATH_TO_VAULT : str
    Path to the default vault folder in the slack-pack project

"""

from getpass import getpass
from simplecrypt import encrypt, decrypt


from os.path import abspath
from glob import glob


# Obtain the absolute path to the corpora folder
__path = abspath('.')
__pos = __path.index('slack-pack')

PATH_TO_VAULT = __path[:__pos + 10] + '/data/vault/'  # len('slack-pack') --> 10


def write_file(data, file_name, password=None, vault=None):
    """Password encrypt a file and write it into a file

    Parameters
    ----------
    data : str
        Data to be encrypted
    file_name : str
        Name of the encrypted file
    password : str, optional
        Password with which to password encrypt. If not specified a prompt will appear
    vault : str, optional
        Path to the folder where the encrypted file will be written to. If not specified default to the default slack-pack vault folder

    """
    # If no vault folder was specified default to data/vault
    if vault is None:
        vault = PATH_TO_VAULT

    # If no password was specified prompt for password
    if password is None:
        password = getpass('Password: ')

    with open(vault + file_name, 'wb') as f:
        f.write( encrypt(data=data, password=password) )

    print('Encrypted data into:  {}'.format(vault + file_name))


def read_file(file_name, password=None, vault=None):
    """Read a password-encrypted file

    Parameters
    ----------
    file_name : str
        Name of the encrypted file
    password : str, optional
        Password with which to password encrypt. If not specified a prompt will appear
    vault : str, optional
        Path to the folder where the encrypted file will be written to. If not specified default to the default slack-pack vault folder

    Returns
    -------
    str
        The password-encrypted message
    """
    # If no vault folder was specified default to data/vault
    if vault is None:
        vault = PATH_TO_VAULT

    # If no password was specified prompt for password
    if password is None:
        password = getpass('Password: ')

    with open(vault + file_name,'rb') as f:
        decrypted_message = decrypt( password=password, data=f.read() )

    return decrypted_message
