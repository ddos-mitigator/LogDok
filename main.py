# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2019 BIFIT

import docker
import os


status_ok = '200 OK'
status_400 = '400 Bad Request'
status_401 = '401 Unauthorized'
status_403 = '403 Forbidden'
status_404 = '404 Not Found'
status_500 = '500 Internal Server Error'

headers_html = [('Content-Type','text/html')]
headers_plain = [('Content-Type','text/plain')]

client = docker.APIClient()


class SiteAccessException(Exception):
  def __init__(self, content):
    super(SiteAccessException).__init__()
    self.content = content

class SiteQueryException(Exception):
  def __init__(self, content):
    super(SiteQueryException).__init__()
    self.content = content


def get_maincontent():
  container_list = get_containerslist()
  content_string = '\n'.join(
    f'''
          <tr>
            <td>{container['Name']}</td>
            <td><a href="log?name={container['Name']}">{container['Status']}</a></td>
          </tr>'''
    for container in container_list)
  return content_string.encode()

def get_containerslist():
  container_list = [{'Name': container["Names"][0][1:], 'Status': container["Status"]}
    for container in client.containers(all=True)]

  return container_list


def get_log(query_string, auth_string):
  auth_key = os.getenv('SP_AUTH_KEY')
  if auth_key and auth_string != auth_key:
    raise SiteAccessException('X-Auth-Token not valid')

  if query_string:
    query_list = query_string.split('&')
    container_name = None
    try:
      env_tail = os.getenv('SP_DEFAULT_TAIL')
      tail = env_tail if env_tail == 'all' else int(env_tail)
    except (ValueError, TypeError):
      tail = 15

    for query in query_list:
      param_list = query.split('=')
      try:
        if param_list[0] == 'name':
          container_name = param_list[1]
        elif param_list[0] == 'tail':
          tail = param_list[1] if param_list[1] == 'all' else int(param_list[1])
      except (IndexError, ValueError):
        raise SiteQueryException(f'for field {param_list[0]} value not set [or incorrect]\n'.encode())

    try:
      return get_containerlog(container_name, tail)
    except:
      raise SiteQueryException(f'logs not found for {container_name}, tail {tail}\n'.encode())

  else:
    raise SiteQueryException('query not set\n'.encode())

def get_containerlog(container_name, tail):
  log = client.logs(container_name, tail=tail)
  if not log:
    log = 'log is empty'.encode()
  return log


def application(env, start_responce):

  path = env.get('PATH_INFO')

  try:
    client.ping()
  except:
    start_responce(status_500, headers_plain)
    print('\nERROR:\nDocker client not init\n')
    return 'c.p() error, contact administrator\n'.encode()

  if path == '/stat':
    start_responce (status_ok, headers_html)
    return get_maincontent()

  elif path == '/log':

    print('\n',env,'\n')

    query_string = env.get('QUERY_STRING')
    auth_string = env.get('HTTP_X_AUTH_TOKEN')

    try:
      content = get_log(query_string, auth_string)
      start_responce(status_ok, headers_plain)
      return content
    except SiteQueryException as qe:
      start_responce(status_400, headers_plain)
      return qe.content
    except SiteAccessException as ae:
      start_responce(status_403, headers_plain)
      return ae.content

  else:
    start_responce(status_404, headers_plain)
    return 'not found\n'.encode()
