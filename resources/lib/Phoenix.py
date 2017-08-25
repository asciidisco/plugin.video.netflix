"""ADD ME"""

import os
import sys
import json
import urllib
import zipfile
import xbmc
import xbmcvfs


class Phoenix(object):
    """ADD ME"""

    def __init__(self, addon_id, mount=None, dep_file=None, log=None):
        """ADD ME"""
        # default paths
        default_mount = 'special://home/addons/{addon_id}/resources/lib/phoenix'
        default_dep_file = 'special://home/addons/{addon_id}/phoenix.json'
        # check if local or external log should be used
        self.log = log if log is not None else self.__log
        # calculate and setup mount dir
        self.mount = self.__setup_mount(
            addon_id=addon_id,
            mount=mount,
            default_mount=default_mount)
        # calculate and setup dependency file location
        self.dep_file = self.__setup_dependency_file(
            addon_id=addon_id,
            dep_file=dep_file,
            default_dep_file=default_dep_file)
        # just a default for the checked dependency tuple
        self.default_dep = (False, False)

    def run(self):
        """ADD ME"""
        # check dependencies (existance & version)
        dependencies = self.check_dependencies()
        # iterate over all dependencies to see if we need to install/update them
        for dependency in dependencies:
            # check if the `installed`flag of the dep is not true
            if dependencies.get(dependency, self.default_dep)[0] is not True:
                # install the dependency (download zip, unzip, remove zip)
                self.install_dependency(
                    dependency=dependency,
                    version=dependencies.get(dependency, self.default_dep)[1])
        # mount dependecies to the sys path
        self.__mount_dependencies(dependencies=dependencies)

    def check_dependencies(self):
        """ADD ME"""
        deps = {}
        # load contents of the dependency file
        dependencies = self.__load_dependency_file(path=self.dep_file)
        # fetch dependencies map
        __dependencies = dependencies.get('dependencies', {})
        # check each dependency for existance
        for dependency in __dependencies:
            version = __dependencies.get(dependency, False)
            # get the real folder of the deopendency
            folder = self.__get_dependency_folder(
                mount=self.mount,
                dependency=dependency,
                version=version)
            # determine if the dependency exists & store the result
            deps[dependency] = (
                self.__check_if_dependency_exists(folder=folder),
                version)
        # check if we need to delete old versions of dependencies
        # TODO
        return deps

    def install_dependency(self, dependency, version):
        """ADD ME"""
        # fetch the remote url, local path & zi file name of the dep
        url = self.__get_remote_url(dependency=dependency, version=version)
        path = self.__get_system_mount_path(mount=self.mount)
        zip_file = self.__get_zip_file_name(dependency=dependency, version=version)
        # download the zip file release
        urllib.urlretrieve(url, path + zip_file)
        # extract the zip file
        self.__extract_zip_file(path=path, zip_file=zip_file)

    def __load_dependency_file(self, path):
        """ADD ME"""
        if self.__dependency_file_exists(path=path):
            contents = self.__read_dependency_file(path=path)
            parsed_contents = json.loads(contents)
            return parsed_contents
        return None

    def __mount_dependencies(self, dependencies):
        """ADD ME"""
        for dependency in dependencies:
            path = self.__get_mount_folder(
                mount=self.mount,
                dependency=dependency,
                version=dependencies.get(dependency)[1])
            sys.path.insert(0, path)

    def __get_mount_folder(self, mount, dependency, version):
        """ADD ME"""
        return xbmc.translatePath(self.__get_dependency_folder(
            mount=mount,
            dependency=dependency,
            version=version))

    @classmethod
    def __log(cls, msg):
        """ADD ME"""
        xbmc.log('[Phoenix Dependency Manager] ' + str(msg), xbmc.LOGNOTICE)

    @classmethod
    def __dependency_file_exists(cls, path):
        """ADD ME"""
        return bool(xbmcvfs.exists(path))

    @classmethod
    def __read_dependency_file(cls, path):
        """ADD ME"""
        dep_file = xbmcvfs.File(path, 'r')
        contents = dep_file.read()
        dep_file.close()
        return contents

    @classmethod
    def __setup_mount(cls, addon_id, mount, default_mount):
        """ADD ME"""
        mount = default_mount if mount is None else mount
        mount = mount.replace('{addon_id}', addon_id)
        if not bool(xbmcvfs.exists(mount)):
            xbmcvfs.mkdirs(mount)
        return mount

    @classmethod
    def __setup_dependency_file(cls, addon_id, dep_file, default_dep_file):
        """ADD ME"""
        dep_file = default_dep_file if dep_file is None else dep_file
        return dep_file.replace('{addon_id}', addon_id)

    @classmethod
    def __get_dependency_folder(cls, mount, dependency, version):
        """ADD ME"""
        folder = mount
        folder += os.path.sep + dependency.split('/')[1]
        folder += '-' + version.replace('v', '')
        return folder

    @classmethod
    def __check_if_dependency_exists(cls, folder):
        """ADD ME"""
        return bool(xbmcvfs.exists(folder + os.path.sep + 'setup.py'))

    @classmethod
    def __get_remote_url(cls, dependency, version):
        """ADD ME"""
        return 'https://github.com/' + dependency + '/archive/' + version + '.zip'

    @classmethod
    def __get_system_mount_path(cls, mount):
        """ADD ME"""
        return xbmc.translatePath(mount)   

    @classmethod
    def __get_zip_file_name(cls, dependency, version):
        """ADD ME"""
        return dependency.replace('/', '_') + '_' + version + '.zip'

    @classmethod
    def __extract_zip_file(cls, path, zip_file):
        """ADD ME"""
        zip_ref = zipfile.ZipFile(path + zip_file, 'r')
        zip_ref.extractall(path)
        zip_ref.close()
        xbmcvfs.delete(path + zip_file)
