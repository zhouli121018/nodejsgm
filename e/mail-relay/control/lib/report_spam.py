# coding=utf-8
import time

import re
import uuid
import os
import subprocess

from common import shell_escape_str, timeout_command

DSPAMC = '/usr/bin/dspamc --client --user umail --stdout --deliver=summary'
SPAMC = "cat '{}' | /usr/bin/spamc -R"
SAVSCAN = '/usr/local/bin/savscan -ss {}'


def dspamc(file_path='', sig='', report=''):
    kwargs = {
        'file_path': shell_escape_str(file_path),
        'sig': sig,
        'report': report,
        'dspamc': DSPAMC
    }
    if report:
        cmd = "cat '{file_path}' | {dspamc} --mode=teft --source=corpus --class={report} --feature=noise".format(
            **kwargs)
        """
        if sig and sig != 'n/a':
            cmd = "{dspamc} --class={report} --source=error --signature={sig}".format(**kwargs)
        else:
            cmd = "cat '{file_path}' | {dspamc} --mode=teft --source=corpus --class={report} --feature=noise".format(
                **kwargs)
        """
    else:
        cmd = "cat '{file_path}' | /usr/bin/dspamc --classify --user umail --stdout --deliver=summary".format(**kwargs)
    res = timeout_command(cmd, timeout=30)
    # res = subprocess.check_output(cmd, shell=True)
    res = parse_dspamc_result(res)
    return res

def dspamc2(message):
    p = subprocess.Popen(DSPAMC.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    output, _ = p.communicate(message)
    return parse_dspamc_result(output)


def spamc(file_path):
    cmd = SPAMC.format(shell_escape_str(file_path))
    # res = subprocess.check_output(cmd, shell=True)
    res = timeout_command(cmd, timeout=60)
    res = parse_spamc_result(res)
    return res


def esets(file_path):
    cmd = "/opt/eset/esets/bin/esets_cli '{}'".format(file_path)
    try:
        res = timeout_command(cmd, 30)
        message = ''.join(res)
        m0 = re.search('action="(.+)"', message)
        if m0 is not None:
            return {
                'action': m0.group(1),
                'message': message
            }
    except Exception as e:
        message = repr(e)
    return {
        'action': 'exception',
        'message': message,
    }


def parse_dspamc_result(res):
    if not res:
        return {}
    if isinstance(res, list):
        res = res[0]
    d = dict([l.lower().replace('"', '').replace('=', ':').replace(' ', '').split(':') for l in res.replace('\n', '').split(';')])
    d['message'] = res
    return d

def parse_spamc_result(res):
    if not res:
        return {}
    d = {}
    try:
        d['score'] = res[0].split('/')[0]
    except BaseException as e:
        d['score'] = ''
    message = ''.join(res)
    d['message'] = message[message.find('Content analysis details'): -1].replace('\n', '</br>')
    return d

def savscan_attach(attach):
    """
    :param attachdict {'name', 'decode_name', 'data'}:
    :return:
    """
    filename = '/tmp/{}'.format(str(uuid.uuid1()))
    with open(filename, 'w') as fw:
        fw.write(attach.get('data', ''))
    res = savscan(filename)
    os.unlink(filename)
    return res


def savscan(file_path):
    cmd = SAVSCAN.format(shell_escape_str(file_path))
    res = timeout_command(cmd, timeout=60)
    res = parse_savscan_result(res)
    return res


def parse_savscan_result(res):
    if not res:
        return {}
    res = res[0]
    return re.findall("Virus '(.*?)' found", res)


if __name__ == "__main__":
    print time.time()
    file_path = '/home/comingchina/documents/3.eml'
    file_path = '/home/comingchina/work/mail-relay/data/20150605/20150605,1637,5,aaa@dspam.org.cn,881bbb@dspam.org.cn'
    # res = spamc(file_path)
    file_path = '/tmp/transcript.zip'
    #res = savscan(file_path)
    #print res
    file_path = '/home/umail/data/c_20160831/20160831,32661'
    from parse_email import ParseEmail
    email_str = open(file_path, 'r').read()
    print len(email_str)
    print dspamc2(email_str)
    #p = ParseEmail(email_str)
    # print p.get_login_username()
    #data = p.parseMailTemplate()
    #for attach in data.get('attachments', []):
    #    print savscan_attach(attach)
    # str = 'X-DSPAM-Result: extmail; result="Innocent"; class="Innocent"; probability=0.0000; confidence=0.95; signature=26,5559a5f4218361037928413'
    # print len(str)
    # res = parse_dspamc_result(str)
    # res = dspamc(sig='26,556d25d725925734528481', report='spam')
    # print res
    # print res.get('result', '')
