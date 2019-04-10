"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of aniremind.

aniremind is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

aniremind is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with aniremind.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

from kudubot.Bot import Bot
from bokkichat.entities.message.Message import Message


class AniRemindBot(Bot):
    """
    The Aniremind Bot class that defines the anime reminder
    functionality.
    """

    def on_msg(self, message: Message):
        """
        Handles received messages
        :param message: The received message
        :return: None
        """
        self.connection.send(message.make_reply())
