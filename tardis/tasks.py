import traceback
import os
import logging

from django.conf import settings

from tardis.celery import app
from tardis.utils import checksum

logger = logging.getLogger(__name__)


@app.task(name='mytardis.verify_dfo')
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
            app.send_task(
                'tardis_portal.datafileobject.verified',
                args=[
                    dfo_id,
                    algorithm,
                    chksum
                ],
                queue=settings.API_QUEUE,
                priority=settings.API_TASK_PRIORITY
            )
        except Exception as e:
            logger.error('dfo=%s: an error occurred', dfo_id)
            logger.error(str(e))
            logger.debug(traceback.format_exc())
    else:
        logger.error('dfo=%s: file does not exist', dfo_id)
