# coding: utf-8

# Copyright (C) 2014 by Ronnie Sahlberg<ronniesahlberg@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2.1 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

from pydiskcmd.pyscsi.scsi_command import SCSICommand

#
# SCSI ata-pass-through command and definitions
#

def lba_convert(lba):
    """
    This function converts the lba to the ATAPassThrough12->lba field.

    :param lba: lba(int) to convert
    :return: ATAPassThrough12->lba
    """
    result = 0
    result += ((lba & 0xFF) << 16)
    result += (((lba >> 8) & 0xFF) << 8)
    result += ((lba >> 16) & 0xFF)
    return result


class ATAPassThrough12(SCSICommand):
    """
    A class to send a ATAPassThrough12 command to a ata device
    """
    _cdb_bits = {'opcode': [0xff, 0],
                 'reserved1':[0x01,1],
                 'protocol':[0x1E,1],
                 'obsolete1':[0xE0,1],
                 't_length':[0x03,2],
                 'byte_block':[0x04,2],
                 't_dir':[0x08,2],
                 't_type':[0x10,2],
                 'ck_cond':[0x20,2],
                 'off_line':[0xC0,2],
                 'fetures':[0xff,3],
                 'count':[0xff,4],
                 'lba':[0xffffff,5],
                 'device':[0xff,8],
                 'command':[0xff,9],
                 'reserved10':[0xff,10],
                 'control':[0xff,11], }

    def __init__(self,
                 opcode,
                 protocal,
                 t_length,
                 byte_block,
                 t_dir,
                 t_type,
                 off_line,
                 fetures,
                 count,
                 lba,
                 command,
                 blocksize=0,
                 ck_cond=0,
                 device=0x00,
                 control=0,
                 data=None,
                 sense_data_len=32):
        """
        initialize a new instance

        :param opcode: a OpCode instance
        :param protocal: ATAPassthrough12 PROTOCOL field
        :param t_length: ATAPassthrough12 t_length field
        :param byte_block: ATAPassthrough12 byte_block field
        :param t_dir: ATAPassthrough12 t_dir field
        :param t_type: ATAPassthrough12 t_type field
        :param off_line: ATAPassThrough12 off_line field
        :param fetures: ATAPassThrough12 fetures field
        :param count: ATAPassThrough12 count field
        :param lba: ATAPassThrough12 lba field
        :param command: ATAPassThrough12 command field
        :param blocksize=None: a blocksize
        :param ck_cond=0: ATAPassThrough12 ck_cond field
        :param device=0: ATAPassThrough12 device field
        :param control=0: ATAPassThrough12 control field
        :param data=None: a byte array with data, if command need data-in data-out
        :param sense_data_len=32: a byte array with data, if need command sense
        """
        tl = 0
        if t_length == 1:
            # The transfer length is an unsigned integer specified in the FEATURES (7:0) field and, 
            # for the ATA PASS-THROUGH (16) command and the ATA PASS-THROUGH (32) command, the
            # FEATURES (15:8) field.
            tl = fetures
        elif t_length == 2:
            # The transfer length is an unsigned integer specified in the COUNT (7:0) field and, for 
            # the ATA PASS-THROUGH(16) command and the ATA PASS-THROUGH (32) command, the COUNT(15:8)
            # field.
            tl = count
        elif t_length == 3:
            # The transfer length is an unsigned integer specified in the TPSIU
            # TODO
            pass

        if byte_block and (not t_type) and t_length:
            # fix the blocksize to 512
            blocksize = 512
        elif byte_block and t_type and t_length:
            # The number of ATA logical sector size blocks to be transferred, set it in param blocksize
            if blocksize == 0:
                raise SCSICommand.MissingBlocksizeException
        elif (not byte_block) and t_length:
            blocksize = 1
        elif not t_length:
            ## No data to transfer
            blocksize = 0

        if t_dir == 0:
            # transfer data from the application client to the ATA device
            dataout_alloclen = tl * blocksize
            datain_alloclen = 0
        else:
            # transfer data from the ATA device to the application client
            dataout_alloclen = 0
            datain_alloclen = tl * blocksize

        SCSICommand.__init__(self,
                             opcode,
                             dataout_alloclen,
                             datain_alloclen)
        ## need get the sense data to decode ATA Return Descriptor
        if sense_data_len > 0:
            self.sense = bytearray(sense_data_len)
        # set data if need
        if data:
            self.dataout = data
        self.cdb = self.build_cdb(opcode=self.opcode.value,
                                  protocol=protocal,
                                  t_length=t_length,
                                  byte_block=byte_block,
                                  t_dir=t_dir,
                                  t_type=t_type,
                                  off_line=off_line,
                                  fetures=fetures,
                                  count=count,
                                  lba=lba_convert(lba),
                                  command=command,
                                  control=control,
                                  ck_cond=ck_cond,
                                  device=device)
