import asyncio
import logging
import os
from dotenv import load_dotenv
from panoramisk import Manager, Message

load_dotenv()
manager = Manager(
    host=os.getenv('AMI_HOST'),
    port=os.getenv('AMI_PORT'),
    username=os.getenv('AMI_USERNAME'),
    secret=os.getenv('AMI_SECRET'),
    ping_delay=10,  # Delay after start
    ping_interval=10,  # Periodically ping AMI (dead or alive)
    reconnect_timeout=2)  # Timeout reconnect if connection lost


def on_connect(mngr: Manager):
    logging.info('Connected to %s:%s AMI socket successfully' %
                 (mngr.config['host'], mngr.config['port']))


def on_login(mngr: Manager):
    logging.info('Connected user:%s to AMI %s:%s successfully' %
                 (mngr.config['username'], mngr.config['host'], mngr.config['port']))


def on_disconnect(mngr: Manager, exc: Exception):
    logging.info('Disconnect user:%s from AMI %s:%s' %
                 (mngr.config['username'], mngr.config['host'], mngr.config['port']))
    logging.debug(str(exc))


async def on_startup(mngr: Manager):
    await asyncio.sleep(0.1)
    logging.info('Something action...')


async def on_shutdown(mngr: Manager):
    await asyncio.sleep(0.1)
    logging.info('Shutdown AMI connection on %s:%s' %
                 (mngr.config['host'], mngr.config['port']))


@manager.register_event('*')  # Register all events
async def ami_callback(mngr: Manager, msg: Message):
    if msg.Event == 'FullyBooted':
        # print(msg)
        return msg


@manager.register_event('Newchannel')
async def callback(mngr: Manager, msg: Message):
    if msg.ChannelStateDesc == 'Down' and msg.Context != 'from-internal':
        if msg.CallerIDNum and msg.Exten:
            caller = msg.CallerIDNum
            number = msg.Exten
            # print(f'\nIncoming call\nfrom number: {caller}\nto number: {number}')
            return caller, number
    await asyncio.sleep(1)


@manager.register_event('Dial')
async def callback(mngr: Manager, msg: Message):
    if msg.DialStatus == 'ANSWER':
        # print('Call ended')
        call = 'Call ended'
        return call
    await asyncio.sleep(1)


def ami_connect():
    logging.basicConfig(level=logging.INFO)
    manager.on_connect = on_connect
    manager.on_login = on_login
    manager.on_disconnect = on_disconnect
    manager.connect(run_forever=True, on_startup=on_startup, on_shutdown=on_shutdown)


# ami_connect()
