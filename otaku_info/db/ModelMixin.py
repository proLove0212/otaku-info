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

from typing import Tuple
from jerrycan.db.ModelMixin import ModelMixin as PuffotterModelMixin


class ModelMixin(PuffotterModelMixin):
    """
    Class that define methods that greatly ease working with existing database
    entries
    """

    @property
    def identifier_tuple(self) -> Tuple:
        """
        :return: A tuple that's unique to this database entry
        """
        raise NotImplementedError()

    def update(self, new_data: "ModelMixin"):
        """
        Updates the data in this record based on another object
        :param new_data: The object from which to use the new values
        :return: None
        """
        raise NotImplementedError()
