import os
import pandas as pd
from user_agents import parse
import itertools
import random
import threading
from django.conf import settings
from ..models import IP, Agent
from ..log import log_etl as log


def extractor(file_name):
    """
    Method that reads a file in chunks of chunk_size
    :param file_name: name of the file
    :param chunk_size: the size of the batches
    :return: a list of dataframes. A dataframe is a list of chunk_size rows containing the row index as first element.
    """
    log.info('Extractor is running for file: %s', file_name)
    chunk_list = []
    # merge date and time columns in a single date_time column(improves performance - speed and memory used)
    # url column is not needed for the task so it's not loaded from the file (improves performance)
    index = 0
    for chunk in pd.read_csv(file_name,
                             sep='\t',
                             names=['date', 'time', 'user_id', 'url', 'IP', 'user_agent_string'],
                             chunksize=random.randint(settings.CHUNK_SIZE_MIN, settings.CHUNK_SIZE_MAX),
                             compression='gzip',
                             parse_dates=[[0, 1]], usecols=[0, 1, 2, 4, 5],
                             engine='c'):
        log.info('Extracted chunk: %s', chunk.axes[0])
        chunk_list.append(chunk)
        # if index > 10:
        #     break
        index += 1

    return chunk_list


def parse_user_agent(ua_string):
    """
    Method that parses the user agent string. It identifies the browser,
    browser version, os and os version, device manufacturer and device type:mobile,tablet,
    pc,console.
    Method is also creating the database object, without actually inserting it in the db.
    :param ua_string:
    :return: Agent instance
    """
    agent = Agent()
    try:
        result = parse(ua_string)
    except Exception:
        log.exception('Unable to parse user agent: %s', ua_string)
        return [agent]

    # if len(ua_string) >= 256:
    #     log.warning('ua_string > 256. Will be truncated: %s', ua_string)
    agent.agent_string = ua_string[:256]
    agent.op_sys = result.os.family
    agent.op_sys_version = result.os.version_string
    agent.browser = result.browser.family
    agent.browser_version = result.browser.version_string
    agent.device = result.device.family
    agent.device_brand = result.device.brand
    if result.is_pc:
        agent.device_type = 'desktop'
    elif result.is_mobile:
        agent.device_type = 'mobile'
    elif result.is_tablet:
        agent.device_type = 'tablet'
    elif result.is_bot:
        agent.device_type = 'crawler'
    else:
        agent.device_type = 'unknown'
    return agent


def parse_user(user_id, users):
    """
    It's not parsing anything, just creates a CustomUser instance
    :param user_id: user_id string
    :return: CustomUser instance
    """
    # check if the user is already in the database. It must be unique
    # log.info('index %s', user_id)
    return users.loc[user_id].custom_user


def get_city_country(ip, ip2loc):
    """
    Get from one run the city and the country in a touple
    :param ip:
    :param ip2loc:
    :return:
    """
    try:
        ip_all = ip2loc.get_all(ip)
        ip_instance = IP(ip=ip, city=ip_all.city, country=ip_all.country_long)
    except Exception as err:
        ip_instance = IP(ip=ip)
    return ip_instance


def transform_and_load(chunk, users, ip2loc):
    """
    Transforms the data and loads it into a database for further use/processing
    :return:
    """
    # initialize IP parsers

    chunk['ip_instances'] = chunk.IP.apply(lambda row: [get_city_country(ip.strip(), ip2loc) for ip in row.split(',')])

    # save into the database using a separate thread. This task is IO bound. Parsing the agents is CPU bound.
    # maximize the use of CPU this way
    threads = []
    ip_thread = threading.Thread(target=IP.objects.bulk_create,
                     args=[list(itertools.chain.from_iterable(chunk.ip_instances)), settings.CHUNK_SIZE])
    threads.append(ip_thread)
    ip_thread.start()
    chunk['agent_instances'] = chunk.user_agent_string.apply(parse_user_agent)

    agent_thread = threading.Thread(target=Agent.objects.bulk_create,
                     args=[list(chunk.agent_instances.values), settings.CHUNK_SIZE])
    threads.append(agent_thread)
    agent_thread.start()
    chunk['custom_users'] = chunk.user_id.apply(lambda row: parse_user(row, users))
