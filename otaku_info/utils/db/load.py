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

from typing import Dict, Tuple, List, Optional
from puffotter.flask.base import db
from otaku_info.enums import ListService, MediaType
from otaku_info.db.MediaId import MediaId
from otaku_info.db.MediaItem import MediaItem
from otaku_info.db.MediaList import MediaList
from otaku_info.db.MediaListItem import MediaListItem
from otaku_info.db.MediaUserState import MediaUserState


def load_existing_media_data() -> Tuple[
    Dict[Tuple, MediaItem],
    Dict[Tuple, MediaId],
    Dict[Tuple, MediaUserState]
]:
    """
    Loads current database media data (MediaItem, MediaId and MediaUserState)
    :return: The database contents
    """
    media_items: Dict[Tuple, MediaItem] = {
        x.identifier_tuple: x
        for x in MediaItem.query.options(
            db.joinedload(MediaItem.media_ids)
              .subqueryload(MediaId.media_user_states)
        ).all()
    }
    media_ids: Dict[Tuple, MediaId] = {}
    media_user_states: Dict[Tuple, MediaUserState] = {}
    for media_item in media_items.values():
        for media_id in media_item.media_ids:
            media_ids[media_id.identifier_tuple] = media_id
            for user_state in media_id.media_user_states:
                media_user_states[user_state.identifier_tuple] = user_state

    return media_items, media_ids, media_user_states


def load_existing_media_list_data() -> Tuple[
    Dict[Tuple, MediaList],
    Dict[Tuple, MediaListItem]
]:
    """
    Loads current database media list data (MediaList, MediaListItem)
    :return: The database contents
    """
    media_lists: Dict[Tuple, MediaList] = {
        x.identifier_tuple: x
        for x in MediaList.query.options(
            db.joinedload(MediaList.media_list_items)
        ).all()
    }
    media_list_items: Dict[Tuple, MediaListItem] = {}
    for media_list in media_lists.values():
        for list_item in media_list.media_list_items:
            media_list_items[list_item.identifier_tuple] = list_item

    return media_lists, media_list_items


def load_service_ids(
        limit_media_type_to: Optional[MediaType] = None
) -> Dict[ListService, Dict[str, MediaId]]:
    """
    Loads Media IDs from the database and maps them to their service id
    :param limit_media_type_to: If set, limits the media type
    :return: The mapped ids
    """
    media_ids: List[MediaId] = MediaId.query.options(
        db.joinedload(MediaId.media_item)
          .subqueryload(MediaItem.media_ids)
    ).all()

    if limit_media_type_to is not None:
        media_ids = list(filter(
            lambda x: x.media_type == limit_media_type_to,
            media_ids
        ))

    mapped_ids = {x: {} for x in ListService}
    for media_id in media_ids:
        mapped_ids[media_id.service][media_id.service_id] = media_id

    return mapped_ids
