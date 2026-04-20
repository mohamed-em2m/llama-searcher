from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def parse_iso_datetime(s: str) -> Optional[datetime]:
    if not s:
        return None

    now = datetime.now(timezone.utc).astimezone()

    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(s, fmt)
        except (ValueError, TypeError):
            continue

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=now.tzinfo)

        if dt >= now:
            return dt

    return None


def extract_events(data: List[Dict[str, Any]]) -> str:
    events = []
    for item in data:
        if "pagemap" in item and "Event" in item["pagemap"]:
            events.append("Name|Date|url")
            for event in item["pagemap"]["Event"]:
                events.append(
                    f"{event.get('name')}|{event.get('startDate')}|{event.get('url')}"
                )
    return "\n".join(events)


def extract_events_from_search(
    search_results: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    extracted_events = []
    if not isinstance(search_results, list):
        return extracted_events

    seen_events = set()

    for result in search_results:
        pagemap = result.get("pagemap", {})
        if not pagemap:
            continue

        for event_type, extract_keys in [
            (
                "sportsevent",
                ("name", "startdate", "hometeam", "awayteam", "organization"),
            ),
            ("hcalendar", ("summary", "dtstart", "description", None, None)),
            ("event", ("summary", "dtstart", "description", None, None)),
        ]:
            for event_data in pagemap.get(event_type, []):
                name = event_data.get(extract_keys[0])
                start_date_str = event_data.get(extract_keys[1])

                event_identifier = (name, start_date_str)
                if event_identifier in seen_events:
                    continue

                event_info = {
                    "source": event_type,
                    "name": name,
                    "start_date_raw": start_date_str,
                    "location": event_data.get("location"),
                    "url": event_data.get("url"),
                    "result_title": result.get("title"),
                    "result_link": result.get("link"),
                }

                if extract_keys[2]:
                    event_info["description"] = event_data.get(extract_keys[2])
                if len(extract_keys) > 3 and extract_keys[3]:
                    event_info["home_team"] = event_data.get(extract_keys[3])
                if len(extract_keys) > 4 and extract_keys[4]:
                    event_info["organization"] = event_data.get(extract_keys[4])

                try:
                    if start_date_str:
                        dt_part = start_date_str.split("T")[0]
                        event_info["start_date_parsed"] = datetime.strptime(
                            dt_part, "%Y-%m-%d"
                        ).date()
                except (ValueError, TypeError):
                    event_info["start_date_parsed"] = None

                if name and start_date_str:
                    extracted_events.append(event_info)
                    seen_events.add(event_identifier)

    extracted_events.sort(
        key=lambda x: x.get("start_date_parsed") or datetime.min.date()
    )
    return extracted_events


def format_extracted_events(events: List[Dict[str, Any]]) -> str:
    if not events:
        return "No events found"

    result = ["source|name|start_date|location|url|result_title|result_link"]
    now = datetime.now().date()

    for event in events:
        date_str = (
            str(event.get("start_date_parsed", "N/A"))
            if event.get("start_date_parsed")
            else event.get("start_date_raw", "N/A")
        )
        row = f"{event.get('source', 'N/A')}|{event.get('name', 'N/A')}|{date_str}|{event.get('location', 'N/A')}|{event.get('url', 'N/A')}|{event.get('result_title', 'N/A')}|{event.get('result_link', 'N/A')}"

        try:
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if parsed_date >= now:
                result.append(row)
        except ValueError:
            result.append(row)

    return "\n".join(result)


def extract_events_all(items: List[Dict[str, Any]]) -> str:
    events = ["title|summary|description|dtstart|startdate|url"]

    for item in items:
        pm = item.get("pagemap", {})
        for key in ("event", "hcalendar", "sportsevent"):
            for ev in pm.get(key, []):
                summary = (
                    ev.get("summary") or ev.get("name") or ev.get("description", "")
                )
                dt_str = ev.get("dtstart") or ev.get("startdate")
                dt = parse_iso_datetime(dt_str) if dt_str else None
                url = ev.get("url") or item.get("link", "")

                if dt:
                    events.append(f"{item.get('title', 'N/A')}|{summary}|{dt}|{url}")

    return "\n".join(events)
