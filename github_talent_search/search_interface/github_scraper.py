import re
import logging
from collections import Counter
from logging import Logger
from typing import Dict

import requests
from django.conf import settings
from google.cloud import bigquery
from google.oauth2 import service_account
from jinjasql import JinjaSql

from search_interface.models import UserEmail

logger: Logger = logging.getLogger(__name__)

with settings.USERS_QUERY_FILE_PATH.open() as query_file:
    query_template: str = query_file.read()


class Scraper:
    github_events_url: str = 'https://api.github.com/users/{username}/events/public?per_page=100'
    email_regex = r'"email":"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"'

    def __init__(self):
        self.github_token: str = settings.GITHUB_TOKEN
        credentials = service_account.Credentials.from_service_account_file(str(settings.CREDENTIALS_FILE_PATH))

        self.client = bigquery.Client(credentials=credentials)

    def find_emails(self, event_response: str):
        regex = re.compile(self.email_regex)
        all_emails = regex.findall(event_response)
        return dict(Counter(all_emails))

    def save_emails(self, username, emails):
        for email, occurrence in emails.items():
            logger.info(f'saving email {email} for user {username}')
            UserEmail.objects.get_or_create(username=username, email=email, occurrence=occurrence)

    def scrape_user_emails(self, username):
        logger.info(f'scraping emails for user {username}')
        # get stored emails if user has been searched for before
        emails_queryset = UserEmail.objects.filter(username=username)
        if emails_queryset.exists():
            emails = {email: occurrence for email, occurrence in emails_queryset.values_list('email', 'occurrence')}
            logger.info(f'{emails_queryset.count()} emails found in the database for username {username}: {emails}')
            return emails

        # TODO: do this in a loop a couple of times if no email has been found
        # in hopes there's some pushevent buried under other activity
        logger.info(f'no emails in database for user {username}, looking for emails in github now.')
        response = requests.get(self.github_events_url.format(username=username),
                                headers={'Authorization': f'token {self.github_token}'})
        emails = self.find_emails(response.text)
        logger.info(f'{len(emails)} emails found in github for username {username}: {emails}')
        self.save_emails(username, emails)
        return emails

    def query_github_projects(self, query_data):
        parser = JinjaSql(param_style='pyformat')
        query, bind_params = parser.prepare_query(query_template, query_data)
        query_results = self.client.query(query % bind_params)
        return query_results

    def get_projects(self, query_criteria: Dict):
        project_results = self.query_github_projects(query_criteria)
        projects_data = [
            {
                'username': project_data['username'],
                'emails': self.scrape_user_emails(project_data['username']),
                'country': project_data['country_name'],
                'project_of_interest': project_data['project_name'],
                'project_stars': project_data['project_stars'],
                'project_url': project_data['project_url']
            } for project_data in project_results
        ]
        logger.info(f'data found: {projects_data}')
        return projects_data
