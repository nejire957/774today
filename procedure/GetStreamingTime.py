import requests,json,datetime,dateutil.parser,calendar,os,io
from ftplib import FTP
def lambda_handler(lambdaEvent,context):
    JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')
    now = datetime.datetime.now(JST)
    print(now.astimezone(JST).isoformat())
    yesterday = (now - datetime.timedelta(days=1)).replace(hour=0,minute=0)
    publishedAfter = (now - datetime.timedelta(days=7)).replace(hour=0,minute=0)
    publishedBefore = (now + datetime.timedelta(days=2)).replace(hour=0,minute=0)
    twoHourAgo = now - datetime.timedelta(hours=2)
    apiKey = os.environ['apiKey']
    resources = requests.get("https://774today.ytclipplay.website/resources.json").json()
    knownEvents = requests.get("https://774today.ytclipplay.website/events.json").json()
    events = []
    failedResource = []
    for knownEvent in knownEvents:
        start = dateutil.parser.parse(knownEvent["start"])
        if yesterday < start < twoHourAgo:
            events.append(knownEvent)
    newEventCount = 0
    for group in resources:
        for streamer in group["children"]:
            print(streamer["title"])
            channelResponse = requests.get("https://www.googleapis.com/youtube/v3/search",params={
                "key":apiKey,
                "channelId":streamer["id"],
                "part":"id",
                "fields":"nextPageToken,items(id(videoId))",
                "type":"video",
                "order":"date",
                "publishedAfter":publishedAfter.isoformat(),
                "publishedBefore":publishedBefore.isoformat()
            })
            timeoverFlag = False
            try:
                channelData = channelResponse.json()
                for item in channelData["items"]:
                    isKnown = False
                    skip = False
                    for event in events:
                        if event["id"] == item["id"]["videoId"]:
                            isKnown = True
                            if event["liveBroadcastContent"] == "over" or event["liveBroadcastContent"] == "none":
                                skip = True
                            else:
                                oldEvent = event
                            break
                    if isKnown:
                        if skip:
                            continue
                        else:
                            events.remove(oldEvent)
                    videoResponse = requests.get("https://www.googleapis.com/youtube/v3/videos",params={
                        "key":apiKey,
                        "id":item["id"]["videoId"],
                        "part":"snippet,liveStreamingDetails",
                        "fields":"items(snippet(title,publishedAt),liveStreamingDetails(actualStartTime,actualEndTime,scheduledStartTime))"
                    })
                    videoData = videoResponse.json()
                    if "items" not in videoData or len(videoData["items"]) == 0:
                        continue
                    if "liveStreamingDetails" in videoData["items"][0]:
                        if "actualStartTime" in videoData["items"][0]["liveStreamingDetails"]:
                            start = dateutil.parser.parse(videoData["items"][0]["liveStreamingDetails"]["actualStartTime"])
                            if start < yesterday:
                                continue
                            if "actualEndTime" in videoData["items"][0]["liveStreamingDetails"]:
                                end = dateutil.parser.parse(videoData["items"][0]["liveStreamingDetails"]["actualEndTime"])
                                if end - start > datetime.timedelta(minutes=55):
                                    events.append({
                                        "id":item["id"]["videoId"],
                                        "title":videoData["items"][0]["snippet"]["title"],
                                        "resourceId":streamer["id"],
                                        "color":streamer["color"],
                                        "textColor":streamer["textColor"],
                                        "borderColor":streamer["borderColor"],
                                        "start":start.astimezone(JST).isoformat(),
                                        "end":end.astimezone(JST).isoformat(),
                                        "imageurl":streamer["imageurl"],
                                        "liveBroadcastContent":"over",
                                        "channelName":streamer["channelName"]
                                    })
                                    newEventCount += 1
                                else:
                                    events.append({
                                        "id":item["id"]["videoId"],
                                        "title":videoData["items"][0]["snippet"]["title"],
                                        "resourceId":streamer["id"],
                                        "color":streamer["color"],
                                        "textColor":streamer["textColor"],
                                        "borderColor":streamer["borderColor"],
                                        "start":start.astimezone(JST).isoformat(),
                                        "allDay":False,
                                        "imageurl":streamer["imageurl"],
                                        "liveBroadcastContent":"over",
                                        "channelName":streamer["channelName"]
                                    })
                                    newEventCount += 1
                            else:
                                if (now - start) > datetime.timedelta(hours=1):
                                    events.append({
                                        "id":item["id"]["videoId"],
                                        "title":videoData["items"][0]["snippet"]["title"],
                                        "resourceId":streamer["id"],
                                        "color":streamer["color"],
                                        "textColor":streamer["textColor"],
                                        "borderColor":streamer["borderColor"],
                                        "start":start.astimezone(JST).isoformat(),
                                        "end":(now + datetime.timedelta(hours=1)).astimezone(JST).isoformat(),
                                        "imageurl":streamer["imageurl"],
                                        "liveBroadcastContent":"live",
                                        "channelName":streamer["channelName"]
                                    })
                                    newEventCount += 1
                                else:
                                    events.append({
                                        "id":item["id"]["videoId"],
                                        "title":videoData["items"][0]["snippet"]["title"],
                                        "resourceId":streamer["id"],
                                        "color":streamer["color"],
                                        "textColor":streamer["textColor"],
                                        "borderColor":streamer["borderColor"],
                                        "start":start.astimezone(JST).isoformat(),
                                        "allDay":False,
                                        "imageurl":streamer["imageurl"],
                                        "liveBroadcastContent":"live",
                                        "channelName":streamer["channelName"]
                                    })
                                    newEventCount += 1
                        else:
                            start = dateutil.parser.parse(videoData["items"][0]["liveStreamingDetails"]["scheduledStartTime"])
                            if start < yesterday:
                                continue
                            events.append({
                                "id":item["id"]["videoId"],
                                "title":videoData["items"][0]["snippet"]["title"],
                                "resourceId":streamer["id"],
                                "color":streamer["color"],
                                "textColor":streamer["textColor"],
                                "borderColor":streamer["borderColor"],
                                "start":start.astimezone(JST).isoformat(),
                                "allDay":False,
                                "imageurl":streamer["imageurl"],
                                "liveBroadcastContent":"upcoming",
                                "channelName":streamer["channelName"]
                            })
                            newEventCount += 1
                    else:
                        start = dateutil.parser.parse(videoData["items"][0]["snippet"]["publishedAt"])
                        if start < yesterday:
                            continue
                        events.append({
                            "id":item["id"]["videoId"],
                            "title":videoData["items"][0]["snippet"]["title"],
                            "resourceId":streamer["id"],
                            "color":streamer["color"],
                            "textColor":streamer["textColor"],
                            "borderColor":streamer["borderColor"],
                            "start":start.astimezone(JST).isoformat(),
                            "allDay":False,
                            "imageurl":streamer["imageurl"],
                            "liveBroadcastContent":"none",
                            "channelName":streamer["channelName"]
                        })
                        newEventCount += 1
            except:
                failedResource.append(streamer["title"])
                continue                
    log = {
        "datetime":now.astimezone(JST).isoformat(),
        "newEvents":str(newEventCount),
        "totalEvents":str(len(events)),
        "failedResource":','.join(failedResource)
    }
    ftp = FTP("sv37.star.ne.jp","ytclipplay.website",os.environ['serverPassword'])
    ftp.cwd("774today.ytclipplay.website")
    f = io.BytesIO(json.dumps(events, indent=4).encode())
    ftp.storlines("STOR events.json",f)
    f = io.BytesIO(json.dumps(log, indent=4).encode())
    ftp.storlines("STOR log.json",f)
    ftp.quit()
    if 0 < len(failedResource):
        raise NameError("Failed to access channels of " + ','.join(failedResource))
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/html"},
        "body": "Update events successfully."
    }
