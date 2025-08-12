import json
import os
import re
import csv
from collections import Counter, defaultdict
from datetime import datetime
from itertools import combinations

from modules.json_utils import JsonUtils


class TicketData:
    # Stores the path to the JSON file in self.file_path
    # Loads the ticket data using self.load_tickets()
    # and stores it in self.tickets
    def __init__(self, file_path):
        self.file_path = file_path
        self.tickets = self.load_tickets()


    # opens the file at self.file_path (which is the JSON file)
    # reads and loads the file using json.load(f)
    # json.load(f) returns the contents of a JSON file into a Python object
    # The JSON file contains a list of dictionaries, so json.load(f) returns a Python list of dicts
    # This result is returned by the method and saved as self.tickets in the constructor
    def load_tickets(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"{self.file_path} not found.")
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)


    def __iter__(self):
        return iter(self.tickets)


    def save(self):
        JsonUtils.save_list_to_json(self.tickets, self.file_path)
        print(f"✅ Tickets saved to {self.file_path}")


    def get_last_ticket_id(self):
        if not self.tickets:
            return None
        return max(ticket["id"] for ticket in self.tickets)
    

    def clean_tags(self):
        known_tags = set()
        for ticket in self.tickets:
            known_tags.update(ticket["tags"])

        tag_replacements = {}
        for tag in list(known_tags):
            if "_" in tag:
                continue
            for other in known_tags:
                if "_" in other and other.replace("_", "") == tag:
                    tag_replacements[tag] = other
                    break

        modified = 0
        for ticket in self.tickets:
            updated = []
            for tag in ticket["tags"]:
                if tag in tag_replacements:
                    updated.append(tag_replacements[tag])
                    modified += 1
                else:
                    updated.append(tag)
            ticket["tags"] = updated

        print(f"🔧 Cleaned {modified} tags.")
        self.save()


    def sanitize_tags(self):
        def clean_tag(tag):
            return re.sub(r'[\\/:*?"<>|]', "_", tag)

        modified = 0
        for ticket in self.tickets:
            cleaned_tags = []
            for tag in ticket.get("tags", []):
                clean = clean_tag(tag)
                if clean != tag:
                    modified += 1
                cleaned_tags.append(clean)
            ticket["tags"] = cleaned_tags

        print(f"🧼 Sanitized {modified} tag(s).")
        self.save()
        


    def seperate_version_tags(self):
        modified_count = 0

        for ticket in self.tickets:
            if "version" in ticket:
                continue

            ticket_tags = ticket.get("tags", [])
            version = []

            for ticket_tag in ticket_tags:

                if ticket_tag and ticket_tag[0].isdigit():
                    version.append(ticket_tag)

            if version:
                ticket["version"] = version
                for item in version:
                    ticket_tags.remove(item)
                    modified_count += 1
            else:
                ticket["version"] = None

        self.save()
        print(
            f"✅ Version tags extracted from {modified_count} tickets and removed from their tags."
        )


    def get_tags(self, file_path=None, return_tags=False):
        all_ticket_tags = []
        all_ticket_tags.extend(
            tag 
            for ticket in self.tickets 
            for tag in ticket.get("tags", [])
        )

        if file_path:
            unique_ticket_tags = set(all_ticket_tags)
            sorted_ticket_tags = sorted(unique_ticket_tags)
            JsonUtils.save_list_to_json(sorted_ticket_tags, file_path)

        if return_tags:
            return all_ticket_tags


    def count_tags(self, csv_file=None, ignored_tags=None):
        all_ticket_tags = self.get_tags(return_tags=True)

        if ignored_tags:
            filtered_tags = (tag for tag in all_ticket_tags if tag not in ignored_tags)
        else:
            filtered_tags = all_ticket_tags

        tag_counter = Counter(filtered_tags)

        if csv_file:
            with open(csv_file, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=["tags", "count"])
                writer.writeheader()
                for tag, count in tag_counter.most_common():
                    writer.writerow({"tags": tag, "count": count})

        return tag_counter


    def _parse_date_safe(self, date_string: str):
        if not date_string or date_string.strip() == "\u00a0":
            return None
        
        for date_format in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ"):
            try:
                return datetime.strptime(date_string, date_format)
            except ValueError:
                continue
        
        return None


    def get_monthly_tag_counts(self, tags, ignored_tags=None, months=12):
        selected_tags = set(tags)
        ignored_tags = set(ignored_tags or [])

        latest_ticket_date = self._parse_date_safe(self.tickets[-1].get("date_created", ""))

        months_list = []
        year = latest_ticket_date.year
        month = latest_ticket_date.month

        month -= 1
        if month == 0:
            month = 12
            year -= 1
            
        for _ in range(months):
            months_list.append((year, month))
            month -= 1
            if month == 0:
                month = 12
                year -= 1
        months_list.reverse()  # chronological order

        monthly_counts = defaultdict(int)

        valid_months = set(months_list)  # quick lookup

        min_year, min_month = months_list[0]      # earliest in window
        max_year, max_month = months_list[-1]     # latest in window

        for ticket in reversed(self.tickets):  # newest first
            ticket_date = self._parse_date_safe(ticket.get("date_created", ""))
            if not ticket_date:
                continue

            ym = (ticket_date.year, ticket_date.month)

            if ym > (max_year, max_month):
                continue

            if ym < (min_year, min_month):
                break

            for tag in ticket.get("tags", []):
                if tag in selected_tags and tag not in ignored_tags:
                    monthly_counts[(ym, tag)] += 1

        index = [datetime(y, m, 1) for (y, m) in months_list]
        series = {
            tag: [monthly_counts.get(((y, m), tag), 0) for (y, m) in months_list]
            for tag in selected_tags
            if tag not in ignored_tags
        }

        return index, series

    
    def get_yearly_tag_counts(self, tags, ignored_tags=None, start_year=2017):
        selected_tags = set(tags)
        ignored_tags = set(ignored_tags or [])
        
        latest_ticket_date = self._parse_date_safe(self.tickets[-1].get("date_created", ""))
        if not latest_ticket_date:
            return [], {tag: [] for tag in tags}
        
        years_list = list(range(start_year, latest_ticket_date.year + 1))
        yearly_counts = defaultdict(int)
        
        for ticket in reversed(self.tickets):  # newest → oldest
            ticket_date = self._parse_date_safe(ticket.get("date_created", ""))
            if not ticket_date:
                continue

            year_val = ticket_date.year
            if year_val < start_year:
                break  # stop when we go before our window

            for tag in ticket.get("tags", []):
                if tag in selected_tags and tag not in ignored_tags:
                    yearly_counts[(year_val, tag)] += 1

        index = [datetime(y, 1, 1) for y in years_list]
        series = {
            tag: [yearly_counts.get((y, tag), 0) for y in years_list]
            for tag in selected_tags
            if tag not in ignored_tags
        }

        return index, series


    def build_cooccurrence(self, tags, ignored_tags=None):
        ignored = set(ignored_tags or [])
        labels = [t for t in tags if t not in ignored]

        tag_index = {t: i for i, t in enumerate(labels)}
        n = len(labels)

        matrix = [[0] * n for _ in range(n)]

        for ticket in self.tickets:
            ticket_tags = ticket.get("tags", []) or []
            present = [t for t in set(ticket_tags) if t in tag_index]
            if len(present) < 2:
                continue
            for a, b in combinations(present, 2):
                i, j = tag_index[a], tag_index[b]
                matrix[i][j] += 1
                matrix[j][i] += 1  # keep symmetric
            
        return matrix, labels
        
















    # self refers to the instance of the class you are calling the method on.
    # "ignore_tags=None" so that we can call this method without needing to pass a second argument
    def create_tag_subfolders(self, base_dir, ignore_tags=None):
        # Because None is not iterable
        # this check ensures ignore_tags is always a list
        # — either passed by you or defaulting to []
        if ignore_tags is None:
            ignore_tags = []

        for ticket in self.tickets:
            # Uses .get() in case the "type" key does not exist.
            # If the value is None or "", it still assigns "null" using 'or "null"'
            ticket_type = ticket.get("type", "null") or "null"
            ticket_tags = ticket.get("tags", [])

            # the base directory is "D:\Desktop\larsa_AI_project\zendesk\ticket_comments"
            # folders for all ticket types are created
            # "exist_ok=True" tells python do not throw an error if this folder already exists.
            type_folder = os.path.join(base_dir, ticket_type)
            os.makedirs(type_folder, exist_ok=True)

            for ticket_tag in ticket_tags:
                if ticket_tag in ignore_tags:
                    continue
                ticket_tag_folder = os.path.join(type_folder, ticket_tag)
                os.makedirs(ticket_tag_folder, exist_ok=True)

        print(f"✅ Folders created at: {base_dir}")
