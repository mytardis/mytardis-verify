import traceback
import os
import logging

from verify.settings import config
from verify.worker import app
from verify.utils import checksum

logger = logging.getLogger(__name__)


@app.task(name='verify_dfo')
def verify_dfo(dfo_id, filename, ref_id, algorithm='md5'):
    # Accept task
    logger.debug('dfo=%s: verify %s (ref=%s)', dfo_id, filename, ref_id)

    # Check if file exists
    if os.path.exists(filename):
        # Calculate checksum
        chksum = checksum(filename, algorithm)
        logger.debug('dfo=%s: checksum %s', dfo_id, chksum)
        try:
            # Send checksum back to mothership
            q = config['queues']['api']
            app.send_task(
                'tardis_portal.datafileobject.verified',
                args=[
                    dfo_id,
                    algorithm,
                    chksum
                ],
                queue=q['name'],
                priority=q['task_priority']
            )
        except Exception as e:
            logger.error('dfo=%s: an error occurred', dfo_id)
            logger.error(str(e))
            logger.debug(traceback.format_exc())
    else:
        logger.error('dfo=%s: file does not exist (%s)', dfo_id, filename)
