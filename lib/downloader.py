# -*- coding: utf-8 -*-

import sys
import os
import glob
import logging
import sh
from lib.utils import download_with_progress

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

            # hacky way to validate if the MP4 is not corrupt
            mediainfo = sh.mediainfo(path).rstrip()
            if "Codec ID/Info" not in mediainfo:
                logging.error('Downloaded file doesn\'t look like a valid mp4 file: %s (hash=%s)', slide['url'], slide['hash'])
                os.remove(path)


    def remove_unused(self, slides_to_download):
        download_hashes = []
        for slide in slides_to_download:
            download_hashes.append(slide['hash'])

        for path in glob.glob(self.get_directory() + '/*'):
            filename = os.path.basename(path)
            if filename not in download_hashes:
                logging.info('File %s will be removed as it\'s unused', filename)
                os.remove(path)


    def get_path_for_slide(self, slide):
        return self.get_directory() + '/' + slide['hash']


    def get_slides_to_download(self, slides):
        slides_to_download = []
        for slide in slides:
            if slide['type'] == 'video':
                slides_to_download.append(slide)

        return slides_to_download


    def get_directory(self):
        return '/data/cast-downloads'
