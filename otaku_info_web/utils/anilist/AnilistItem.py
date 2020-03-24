"""LICENSE
Copyright 2020 Hermann Krumrey <hermann@krumreyh.com>

This file is part of otaku-info-web.

otaku-info-web is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

otaku-info-web is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with otaku-info-web.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

from typing import Optional
from otaku_info_web.utils.enums \
    import MediaType, MediaSubType, ReleasingState, ConsumingState


class AnilistItem:
    """
    Class that models an anilist list item for a user
    Represents the information fetched using anilist's API
    """
    def __init__(
            self,
            anilist_id: int,
            media_type: MediaType,
            media_subtype: MediaSubType,
            english_title: Optional[str],
            romaji_title: str,
            cover_url: str,
            chapters: Optional[int],
            episodes: Optional[int],
            releasing_state: ReleasingState,
            score: Optional[int],
            progress: Optional[int],
            consuming_state: ConsumingState,
            list_name: str
    ):
        """
        Initializes the AnilistItem object
        :param anilist_id: The anilist ID of the series
        :param media_type: The media type of the series
        :param media_subtype: The media subtype of the series
        :param english_title: The English title of the series
        :param romaji_title: The Japanes title of the series written in romaji
        :param cover_url: URL to a cover image for the series
        :param chapters: The total amount of known manga chapters
        :param episodes: The total amount of known anime episodes
        :param releasing_state: The current releasing state of the series
        :param score: The user's score for the series
        :param progress: The user's progress for the series
        :param consuming_state: The user's consumption state for the series
        :param list_name: Which of the user's lists this entry belongs to
        """
        self.anilist_id = anilist_id
        self.media_type = media_type
        self.media_subtype = media_subtype
        self.english_title = english_title
        self.romaji_title = romaji_title
        self.cover_url = cover_url
        self.chapters = chapters
        self.episodes = episodes
        self.releasing_state = releasing_state
        self.score = score
        self.progress = progress
        self.consuming_state = consuming_state
        self.list_name = list_name

    @property
    def latest_release(self) -> Optional[int]:
        """
        :return: The latest release. Chapters for manga, episodes for anime
        """
        if self.media_type == MediaType.ANIME:
            return self.episodes
        else:
            return self.chapters
