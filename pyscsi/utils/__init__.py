# SPDX-FileCopyrightText: 2014 The python-scsi Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

import socket

from .converter import *
from .enum import *


def init_device(
    dev,
    read_write=False,
    initiator_name=f"iqn.2018-01.org.pyscsi:{socket.gethostname()}",
    context_params=None,
):
    """
    :param context_params: iSCSI-only.  An optional dict of extra
        iscsi.Context settings applied before login, e.g.
        {"isid_en": (enterprise_number, qualifier)}.  See ISCSIDevice.
        Ignored for local (/dev/) devices, which have no login step.
    """
    if dev[:5] == "/dev/":
        from pyscsi.pyscsi.scsi_device import SCSIDevice

        device = SCSIDevice(dev, read_write)
    elif dev[:8] == "iscsi://":
        from pyscsi.pyiscsi.iscsi_device import ISCSIDevice

        device = ISCSIDevice(dev, initiator_name, context_params)
    else:
        raise NotImplementedError("No backend implemented for %s" % dev)
    return device
