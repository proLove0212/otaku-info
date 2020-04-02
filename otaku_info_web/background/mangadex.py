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

import time
from typing import Dict, List, Optional
from puffotter.flask.base import db, app
from otaku_info_web.db.MediaItem import MediaItem
from otaku_info_web.db.MediaId import MediaId
from otaku_info_web.utils.enums import ListService, MediaType
from otaku_info_web.utils.mangadex.api import get_external_ids
from otaku_info_web.utils.anilist.api import load_media_info


def load_id_mappings():
    """
    Goes through mangadex IDs sequentially and stores ID mappings for
    these entries if found
    :return: None
    """
    mangadex_id = 23438
    endcounter = 0

    mangadex_ids: List[int] = [
        int(x.service_id)
        for x in MediaId.query.all()
        if x.service == ListService.MANGADEX
    ]

    while True:
        time.sleep(0.5)
        mangadex_id += 1

        if mangadex_id in mangadex_ids:
            continue

        app.logger.debug(f"Probing mangadex id {mangadex_id}")

        other_ids = get_external_ids(mangadex_id)

        if other_ids is None:
            endcounter += 1
            if endcounter > 1000:
                break
            else:
                continue
        else:
            endcounter = 0

        store_ids(mangadex_id, other_ids)


def store_ids(mangadex_id: int, other_ids: Dict[ListService, str]):
    """
    Stores the fetched IDs in the database
    :param mangadex_id: The mangadex ID
    :param other_ids: The other IDs
    :return: None
    """
    if ListService.ANILIST not in other_ids:
        return

    all_ids: List[MediaId] = MediaId.query.all()
    anilist_ids: Dict[str, MediaId] = {
        x.service_id: x for x in
        all_ids
        if x.service == ListService.ANILIST
    }

    anilist_id = other_ids[ListService.ANILIST]
    if anilist_id not in anilist_ids:
        media_item = create_anilist_media_item(int(anilist_id))
        if media_item is None:
            return
        else:
            media_item_id = media_item.id
    else:
        media_item_id = anilist_ids[anilist_id].media_item_id

    existing_ids = [
        x.service
        for x in all_ids
        if x.media_item_id == media_item_id
    ]

    app.logger.debug(f"Storing external IDS for mangadex id {mangadex_id}")

    for list_service, _id in other_ids.items():
        if list_service not in existing_ids:
            media_id = MediaId(
                media_item_id=media_item_id,
                service=list_service,
                service_id=_id
            )
            db.session.add(media_id)

    db.session.commit()


def create_anilist_media_item(anilist_id: int) -> Optional[MediaItem]:
    """
    Creates an anilist media item using an anilist ID, fetching the data using
    the anilist API
    :param anilist_id: The anilist ID of the media
    :return: The generated Media Item
    """
    anilist_entry = load_media_info(anilist_id, MediaType.MANGA)
    if anilist_entry is None:
        return None
    media_item = MediaItem(
        media_type=MediaType.MANGA,
        media_subtype=anilist_entry.media_subtype,
        english_title=anilist_entry.english_title,
        romaji_title=anilist_entry.romaji_title,
        cover_url=anilist_entry.cover_url,
        latest_release=anilist_entry.latest_release,
        releasing_state=anilist_entry.releasing_state
    )
    db.session.add(media_item)
    db.session.commit()
    return media_item
