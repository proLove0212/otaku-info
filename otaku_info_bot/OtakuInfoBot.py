"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of otaku-info-bot.

otaku-info-bot is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

otaku-info-bot is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with otaku-info-bot.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

import time
import json
import math
import requests
from typing import Dict, List, Any
from datetime import datetime
from kudubot.Bot import Bot
from kudubot.db.Address import Address
from kudubot.parsing.CommandParser import CommandParser
from bokkichat.entities.message.TextMessage import TextMessage
from sqlalchemy.orm import Session
from otaku_info_bot.db.Reminder import Reminder
from otaku_info_bot.OtakuInfoCommandParser import OtakuInfoCommandParser
from otaku_info_bot.fetching.anime import load_newest_episodes
from otaku_info_bot.fetching.ln import load_ln_releases
from otaku_info_bot.db.MangaEntry import MangaEntry
from otaku_info_bot.db.MangaUpdate import MangaUpdate
from otaku_info_bot.db.MangaUpdateConfig import MangaUpdateConfig


class OtakuInfoBot(Bot):
    """
    The OtakuInfo Bot class that defines the anime reminder
    functionality.
    """

    @classmethod
    def name(cls) -> str:
        """
        :return: The name of the bot
        """
        return "otaku-info-bot"

    @classmethod
    def parsers(cls) -> List[CommandParser]:
        """
        :return: A list of parser the bot supports for commands
        """
        return [OtakuInfoCommandParser()]

    def on_command(
            self,
            message: TextMessage,
            parser: CommandParser,
            command: str,
            args: Dict[str, Any],
            sender: Address,
            db_session: Session
    ):
        """
        Handles incoming command messages
        :param message: The incoming message
        :param parser: The parser that matches the message
        :param command: The command that matches the message
        :param args: The arguments that match the message
        :param sender: The sender of the message
        :param db_session: The database session to use
        :return: None
        """
        if command == "list_anime_series_names":
            self._handle_list_anime_series_names(sender)
        elif command == "register_anime_reminder":
            self._handle_register_anime_reminder(sender, args, db_session)
        elif command == "list_anime_reminders":
            self._handle_list_anime_reminders(sender, db_session)
        elif command == "delete_anime_reminder":
            self._handle_delete_anime_reminder(sender, args, db_session)
        elif command == "list_ln_releases":
            self._handle_list_ln_releases(sender, args)
        elif command == "activate_manga_updates":
            self._handle_activate_manga_updates(sender, args, db_session)
        elif command == "deactivate_manga_updates":
            self._handle_deactivate_manga_updates(sender, db_session)

    def _handle_list_anime_series_names(self, address: Address):
        """
        Handles listing anime series names
        :return: None
        """
        series = load_newest_episodes()
        series_str = ""
        for name in series:
            series_str += name + "\n"
        self.send_txt(address, series_str, "Anime IDs")

    def _handle_register_anime_reminder(
            self,
            address: Address,
            args: Dict[str, Any],
            db_session: Session
    ):
        """
        Registers a new anime reminder for a user
        :param address: The address for which to register the reminder
        :param args: The arguments containing the show name
        :param db_session: The session to use
        :return: None
        """
        show_name = args["show_name"]

        self.logger.info(
            "Storing show {} for address {}".format(show_name, address.address)
        )

        latest_episodes = load_newest_episodes()
        last_episode = latest_episodes.get(show_name.lower(), 0)

        reminder = Reminder(
            address_id=address.id,
            show_name=show_name,
            last_episode=last_episode
        )
        db_session.add(reminder)
        db_session.commit()
        self.send_txt(address, "{} registered".format(reminder))

    def _handle_list_anime_reminders(
            self,
            address: Address,
            db_session: Session
    ):
        """
        Handles listing all anime reminders of a user
        :param address: The address of the user
        :param db_session: The database session to use
        :return: None
        """
        self.logger.info(
            "Listing reminders for {}".format(address.address)
        )

        reminders = db_session.query(Reminder).filter_by(address=address).all()
        reminders = list(map(lambda x: str(x), reminders))
        body = "List of reminders:\n" + "\n".join(reminders)
        self.send_txt(address, body)

    def _handle_delete_anime_reminder(
            self,
            address: Address,
            args: Dict[str, Any],
            db_session: Session
    ):
        """
        Handles deleting an anime reminder
        :param address: The user that requested the deletion
        :param args: The arguments for which reminder to delete
        :param db_session: The database session to use
        :return: None
        """
        _id = args["id"]
        self.logger.info("Removing Reminder #{}".format(_id))

        reminder = db_session.query(Reminder) \
            .filter_by(id=_id, address_id=address.id).first()

        if reminder is not None:
            db_session.delete(reminder)
            db_session.commit()
            body = "Reminder #{} was deleted".format(args["id"])
        else:
            body = "Reminder #{} could not be deleted".format(args["id"])
        self.send_txt(address, body)

    def _handle_list_ln_releases(
            self,
            address: Address,
            args: Dict[str, Any]
    ):
        """
        Handles listing current light novel releases
        :param address: The user that sent this request
        :param args: The arguments to use
        :return: None
        """
        year = args.get("year")
        month = args.get("month")

        now = datetime.utcnow()

        if year is None:
            year = now.year
        if month is None:
            month = now.strftime("%B")

        releases = load_ln_releases().get(year, {}).get(month.lower(), [])
        body = "Light Novel Releases {} {}\n\n".format(month, year)

        for entry in releases:
            body += "{}: {} {}\n".format(
                entry["day"],
                entry["title"],
                entry["volume"]
            )
        self.send_txt(address, body)

    def _handle_activate_manga_updates(
            self,
            address: Address,
            args: Dict[str, Any],
            db_session: Session
    ):
        """
        Handles activating manga updates for a user using anilist
        :param address: The user that sent this request
        :param args: The arguments to use
        :param db_session: The database session to use
        :return: None
        """
        exists = db_session.query(MangaUpdateConfig.id)\
            .filter_by(address=address).first() is not None
        if exists:
            self.send_txt(
                address, "Manga Updates already activated", "Already Active"
            )
            return

        username = args["anilist-username"]
        custom_list = args["custom-list"]
        config = MangaUpdateConfig(
            anilist_username=username,
            custom_list=custom_list,
            address=address
        )
        db_session.add(config)
        db_session.commit()

        self.send_txt(address, "Manga Updates Activated", "Activated")

        self._update_manga_entries(db_session)
        self._send_manga_updates(db_session)

    def _handle_deactivate_manga_updates(
            self,
            address: Address,
            db_session: Session
    ):
        """
        Handles listing current light novel releases
        :param address: The user that sent this request
        :param db_session: The database session to use
        :return: None
        """
        existing = db_session.query(MangaUpdateConfig)\
            .filter_by(address=address).first()
        if existing is not None:
            db_session.delete(existing)
            db_session.commit()
        self.send_txt(address, "Deactivated Manga Updates", "Deactivated")

    def _update_manga_entries(self, db_session: Session):
        """
        Updates the internal database of the manga entries with the newest
        information
        :param db_session: The database session to use
        :return: None
        """
        self.logger.info("Updating Manga Entries")
        configs = db_session.query(MangaUpdateConfig).all()

        manga_progress = {}

        for config in configs:  # type: MangaUpdateConfig
            anilist = self._load_user_anilist(
                config.anilist_username, config.custom_list
            )

            for entry in anilist:
                anilist_id = entry["media"]["id"]
                name = entry["media"]["title"]["english"]
                if name is None:
                    name = entry["media"]["title"]["romaji"]
                user_chapters = entry["progress"]

                chapters = entry["media"]["chapters"]
                if chapters is None:
                    chapters = manga_progress.get(anilist_id)
                if chapters is None:
                    chapters = self._guess_latest_manga_chapter(anilist_id)
                manga_progress[anilist_id] = chapters

                manga_entry = db_session.query(MangaEntry)\
                    .filter_by(id=anilist_id).first()
                manga_update = db_session.query(MangaUpdate)\
                    .filter_by(entry_id=anilist_id, address=config.address)\
                    .first()

                if manga_entry is None:
                    manga_entry = MangaEntry(
                        id=anilist_id,
                        name=name,
                        latest_chapter=chapters
                    )
                    db_session.add(manga_entry)
                else:
                    manga_entry.latest_chapter = chapters

                if manga_update is None:
                    manga_update = MangaUpdate(
                        address=config.address,
                        entry=manga_entry,
                        last_update=user_chapters
                    )
                    db_session.add(manga_update)

        db_session.commit()
        self.logger.info("Finished updating manga entries")

    def _send_manga_updates(self, db_session: Session):
        """
        Sends manga updates to the users with activated manga updates
        :return: None
        """
        self.logger.info("Sending Manga Updates")
        configs = db_session.query(MangaUpdateConfig).all()
        for config in configs:  # type: MangaUpdateConfig

            due = []

            updates = db_session.query(MangaUpdate)\
                .filter_by(address=config.address).all()

            for update in updates:  # type: MangaUpdate
                if update.diff > 0:
                    due.append(update)

            if len(due) == 0:
                continue

            due.sort(key=lambda x: x.diff, reverse=True)

            message = "New Manga Updates:\n\n"
            for update in due:
                message += "\\[{}] {} Chapter {}\n".format(
                    update.diff,
                    update.entry.name,
                    update.entry.latest_chapter
                )
                update.last_update = update.entry.latest_chapter

            self.send_txt(config.address, message, "Manga Updates")

        db_session.commit()
        self.logger.info("Finished Sending Manga Updates")

    @staticmethod
    def _load_user_anilist(username: str, custom_list: str) \
            -> List[Dict[str, Any]]:
        """
        Loads the anilist for a user
        :param username: The username
        :param custom_list: The custom list to load
        :return: The anilist
        """
        query = """
            query ($username: String) {
                MediaListCollection(userName: $username, type: MANGA) {
                    lists {
                        name
                        entries {
                            progress
                            media {
                                id
                                chapters
                                title {
                                    english
                                    romaji
                                }
                            }
                        }
                    }
                }
            }
            """
        user_lists = json.loads(requests.post(
            "https://graphql.anilist.co",
            json={"query": query, "variables": {"username": username}}
        ).text)["data"]["MediaListCollection"]["lists"]

        entries = []
        for _list in user_lists:
            if _list["name"] == custom_list:
                entries += _list["entries"]

        return entries

    @staticmethod
    def _guess_latest_manga_chapter(anilist_id: int) -> int:
        """
        Guesses the latest chapter number based on anilist user activity
        :param anilist_id: The anilist ID to check
        :return: The latest chapter number
        """
        query = """
        query ($id: Int) {
          Page(page: 1) {
            activities(mediaId: $id, sort: ID_DESC) {
              ... on ListActivity {
                progress
                userId
              }
            }
          }
        }
        """
        resp = requests.post(
            "https://graphql.anilist.co",
            json={"query": query, "variables": {"id": anilist_id}}
        )
        data = json.loads(resp.text)["data"]["Page"]["activities"]

        progresses = []
        for entry in data:
            progress = entry["progress"]
            if progress is not None:
                progress = entry["progress"].split(" - ")[-1]
                progresses.append(int(progress))

        progresses.sort(reverse=True)
        best_guess = progresses[0]

        if len(progresses) > 2:
            diff = progresses[0] - progresses[1]
            inverse_diff = 1 + math.ceil(50 / (diff + 1))
            if len(progresses) >= inverse_diff:
                if progresses[1] == progresses[inverse_diff]:
                    best_guess = progresses[1]

        return best_guess

    def run_in_bg(self):
        """
        Periodically checks for new reminders to update and manga updates
        :return: None
        """
        counter = 0
        while True:
            db_session = self.sessionmaker()

            self.logger.info("Start looking for due reminders")
            latest = load_newest_episodes()

            for reminder in db_session.query(Reminder).all():

                self.logger.debug(
                    "Checking if reminder {} is due".format(reminder)
                )

                latest_episode = latest.get(reminder.show_name.lower(), 0)

                if reminder.last_episode < latest_episode:
                    self.logger.info("Found due reminder {}".format(reminder))
                    message = TextMessage(
                        self.connection.address,
                        reminder.address,
                        "Episode {} of '{}' has aired.".format(
                            latest_episode, reminder.show_name
                        )
                    )
                    self.connection.send(message)
                    reminder.last_episode = latest_episode
                    db_session.commit()

            if counter % 10 == 0:
                self._update_manga_entries(db_session)
                self._send_manga_updates(db_session)

            self.sessionmaker.remove()
            time.sleep(60)
            counter += 1
