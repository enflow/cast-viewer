# -*- coding: utf-8 -*-

import sys
import os
import glob
import logging
from lib.utils import download_with_progress
from lib.utils import md5

class Downloader(object):
    def __init__(self):
        logging.debug('Downloader init')


    def download(self, slides):
        slides_to_download = self.get_slides_to_download(slides)
        logging.debug('Downloader.download: %s', slides_to_download)

        self.remove_unused(slides_to_download)

        for slide in slides_to_download:
            path = self.get_path_for_slide(slide)

            if not os.path.isfile(path):
                download_with_progress(path, slide['url'])

            md5_on_filesystem = md5(path)
            if md5_on_filesystem != slide['download_hash']:
                logging.error('Downloaded file hashes don\'t match. Removing file. %s != %s', md5_on_filesystem, slide['download_hash'])
                os.remove(path)


    def remove_unused(self, slides_to_download):
        download_hashes = []
        for slide in slides_to_download:
            download_hashes.append(slide['download_hash'])

        for path in glob.glob(self.get_directory() + '/*'):
            filename = os.path.basename(path)
            if filename not in download_hashes:
                logging.info('File %s will be removed as it\'s unused', filename)
                os.remove(path)


    def get_path_for_slide(self, slide):
        return self.get_directory() + '/' + slide['download_hash']


    def get_slides_to_download(self, slides):
        slides_to_download = []
        for slide in slides:
            if 'download_hash' in slide:
                slides_to_download.append(slide)

        return slides_to_download


    def get_directory(self):
        directory = '/home/pi/cast-viewer-downloads'

        if not os.path.exists(directory):
            os.makedirs(directory)

        return directory
