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

from enum import Enum


class MediaType(Enum):
    """
    Enumeration that differentiates between anime and manga
    """
    ANIME = "anime"
    MANGA = "manga"


class ReleaseState(Enum):
    """
    Enumeration of possible release states for media entries
    """
    RELEASING = "releasing"
    FINISHED = "finished"
    CANCELLED = "cancelled"
    NOT_RELEASED = "not_yet_released"
