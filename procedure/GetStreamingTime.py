# Copyright (c) 2022 nejire957
# This file is part of 774today.
# 774today is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
# 774today is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with Foobar.
# If not, see <https://www.gnu.org/licenses/>.

import requests
import json
import datetime
import dateutil.parser
import os
import io
import re
from ftplib import FTP
from xml.etree import ElementTree


def getEventData(streamer, id):
    # 動画データを取得
    videoResponse = requests.get(
        "https://www.googleapis.com/youtube/v3/videos",
        params={
            "key": apiKey,
            "id": id,
            "part": "snippet,liveStreamingDetails",
            "fields": "items(snippet(title,publishedAt),liveStreamingDetails(actualStartTime,actualEndTime,scheduledStartTime))",  # noqa
        },
    )
    videoData = videoResponse.json()
    # 取得できないなら終了
    if "items" not in videoData or len(videoData["items"]) == 0:
        return None
    # 生放送の場合
    if "liveStreamingDetails" in videoData["items"][0]:
        # 配信開始後の場合
        if "actualStartTime" in videoData["items"][0]["liveStreamingDetails"]:
            start = dateutil.parser.parse(
                videoData["items"][0]["liveStreamingDetails"]["actualStartTime"]
            )
            # 配信開始時間が昨日より前なら終了
            if start < yesterday:
                return None
            # 配信終了後の場合
            if "actualEndTime" in videoData["items"][0]["liveStreamingDetails"]:
                end = dateutil.parser.parse(
                    videoData["items"][0]["liveStreamingDetails"]["actualEndTime"]
                )
                # 配信時間が1時間以上の場合
                if (end - start) > datetime.timedelta(minutes=55):
                    return {
                        "id": id,
                        "title": videoData["items"][0]["snippet"]["title"],
                        "resourceId": streamer["id"],
                        "color": streamer["color"],
                        "textColor": streamer["textColor"],
                        "borderColor": streamer["borderColor"],
                        "start": start.astimezone(JST).isoformat(),
                        "end": end.astimezone(JST).isoformat(),
                        "imageurl": streamer["imageurl"],
                        "liveBroadcastContent": "over",
                        "channelName": streamer["channelName"],
                        "mode": "auto",
                        "platform": "youtube",
                        "thumbnailUrl": "https://img.youtube.com/vi/{0}/maxresdefault.jpg".replace(
                            "{0}", id
                        ),
                        "channelUrl": "https://www.youtube.com/channel/" + streamer["id"],
                    }
                # 配信時間が1時間以内の場合
                else:
                    return {
                        "id": id,
                        "title": videoData["items"][0]["snippet"]["title"],
                        "resourceId": streamer["id"],
                        "color": streamer["color"],
                        "textColor": streamer["textColor"],
                        "borderColor": streamer["borderColor"],
                        "start": start.astimezone(JST).isoformat(),
                        "allDay": False,
                        "imageurl": streamer["imageurl"],
                        "liveBroadcastContent": "over",
                        "channelName": streamer["channelName"],
                        "mode": "auto",
                        "platform": "youtube",
                        "thumbnailUrl": "https://img.youtube.com/vi/{0}/maxresdefault.jpg".replace(
                            "{0}", id
                        ),
                        "channelUrl": "https://www.youtube.com/channel/" + streamer["id"],
                    }
            # 配信中の場合
            else:
                # 配信時間が30分以上の場合
                if (now - start) > datetime.timedelta(minutes=25):
                    return {
                        "id": id,
                        "title": videoData["items"][0]["snippet"]["title"],
                        "resourceId": streamer["id"],
                        "color": streamer["color"],
                        "textColor": streamer["textColor"],
                        "borderColor": streamer["borderColor"],
                        "start": start.astimezone(JST).isoformat(),
                        "end": (now + datetime.timedelta(hours=1)).astimezone(JST).isoformat(),
                        "imageurl": streamer["imageurl"],
                        "liveBroadcastContent": "live",
                        "channelName": streamer["channelName"],
                        "mode": "auto",
                        "platform": "youtube",
                        "thumbnailUrl": "https://img.youtube.com/vi/{0}/maxresdefault.jpg".replace(
                            "{0}", id
                        ),
                        "channelUrl": "https://www.youtube.com/channel/" + streamer["id"],
                    }
                # 配信時間が30分以内の場合
                else:
                    return {
                        "id": id,
                        "title": videoData["items"][0]["snippet"]["title"],
                        "resourceId": streamer["id"],
                        "color": streamer["color"],
                        "textColor": streamer["textColor"],
                        "borderColor": streamer["borderColor"],
                        "start": start.astimezone(JST).isoformat(),
                        "allDay": False,
                        "imageurl": streamer["imageurl"],
                        "liveBroadcastContent": "live",
                        "channelName": streamer["channelName"],
                        "mode": "auto",
                        "platform": "youtube",
                        "thumbnailUrl": "https://img.youtube.com/vi/{0}/maxresdefault.jpg".replace(
                            "{0}", id
                        ),
                        "channelUrl": "https://www.youtube.com/channel/" + streamer["id"],
                    }
        # 配信開始前の場合
        else:
            start = dateutil.parser.parse(
                videoData["items"][0]["liveStreamingDetails"]["scheduledStartTime"]
            )
            if start < yesterday:
                return None
            return {
                "id": id,
                "title": videoData["items"][0]["snippet"]["title"],
                "resourceId": streamer["id"],
                "color": streamer["color"],
                "textColor": streamer["textColor"],
                "borderColor": streamer["borderColor"],
                "start": start.astimezone(JST).isoformat(),
                "allDay": False,
                "imageurl": streamer["imageurl"],
                "liveBroadcastContent": "upcoming",
                "channelName": streamer["channelName"],
                "mode": "auto",
                "platform": "youtube",
                "thumbnailUrl": "https://img.youtube.com/vi/{0}/maxresdefault.jpg".replace(
                    "{0}", id
                ),
                "channelUrl": "https://www.youtube.com/channel/" + streamer["id"],
            }
    # 動画の場合
    else:
        start = dateutil.parser.parse(videoData["items"][0]["snippet"]["publishedAt"])
        if start < yesterday:
            return None
        return {
            "id": id,
            "title": videoData["items"][0]["snippet"]["title"],
            "resourceId": streamer["id"],
            "color": streamer["color"],
            "textColor": streamer["textColor"],
            "borderColor": streamer["borderColor"],
            "start": start.astimezone(JST).isoformat(),
            "allDay": False,
            "imageurl": streamer["imageurl"],
            "liveBroadcastContent": "none",
            "channelName": streamer["channelName"],
            "mode": "auto",
            "platform": "youtube",
            "thumbnailUrl": "https://img.youtube.com/vi/{0}/maxresdefault.jpg".replace("{0}", id),
            "channelUrl": "https://www.youtube.com/channel/" + streamer["id"],
        }


def getTwitchHeaders(clientId, clientSecret):
    """Twitch認証"""
    url = "https://id.twitch.tv/oauth2/token"
    json = {
        "client_id": clientId,
        "client_secret": clientSecret,
        "grant_type": "client_credentials",
    }
    response = requests.post(url, json=json).json()
    headers = {
        "Authorization": "Bearer " + response["access_token"],
        "Client-id": clientId,
    }
    return headers


def getTwitchStreamEvent(headers, streamer):
    """Twitchライブデータ取得"""
    url = "https://api.twitch.tv/helix/streams"
    params = {"user_id": streamer["twitchId"]}
    response = requests.get(url, headers=headers, params=params).json()
    if len(response["data"]) == 0:
        streamEvent = {}
    else:
        videoData = response["data"][0]
        start = dateutil.parser.parse(videoData["started_at"])
        if now - start > datetime.timedelta(minutes=25):
            streamEvent = {
                "id": videoData["id"],
                "title": videoData["title"],
                "resourceId": streamer["id"],
                "color": streamer["color"],
                "textColor": streamer["textColor"],
                "borderColor": streamer["borderColor"],
                "start": start.astimezone(JST).isoformat(),
                "end": (now + datetime.timedelta(hours=1)).astimezone(JST).isoformat(),
                "imageurl": streamer["imageurl"],
                "liveBroadcastContent": "live",
                "channelName": streamer["channelName"],
                "mode": "auto",
                "platform": "twitch",
                "thumbnailUrl": videoData["thumbnail_url"]
                .replace("{width}", "1280")
                .replace("{height}", "720"),
                "channelUrl": "https://www.twitch.tv/" + streamer["englishTitle"],
            }
        else:
            streamEvent = {
                "id": videoData["id"],
                "title": videoData["title"],
                "resourceId": streamer["id"],
                "color": streamer["color"],
                "textColor": streamer["textColor"],
                "borderColor": streamer["borderColor"],
                "start": start.astimezone(JST).isoformat(),
                "allDay": False,
                "imageurl": streamer["imageurl"],
                "liveBroadcastContent": "live",
                "channelName": streamer["channelName"],
                "mode": "auto",
                "platform": "twitch",
                "thumbnailUrl": videoData["thumbnail_url"]
                .replace("{width}", "1280")
                .replace("{height}", "720"),
                "channelUrl": "https://www.twitch.tv/" + streamer["englishTitle"],
            }
    return streamEvent


def getTwitchArchive(headers, streamer):
    """Twitchアーカイブデータ取得"""
    url = "https://api.twitch.tv/helix/videos"
    params = {"user_id": streamer["twitchId"]}
    response = requests.get(url, headers=headers, params=params).json()
    videos = []
    for video in filter(lambda x: x["type"] == "archive", response["data"]):
        videos.append(video)
    return videos


def parseTwitchEventData(streamer, videoData):
    """Twitchビデオデータ整形"""
    start = dateutil.parser.parse(videoData["published_at"])
    if start < yesterday:
        return None
    regex = re.compile(r"((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?")
    parts = regex.match(videoData["duration"]).groupdict()  # type:ignore
    time_params = {}
    for name, param in parts.items():
        if param:
            time_params[name] = int(param)
    end = start + datetime.timedelta(**time_params)
    if end - start > datetime.timedelta(minutes=55):
        return {
            "id": videoData["id"],
            "title": videoData["title"],
            "resourceId": streamer["id"],
            "color": streamer["color"],
            "textColor": streamer["textColor"],
            "borderColor": streamer["borderColor"],
            "start": start.astimezone(JST).isoformat(),
            "end": end.astimezone(JST).isoformat(),
            "imageurl": streamer["imageurl"],
            "liveBroadcastContent": "over",
            "channelName": streamer["channelName"],
            "mode": "auto",
            "platform": "twitch",
            "thumbnailUrl": videoData["thumbnail_url"]
            .replace("%{width}", "1280")
            .replace("%{height}", "720"),
            "channelUrl": "https://www.twitch.tv/" + streamer["englishTitle"],
        }
    else:
        return {
            "id": videoData["id"],
            "title": videoData["title"],
            "resourceId": streamer["id"],
            "color": streamer["color"],
            "textColor": streamer["textColor"],
            "borderColor": streamer["borderColor"],
            "start": start.astimezone(JST).isoformat(),
            "allDay": False,
            "imageurl": streamer["imageurl"],
            "liveBroadcastContent": "over",
            "channelName": streamer["channelName"],
            "mode": "auto",
            "platform": "twitch",
            "thumbnailUrl": videoData["thumbnail_url"]
            .replace("%{width}", "1280")
            .replace("%{height}", "720"),
            "channelUrl": "https://www.twitch.tv/" + streamer["englishTitle"],
        }


def lambda_handler(lambdaEvent, context):
    # 変数の初期化
    global JST
    JST = datetime.timezone(datetime.timedelta(hours=+9), "JST")
    global now
    now = datetime.datetime.now(JST)
    print(now.astimezone(JST).isoformat())
    global yesterday
    yesterday = (now - datetime.timedelta(days=2)).replace(hour=12, minute=0)
    sevenDaysAgo = (now - datetime.timedelta(days=7)).replace(hour=0, minute=0)
    dayAfterTomorrow = (now + datetime.timedelta(days=2)).replace(hour=0, minute=0)
    # twoHoursAgo = now - datetime.timedelta(hours=2)
    global apiKey
    apiKey = os.environ["apiKey"]
    events = []
    failedResource = []
    checkPageCount = 2
    idList = []
    knownIdList = []
    # リソースデータとイベントデータを取得
    resources = requests.get("https://774today.ytclipplay.website/resources.json").json()
    knownEvents = requests.get("https://774today.ytclipplay.website/events.json").json()
    # 既存イベントの整理(youtubeのみ)
    for knownEvent in filter(lambda x: x["platform"] == "youtube", knownEvents):
        knownIdList.append(knownEvent["id"])
        # 配信中または配信前の場合はラベルを維持して更新
        if (
            knownEvent["liveBroadcastContent"] == "live"
            or knownEvent["liveBroadcastContent"] == "upcoming"
        ):
            for group in resources:
                for streamer in group["children"]:
                    if knownEvent["resourceId"] == streamer["id"]:
                        eventData = getEventData(streamer, knownEvent["id"])
                        if eventData is not None:
                            eventData["mode"] = knownEvent["mode"]
                            events.append(eventData)
        else:
            start = dateutil.parser.parse(knownEvent["start"])
            # 配信開始が昨日以降の場合は既存データを維持
            if yesterday < start:
                events.append(knownEvent)
            # それ以外は維持しない（削除）
            else:
                pass

    # グループごとに繰り返し
    for group in resources:
        # メンバーごとに繰り返し
        for streamer in group["children"]:
            print(streamer["title"])
            try:
                # チャンネルの配信を検索
                channelResponse = requests.get(
                    "https://www.googleapis.com/youtube/v3/search",
                    params={
                        "key": apiKey,
                        "channelId": streamer["id"],
                        "part": "id",
                        "fields": "nextPageToken,items(id(videoId))",
                        "type": "video",
                        "order": "date",
                        "publishedAfter": sevenDaysAgo.isoformat(),
                        "publishedBefore": dayAfterTomorrow.isoformat(),
                    },
                )
                # ページごとに繰り返し
                for pageNum in range(checkPageCount):
                    channelData = channelResponse.json()
                    # 未知のidを残す
                    idList = [
                        item["id"]["videoId"]
                        for item in channelData["items"]
                        if item["id"]["videoId"] not in knownIdList
                    ]
                    # idごとに繰り返し
                    for id in idList:
                        knownIdList.append(id)
                        # イベントデータを取得
                        eventData = getEventData(streamer, id)
                        if eventData is not None:
                            events.append(eventData)
                    # ページがまだあれば繰り返し
                    if pageNum < checkPageCount - 1 and "nextPageToken" in channelData:
                        channelResponse = requests.get(
                            "https://www.googleapis.com/youtube/v3/search",
                            params={
                                "key": apiKey,
                                "channelId": streamer["id"],
                                "part": "id",
                                "fields": "nextPageToken,items(id(videoId))",
                                "type": "video",
                                "order": "date",
                                "publishedAfter": sevenDaysAgo.isoformat(),
                                "publishedBefore": dayAfterTomorrow.isoformat(),
                                "pageToken": channelData["nextPageToken"],
                            },
                        )
                    else:
                        break
                # RSSフィードから近日の配信予定を取得
                streamerId = streamer["id"]
                namespace = "{http://www.w3.org/2005/Atom}"
                yt = "{http://www.youtube.com/xml/schemas/2015}"
                rssPage = requests.get(
                    f"https://www.youtube.com/feeds/videos.xml?channel_id={streamerId}"
                ).text
                root = ElementTree.fromstring(rssPage)
                for item in root.findall(f"{namespace}entry/{yt}videoId"):
                    videoId = item.text
                    if videoId not in knownIdList:
                        eventData = getEventData(streamer, videoId)
                        if eventData is not None:
                            eventData["mode"] = "rss"
                            events.append(eventData)
            except:
                failedResource.append(streamer["title"])
                continue

    # Twitch配信データ更新
    clientId = os.environ["clientId"]
    clientSecret = os.environ["clientSecret"]
    headers = getTwitchHeaders(clientId, clientSecret)
    for group in resources:
        for streamer in group["children"]:
            if streamer["twitchId"] < 0:
                continue
            print(streamer["title"] + "(Twitch)")
            try:
                streamEvent = getTwitchStreamEvent(headers, streamer)
                if streamEvent != {}:
                    events.append(streamEvent)
                videos = getTwitchArchive(headers, streamer)
                for video in filter(
                    lambda x: "id" not in streamEvent or x["stream_id"] != streamEvent["id"],
                    videos,
                ):
                    eventData = parseTwitchEventData(streamer, video)
                    if eventData is not None:
                        events.append(eventData)
            except:
                failedResource.append(streamer["title"] + "(Twitch)")
                continue

    log = {
        "datetime": datetime.datetime.now(JST).isoformat(),
        "totalEvents": str(len(events)),
        "failedResource": ",".join(failedResource),
    }

    ftp = FTP("sv37.star.ne.jp", "ytclipplay.website", os.environ["serverPassword"])
    ftp.cwd("774today.ytclipplay.website")
    f = io.BytesIO(json.dumps(events, indent=4).encode())
    ftp.storlines("STOR events.json", f)
    f = io.BytesIO(json.dumps(log, indent=4).encode())
    ftp.storlines("STOR log.json", f)
    ftp.quit()

    if 0 < len(failedResource):
        raise NameError("Failed to access channels of " + ",".join(failedResource))
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/html"},
        "body": "Update events successfully.",
    }
