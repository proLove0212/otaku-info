"""LICENSE
Copyright 2020 Hermann Krumrey <hermann@krumreyh.com>

This file is part of otaku-info.

otaku-info is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

otaku-info is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with otaku-info.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

from otaku_info.enums import MediaType
from otaku_info.external.anilist import load_anilist_info
from otaku_info.test.TestFramework import _TestFramework


class TestAnilist(_TestFramework):
    """
    Class that tests the anilist functionality
    """

    def test_retrieving_anilist_item(self):
        """
        Tests retrieving an anilist item
        :return: None
        """
        item = load_anilist_info(9253, MediaType.ANIME)
        self.assertIsNotNone(item)
        self.assertEqual(item.english_title, "Steins;Gate")
