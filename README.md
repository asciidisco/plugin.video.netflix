# Netflix Plugin for Kodi 18 (plugin.video.netflix)

[![Build Status](https://travis-ci.org/asciidisco/plugin.video.netflix.png?branch=master)](https://travis-ci.org/asciidisco/plugin.video.netflix)
[![Code Climate](https://codeclimate.com/github/asciidisco/plugin.video.netflix/badges/gpa.svg)](https://codeclimate.com/github/asciidisco/plugin.video.netflix)
[![Test Coverage](https://codeclimate.com/github/asciidisco/plugin.video.netflix/badges/coverage.svg)](https://codeclimate.com/github/asciidisco/plugin.video.netflix/coverage)
[![GitHub release](https://img.shields.io/github/release/asciidisco/plugin.video.netflix.svg)](https://github.com/asciidisco/plugin.video.netflix/releases)

## Disclaimer

This plugin is not officially commisioned/supported by Netflix.
The trademark "Netflix" is registered by "Netflix, Inc."

## Prerequisites

- Kodi 18 [agile build](https://github.com/FernetMenta/kodi-agile)
- Libwidevine 1.4.8.962 (A german description how to get/install it, can be found [here](https://www.kodinerds.net/index.php/Thread/51486-Kodi-17-Inputstream-HowTo-AddOns-f%C3%BCr-Kodi-17-ab-Beta-6-aktuelle-Git-builds-Updat/))
- Inputstream.adaptive [agile branch build](https://github.com/liberty-developer/inputstream.adaptive/tree/agile)

You can obtain this plugin by using this [repo]()

## FAQ

- [Does it work with Kodi 17](https://github.com/asciidisco/plugin.video.netflix/issues/25)
- [Does it work on a RPI](https://github.com/asciidisco/plugin.video.netflix/issues/28)
- [Which video resolutions are supported](https://github.com/asciidisco/plugin.video.netflix/issues/27)

## Functionality

- Multiple profiles
- Search Netflix (incl. suggestions)
- Netflix categories, recommendations, "my list", genres & continue watching
- Rate show/movie
- Enable/disable adult pin
- Add & remove to/from "my list"
- Export of complete shows & movies in local database (custom library folder can be configured, by default the .strm files are stored in `userdata/addon_data/plugin.video.netflix` )

## Contribute

If you feel, you´d like to contribute to this plugin or directly work on one of these items,
please open an issue & we can provide you with some help to get started

Open issues & planned enhancements can be found [here](https://github.com/asciidisco/plugin.video.netflix/issues?utf8=%E2%9C%93&q=is%3Aissue%20is%3Aopen%20)

More detailed information on the development process can be found [here](CONTRIBUTING.md)

## Something doesn't work

If something doesn't work for you, please:

- Make sure all prerequisites are met
- Make sure you´re running the latest version
- Enable verbose logging in the plugin settings
- Enable the Debug log in you Kodi settings
- Open an issue with a titles that summarises your problems and include:
	- Kodi version (git sha as long as we´re on agile only)
	- Inputstream.adaptive version (git sha as long as we´re on the agile branch)
	- Your OS and OS version
	- Libwidevine version
	- A Kodi debug log that represents your issue

Solved issues can be found [here](https://github.com/asciidisco/plugin.video.netflix/issues?utf8=%E2%9C%93&q=is%3Aissue%20is%3Aclosed%20) please check them first before open an issue

## Code of Conduct

[Contributor Code of Conduct](Code_of_Conduct.md). By participating in this project you agree to abide by its terms.

## Licence

Licenced under The MIT License.
Includes [Universal Tracker]() which is released under BSD 3 License
