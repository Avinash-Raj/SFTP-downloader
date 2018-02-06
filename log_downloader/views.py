import os
from django.http import JsonResponse
from django.shortcuts import render
# from django.exceptions import HttpResponseNotAllowed
from django.conf import settings
from paramiko.client import SSHClient, AutoAddPolicy
from contextlib import closing


def download_via_sftp(remote_dir, config):
    with closing(SSHClient()) as client:
        client.set_missing_host_key_policy(AutoAddPolicy)
        client.connect(
            config['host']
        )
        sftp_client = client.open_sftp()
        files = sftp_client.listdir(remote_dir)
        for file in files:
            local_dir = os.path.join(settings.MEDIA_PATH, config['host'])
            if not os.path.exists(local_dir): os.makedirs(local_dir)
            local_path = os.path.join(local_dir, file)
            remote_path = os.path.join(remote_dir, file)
            sftp_client.get(remote_path, local_path)

def download_view(request, *args, **kwargs):
    if request.method == 'GET':
        return JsonResponse({'resp': 'success'})

    try:
        hosts = dict(request.POST).get('hosts')
        if not hosts:
            return JsonResponse({'err': 'No hosts'})

        for host in hosts:
            download_via_sftp(settings.LOGS_PATH, {'host': host})

        return JsonResponse({'success': 'Files downloaded successfully'})
    except Exception:
        return JsonResponse({'err': 'Files failed to download!'})
