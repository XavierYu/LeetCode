import zlib
import re
import time
import os
import System
import array
from System import Array
from System import Byte
import datetime
from datetime import datetime
import opcode
import random

# from test.test_gzip import data1
# from test.badsyntax_future3 import result


# SPILittleEndian = 1
spiSeqNo = 1

spiMaxReplyPacketLength = {}
spiMaxReplyPacketLength['spiDefaultReplyPacket'] = 6 * 4 + (
4 + 4 + 8 + 11 + 255)  # HWR (4) + FWR (4) + SNO (8) + MFD (11) + LBL (255)
spiMaxReplyPacketLength['spiReplyPacketWithoutData'] = 5 * 4
spiMaxReplyPacketLength['4'] = 6 * 4 + 4
spiMaxReplyPacketLength['7'] = 6 * 4 + 4
spiMaxReplyPacketLength['8'] = 6 * 4 + 4
spiMaxReplyPacketLength['9'] = 6 * 4 + 8
spiMaxReplyPacketLength['10'] = 6 * 4 + 11
spiMaxReplyPacketLength['11'] = 6 * 4 + 255
spiMaxReplyPacketLength['13'] = 6 * 4 + 255
spiMaxReplyPacketLength['15'] = 6 * 4 + 4
spiMaxReplyPacketLength['16'] = 6 * 4 + 4
spiMaxReplyPacketLength['17'] = 6 * 4 + 4
spiMaxReplyPacketLength['19'] = 6 * 4 + 2
spiMaxReplyPacketLength['20'] = 6 * 4 + 2
spiMaxReplyPacketLength['22'] = 6 * 4 + (1 + (6 * 800))  # W (1byte) + {SPPA (6 bytes) * slice count}
spiMaxReplyPacketLength['26'] = 6 * 4 + 1
spiMaxReplyPacketLength['31'] = 6 * 4 + 1 + 10 * 2
spiMaxReplyPacketLength['SPIEMPTYPACKETLENGTH'] = 5 * 4


class regs:
    class HD:
        class OSSRegister:
            ReadyBit = 0
            HardwareErrorBit = 1
            HardwareErrorLatchedBit = 2
            ModuleRestartedLatchedBit = 3
            StartupActiveBit = 4
            OpticsNotReadyBit = 5
            OpticsDisabledBit = 6
            PendingBit = 7

    class DWP:
        class OSSRegister:
            ReadyBit = 0
            HardwareErrorBit = 1
            HardwareErrorLatchedBit = 2
            ModuleRestartedLatchedBit = 3
            OpticsNotReadyBit = 5
            LoadingCalibrationBit = 6
            StartupActiveBit = 7
            DataFailedBit = 8
            DataFailedLatchedBit = 9
            OpticsDisabledBit = 10

    class DWP_DPRAM:
        FirmwareVersionHigh = 0x7
        FirmwareVersionLow = 0x8
        CmdReg = 0x20
        CmdCodeReg = 0x21
        Data1Reg = 0x22
        Data2Reg = 0x34
        Data3Reg = 0x35
        Data4Reg = 0x36
        StatusReg = 0x23
        ErrorCodeReg = 0x25
        HardwareErrorReg = 0x29
        OverAllFileCRCHI = 0x57
        OverAllFileCRCLO = 0x58
        FirmwareTransferBufferSize = 0x0400
        FirmwareTransferBufferOffset = 0x0A00
        MM1_START = 0x0100
        MM1_END = 0x0FFF

    class Huawei_HDSP:
        class ErrorCodeRegisterHardResetRecoverableCurrent:
            InternalSoftwareErrorBit = 0
            InvalidCommandBit = 1
            ParameterErrorBit = 2
            DownloadSizeErrorBit = 3
            FirmwareDownloadErrorBit = 4
            FirmwareDownloadIncompleteBit = 5
            DownloadCheckSumErrorBit = 6
            SelfTestErrorBit = 7
            WatchdogErrorBit = 8

        class ErrorCodeRegisterHardResetRecoverableLatch:
            InternalSoftwareErrorBit = 0
            InvalidCommandBit = 1
            ParameterErrorBit = 2
            DownloadSizeErrorBit = 3
            FirmwareDownloadErrorBit = 4
            FirmwareDownloadIncompleteBit = 5
            DownloadCheckSumErrorBit = 6
            SelfTestErrorBit = 7
            WatchdogErrorBit = 8

        class ErrorCodeRegisterHardResetUnrecoverableCurrent:
            HardwareErrorBit = 0
            CommunicationErrorBit = 1
            ModuleNotReadyBit = 2
            ModuleShutdownBit = 3
            OpticsNotReadyBit = 4
            VCOMControlErrorBit = 5
            NVRAMErrorBit = 6
            ThermalErrorBit = 7
            CaseTemperatureHighBit = 8
            CaseTemperatureHighLow = 9
            InternalTemperatureHighBit = 10
            InternalTemperatureLowBit = 11
            PowerRailErrorBit = 12
            PowerSupplyErrorBit = 13
            CrystalErrorBit = 14
            FPGAErrorBit = 15
            MCUErrorBit = 16
            LCOSPowerErrorBit = 17
            InternalBusErrorBit = 18
            CalibrationDataErrorBit = 19

        class ErrorCodeRegisterHardResetUnrecoverableLatch:
            HardwareErrorBit = 0
            CommunicationErrorBit = 1
            ModuleNotReadyBit = 2
            ModuleShutdownBit = 3
            OpticsNotReadyBit = 4
            VCOMControlErrorBit = 5
            NVRAMErrorBit = 6
            ThermalErrorBit = 7
            CaseTemperatureHighBit = 8
            CaseTemperatureHighLow = 9
            InternalTemperatureHighBit = 10
            InternalTemperatureLowBit = 11
            PowerRailBit = 12
            PowerSupplyBit = 13
            CrystalErrorBit = 14
            FPGAErrorBit = 15
            MCUErrorBit = 16
            LCOSPowerErrorBit = 17
            InternalBusErrorBit = 18
            CalibrationDataErrorBit = 19


class SPICOMResult:
    spiComResultPEND = -1
    spiComResultOK = 0
    spiComResultCER = 1
    spiComResultAER = 2
    spiComResultVER = 3
    spiComResultNOCHK = 4


class ReplyReg:
    SPIMAGIC_VAL = 0x0F1E2D3C
    SPILENGTH = 0x04
    SPISEQNO = 0x08
    SPICOMRES = 0x0C
    SPICRC1 = 0x10
    SPIDATA = 0x14


class SPICmdOpCode:
    spiNOP = 0x00000001
    spiRES = 0x00000002
    spiSTR = 0x00000003
    spiSUS_Q = 0x00000004
    spiSFD = 0x00000005
    spiSLS = 0x00000006
    spiHWR_Q = 0x00000007
    spiFWR_Q = 0x00000008
    spiSNO_Q = 0x00000009
    spiMFD_Q = 0x0000000A
    spiLBL_Q = 0x0000000B
    spiMID = 0x0000000C
    spiMID_Q = 0x0000000D
    spiTEST = 0x0000000E
    spiOSS_Q = 0x0000000F
    spiHSS_Q = 0x00000010
    spiLSS_Q = 0x00000011
    spiCLE = 0x00000012
    spiCSS_Q = 0x00000013
    spiISS_Q = 0x00000014
    spiSPA = 0x00000015
    spiSPA_Q = 0x00000016
    spiFWT = 0x00000017
    spiFWS = 0x00000018
    spiFWL = 0x00000019
    spiFWP_Q = 0x0000001A
    spiFWE = 0x0000001B
    spiSSR = 0x0000001C
    spiMSR = 0x0000001D
    spiRSR = 0x0000001E
    spiGSR_Q = 0x0000001F


class DPRAMCmdCode:
    dpramNOP = 0x0001  # NOP
    # dpramRWS = 0x0002 #DPRAM only not included
    dpramUCA = 0x0002  # RWS
    dpramSLS = 0x0003  # Set Startup State - SLS
    dpramSFD = 0x0003  # Set Startup State - SFD
    dpramSAB = 0x0003  # Set Startup State - SAB
    dpramSTR = 0x0004  # STR
    dpramSTARTFWD = 0x0005  # ?
    dpramFWS = 0x0007  # FWS
    dpramFWL = 0x0008  # FWL
    dpramFWE = 0x0009  # FWE
    dpramTEST = 0x000A  # TEST
    dpramRES = 0x000B  # RES
    dpramChangeOneChannel = 0x000D  # not included
    dpramChangeOnePort = 0x000E  # not included
    dpramChangeOneAttn = 0x000F  # not included
    dpramBLOCKALL = 0x0010  # BlockAll
    dpramUPA = 0x0011  # not included
    dpramCHW = 0x0012  # CHW
    dpramCLE = 0x0013  # CLE
    dpramFWT = 0x0014  # FWT
    dpramDCC = 0x0020  # DCC
    dpramCMM = 0x0022  # DPRAM only
    dpramDCR = 0x0023  # not included
    dpramDCR_Q = 0x0024  # DCR?
    dpramCCC = 0x0025  # not included
    dpramDCS = 0x0026  # not included
    dpramDCS_Q = 0x0027  # DCS? included
    dpramNTZ = 0x0028  # NTZ


class NokiaCmdCode:
    # CMD SET: 10
    # NokiaSNO = 0x01 #SNO?
    NokiaHWR = 0x02  # HWR?
    NokiaFWR = 0x02  # FWR?
    # NokiaMFD_Q = 0x02 #MFD?
    NokiaUCA = 0x03  # UCA
    NokiaModifyChBW = 0x08  # Modify CH's BW
    # NokiaReadGranularity = 0x19 #Read Granularity
    NokiaDCC = 0x20  # DCC
    # NokiaDCC_Q = 0x21 #DCC?
    # NokiaOSS_Q = 0x22 #OSS?
    # NokiaReadInternalTemperatureHighLowLimits = 0x023 #Read Internal Temperature HighLowLimits
    # NokiaReadPowerSupplyVolatge = 0x026 #Read Power Supply voltage

    #   NokiaRES = 0x04 #RES
    NokiaStartFirmwareLoading = 0x0C  # FWL
    NokiaLoadNewFirmware = 0x0D  # FWT
    NokiaInsatllFirmware = 0x0E  # FWE

    Nokia0x01 = 0x01  # SNO?
    Nokia0x02 = 0x02  # HWR?#UCA#FWR?
    Nokia0x03 = 0x03  # UCA
    Nokia0x08 = 0x08  # Modify CH's BW
    Nokia0x13 = 0x13
    Nokia0x19 = 0x19  # Read Granularity
    Nokia0x20 = 0x20  # DCC
    Nokia0x21 = 0x21  # DCC?
    Nokia0x22 = 0x22  # OSS?
    Nokia0x23 = 0x23  # Read Internal Temperature HighLowLimits
    Nokia0x26 = 0x26  # Read Power Supply voltage


# def GetByte(data, order):
#    if SPILittleEndian == 1:
#        return (data >> (8 * order)) & 0xFF # for little endian
#    else:
#        return (data >> (8 * (3 - order))) & 0xFF # for big endian

def SetSeqNo(seqNoSet=1):
    global spiSeqNo
    spiSeqNo = seqNoSet


def GetSeqNo():
    global spiSeqNo
    if spiSeqNo > 0xFFFFFF10:
        SetSeqNo()
    else:
        spiSeqNo = spiSeqNo + 1
    return spiSeqNo


def SPI_ResetAndReady(WSSobj, TestInfo, opCode, data):
    libpath = os.path.dirname(os.path.abspath(__file__))
    txtTemplateFile = libpath + '\\..\\template\\Textfile\\texttpl_SPI.txt'
    txtPath = TestInfo.Variables['TxtPath']
    txtName = TestInfo.Variables['TCName'] + '_OpCode' + str(hex(opCode)) + '_' + str(datetime.now().hour) + '_' + str(
        datetime.now().minute) + '_' + str(datetime.now().second) + '.txt'
    if not os.path.exists(txtPath):
        os.makedirs(txtPath)
    txtRun = open(txtPath + '\\' + txtName, 'w')
    with open(txtTemplateFile) as openfileobject:
        for line in openfileobject:
            if line.find('key_TestData') >= 0:
                txtRun.write(SPI_PrepareResetAndReady(TestInfo=TestInfo, opCode=opCode, data=data))
            else:
                txtRun.write(line)

    openfileobject.close()
    txtRun.close()
    return SendRunTestFile(WSSobj=WSSobj, TestInfo=TestInfo, fileToTransfer=txtPath + '\\' + txtName, waitExeTimeInS=20)


def SPI_PrepareResetAndReady(TestInfo, opCode, data, seqNoIn=None):
    global spiSeqNo
    if seqNoIn == None:
        sequenceNum = GetSeqNo()
    else:
        sequenceNum = seqNoIn
    sendMsg = AssembleAndSendPacket(opCode, sequenceNum, TestInfo, data)
    resultMsg = '#-------' + sendMsg + '\n'
    resultMsg += sendMsg + '\n'

    result, pollMsg = SPIPoll(opCode=opCode, sequenceNumber=sequenceNum, expectedRet='OK', sendCmd=False,
                              TestInfo=TestInfo)
    if result == False:
        raise Exception('Error - Reset Poll Error.')
    resultMsg += '#----------' + pollMsg.replace('\n', '\n#----------', 1)
    resultMsg += pollMsg
    resultMsg += '#------G<WGPIO RD 0 200000 1\n'
    resultMsg += 'G<WGPIO RD 0 200000 1\n'
    resultMsg += '#------G<WGPIO PS 1 200000 1\n'
    resultMsg += 'G<WGPIO PS 1 200000 1\n'
    resultMsg += '#------G<WGPIO RD 1 200000 1\n'
    resultMsg += 'G<WGPIO RD 1 200000 1\n'
    resultMsg += '#------P<WBSI 0xF 0xC xxxxxxxxxxx0xxxx 0x1C 10000 200000 0x14 xxxxxxxxxxxxxxx1\n'
    resultMsg += 'P<WBSI 0xF 0xC xxxxxxxxxxx0xxxx 0x1C 10000 200000 0x14 xxxxxxxxxxxxxxx1\n'
    return resultMsg


def SPI_GenerateCmd(WSSobj, Cmd, TestInfo, expectRet=None, seqNoIn=None):
    Cmd = Cmd.strip(' ')
    if Cmd.find(' ') >= 0:
        opIndex = Cmd.index(' ')
    else:
        opIndex = len(Cmd)

    opCodeStr = 'spi' + Cmd[:opIndex].upper()
    opCodeStr = opCodeStr.replace('?', '_Q')
    try:
        opCode = getattr(SPICmdOpCode, opCodeStr)
    except:
        opCode = 0x0000002F
    data = Cmd[opIndex:].strip(' ')

    if opCode == SPICmdOpCode.spiSPA:
        data = Internal_Generate_SPISPADataBlock(strSPA=data, TestInfo=TestInfo)

    elif opCode == SPICmdOpCode.spiSSR:
        data = Internal_Generate_SPISSRDataBlock(strSSR=data, TestInfo=TestInfo)

    elif opCode == SPICmdOpCode.spiMSR:
        data = Internal_Generate_SPIMSRDataBlock(strMSR=data, TestInfo=TestInfo)

    elif opCode == SPICmdOpCode.spiGSR_Q:
        data = Internal_Generate_SPIGSRRSRDataBlock(strGSR=data, TestInfo=TestInfo)

    elif opCode == SPICmdOpCode.spiRSR:
        data = Internal_Generate_SPIGSRRSRDataBlock(strGSR=data, TestInfo=TestInfo)
    elif data != '':
        strType = False
        fwt = False
        if opCode == SPICmdOpCode.spiMID:
            strType = True
        elif opCode == SPICmdOpCode.spiFWT:
            fwt = True
        data = SPIDataToByte(strSPIData=data, strType=strType, fwt=fwt)

    if (Cmd == 'FWE' or Cmd == 'RES') and (expectRet is None or expectRet == 'OK' or expectRet == 'Ready'):
        # libpath = os.path.dirname(os.path.abspath(__file__))
        # txtTemplateFile = libpath + '\\..\\template\\Textfile\\texttpl.txt'
        return SPI_ResetAndReady(WSSobj=WSSobj, TestInfo=TestInfo, opCode=opCode, data=data)

    global spiSeqNo
    if seqNoIn == None:
        sequenceNum = GetSeqNo()
    else:
        sequenceNum = seqNoIn

    spiCmd = AssembleAndSendPacket(opCode, sequenceNum, TestInfo, data)

    # print spiCmd
    spiRet = WSSobj.SerialQuery(spiCmd)
    print spiRet

    while (spiRet.find('Server closed connection') >= 0 or spiRet.find('Segmentation fault') >= 0):
        print 'resend command...'
        time.sleep(0.2)
        spiRet = WSSobj.SerialQuery(spiCmd)
        print spiRet

    # TestInfo.ResultMessage += spiRet
    if spiRet.find('ms S') == -1:
        result = False
        msg = 'ERROR - SPI command ' + str(hex(opCode)) + ' failed'
        print msg
        TestInfo.ResultMessage += msg
        return result

    if expectRet is None or expectRet == '':
        expectRet = 'OK'

    result, pollMsg = SPIPoll(WSSobj, opCode, sequenceNum, expectRet, True, TestInfo)

    if opCode in [SPICmdOpCode.spiSPA, SPICmdOpCode.spiSSR, SPICmdOpCode.spiMSR] and expectRet == 'OK':
        resultPend = SPIWaitForOSSReady(WSSobj=WSSobj, TestInfo=TestInfo)
        result = result and resultPend

    spiRDRet = WSSobj.SerialQuery('G<RD 1')
    print spiRDRet

    while (spiRDRet.find('Server closed connection') >= 0 or spiRDRet.find('Segmentation fault') >= 0):
        print 'resend command...'
        time.sleep(0.2)
        spiRDRet = WSSobj.SerialQuery('G<RD 1')
        print spiRDRet

    if spiRDRet.find('ms S') == -1:
        result = False
        msg = 'ERROR - Verify Ready Line High Failed'
        print msg
        TestInfo.ResultMessage += msg

    spiALRet = WSSobj.SerialQuery('G<AL 1')
    print spiALRet

    while (spiALRet.find('Server closed connection') >= 0 or spiALRet.find('Segmentation fault') >= 0):
        print 'resend command...'
        time.sleep(0.2)
        spiALRet = WSSobj.SerialQuery('G<AL 1')
        print spiALRet

    if spiALRet.find('ms S') == -1:
        result = False
        msg = 'ERROR - Verify Alarm Line High Failed'
        print msg
        TestInfo.ResultMessage += msg

    return result


def AssembleAndSendPacket(opCode, sequenceNum, TestInfo, data):
    packet_bytes = AssemblePacket(opCode, sequenceNum, TestInfo, data)
    result = SendPacket(packet_bytes)
    return result


def AssemblePacket(opCode, sequenceNum, TestInfo, data):
    """
    Create a SPI packet and return it as a list of bytes

    Arguments:
        opCode - SPI Command Code

    Optional arguments:
        data - a 32-bit word or a list of bytes
        length - length of data

    Returns:
        list of bytes

    """
    # seqWord = seqNo & 0xFFFFFFFF
    packet_bytes = []

    if data == '':
        """
        There is no data in SPI Request. Packet structure is as follows:
        Magic (32-bit) + Length (32-bit) + SeqNo (32-bit) + OpCode (32-bit) + CRC1 (32-bit)

        Length will be 20
        There will be no DATA and CRC2 fields
        """
        length = 5 * 4
        word_list = [ReplyReg.SPIMAGIC_VAL, length, sequenceNum, opCode]
        crc1 = SPICrc(WordsToBytes(wordsList=word_list, littleEndian=TestInfo.Variables['SPILittleEndian']))

        word_list.append(crc1)
        packet_bytes = WordsToBytes(wordsList=word_list, littleEndian=TestInfo.Variables['SPILittleEndian'])

    elif (type(data) == type([])) and len(data) < 9000:
        """
        Packet structure, with DATA, is as follows:
        Magic (32-bit) + Length (32-bit) + SeqNo (32-bit) + OpCode (32-bit) + CRC1 (32-bit) + DATA[] + CRC2 (32-bit)

        Length will be 24 + len(DATA)
        """
        # data is an array of 8bit bytes - max length spiSPA
        # safeguard against payload size, max payload is spiSPA - 6001 bytes (assuming max slice can be 1000)
        length = 6 * 4 + len(data)
        word_list = [ReplyReg.SPIMAGIC_VAL, length, sequenceNum, opCode]
        crc1 = SPICrc(WordsToBytes(wordsList=word_list, littleEndian=TestInfo.Variables['SPILittleEndian']))

        word_list.append(crc1)
        packet_bytes = WordsToBytes(wordsList=word_list, littleEndian=TestInfo.Variables['SPILittleEndian'])

        # word_list.extend(data)
        packet_bytes.extend(data)

        crc2 = SPICrc(packet_bytes)

        # word_list.append(crc2)
        packet_bytes.extend(WordsToBytes(wordsList=[crc2], littleEndian=TestInfo.Variables['SPILittleEndian']))
        # packet_bytes.extend(WordsToBytes(wordsList = word_list, littleEndian = TestInfo.Variables['SPILittleEndian']))

    elif (type(data) == type([])) and len(data) > 9000:
        # For firmware download use buffer inside Test Driver memory
        msg = 'Unsupported packet type - For firmware download, assemble packet inside Test Driver memory using T>WBFR and T>COPYF2X commands. Data length = %s' % (
        len(data))
        raise RuntimeError(msg)

    else:
        msg = 'Unsupported data type - Data = %s, Data must be an array of bytes' % (data)
        raise RuntimeError(msg)

    return packet_bytes


def SendPacket(packet_bytes):
    packet_string = BytesListToString(packet_bytes)
    packet_length = len(packet_bytes)

    result = SendBinaryData(packet_string, downloadViaSPI=True)
    return result


def SPICrc(word_list):
    packet_string = BytesListToBinaryString(word_list)
    return calculateCRC(packet_string)


def calculateCRC(s1):
    crc = zlib.crc32(s1)
    return crc


def calculateFileCRC(fileName):
    f = open(fileName, 'rb')
    s = f.read()
    crc = zlib.crc32(s)
    f.close()
    return crc


def Internal_GetFileLength(filePath):
    length = 0;
    try:
        fileObject = open(filePath, 'rb')
        allData = fileObject.read()
        length = len(allData)
    finally:
        fileObject.close()
    return length


def WordsToBytes(wordsList, wordLengthInBits=32, littleEndian=1, bitSwap=False):
    """
    It converts 32-bit words to bytes

    Arguments:
        wordsList - words list

    Optional arguments:
        littleEndian - LSB first in a 32bit or 16bit word e.g. 1 => 0x01000000, if not provided then SPILittleEndian parameter from INI file will be used
        bitSwap - bits with a byte will be swapped

    Returns:
        list of bytes
    """
    result = []
    for aWord in wordsList:
        b1 = aWord & 0x000000FF
        b2 = ((aWord & 0x0000FF00) >> 8) & 0xFF
        b3 = ((aWord & 0x00FF0000) >> 16) & 0xFF
        b4 = ((aWord & 0xFF000000) >> 24) & 0xFF

        bytes_in_orginal_order = [b1, b2, b3, b4]
        if wordLengthInBits == 16:
            bytes_in_orginal_order = [b1, b2]
        elif wordLengthInBits == 8:
            bytes_in_orginal_order = [b1]

        if not littleEndian:
            i = len(bytes_in_orginal_order) - 1
        else:
            i = 0
        while True:
            b = bytes_in_orginal_order[i]
            if bitSwap:
                b = SwapBits8b(b)
            result.append(b)
            if not littleEndian:
                i -= 1
                if i < 0:
                    break
            else:
                i += 1
                if i >= len(bytes_in_orginal_order):
                    break
    return result


def BytesListToBinaryString(bytesList):
    """
    It converts a bytes list to a string, each byte is converted to a character
    e.g. input => [65,66,67,32,67]      output => 'ABC C'

    Arguments:
        bytesList

    Returns:
        string
    """
    result = []
    for aByte in bytesList:
        result.append(chr(aByte))
    return ''.join(result)


def BytesListToString(bytesList):
    """
    It converts a bytes list to a string of numbers in hex format
    e.g. input => [65,66,67,32,67]      output => '0x41 0x42 0x43 0x20 0x43'

    Arguments:
        bytesList

    Returns:
        string
    """
    result = ''
    for aByte in bytesList:
        result += '0x%X ' % aByte
    result = result[:-1]
    return result


def SendBinaryData(dataString, downloadViaSPI=False):
    """
    Send binary data to UUT via serial or SPI interface

    Arguments:
        dataString - data values in hex or decimal format e.g. '0x0A 15 255 13 10'

    Optional Arguments:
        downloadViaSPI - if true send data on SPI, default via serial

    """
    cmd = 'T>SEND 1 '
    if downloadViaSPI:
        cmd = 'T>SEND 2 '
    req = cmd + dataString
    return req


def SPIPoll(WSSobj=None, opCode=None, sequenceNumber=None, expectedRet='OK', sendCmd=True, TestInfo=None):
    """
    Get WSS SPI Reply Packet and store it in Test Driver memory
    Test Driver sends all zeros to get contents of WSS SPI Reply Packet

    It will generate P>POLL low level protocol, which takes followind parameters:
    P>POLL <length> [<sequenceNumber> <interNOPTimeInMS> <timeOutInMS> <offset> <bitstring>]

    Optional Arguments:
        opCode - if provided it will be used to determine the Reply Packet length, otherwise default packet length will be used
        Sequence number - if provided, Test Driver will keep requesting SPIFile by sending spiNOPs
                            untill a packet with matching sequence number is received, or timeout occur
        length - how much data to request (in bytes)
        waitForCommandToFinish - should we wait for command to finish i.e. observe SPICOMRES field and wait for it to become non -1
        expectedRet - result code to be matched in SPICOMRES field
    """
    if sendCmd and WSSobj is None:
        raise Exception('Error - SPIPoll send Cmd is true and WSSobj is None')
    print 'expectedRet: ' + str(expectedRet)
    # global spiMaxReplyPacketLength, ReplyReg, SPICOMResult
    # if we are expecting an error e.g. AER, then we need to only POLL for an empty packet, because DATA and CRC2 will be void
    result = True
    if expectedRet == 'OK':
        expectedRet = SPICOMResult.spiComResultOK
    elif expectedRet == 'AER':
        expectedRet = SPICOMResult.spiComResultAER
    elif expectedRet == 'CER':
        expectedRet = SPICOMResult.spiComResultCER
    elif expectedRet == 'VER':
        expectedRet = SPICOMResult.spiComResultAER
    elif expectedRet == 'NOCHK':
        expectedRet = SPICOMResult.spiComResultCER
    elif expectedRet == 'PENDING':
        expectedRet = SPICOMResult.spiComResultPEND
    else:
        result = False
        return result, 'Error - result code ' + str(expectedRet) + ' not supported!'

    if (expectedRet is not None) and (not (
                expectedRet is SPICOMResult.spiComResultOK or expectedRet is SPICOMResult.spiComResultPEND or expectedRet is SPICOMResult.spiComResultNOCHK)):
        length = spiMaxReplyPacketLength['SPIEMPTYPACKETLENGTH']
    else:
        length = GetSPIReplyPacketSize(opCode)

    spiPollStr = 'P'
    spiPollStr += '>POLL 0x%X' % (length)

    if sequenceNumber is not None:
        spiPollStr += ' 0x%X %d %d' % (sequenceNumber, 10, 200000)  # SPIPollingTimeInMS = 10, timeout = 200000

    """
    Wait for result code to become anything other than -1.

    Bit 4 in SPICOMRE register is unused, it should be zero for all other cases
    except 'command is being executed' which is -1 (0xFFFFFFFF)
    """
    regMask = 1 << 4
    symBitsDict = GenerateStatusBits()
    finalStr = SPICombineMaskWithBits(regMask, symBitsDict)
    spiPollStr += ' 0x%X %s' % (ReplyReg.SPICOMRES, finalStr)

    spiPollStr += '\n'
    if not sendCmd:
        if (expectedRet is not None) and (expectedRet is not SPICOMResult.spiComResultNOCHK):
            spiPollStr += VerifySPICOMResult(expectedRet=expectedRet)
        return result, spiPollStr

    spiPollRetStr = WSSobj.SerialQuery(spiPollStr)
    while (spiPollRetStr == ''):
        spiPollRetStr = WSSobj.SerialRead()
    msg = spiPollRetStr
    print spiPollRetStr

    while (spiPollRetStr.find('Server closed connection') >= 0 or spiPollRetStr.find('Segmentation fault') >= 0):
        print 'resend command...'
        time.sleep(0.2)
        spiPollRetStr = WSSobj.SerialQuery(spiPollStr)
        msg = spiPollRetStr
        print spiPollRetStr

    pollcount = 3
    while spiPollRetStr.find('ms S') == -1 and spiPollRetStr.find('ms F') == -1 and pollcount > 0:
        time.sleep(10)
        spiPollRetStr = WSSobj.SerialQuery(spiPollStr)
        print spiPollRetStr
        pollcount -= 1
    if spiPollRetStr.find('ms S') == -1:
        result = False
        errormsg = 'ERROR - SPI command Poll failed'
        print errormsg
        msg += errormsg
        TestInfo.ResultMessage += errormsg

    if (expectedRet is not None) and (expectedRet is not SPICOMResult.spiComResultNOCHK):
        time.sleep(3)
        spiVmStr = VerifySPICOMResult(expectedRet=expectedRet)
        spiVmRetStr = WSSobj.SerialQuery(spiVmStr)
        msg += spiVmRetStr
        print spiVmRetStr
        while (spiVmRetStr.find('Server closed connection') >= 0 or spiVmRetStr.find('Segmentation fault') >= 0):
            print 'resend command...'
            time.sleep(0.2)
            spiVmRetStr = WSSobj.SerialQuery(spiVmStr)
            msg += spiVmRetStr
            print spiVmRetStr

        if spiVmRetStr.find('ms S') == -1:
            result = False
            errormsg = 'ERROR - SPI Verify Memory Error'
            print errormsg
            msg += errormsg
            TestInfo.ResultMessage += errormsg

    return result, msg


def SPICombineMaskWithBits(mask, bitValues, wordLengthInBits=16):
    return CombineMaskWithBits(mask=mask, bitValues=bitValues, wordLengthInBits=wordLengthInBits)


def CombineMaskWithBits(mask, bitValues, wordLengthInBits=16):
    """
    Combines the bit mask with the actual bit values required

    Arguments:

    mask - a 16/32 bit mask e.g. 0x03CF
    bitValues - a dictionary with bit position and a value of 0 or 1 for that bit position, bit position range from 0-15 or 0-31

    Returns:

    a 16/32 character string with 0, 1 or x e.g. 'xxxxxx11x0001101'
    """
    result = ''
    print '2'
    if mask > (0xFFFF):
        wordLengthInBits = 32
    print '3'
    for i in range(0, wordLengthInBits):
        if not (mask & (1 << i)):
            result = 'x' + result
        else:
            try:
                if bitValues[i] == 99:  # IGNORE_BIT
                    result = 'x' + result
                elif bitValues[i] == 1:
                    result = '1' + result
                elif bitValues[i] == 0:
                    result = '0' + result
                else:
                    raise SyntaxError('Unknown bit value - %d for bitPos - %d' % (bitValues[i], i))
            except KeyError:
                result = '0' + result
    return result


def GenerateStatusBits(allOnes=False, wordLengthInBits=16):
    """
    Generate all zero or ones values for all 16/32 bits

    Returns:

    a dictionary with bit position and a value of 0 or 1 for all bit position, bit position range from 0-15 or 0-31
    """
    val = 0
    if allOnes:
        val = 1
    result = {}
    for i in range(0, wordLengthInBits):
        result[i] = val
    return result


def VerifySPICOMResult(expectedRet=SPICOMResult.spiComResultOK):
    """
    Verify that contents at offset SPICOMRES in SPIFile
    """
    if type(expectedRet) != type(1):
        raise RuntimeError('expectedRet must of type int or SPICOMResult for SPI, actual = %s' % (expectedRet))

    result = VerifyMemory(ReplyReg.SPICOMRES, [expectedRet])
    return result


def GetSPIReplyPacketSize(opCode=None):
    # global spiMaxReplyPacketLength
    if str(opCode) in spiMaxReplyPacketLength:
        return spiMaxReplyPacketLength[str(opCode)]
    else:
        return spiMaxReplyPacketLength['spiReplyPacketWithoutData']


def VerifyMemory(offset, wordsList, wordLengthInBytes=4):
    result = 'P'
    result += '<VM 0x%X %d ' % (offset, wordLengthInBytes)
    for i in range(0, len(wordsList)):
        if wordLengthInBytes == 4:
            result += '0x%08X ' % (wordsList[i])
        elif wordLengthInBytes == 2:
            result += '0x%04X ' % (wordsList[i])
        else:
            result += '0x%02X ' % (wordsList[i])
    result = result[:-1]
    result += '\n'
    return result


def Internal_Generate_SPISPADataBlock(strSPA, TestInfo):
    """
    This function returns a byte array filled with SPA data, the format of array is as follows (as per SIS):
    <W> <S><S><P><P><A> <S><S><P><P><A>...

    <W> - 8bit  signed
    <S> - 16bit unsigned
    <P> - 8bit  unsigned
    <A> - 16bit signed
    """
    spaObj = ParseSPAString(strSPA)

    finalSPABlock = [int(spaObj['wss']) & 0xFF]  # <W> - 8bit  signed

    for innerT in spaObj['spa']:
        if innerT['EndSlice']:
            finalSPABlock.extend(WordsToBytes(wordsList=[innerT['StartSlice'] & 0xFFFF], wordLengthInBits=16,
                                              littleEndian=TestInfo.Variables[
                                                  'SPILittleEndian']))  # <S> - 16bit unsigned
            finalSPABlock.extend(WordsToBytes(wordsList=[innerT['EndSlice'] & 0xFFFF], wordLengthInBits=16,
                                              littleEndian=TestInfo.Variables[
                                                  'SPILittleEndian']))  # <S> - 16bit unsigned
            finalSPABlock.append(int(innerT['CPort']) & 0xFF)  # <P> - 8bit  unsigned
            finalSPABlock.append(int(innerT['IOPort']) & 0xFF)  # <P> - 8bit  unsigned
            finalSPABlock.extend(WordsToBytes(wordsList=[int(innerT['Atten']) & 0xFFFF], wordLengthInBits=16,
                                              littleEndian=TestInfo.Variables['SPILittleEndian']))  # <A> - 16bit signed
        else:
            finalSPABlock.extend(WordsToBytes(wordsList=[innerT['StartSlice'] & 0xFFFF], wordLengthInBits=16,
                                              littleEndian=TestInfo.Variables[
                                                  'SPILittleEndian']))  # <S> - 16bit unsigned
            finalSPABlock.append(int(innerT['CPort']) & 0xFF)  # <P> - 8bit  unsigned
            finalSPABlock.append(int(innerT['IOPort']) & 0xFF)  # <P> - 8bit  unsigned
            finalSPABlock.extend(WordsToBytes(wordsList=[int(innerT['Atten']) & 0xFFFF], wordLengthInBits=16,
                                              littleEndian=TestInfo.Variables['SPILittleEndian']))  # <A> - 16bit signed
    return finalSPABlock


def Internal_Generate_SPISSRDataBlock(strSSR, TestInfo):
    """
    This function returns a byte array filled with SSR data, the format of array is as follows (as per SIS):
    <W> <I><S><S><P><P><A> <I><S><S><P><P><A>...

    <W> - 8bit  unsigned

    <I> - 16bit unsigned
    <S> - 16bit unsigned
    <S> - 16bit unsigned
    <P> - 8bit  unsigned
    <P> - 8bit  unsigned
    <A> - 16bit signed
    """

    ssrObj = ParseSSRString(strSSR)

    memBlock = [int(ssrObj['wss']) & 0xFF]  # <W> - 8bit  signed

    for aRecord in ssrObj['ssr']:
        memBlock.extend(
            WordsToBytes(wordsList=[aRecord['Channel'] & 0xFFFF], wordLengthInBits=16))  # <S> - 16bit unsigned
        memBlock.extend(
            WordsToBytes(wordsList=[aRecord['StartSlice'] & 0xFFFF], wordLengthInBits=16))  # <S> - 16bit unsigned
        memBlock.extend(
            WordsToBytes(wordsList=[aRecord['EndSlice'] & 0xFFFF], wordLengthInBits=16))  # <S> - 16bit unsigned
        memBlock.append(int(aRecord['CommonPort']) & 0xFF)  # <P> - 8bit  unsigned
        memBlock.append(int(aRecord['IOPort']) & 0xFF)  # <P> - 8bit  unsigned
        memBlock.extend(
            WordsToBytes(wordsList=[int(aRecord['Attenuation']) & 0xFFFF], wordLengthInBits=16))  # <A> - 16bit signed

    return memBlock


def Internal_Generate_SPIMSRDataBlock(strMSR, TestInfo):
    """
    This function returns a byte array filled with MSR data, the format of array is as follows (as per SIS):
    <W> <I><V><S><S><P><P><A> <I><V><S><S><P><P><A>...

    <W> - 8bit  unsigned

    <I> - 16bit unsigned
    <V> - 8bit  unsigned
    <S> - 16bit unsigned
    <S> - 16bit unsigned
    <P> - 8bit  unsigned
    <P> - 8bit  unsigned
    <A> - 16bit signed
    """
    msrObj = ParseMSRString(strMSR)

    memBlock = [int(msrObj['wss']) & 0xFF]  # <W> - 8bit  signed

    for aRecord in msrObj['msr']:
        memBlock.extend(
            WordsToBytes(wordsList=[aRecord['Channel'] & 0xFFFF], wordLengthInBits=16))  # <S> - 16bit unsigned
        memBlock.append(int(aRecord['ValidMode']) & 0xFF)  # <V> - 8bit  unsigned
        memBlock.extend(
            WordsToBytes(wordsList=[aRecord['StartSlice'] & 0xFFFF], wordLengthInBits=16))  # <S> - 16bit unsigned
        memBlock.extend(
            WordsToBytes(wordsList=[aRecord['EndSlice'] & 0xFFFF], wordLengthInBits=16))  # <S> - 16bit unsigned
        memBlock.append(int(aRecord['CommonPort']) & 0xFF)  # <P> - 8bit  unsigned
        memBlock.append(int(aRecord['IOPort']) & 0xFF)  # <P> - 8bit  unsigned
        memBlock.extend(
            WordsToBytes(wordsList=[int(aRecord['Attenuation']) & 0xFFFF], wordLengthInBits=16))  # <A> - 16bit signed
    return memBlock


def Internal_Generate_SPIGSRRSRDataBlock(strGSR, TestInfo):
    """
    This function returns a byte array filled with GSR/RSR data, the format of array is as follows (as per SIS):
    <W> <I> <I>...

    <W> - 8bit  unsigned

    <I> - 16bit unsigned
    """

    if not strGSR:
        raise Exception('Error : Wrong format, strGSR can not be empty or None - %s')
    # change multiple white spaces to single white spaces
    tempStr = ' '.join(strGSR.strip().split())
    elements = tempStr.split()
    if len(elements) < 2:
        raise Exception(
            'Error : Wrong format, there should be min 2 components in input str separated be space - %s' % (strGSR))
    wss = elements.pop(0)
    memBlock = [int(wss) & 0xFF]  # <W> - 8bit  signed
    # loop over the rest
    innerList = []
    for anElement in elements:
        # each inner part has the following format - 'identifier'
        # verify identifier
        try:
            identifier = evaluateStr(anElement)
            identifier = int(identifier)
            memBlock.extend(WordsToBytes(wordsList=[identifier & 0xFFFF], wordLengthInBits=16))  # <S> - 16bit unsigned
        except:
            raise Exception(
                'Error : Wrong identifier format (note that identifier should be int) - %s in %s inputMSR str = %s' % (
                identifier, anElement, strMSR))
    return memBlock


def SPIDataToByte(strSPIData, strType=True, fwt=False):
    bytesList = []
    if strType:
        for aCh in strSPIData:
            bytesList.append(ord(aCh))
    elif fwt:
        try:
            seperateIndex = strSPIData.find(',')
            bytesListFromFile = []
            for ch in strSPIData[seperateIndex + 1:]:
                bytesListFromFile.append(ord(ch))
            bytesList = self.utils.WordsToBytes(wordsList=[strSPIData[:seperateIndex]], wordLengthInBits=32)
            bytesList.extend(bytesListFromFile)
        except:
            for aCh in strSPIData:
                bytesList.append(ord(aCh))
    else:
        try:
            bytesList.append(int(strSPIData) & 0xFF)
        except:
            for aCh in strSPIData:
                bytesList.append(ord(aCh))
    return bytesList


def ParseSPAString(strSPA):
    wss = None
    startSlice = 0
    endSlice = None
    atten = 0.0
    CPort = ''
    IOPort = ''

    if not strSPA:
        raise Exception('Error : Wrong format, strSPA can not be empty or None - %s')

    # change multiple white spaces to single white spaces
    tempStr = ' '.join(strSPA.strip().split())
    elements = tempStr.split()

    if len(elements) < 2:
        raise Exception(
            'Error : Wrong format, there should be min 2 components in input str separated be space - %s' % (strSPA))
    wss = elements.pop(0)

    # loop over the rest
    innerList = []
    for anElement in elements:
        # each inner part has the following format - 'slice,port1:port2,atten' or 'slice1:slice2,port1:port2,atten'
        innerElements = anElement.split(',')

        # count should be 3 elements
        if len(innerElements) != 3:
            raise Exception(
                'Error : Wrong format, there should be 3 components separated be comma - %s, inputSPA str = %s' % (
                innerElements, strSPA))

        slices = innerElements[0]
        ports = innerElements[1]
        atten = innerElements[2]

        # verify slices format - \d+:\d+
        sliceParts = slices.split(':')
        if len(sliceParts) == 2:
            # case 2 - slice range - slice1:slice2
            startSlice, endSlice = sliceParts[0], sliceParts[1]
            startSlice = evaluateStr(startSlice)
            endSlice = evaluateStr(endSlice)
        else:
            raise Exception(
                'Error : Wrong slice format (note that slices should be int) - %s in %s inputSPA str = %s' % (
                slices, anElement, strSPA))

        # verify port format - \w+:\w+
        pat2 = r'(-?\w+):(-?\w+)'
        match = re.search(pat2, ports)
        if match:
            CPort, IOPort = str(match.groups()[0].strip()), str(match.groups()[1].strip())
        else:
            raise Exception('Error : Wrong port format (note that ports are str) - %s in %s inputSPA str = %s' % (
            ports, anElement, strSPA))

        # verify atten format - an int
        try:
            atten = evaluateStr(atten)
            atten = int(atten)
        except ValueError:
            raise Exception('Wrong format, atten should be an int or a float - %s' % (atten))

        innerList.append(
            {'StartSlice': startSlice, 'EndSlice': endSlice, 'CPort': CPort, 'IOPort': IOPort, 'Atten': atten})

    SPAResult = {
        'wss': wss,
        'spa': innerList
    }
    return SPAResult


def ParseSSRString(strSSR):
    wss = None
    startSlice = 0
    endSlice = None
    atten = 0.0
    CPort = ''
    IOPort = ''
    identifier = 0

    if not strSSR:
        raise Exception('Error : Wrong format, strSSR can not be empty or None - %s')

    # change multiple white spaces to single white spaces
    tempStr = ' '.join(strSSR.strip().split())
    elements = tempStr.split()

    if len(elements) < 2:
        raise Exception(
            'Error : Wrong format, there should be min 2 components in input str separated be space - %s' % (strSSR))
    wss = elements.pop(0)

    # loop over the rest
    innerList = []
    for anElement in elements:
        # each inner part has the following format - 'identifier,startslice:endslice,port1:port2,atten'
        innerElements = anElement.split(',')

        # count should be 4 elements
        if len(innerElements) != 4:
            raise Exception(
                'Error : Wrong format, there should be 4 components separated be comma - %s, inputSSR str = %s' % (
                innerElements, strSSR))

        identifier = innerElements[0]
        slices = innerElements[1]
        ports = innerElements[2]
        atten = innerElements[3]

        # verify identifier
        try:
            identifier = evaluateStr(identifier)
            identifier = int(identifier)
        except:
            raise Exception(
                'Error : Wrong identifier format (note that identifier should be int) - %s in %s inputSSR str = %s' % (
                identifier, anElement, strSSR))

        # verify slices format - \d+:\d+
        sliceParts = slices.split(':')
        if len(sliceParts) == 2:
            # case 2 - slice range - slice1:slice2
            startSlice, endSlice = sliceParts[0], sliceParts[1]
            startSlice = evaluateStr(startSlice)
            endSlice = evaluateStr(endSlice)
        else:
            raise Exception(
                'Error : Wrong slice format (note that slices should be int) - %s in %s inputSSR str = %s' % (
                slices, anElement, strSSR))

        # verify port format - \w+:\w+
        pat2 = r'(-?\w+):(-?\w+)'
        match = re.search(pat2, ports)
        if match:
            CPort, IOPort = str(match.groups()[0].strip()), str(match.groups()[1].strip())
        else:
            raise Exception('Error : Wrong port format (note that ports are str) - %s in %s inputSSR str = %s' % (
            ports, anElement, strSSR))

        # verify atten format - an int
        try:
            atten = evaluateStr(atten)
            atten = int(atten)
        except ValueError:
            raise Exception('Wrong format, atten should be an int or a float - %s' % (atten))

        innerList.append({'Channel': identifier, 'StartSlice': startSlice, 'EndSlice': endSlice, 'CommonPort': CPort,
                          'IOPort': IOPort, 'Attenuation': atten})

    SSRResult = {
        'wss': wss,
        'ssr': innerList
    }
    return SSRResult


def ParseMSRString(strMSR):
    wss = None
    startSlice = 0
    endSlice = None
    atten = 0.0
    CPort = ''
    IOPort = ''
    identifier = 0
    validMode = 0

    if not strMSR:
        raise Exception('Error : Wrong format, strMSR can not be empty or None - %s')

    # change multiple white spaces to single white spaces
    tempStr = ' '.join(strMSR.strip().split())
    elements = tempStr.split()

    if len(elements) < 2:
        raise Exception(
            'Error : Wrong format, there should be min 2 components in input str separated be space - %s' % (strMSR))
    wss = elements.pop(0)

    # loop over the rest
    innerList = []
    for anElement in elements:
        # each inner part has the following format - 'identifier,validmode,startslice:endslice,port1:port2,atten'
        innerElements = anElement.split(',')

        # count should be 5 elements
        if len(innerElements) != 5:
            raise Exception(
                'Error : Wrong format, there should be 4 components separated be comma - %s, inputMSR str = %s' % (
                innerElements, strMSR))

        identifier = innerElements[0]
        validMode = innerElements[1]
        slices = innerElements[2]
        ports = innerElements[3]
        atten = innerElements[4]

        # verify identifier
        try:
            identifier = evaluateStr(identifier)
            identifier = int(identifier)
        except:
            raise Exception(
                'Error : Wrong identifier format (note that identifier should be int) - %s in %s inputMSR str = %s' % (
                identifier, anElement, strMSR))

        # verify validMode
        validMode = evaluateStr(validMode)
        validMode = int(validMode)

        # verify slices format - \d+:\d+
        sliceParts = slices.split(':')
        if len(sliceParts) == 2:
            # case 2 - slice range - slice1:slice2
            startSlice, endSlice = sliceParts[0], sliceParts[1]
            startSlice = evaluateStr(startSlice)
            endSlice = evaluateStr(endSlice)
        else:
            raise Exception(
                'Error : Wrong slice format (note that slices should be int) - %s in %s inputMSR str = %s' % (
                slices, anElement, strMSR))

        # verify port format - \w+:\w+
        pat2 = r'(-?\w+):(-?\w+)'
        match = re.search(pat2, ports)
        if match:
            CPort, IOPort = str(match.groups()[0].strip()), str(match.groups()[1].strip())
        else:
            raise Exception('Error : Wrong port format (note that ports are str) - %s in %s inputMSR str = %s' % (
            ports, anElement, strMSR))

        # verify atten format - an int
        try:
            atten = evaluateStr(atten)
            atten = int(atten)
        except ValueError:
            raise Exception('Wrong format, atten should be an int or a float - %s' % (atten))

        innerList.append({'Channel': identifier, 'ValidMode': validMode, 'StartSlice': startSlice, 'EndSlice': endSlice,
                          'CommonPort': CPort, 'IOPort': IOPort, 'Attenuation': atten})

    MSRResult = {
        'wss': wss,
        'msr': innerList
    }
    return MSRResult


def evaluateStr(inStr):
    if not inStr:
        raise Exception('Formatting Error: %s' % inStr)
    else:
        try:
            inStr = eval(inStr + ' + 0')
        except NameError as ex:
            raise Exception('Formatting Error - %s' % (ex))
        return inStr


"""
Description:
    A function to send command to WSS

    Parameters:
    - string Command : command to be sent
    - string ret : expected command execution status
    - output string retString : returned string from command

    Required object:
    - Device: object of type WSS
"""


def Serial_GenerateCmd(WSSobj, Command, TestInfo, ret=None, response=None, checkResponse=True):
    if ret is None and (Command.upper() == 'RES' or Command.upper() == 'FWE'):
        ret = 'Ready'
    elif ret is None or '':
        ret = 'OK'

    msg = ''
    result = True
    retString = WSSobj.SerialQuery(Command)
    print retString
    # Wait until WSS is ready
    if not checkResponse:
        return result

    if Command.upper() == 'RES' or Command.upper() == 'FWE':
        timeout = 60
        while 'Ready' not in retString or timeout < 0:
            readStr = WSSobj.SerialRead()
            print readStr
            retString += readStr
            timeout -= 2
            time.sleep(2)

        if timeout < 0:
            result = False
            msg = 'ERROR - WSS error, command ' + Command + ' expecting return ' + ret
            print msg
            TestInfo.ResultMessage += msg

    elif retString.find(ret) == -1:
        result = False
        msg = 'ERROR - WSS error, command ' + Command + ' expecting return ' + ret
        print msg
        TestInfo.ResultMessage += msg

    if not (response is None):
        if retString.find(response) == -1:
            result = False
            msg = 'ERROR - WSS error, command ' + Command + ' expecting response ' + response
            print msg
            TestInfo.ResultMessage += msg

    # Wait for pending bit to clear
    if Command.find('SPA ') != -1:
        pendResult = SerialWaitForOSSReady(WSSobj, TestInfo)
        result = result and pendResult

    return result


def DPRAM_GenerateCmd(WSSobj, Command, TestInfo, expectFailure=None):
    data1 = None
    data2 = None
    data3 = None
    data4 = None
    result = ''

    # get command and data
    Cmd = Command.strip(' ')
    if Cmd.find(' ') >= 0:
        opIndex = Cmd.index(' ')
    else:
        opIndex = len(Cmd)

    if Cmd == 'OSS?':
        result += DPRAM_VerifyRegs(StatusStr='000000000000x001', ErrStr='0000000000000000', HWErrStr='0000000000000000')
        return result

    opCodeStr = 'dpram' + Cmd[:opIndex].upper()
    opCodeStr = opCodeStr.replace('?', '_Q')

    try:
        dpram_opCode = getattr(DPRAMCmdCode, opCodeStr)
    except:
        dpram_opCode = 0xFFFF

    data = Cmd[opIndex:].strip(' ')

    print 'CMD sent: ' + Cmd

    # memory map 1 commands
    if dpram_opCode == DPRAMCmdCode.dpramDCR or dpram_opCode == DPRAMCmdCode.dpramDCR_Q or dpram_opCode == DPRAMCmdCode.dpramDCS or dpram_opCode == DPRAMCmdCode.dpramDCS_Q or dpram_opCode == DPRAMCmdCode.dpramCCC or dpram_opCode == DPRAMCmdCode.dpramNTZ:
        result += DPRAM_GenerateCmd(WSSobj, Command='CMM 1', TestInfo=TestInfo, expectFailure=None)

    result += ('#----------D>WM 0x%X 1\n' % regs.DWP_DPRAM.CmdReg)
    result += ('D>WM 0x%X 1\n' % regs.DWP_DPRAM.CmdReg)
    result += ('#----------D>WM 0x%X 0x%X\n' % (regs.DWP_DPRAM.CmdCodeReg, dpram_opCode))
    result += ('D>WM 0x%X 0x%X\n' % (regs.DWP_DPRAM.CmdCodeReg, dpram_opCode))

    if dpram_opCode == DPRAMCmdCode.dpramFWT or dpram_opCode == DPRAMCmdCode.dpramFWS or dpram_opCode == DPRAMCmdCode.dpramFWL or dpram_opCode == DPRAMCmdCode.dpramCMM or dpram_opCode == DPRAMCmdCode.dpramCHW:
        data1 = int(data)
        result += DPRAM_WriteArguments(Data1=data1, Data2=data2, Data3=data3, Data4=data4)
    elif dpram_opCode == DPRAMCmdCode.dpramSLS:
        data1 = 3
        result += DPRAM_WriteArguments(Data1=data1, Data2=data2, Data3=data3, Data4=data4)
    elif dpram_opCode == DPRAMCmdCode.dpramSFD:
        data1 = 1
        result += DPRAM_WriteArguments(Data1=data1, Data2=data2, Data3=data3, Data4=data4)
    elif dpram_opCode == DPRAMCmdCode.dpramSAB:
        data1 = 2
        result += DPRAM_WriteArguments(Data1=data1, Data2=data2, Data3=data3, Data4=data4)
    elif dpram_opCode == DPRAMCmdCode.dpramDCC:
        result += DPRAM_ParseDCCString(data, False)
    elif dpram_opCode == DPRAMCmdCode.dpramUCA:
        result += DPRAM_ParseUCAString(data, False)
    elif dpram_opCode == DPRAMCmdCode.dpramDCR:
        temp_str, data1, data2 = DPRAM_ParseDCRString(data, False)
        result += temp_str
    elif dpram_opCode == DPRAMCmdCode.dpramDCR_Q:
        data3 = 0x100
        data4 = 0xEFF
        result += DPRAM_WriteArguments(Data1=data1, Data2=data2, Data3=data3, Data4=data4, toVerify=False)
    elif dpram_opCode == DPRAMCmdCode.dpramDCS_Q:
        data1 = 0x100
        data2 = 0x001
        data3 = 0x102
        data4 = 0xEFD
        result += DPRAM_ParseDCS_QString(data, data1, data2, data3, data4, False)
    elif dpram_opCode == DPRAMCmdCode.dpramSTR or dpram_opCode == DPRAMCmdCode.dpramTEST or dpram_opCode == DPRAMCmdCode.dpramRES or dpram_opCode == DPRAMCmdCode.dpramFWE or dpram_opCode == DPRAMCmdCode.dpramCLE or dpram_opCode == DPRAMCmdCode.dpramNTZ or dpram_opCode == DPRAMCmdCode.dpramNOP or dpram_opCode == 0xFFFF or dpram_opCode == DPRAMCmdCode.dpramBLOCKALL:
        result += ''
    elif dpram_opCode == DPRAMCmdCode.dpramSTARTFWD:
        data1 = (int(data) >> 16) & 0xFFFF
        data2 = (int(data)) & 0xFFFF
        result += DPRAM_WriteArguments(Data1=data1, Data2=data2, Data3=data3, Data4=data4, toVerify=False)
    else:
        raise Exception('Error : Command is not covered - %s')

    if expectFailure == 'CER':
        ErrStr = '0000000000001000'
        StatusStr = '000000000000x011'
        expectFailure = 1
    elif expectFailure == 'AER' or expectFailure == 'RER':
        ErrStr = '0000000000000001'
        StatusStr = '000000000000x011'
        expectFailure = 1
    else:
        ErrStr = '0000000000000000'
        StatusStr = '000000000000x001'
        expectFailure = 0

    result += ('G>ST 0 %d\n' % expectFailure)
    result += '#----------G<NSTART 1\n'
    result += 'G<NSTART 1\n'

    result += ('#----------G<ER %d\n' % expectFailure)
    result += ('G<ER %d\n' % expectFailure)

    result += '#----------G<DN 1\n'
    result += ('G<DN %d\n' % abs(expectFailure - 1))

    result += '#----------G<RD 0\n'
    result += 'G<RD 0\n'

    result += '#----------G<FT 1\n'
    result += 'G<FT 1\n'

    result += '#----------G<AL 1\n'
    result += 'G<AL 1\n'

    result += '#----------T<VBD 0x20 0000000000000000\n'
    result += 'T<VBD 0x20 0000000000000000\n'
    result += ('#----------D>VM 0x%X 0x%X\n' % (regs.DWP_DPRAM.CmdCodeReg, dpram_opCode))
    if dpram_opCode == DPRAMCmdCode.dpramRES or dpram_opCode == DPRAMCmdCode.dpramFWE:
        result += ('D>VM 0x%X 0x%X\n' % (regs.DWP_DPRAM.CmdCodeReg, 0))
    else:
        result += ('D>VM 0x%X 0x%X\n' % (regs.DWP_DPRAM.CmdCodeReg, dpram_opCode))

    result += DPRAM_WriteArguments(Data1=data1, Data2=data2, Data3=data3, Data4=data4, toVerify=True)

    # check channel definition response
    if dpram_opCode == DPRAMCmdCode.dpramDCC:
        result += DPRAM_ParseDCCString(data, True)

    # check port and attenuation response
    if dpram_opCode == DPRAMCmdCode.dpramUCA:
        result += DPRAM_ParseUCAString(data, True)

    # check DCR records
    if dpram_opCode == DPRAMCmdCode.dpramDCR:
        temp_str, data1, data2 = DPRAM_ParseDCRString(data, True, data1, data2)
        result += temp_str

    result += DPRAM_VerifyRegs(StatusStr, ErrStr, HWErrStr='0000000000000000')

    if dpram_opCode == DPRAMCmdCode.dpramDCR or dpram_opCode == DPRAMCmdCode.dpramDCR_Q or dpram_opCode == DPRAMCmdCode.dpramDCS or dpram_opCode == DPRAMCmdCode.dpramDCS_Q or dpram_opCode == DPRAMCmdCode.dpramCCC or dpram_opCode == DPRAMCmdCode.dpramNTZ:
        result += DPRAM_GenerateCmd(WSSobj, Command='CMM 0', TestInfo=TestInfo, expectFailure=None)

    return result


def DPRAM_VerifyRegs(StatusStr='000000000000x001', ErrStr='0000000000000000', HWErrStr='0000000000000000'):
    regStr = ''
    regStr += (('#----------T<VBD 0x%X ' % regs.DWP_DPRAM.StatusReg) + StatusStr + '\n')
    regStr += (('T<VBD 0x%X ' % regs.DWP_DPRAM.StatusReg) + StatusStr + '\n')

    regStr += (('#----------T<VBD 0x%X ' % regs.DWP_DPRAM.ErrorCodeReg) + ErrStr + '\n')
    regStr += (('T<VBD 0x%X ' % regs.DWP_DPRAM.ErrorCodeReg) + ErrStr + '\n')

    regStr += (('#----------T<VBD 0x%X ' % regs.DWP_DPRAM.HardwareErrorReg) + HWErrStr + '\n')
    regStr += (('T<VBD 0x%X ' % regs.DWP_DPRAM.HardwareErrorReg) + HWErrStr + '\n')
    return regStr


def DPRAMVerifyStatus(WSSobj, TestInfo, Status='000000000000x001', Err='0000000000000000', HWErr='0000000000000000'):
    result = ''
    result += DPRAM_VerifyRegs(StatusStr=Status, ErrStr=Err, HWErrStr=HWErr)
    return DPRAM_SendRunTextFile(WSSobj, TestInfo, 'VerifyStatus', result)


def DPRAM_CMM(WSSobj, MemoryMap, TestInfo, expectFailure=None):
    result = ''
    result += ('D>WM 0x%X 1\n' % regs.DWP_DPRAM.CmdReg)
    result += ('D>WM 0x%X 0x%X\n' % (regs.DWP_DPRAM.CmdCodeReg, DPRAMCmdCode.dpramCMM))
    result += ('D>WM 0x%X 0x%X\n' % (regs.DWP_DPRAM.Data1Reg, int(MemoryMap) & 0xFFFF))
    if expectFailure is None:
        expectFailure = 0;
    else:
        expectFailure = 1;

    return None


def DPRAM_WriteArguments(Data1=None, Data2=None, Data3=None, Data4=None, toVerify=False):
    dataStr = ''
    if toVerify == True:
        if not (Data1 is None):
            dataStr += ('#----------D>VM 0x%X 0x%X\n' % (regs.DWP_DPRAM.Data1Reg, int(Data1) & 0xFFFF))
            dataStr += ('D>VM 0x%X 0x%X\n' % (regs.DWP_DPRAM.Data1Reg, int(Data1) & 0xFFFF))
        if not (Data2 is None):
            dataStr += ('#----------D>VM 0x%X 0x%X\n' % (regs.DWP_DPRAM.Data2Reg, int(Data2) & 0xFFFF))
            dataStr += ('D>VM 0x%X 0x%X\n' % (regs.DWP_DPRAM.Data2Reg, int(Data2) & 0xFFFF))
        if not (Data3 is None):
            dataStr += ('#----------D>VM 0x%X 0x%X\n' % (regs.DWP_DPRAM.Data3Reg, int(Data3) & 0xFFFF))
            dataStr += ('D>VM 0x%X 0x%X\n' % (regs.DWP_DPRAM.Data3Reg, int(Data3) & 0xFFFF))
        if not (Data4 is None):
            dataStr += ('#----------D>VM 0x%X 0x%X\n' % (regs.DWP_DPRAM.Data4Reg, int(Data4) & 0xFFFF))
            dataStr += ('D>VM 0x%X 0x%X\n' % (regs.DWP_DPRAM.Data4Reg, int(Data4) & 0xFFFF))
    else:
        if not (Data1 is None):
            dataStr += ('#----------D>WM 0x%X 0x%X\n' % (regs.DWP_DPRAM.Data1Reg, int(Data1) & 0xFFFF))
            dataStr += ('D>WM 0x%X 0x%X\n' % (regs.DWP_DPRAM.Data1Reg, int(Data1) & 0xFFFF))
        if not (Data2 is None):
            dataStr += ('#----------D>WM 0x%X 0x%X\n' % (regs.DWP_DPRAM.Data2Reg, int(Data2) & 0xFFFF))
            dataStr += ('D>WM 0x%X 0x%X\n' % (regs.DWP_DPRAM.Data2Reg, int(Data2) & 0xFFFF))
        if not (Data3 is None):
            dataStr += ('#----------D>WM 0x%X 0x%X\n' % (regs.DWP_DPRAM.Data3Reg, int(Data3) & 0xFFFF))
            dataStr += ('D>WM 0x%X 0x%X\n' % (regs.DWP_DPRAM.Data3Reg, int(Data3) & 0xFFFF))
        if not (Data4 is None):
            dataStr += ('#----------D>WM 0x%X 0x%X\n' % (regs.DWP_DPRAM.Data4Reg, int(Data4) & 0xFFFF))
            dataStr += ('D>WM 0x%X 0x%X\n' % (regs.DWP_DPRAM.Data4Reg, int(Data4) & 0xFFFF))
    return dataStr


def DPRAM_SendRunTextFile(WSSobj, TestInfo, txtLabel, commandStr, waitExeTimeInS=5):
    libpath = os.path.dirname(os.path.abspath(__file__))
    txtTemplateFile = libpath + '\\..\\template\\Textfile\\texttpl.txt'
    txtPath = TestInfo.Variables['TxtPath'] + '\\textfiles'
    txtName = TestInfo.Variables['TCName'] + txtLabel + str(datetime.now().hour) + '_' + str(
        datetime.now().minute) + '_' + str(datetime.now().second) + '.txt'

    print 'text path: ' + txtPath
    if not os.path.exists(txtPath):
        os.makedirs(txtPath)
    txtRun = open(txtPath + '\\' + txtName, 'w')
    with open(txtTemplateFile) as openfileobject:
        for line in openfileobject:
            if line.find('key_TestData') >= 0:
                txtRun.write(commandStr)
            else:
                txtRun.write(line)
    openfileobject.close()
    txtRun.close()
    return SendRunTestFile(WSSobj=WSSobj, TestInfo=TestInfo, fileToTransfer=txtPath + '\\' + txtName,
                           waitExeTimeInS=waitExeTimeInS)


def DPRAM_ParseDCCString(strDCC, toVerify=False):
    # create initial flexgridScratchpad with 0xFFFF
    flexgridScratchpad = []
    for i in range(512):
        flexgridScratchpad.append('0xFFFF')

    if not strDCC:
        raise Exception('Error : strDCC cannot be empty or None - %s')

    # remove last ';'
    if strDCC[-1] == ';':
        strDCC = strDCC[:-1]

    elements = strDCC.strip().split(';')

    # fill in the scratchpad
    for anElement in elements:
        # each element has the following format - 'chnlNo=slice1:slice2'
        innerElments = anElement.split('=')
        chnlNo = int(innerElments[0])
        slicePart = innerElments[1]
        startSlice = slicePart.split(':')[0]
        endSlice = slicePart.split(':')[1]
        flexgridScratchpad[2 * int(chnlNo) - 2] = '0x%04x' % int(startSlice)
        flexgridScratchpad[2 * int(chnlNo) - 1] = '0x%04x' % int(endSlice)

    DCCString = ' '.join(flexgridScratchpad) + '\n'
    if toVerify == True:
        result = '#------ VerifyFlexgridDesignation\n'
        result += ('#------D>VM 0x0600 ' + DCCString)
        result += ('D>VM 0x0600 ' + DCCString)
        result += '#------ VerifyFlexgridScratchpad\n'
        result += ('#------D>VM 0x0800 ' + DCCString)
        result += ('D>VM 0x0800 ' + DCCString)
    else:
        result = '#------ DefineChannels - UpdateFlexgridSliceScratchpad\n'
        result += ('#------D>WM 0x0800 ' + DCCString)
        result += ('D>WM 0x0800 ' + DCCString)

    return result


def DPRAM_ParseUCAString(strUCA, toVerify=False):
    # create initial port and attenuation array with 0xFFFF
    # PortAttnArray = []
    # for i in range(256):
    # PortAttnArray.append('0xFFFF')
    # currentArray = requiredArray

    if not strUCA:
        raise Exception('Error : strUCA cannot be empty or None - %s')

    # remove last ';'
    if strUCA[-1] == ';':
        strUCA = strUCA[:-1]

    elements = strUCA.strip().split(';')

    # fill in the port and attenuation arrays
    if toVerify == True:
        result = '#------ Verify Required Port and Attenuation\n'
        for anElement in elements:
            # each element has the following format - 'chnlNo,port,attn'
            innerElements = anElement.split(',')
            chnlNo = int(innerElements[0])
            chnlPos = 0x200 + chnlNo - 1
            port = int(innerElements[1]) << 8
            attn = int(float(innerElements[2]) * 10)
            portattn = port + attn
            portattnStr = '0x%04x' % portattn
            result += ('#------D>VM ' + '0x%04x' % chnlPos + ' ' + portattnStr + '\n')
            result += ('D>VM ' + '0x%04x' % chnlPos + ' ' + portattnStr + '\n')
    else:
        result = '#----- Write Required Port and Attenuation\n'
        for anElement in elements:
            # each element has the following format - 'chnlNo,port,attn'
            innerElements = anElement.split(',')
            chnlNo = int(innerElements[0])
            chnlPos = 0x200 + chnlNo - 1
            port = int(innerElements[1]) << 8
            attn = int(float(innerElements[2]) * 10)
            portattn = port + attn
            portattnStr = '0x%04x' % portattn
            result += ('#------D>WM ' + '0x%04x' % chnlPos + ' ' + portattnStr + '\n')
            result += ('D>WM ' + '0x%04x' % chnlPos + ' ' + portattnStr + '\n')
            # PortAttnArray[chnlNo - 1] = portattnStr

            # PortAttnString = ' '.join(PortAttnArray) + '\n'
            # if toVerify == True:
            # result = '#------ Verify Required Port and Attenuation\n'
            # result += ('#------D>VM 0x0200 ' + PortAttnString)
            # result += ('D>VM 0x0200 ' + PortAttnString)
            # result += '#----- Verify Current Port and Attenuation\n'
            # result += ('#------D>VM 0x0300 ' + PortAttnString)
            # result += ('D>VM 0x0300 ' + PortAttnString)
            # else:
            # result = '#----- Write Required Port and Attenuation\n'
            # result += ('#------D>WM 0x0200 ' + PortAttnString)
            # result += ('D>WM 0x0200 ' + PortAttnString)

    return result


def DPRAM_ParseDCRString(strDCR, toVerify=False, DCRInputOffset=None, DCRInputLength=None):
    if not strDCR:
        raise Exception('Error : strDCR cannot be empty or None - %s')

    # remove last ';'
    if strDCR[-1] == ';':
        strDCR = strDCR[:-1]

    elements = strDCR.strip().split(';')
    numElments = len(elements)
    DCRInputData = []

    if DCRInputOffset == None and DCRInputLength == None:
        DCRInputLength = numElments * 5
        DCRInputOffset = random.randint(regs.DWP_DPRAM.MM1_START, regs.DWP_DPRAM.MM1_END - DCRInputLength + 1)

    result = ''
    if not toVerify == True:
        result = DPRAM_WriteArguments(DCRInputOffset, DCRInputLength)

    for anElement in elements:
        # each element has the following format - 'chnlNo=slice1:slice2,range1:range2'
        innerElements = anElement.split('=')
        chnlNo = int(innerElements[0])
        SliceRange = str(innerElements[1])
        slicePart = SliceRange.split(',')[0]
        rangePart = SliceRange.split(',')[1]
        startSlice = int(slicePart.split(':')[0])
        endSlice = int(slicePart.split(':')[1])
        startRange = int(rangePart.split(':')[0])
        endRange = int(rangePart.split(':')[1])
        DCRInputData.append('0x%04x' % chnlNo)
        DCRInputData.append('0x%04x' % startSlice)
        DCRInputData.append('0x%04x' % endSlice)
        DCRInputData.append('0x%04x' % startRange)
        DCRInputData.append('0x%04x' % endRange)

    DCRInputDataString = ' '.join(DCRInputData) + '\n'
    if toVerify == True:
        result += '#------ VerifyDCRRecords\n'
        result += '#------D>VM ' + '0x%04x' % DCRInputOffset + ' ' + DCRInputDataString
        result += 'D>VM ' + '0x%04x' % DCRInputOffset + ' ' + DCRInputDataString
    else:
        result += '#------ DefineChannelAndRange - InputData\n'
        result += '#------D>WM ' + '0x%04x' % DCRInputOffset + ' ' + DCRInputDataString
        result += 'D>WM ' + '0x%04x' % DCRInputOffset + ' ' + DCRInputDataString

    return (result, DCRInputOffset, DCRInputLength)


def DPRAM_ParseDCS_QString(strDCS_Q, Data1=None, Data2=None, Data3=None, Data4=None, toVerify=False):
    if not strDCS_Q:
        raise Exception('Error : strDCS_Q cannot be empty or None - %s')

    result = ''
    if not toVerify == True:
        result += 'D>WM ' + ('0x%04x' % int(Data1)) + ' ' + ('0x%04x' % int(strDCS_Q)) + '\n'
        result += '#------D>WM ' + ('0x%04x' % int(Data1)) + ' ' + ('0x%04x' % int(strDCS_Q)) + '\n'
    result += DPRAM_WriteArguments(Data1, Data2, Data3, Data4, toVerify)
    return result


def WSSQuery(WSSobj, WSScommand, TestInfo, expectedRet=None, checkResponse=True, ERECV=False, ETXT=True,
             processCmd=True):
    if TestInfo.Variables['Interface'] == 'Serial':
        return Serial_GenerateCmd(WSSobj=WSSobj, Command=WSScommand, ret=expectedRet, TestInfo=TestInfo,
                                  checkResponse=checkResponse)
    elif TestInfo.Variables['Interface'] == 'SPI':
        return SPI_GenerateCmd(WSSobj=WSSobj, Cmd=WSScommand, TestInfo=TestInfo, expectRet=expectedRet)
    elif TestInfo.Variables['Interface'] == 'DPRAM':
        if not expectedRet == None and not expectedRet == 'OK':
            commandStr = DPRAM_GenerateCmd(WSSobj=WSSobj, Command=WSScommand, TestInfo=TestInfo,
                                           expectFailure=expectedRet)
        else:
            commandStr = DPRAM_GenerateCmd(WSSobj=WSSobj, Command=WSScommand, TestInfo=TestInfo, expectFailure=None)
        return DPRAM_SendRunTextFile(WSSobj=WSSobj, TestInfo=TestInfo, txtLabel='', commandStr=commandStr)
    elif TestInfo.Variables['Interface'] == 'Huawei_HD':
        return Huawei_GenerateCmd(WSSobj=WSSobj, Command=WSScommand, ret=expectedRet, TestInfo=TestInfo,
                                  checkResponse=checkResponse, ERECV=ERECV, ETXT=ETXT)
    elif TestInfo.Variables['Interface'] == 'Nokia_HD':
        return NokiaSerial_GenerateCmd(WSSobj=WSSobj, Command=WSScommand, Status=expectedRet, TestInfo=TestInfo,
                                       checkResponse=checkResponse, sendRECV=ERECV, byTXT=ETXT, processCmd=processCmd)
    else:
        raise Exception('Exception: interface ' + TestInfo.Variables['Interface'] + ' not supported!')


def SPIVerifyOSS(WSSobj, TestInfo, bitsStr=0x0001):
    result = SPI_GenerateCmd(WSSobj=WSSobj, Cmd='OSS?', TestInfo=TestInfo)
    # if not result:
    # msg = 'ERROR : SPI OSS command failed.'
    # print msg
    # TestInfo.ResultMessage += msg
    # return result
    spiVBSStr = VerifySPIRegister(RegOffset=ReplyReg.SPIDATA, bitsStr=bitsStr, wordLengthInBits=16)
    spiVBSRet = WSSobj.SerialQuery(spiVBSStr)
    print spiVBSRet
    while (spiVBSRet.find('Server closed connection') >= 0 or spiVBSRet.find('Segmentatio fault') >= 0):
        print 'resend command...'
        time.sleep(0.2)
        spiVBSRet = WSSobj.SerialQuery(spiVBSStr)
        print spiVBSRet

    if spiVBSRet.find('ms S') == -1:
        msg = 'ERROR : SPI OSS VBS failed.'
        result = False
        print msg
        TestInfo.ResultMessage += msg
    return result


def SPIVerifyHSS(WSSobj, TestInfo, bitsStr=0x0000):
    result = SPI_GenerateCmd(WSSobj=WSSobj, Cmd='HSS?', TestInfo=TestInfo)
    # if not result:
    # msg = 'ERROR : SPI HSS command failed.'
    # print msg
    # TestInfo.ResultMessage += msg
    # return result
    spiVBSStr = VerifySPIRegister(RegOffset=ReplyReg.SPIDATA, bitsStr=bitsStr, wordLengthInBits=16)
    spiVBSRet = WSSobj.SerialQuery(spiVBSStr)
    print spiVBSRet
    while (spiVBSRet.find('Server closed connection') >= 0 or spiVBSRet.find('Segmentatio fault') >= 0):
        print 'resend command...'
        time.sleep(0.2)
        spiVBSRet = WSSobj.SerialQuery(spiVBSStr)
        print spiVBSRet

    if spiVBSRet.find('ms S') == -1:
        msg = 'ERROR : SPI HSS VBS failed.'
        result = False
        print msg
        TestInfo.ResultMessage += msg
    return result


def SPIVerifyLSS(WSSobj, TestInfo, bitsStr=0x0000):
    result = SPI_GenerateCmd(WSSobj=WSSobj, Cmd='LSS?', TestInfo=TestInfo)
    # if not result:
    # msg = 'ERROR : SPI LSS command failed.'
    # print msg
    # TestInfo.ResultMessage += msg
    # return result
    spiVBSStr = VerifySPIRegister(RegOffset=ReplyReg.SPIDATA, bitsStr=bitsStr, wordLengthInBits=16)
    spiVBSRet = WSSobj.SerialQuery(spiVBSStr)
    print spiVBSRet
    while (spiVBSRet.find('Server closed connection') >= 0 or spiVBSRet.find('Segmentatio fault') >= 0):
        print 'resend command...'
        time.sleep(0.2)
        spiVBSRet = WSSobj.SerialQuery(spiVBSStr)
        print spiVBSRet

    if spiVBSRet.find('ms S') == -1:
        msg = 'ERROR : SPI LSS VBS failed.'
        result = False
        print msg
        TestInfo.ResultMessage += msg
    return result


def SPIVerifyStatus(WSSobj, TestInfo, bitsStrOSS=0x0001, bitsStrHSS=0x0000, bitsStrLSS=0x0000):
    resultOSS = SPIVerifyOSS(WSSobj, TestInfo, bitsStrOSS)
    resultHSS = SPIVerifyHSS(WSSobj, TestInfo, bitsStrHSS)
    resultLSS = SPIVerifyLSS(WSSobj, TestInfo, bitsStrLSS)
    result = resultOSS and resultHSS and resultLSS
    return result


def VerifySPIRegister(RegOffset, bitsStr=0x0001, wordLengthInBits=16):
    finalStr = ''
    for i in range(0, wordLengthInBits):
        if (bitsStr & (1 << i) != 0):
            finalStr = '1' + finalStr
        else:
            finalStr = '0' + finalStr

    if not RegOffset:
        return 'T<VBS %s\n' % (finalStr)
    else:
        result = 'P'
        result += '<VBS 0x%X %s\n' % (RegOffset, finalStr)
        return result


def SerialVerifyOSS(WSSobj, TestInfo, bitsStr=0x0001, verifyPending=False):
    result = True
    retString = WSSobj.SerialQuery('OSS?')
    print retString
    #   hexindex = retString.index('0x')
    #   ossstring = retString[hexindex:hexindex+6]
    #   osshex = int(ossstring, 16)
    if retString.find('OK') == -1:
        result = False
        msg = 'Error - WSS command OSS? failed. '
        print msg
        TestInfo.ResultMessage += msg
        return result
    if verifyPending == False:
        if retString.find('%04X' % bitsStr) == -1 and retString.find('0x0081') == -1:
            result = False
            msg = 'Error - Verify OSS? status failed'
            print msg
            TestInfo.ResultMessage += msg
    else:
        if retString.find('%04X' % bitsStr) == -1:
            result = False
            msg = 'Error - Verify OSS? status failed'
            print msg
            TestInfo.ResultMessage += msg
    return result


def SerialVerifyHSS(WSSobj, TestInfo, bitsStr=0x0000):
    result = True
    retString = WSSobj.SerialQuery('HSS?')
    print retString
    if retString.find('OK') == -1:
        result = False
        msg = 'Error - WSS command HSS? failed. '
        print msg
        TestInfo.ResultMessage += msg
        return result
    if retString.find('%04X' % bitsStr) == -1:
        result = False
        msg = 'Error - Verify HSS? status failed'
        print msg
        TestInfo.ResultMessage += msg
    return result


def SerialVerifyLSS(WSSobj, TestInfo, bitsStr=0x0000):
    result = True
    retString = WSSobj.SerialQuery('LSS?')
    print retString
    if retString.find('OK') == -1:
        result = False
        msg = 'Error - WSS command LSS? failed. '
        print msg
        TestInfo.ResultMessage += msg
        return result
    if retString.find('%04X' % bitsStr) == -1:
        result = False
        msg = 'Error - Verify LSS? status failed'
        print msg
        TestInfo.ResultMessage += msg
    return result


def SerialVerifyStatus(WSSobj, TestInfo, bitsStrOSS=0x0001, bitsStrHSS=0x0000, bitsStrLSS=0x0000):
    resultOSS = SerialVerifyOSS(WSSobj, TestInfo, bitsStrOSS)
    resultHSS = SerialVerifyHSS(WSSobj, TestInfo, bitsStrHSS)
    resultLSS = SerialVerifyLSS(WSSobj, TestInfo, bitsStrLSS)
    result = resultOSS and resultHSS and resultLSS
    return result


def VerifyWSSStatus(WSSobj, TestInfo, bitsStrOSS=0x0001, bitsStrHSS=0x0000, bitsStrLSS=0x0000, bitsStr1='', bitsStr2='',
                    bitsStr3='', bitsStr4='', bitsStr0x23='000000000000x001', bitsStr0x25='0000000000000000',
                    bitsStr0x29='0000000000000000'):
    if TestInfo.Variables['Interface'] == 'Serial':
        return SerialVerifyStatus(WSSobj=WSSobj, TestInfo=TestInfo, bitsStrOSS=bitsStrOSS, bitsStrHSS=bitsStrHSS,
                                  bitsStrLSS=bitsStrLSS)
    if TestInfo.Variables['Interface'] == 'Nokia_HD':
        return NokiaSerialVerifyStatus(WSSobj=WSSobj, TestInfo=TestInfo, bitsStrOSS=bitsStrOSS, bitsStrHSS=bitsStrHSS)
    elif TestInfo.Variables['Interface'] == 'DPRAM':
        return DPRAMVerifyStatus(WSSobj=WSSobj, TestInfo=TestInfo, Status=bitsStr0x23, Err=bitsStr0x25,
                                 HWErr=bitsStr0x29)
    elif TestInfo.Variables['Interface'] == 'SPI':
        return SPIVerifyStatus(WSSobj=WSSobj, TestInfo=TestInfo, bitsStrOSS=bitsStrOSS, bitsStrHSS=bitsStrHSS,
                               bitsStrLSS=bitsStrLSS)
    elif TestInfo.Variables['Interface'] == 'Huawei_HD':
        return HuaweiVerifyStatus(WSSobj=WSSobj, TestInfo=TestInfo, bitsStr1=bitsStr1, bitsStr2=bitsStr2,
                                  bitsStr3=bitsStr3, bitsStr4=bitsStr4)
    else:
        raise Exception('Exception: interface ' + TestInfo.Variables['Interface'] + ' not supported!')


def SPIWaitForOSSReady(WSSobj, TestInfo, bitsStr=0x0001, spiPollingTimeInMS=2000, timeoutInMS=20000):
    result = SPIVerifyOSS(WSSobj=WSSobj, TestInfo=TestInfo, bitsStr=bitsStr)
    while (not result) and timeoutInMS > 0:
        time.sleep(spiPollingTimeInMS / 1000)
        timeoutInMS = timeoutInMS - spiPollingTimeInMS
        result = SPIVerifyOSS(WSSobj=WSSobj, TestInfo=TestInfo, bitsStr=bitsStr)
    if not result:
        msg = 'ERROR - SPI wait for OSS status ' + hex(bitsStr) + ' failed!'
        print msg
        TestInfo.ResultMessage += msg

    return result


def SerialWaitForOSSReady(WSSobj, TestInfo, bitsStr=0x0001, serialPollingTimeInMS=2000, timeoutInMS=20000):
    result = SerialVerifyOSS(WSSobj, TestInfo)
    while (not result) and timeoutInMS > 0:
        time.sleep(serialPollingTimeInMS / 1000)
        timeoutInMS -= serialPollingTimeInMS
        result = SerialVerifyOSS(WSSobj, TestInfo)
    if timeoutInMS <= 0:
        result = False
        msg = 'ERROR - Serial Wait for OSS status ' + hex(bitsStr) + ' failed!'
        print msg
        TestInfo.ResultMessage += msg
    return result


def DPRAMWaitForStatusReady(WSSobj, TestInfo, bitsStr='0000000000000001', DPRAMPollingTimeInMS=2000, timeoutInMS=20000):
    result = DPRAMVerifyStatus(WSSobj, TestInfo, Status=bitsStr)
    while (not result) and timeoutInMS > 0:
        time.sleep(DPRAMPollingTimeInMS / 1000)
        timeoutInMS = timeoutInMS - DPRAMPollingTimeInMS
        result = DPRAMVerifyStatus(WSSobj, TestInfo=TestInfo, Status=bitsStr)
    if timeoutInMS <= 0:
        result = False
        msg = 'ERROR - DPRAM Wait for status ' + bitsStr + ' failed!'
        print msg
        TestInfo.ResultMessage += msg
    return result


def WSSWaitForOSSReady(WSSobj, TestInfo, bitsStr=0x0001, PollingTimeInMS=2000, timeoutInMS=20000):
    if TestInfo.Variables['Interface'] == 'Serial':
        return SerialWaitForOSSReady(WSSobj=WSSobj, TestInfo=TestInfo, bitsStr=0x0001,
                                     serialPollingTimeInMS=PollingTimeInMS, timeoutInMS=timeoutInMS)
    elif TestInfo.Variables['Interface'] == 'Nokia_HD':
        return NokiaSerialWaitForOSSReady(WSSobj=WSSobj, TestInfo=TestInfo, bitsStr=0x0001,
                                          NokiaserialPollingTimeInMS=PollingTimeInMS, timeoutInMS=timeoutInMS)
    elif TestInfo.Variables['Interface'] == 'DPRAM':
        return DPRAMWaitForStatusReady(WSSobj=WSSobj, TestInfo=TestInfo)
    elif TestInfo.Variables['Interface'] == 'SPI':
        return SPIWaitForOSSReady(WSSobj=WSSobj, TestInfo=TestInfo, bitsStr=0x0001, spiPollingTimeInMS=PollingTimeInMS,
                                  timeoutInMS=timeoutInMS)
    elif TestInfo.Variables['Interface'] == 'Huawei_HD':
        return HuaweiWaitForOpticsReady(WSSobj=WSSobj, TestInfo=TestInfo, serialPollingTimeInMS=PollingTimeInMS,
                                        timeoutInMS=timeoutInMS)
    else:
        raise Exception('Error - interface ' + TestInfo.Variables['Interface'] + ' not supported!')


def MasterReset(WSSobj, TestInfo):
    path = os.path.dirname(os.path.abspath(__file__))
    masterresetFile = path + '\\..\\template\\Textfile\\masterreset'
    if TestInfo.Variables['Product'] == 'DWPF2':
        masterresetFile = masterresetFile + 'DWP.txt'
    else:
        if TestInfo.Variables['Interface'] == 'Huawei_HD':
            if TestInfo.Variables['Product'] == 'HDSP':
                masterresetFile = masterresetFile + 'Huawei_HDSP.txt'
            else:
                masterresetFile = masterresetFile + 'Huawei_HDLP.txt'
        else:
            masterresetFile = masterresetFile + 'HD.txt'
    result = SendRunTestFile(WSSobj=WSSobj, TestInfo=TestInfo, fileToTransfer=masterresetFile, waitExeTimeInS=300)
    if TestInfo.Variables['Interface'] == 'Serial':
        serialRetStr = WSSobj.SerialQuery('\r\nuut\r\n\r\n')
        print serialRetStr
        time.sleep(3)
        serialRetStr = WSSobj.SerialQuery('\r\n\r\n')
        if serialRetStr.find('CER') == -1:
            result = False
            msg = 'Error - enter uut mode failed!'
            TestInfo.ResultMessage += msg
    return result


def HardReset(WSSobj, TestInfo):
    path = os.path.dirname(os.path.abspath(__file__))
    hardresetFile = path + '\\..\\template\\Textfile\\hardreset'
    if TestInfo.Variables['Product'] == 'DWPF2':
        hardresetFile = hardresetFile + 'DWP.txt'
    elif TestInfo.Variables['Interface'] == 'Huawei_HD':
        hardresetFile = hardresetFile + 'Huawei_HDSP.txt'
    else:
        hardresetFile = hardresetFile + 'HD.txt'
    result = SendRunTestFile(WSSobj=WSSobj, TestInfo=TestInfo, fileToTransfer=hardresetFile, waitExeTimeInS=12)
    if TestInfo.Variables['Interface'] == 'Serial':
        serialRetStr = WSSobj.SerialQuery('\r\nuut\r\n\r\n')
        print serialRetStr
        time.sleep(3)
        serialRetStr = WSSobj.SerialQuery('\r\n\r\n')
        if serialRetStr.find('CER') == -1:
            result = False
            msg = 'Error - enter uut mode failed!'
            TestInfo.ResultMessage += msg
    return result


def TransferBinaryFile(WSSobj, TestInfo, fileToTransfer, printMsg=True):
    file = open(fileToTransfer, 'rb')
    if printMsg == True:
        print 'File to transfer: ' + fileToTransfer
        print 'File transfer started... '
    i = 0
    while 1:
        nextstr = file.read(1)
        if not nextstr:
            break
        testarray = array.array('B', nextstr)
        transferByte = Array[Byte](testarray)
        WSSobj.SerialWrite(transferByte)
        i += 1

    file.close()
    if printMsg == True:
        print 'File transfer end, ' + str(i) + ' bytes transferred'


def SendRunTestFile(WSSobj, TestInfo, fileToTransfer, waitExeTimeInS=30, spiFwtFlag=False):
    totalTimeOutInS = 1000
    result = True
    if TestInfo.Variables['Interface'] == 'Serial':
        exitMsg = WSSobj.ExitUUT()
        if exitMsg.find('Error') >= 0:
            exitMsg = WSSobj.ExitUUT()
            if exitMsg.find('Error') >= 0:
                result = False
                msg = 'Error - exit uut mode failed!'
                print msg
                TestInfo.ResultMessage += msg
                return result
    UnexpectedError = True
    while (UnexpectedError == True):
        print fileToTransfer
        statinfo = os.stat(fileToTransfer)
        filesize = statinfo.st_size
        print str(filesize)
        retMsg = WSSobj.SerialQuery('\rupload testdata\r' + str(filesize))
        print retMsg
        #   retMsg = WSSobj.SerialQuery(str(filesize))
        #   print retMsg

        #   if retMsg.find('Enter Test Data File Length:') == -1:
        #       result = False
        #       msg = 'Error - upload testdata command failed!'
        #       print msg
        #       TestInfo.ResultMessage += msg
        #       return result


        #   retMsg = WSSobj.SerialQuery(str(filesize))
        #   print retMsg
        if retMsg.find('Transfer Test Data File in Binary') == -1:
            result = False
            msg = 'Error - transfer file error'
            print msg
            TestInfo.ResultMessage += msg
            return result

        TransferBinaryFile(WSSobj=WSSobj, TestInfo=TestInfo, fileToTransfer=fileToTransfer)

        # retMsg = WSSobj.SerialQuery('\r\n')
        # print retMsg
        #   if retMsg.find('File Loaded successfully over RS232') == -1:
        #       result = False
        #       msg = 'Error - file transfer failed!'
        #       print msg
        #       TestInfo.ResultMessage += msg
        #       return result

        retMsg = WSSobj.SerialQuery('run')
        print retMsg
        time.sleep(waitExeTimeInS)
        if retMsg.find('Result End') == -1:
            totalTimeOutInS -= waitExeTimeInS
            readFlag = False
            while totalTimeOutInS > 0:
                resultMsg = WSSobj.SerialRead()
                while resultMsg != '*' and resultMsg.find('No Reading') == -1:
                    retMsg += resultMsg
                    resultMsg = WSSobj.SerialRead()
                    print resultMsg
                    retMsg += resultMsg
                    readFlag = True
                if readFlag:
                    break
                time.sleep(100)
                totalTimeOutInS -= 100
                # resultMsg = WSSobj.SerialRead()

        resultMsg = WSSobj.SerialRead()
        retMsg += resultMsg
        print resultMsg
        while resultMsg != '*' and resultMsg.find('No Reading') == -1:
            resultMsg = WSSobj.SerialRead()
            retMsg += resultMsg
            print resultMsg
        if retMsg.find('Server closed connection') == -1:
            UnexpectedError = False
        else:
            UnexpectedError = True
            print 'Resend Command in Text Mode'
            retMsg = ''
            continue

    if retMsg.find('Pass = 1') == -1:
        if spiFwtFlag == True and retMsg.find('actual=0x00000003') != -1:
            result = 'spiFWT VER'
            msg = 'spiFWT VER Error - running test file ' + fileToTransfer + ' failed! '
            print msg
        else:
            result = False
            msg = 'Error - running test file ' + fileToTransfer + ' failed! '
            print msg
            TestInfo.ResultMessage += msg
    return result


def SPIPrepareFWTransfer(filePath, size, offset=0, expectFailure=None, offsetInFile=None, spiFWTTransferBlockSize=None):
    if offsetInFile is None:
        offsetInFile = offset
    if spiFWTTransferBlockSize is None:
        spiFWTTransferBlockSize = 0

    result = '#------ spiFWT offset=%s offsetInFile=%s, size=%s\n' % (offset, offsetInFile, size)

    # if size < (1024 * 5) and spiFWTTransferBlockSize <= 0 and not sendViaUserDefinedBuffer:
    # if spiFWTTransferBlockSize and spiFWTTransferBlockSize > (1024 * 5):
    # raise RuntimeError('this caes is not yet implemented')

    # fin = open(filePath, 'rb')
    # fin.seek(offsetInFile)
    # fileData = fin.read(size)
    # fin.close()

    # bytesListFromFile = []
    # for ch in fileData:
    # bytesListFromFile.append(ord(ch))

    # dataToSend = self.utils.WordsToBytes(wordsList = [offset], wordLengthInBits = 32)
    # dataToSend.extend(bytesListFromFile)
    # result += self.SPI_GenerateCmd(opCode = self.cmd.spiFWT, sequenceNumber = sequenceNumber, data = dataToSend, expectFailure = expectFailure, length = length, lengthAdjust = lengthAdjust, crc1 = crc1, crcAdjust1 = crcAdjust1, crc2 = crc2, crcAdjust2 = crcAdjust2, waitForCommandToFinish = waitForCommandToFinish)
    # else:
    if spiFWTTransferBlockSize < size and spiFWTTransferBlockSize > 0:

        """
        We are sending firmware in multiple parts - with multiple spiFWT commands!
        For each chunk of firmware file:
            Call SPIPrepareFWTransfer with spiFWTTransferBlockSize = 0 (it's a recursive call to Algorithm SPIPrepareFWTransfer 1.1)
        """
        offsetX = offset
        lengthX = 0

        dx = int(size / spiFWTTransferBlockSize)
        lastBlockSize = size % spiFWTTransferBlockSize

        result += '# Total blocks to transfer - %s of size(%s)' % (dx, spiFWTTransferBlockSize)
        if lastBlockSize > 0:
            result += ', 1 of size(%s)' % (lastBlockSize)
        result += '\n'

        offsetInFileX = offsetInFile
        lengthX = spiFWTTransferBlockSize
        for i in range(dx):
            result += SPIPrepareFWTransfer(filePath=filePath, size=lengthX, offset=offsetX, offsetInFile=offsetInFileX,
                                           spiFWTTransferBlockSize=0)
            offsetX += lengthX
            offsetInFileX += lengthX

        lengthX = lastBlockSize
        if lastBlockSize > 0:
            result += SPIPrepareFWTransfer(filePath=filePath, size=lengthX, offset=offsetX, offsetInFile=offsetInFileX,
                                           spiFWTTransferBlockSize=0)
            offsetX += lengthX
    else:
        """
        Algorithm PrepareFWTransfer 1.1

        We are sending the whole firmware in one go!
        For optimization reasons we will use a temp buffer in Test Driver memory and construct FWT SPI packet in that buffer
        We need to do here everything what SPI_GenerateCmd() do

        Create packet in a user defined buffer in Test Driver memory

        IF there are no user defined buffers THEN
            Create a new buffer

        Write header to buffer
        Copy firmware data from firmware file to user buffer
        Write crc2 to buffer

        """
        if expectFailure is None:
            expectFailure = 'OK'

        result += '#----------T>NEWBFR 1 %d\n' % (1024 * 1024 * 10)
        result += 'T>NEWBFR 1 %d\n' % (1024 * 1024 * 10)

        """
        Assemble packet
        FWT packet consists of 3 parts:
            Magic + Length + SeqNo + OpCode + Crc1 + offset +      ...data...    +     Crc2
                         PART 1                                      PART 2           PART 3
        """
        seqWord = GetSeqNo()
        opCode = SPICmdOpCode.spiFWT

        """
        Prepare and write FWT packet PART 1 to user defined buffer
        """
        length = 7 * 4 + size  # 6 32bit words plus firmware data (in bytes)

        fwtPacketPart1 = [ReplyReg.SPIMAGIC_VAL, length, seqWord, opCode]

        crc1 = SPICrc(WordsToBytes(fwtPacketPart1))

        fwtPacketPart1.append(crc1)
        fwtPacketPart1.append(offset)
        result += '#----------T>WBFR 1 0x%X %s\n' % (0, BytesListToString(WordsToBytes(fwtPacketPart1)))  # write part 1
        result += 'T>WBFR 1 0x%X %s\n' % (0, BytesListToString(WordsToBytes(fwtPacketPart1)))  # write part 1

        """
        Prepare and write FWT packet PART 2 - Copy firmware data from firmware buffer to user defined buffer
        """
        userBufferOffset = 6 * 4
        if size > 0:
            result += '#----------T>COPYF2X 1 %d 1 %d %d\n' % (offsetInFile, userBufferOffset, size)
            result += 'T>COPYF2X 1 %d 1 %d %d\n' % (offsetInFile, userBufferOffset, size)
            userBufferOffset += size

        """
        Prepare and write FWT packet PART 3 to user defined buffer
        """
        tempPacketBytes = WordsToBytes(fwtPacketPart1)
        if size > 0:
            fin = open(filePath, 'rb')
            fin.seek(offsetInFile)
            fileData = fin.read(size)
            fin.close()

            bytesListFromFile = []
            for ch in fileData:
                bytesListFromFile.append(ord(ch))

            tempPacketBytes.extend(bytesListFromFile)

        crc2 = SPICrc(tempPacketBytes)

        fwt_packet_part3 = WordsToBytes([crc2])
        result += '#----------T>WBFR 1 0x%X %s\n' % (
        userBufferOffset, BytesListToString(fwt_packet_part3))  # write part 3
        result += 'T>WBFR 1 0x%X %s\n' % (userBufferOffset, BytesListToString(fwt_packet_part3))  # write part 3

        """
        User buffer now contains a valid FWT SPI packet containing - part 1 + firmware image +  part 3
        Send packet from user buffer to UUT over SPI
        """
        totalLength = userBufferOffset + 4
        result += '#----------T>SENDX 2 1 0x%04X 0x%04X\n' % (0, totalLength)
        result += 'T>SENDX 2 1 0x%04X 0x%04X\n' % (0, totalLength)
        pollresult, pollcmd = SPIPoll(opCode=opCode, sequenceNumber=seqWord, expectedRet=expectFailure, sendCmd=False)
        result += '#----------' + pollcmd.replace('\n', '\n#----------', 1)
        result += pollcmd
        result += '#----------G<RD 1\n'
        result += 'G<RD 1\n'
        result += '#----------G<AL 1\n'
        result += 'G<AL 1\n'

    return result


def SPI_FirmwareTransfer(WSSobj, TestInfo, filePath, offset=0, offsetInFile=None, spiFWTTransferBlockSize=None):
    libpath = os.path.dirname(os.path.abspath(__file__))
    txtTemplateFile = libpath + '\\..\\template\\Textfile\\texttpl_SPI.txt'
    txtPath = TestInfo.Variables['TxtPath']
    txtName = TestInfo.Variables['TCName'] + '_FWT_' + str(datetime.now().hour) + '_' + str(
        datetime.now().minute) + '_' + str(datetime.now().second) + '.txt'

    print 'text path: ' + txtPath
    if not os.path.exists(txtPath):
        os.makedirs(txtPath)
    txtRun = open(txtPath + '\\' + txtName, 'w')

    with open(txtTemplateFile) as openfileobject:
        for line in openfileobject:
            if line.find('key_TestData') >= 0:
                statinfo = os.stat(filePath)
                filesize = statinfo.st_size

                txtRun.write(SPIPrepareFWTransfer(filePath=filePath, size=filesize, offset=0,
                                                  spiFWTTransferBlockSize=spiFWTTransferBlockSize))
            else:
                txtRun.write(line)

    openfileobject.close()
    txtRun.close()
    spiFWTresult = SendRunTestFile(WSSobj=WSSobj, TestInfo=TestInfo, fileToTransfer=txtPath + '\\' + txtName,
                                   waitExeTimeInS=30, spiFwtFlag=True)
    while (spiFWTresult == 'spiFWT VER'):
        result = False
        while (result == False):
            result = UploadFirmware(WSSobj=WSSobj, filePath=filePath)
        spiFWTresult = SendRunTestFile(WSSobj=WSSobj, TestInfo=TestInfo, fileToTransfer=txtPath + '\\' + txtName,
                                       waitExeTimeInS=30, spiFwtFlag=True)
    return spiFWTresult


def SerialPrepareFWTransfer(WSSobj, filePath, TestInfo, size, offset=0, expectFailure=None, offsetInFile=None,
                            serialFWTTransferBlockSize=None, DWN=False):
    if offsetInFile is None:
        offsetInFile = offset
    if serialFWTTransferBlockSize is None:
        serialFWTTransferBlockSize = 0

    if serialFWTTransferBlockSize > size:
        raise Exception('Error - FWT transfer block size is greater than total size')

    if DWN == True and serialFWTTransferBlockSize > 0:
        raise Exception('Error - only one block firmware transfer allowed for DWN command')

    print 'serialFWT offset=%s offsetInFile=%s, size=%s\n' % (offset, offsetInFile, size)
    if serialFWTTransferBlockSize < size and serialFWTTransferBlockSize > 0:
        # Sending fw file in multiple blocks
        offsetX = offset
        lengthX = 0

        dx = int(size / serialFWTTransferBlockSize)
        lastBlockSize = size % serialFWTTransferBlockSize

        print 'Total blocks to transfer - %s of size(%s)' % (dx, serialFWTTransferBlockSize)
        if lastBlockSize > 0:
            print ', 1 of size(%s)' % (lastBlockSize)
        print '\n'

        offsetInFileX = offsetInFile
        lengthX = serialFWTTransferBlockSize
        for i in range(dx):
            SerialPrepareFWTransfer(WSSobj=WSSobj, TestInfo=TestInfo, filePath=filePath, size=lengthX, offset=offsetX,
                                    expectFailure=None, offsetInFile=offsetInFileX, serialFWTTransferBlockSize=0)
            offsetX += lengthX
            offsetInFileX += lengthX

        lengthX = lastBlockSize
        if lastBlockSize > 0:
            SerialPrepareFWTransfer(WSSobj=WSSobj, TestInfo=TestInfo, filePath=filePath, size=lengthX, offset=offsetX,
                                    expectFailure=expectFailure, offsetInFile=offsetInFileX,
                                    serialFWTTransferBlockSize=0)
            offsetX += lengthX

    else:
        if TestInfo.Variables['Product'] in ['HDSP', 'HDLP']:
            WSSQuery(WSSobj=WSSobj, WSScommand='FWT ' + str(offset) + ',' + str(size), TestInfo=TestInfo,
                     checkResponse=False)
        elif DWN == False:
            WSSQuery(WSSobj=WSSobj, WSScommand='FWT 1 ' + str(size) + ' ' + str(offset), TestInfo=TestInfo,
                     checkResponse=False)
        else:
            WSSQuery(WSSobj=WSSobj, WSScommand='DWN 1', TestInfo=TestInfo, checkResponse=False)
        fin = open(filePath, 'rb')
        fin.seek(offsetInFile)

        print 'START TRANSFER BLOCK...'
        i = 0
        while i < size:
            nextstr = fin.read(1)
            if not nextstr:
                break
            testarray = array.array('B', nextstr)
            y = Array[Byte](testarray)
            WSSobj.SerialWrite(y)
            i = i + 1
        fin.close()

        print 'FIRMWARE TRANSFER BLOCK END, ' + str(i) + ' bytes transferred'


def Serial_FirmwareTransfer(WSSobj, TestInfo, filePath, serialFWTTransferBlockSize=None, DWN=None):
    if DWN is None:
        DWN = False

    result = True
    if (TestInfo.Variables['Product'] in ['HDSP', 'HDLP']) and DWN == True:
        raise Exception('DWN is not supported for HD product.')
    # file = open(filePath, 'rb')
    # print 'Firmware file Name: ', file.name
    statinfo = os.stat(filePath)
    filesize = statinfo.st_size
    SerialPrepareFWTransfer(WSSobj=WSSobj, TestInfo=TestInfo, filePath=filePath, size=filesize,
                            serialFWTTransferBlockSize=serialFWTTransferBlockSize, DWN=DWN)

    print 'FIRMWARE TRANSFER END '
    if DWN == True:
        teststatus = WSSobj.SerialRead()
        timeout = 100
        print teststatus
        while teststatus != 'Ready' and timeout > 0:
            teststatus = WSSobj.SerialRead()
            print teststatus
            timeout -= 5
            time.sleep(5)

        if timeout == 0:
            result = False
            msg = 'Error: firmware download failed. Ready not found in return string'
            print msg
            TestInfo.ResultMessage += msg
    else:
        teststatus = WSSobj.SerialRead()
        timeout = 50
        print teststatus
        while teststatus != 'OK' and timeout > 0:
            teststatus = WSSobj.SerialRead()
            print teststatus
            timeout -= 5
            time.sleep(5)

        if timeout == 0:
            result = False
            msg = 'Error: firmware download failed. OK not found in return string'
            print msg
            TestInfo.ResultMessage += msg
    return result


def DPRAM_FirmwareTransfer(WSSobj, TestInfo, filePath, DPRAMFWTTransferBlockSize=None):
    if DPRAMFWTTransferBlockSize == None:
        DPRAMFWTTransferBlockSize = regs.DWP_DPRAM.FirmwareTransferBufferSize
    if DPRAMFWTTransferBlockSize > regs.DWP_DPRAM.FirmwareTransferBufferSize:
        raise Exception('Out of range transfer block size 0x%04X, Valid max size is 0x%04X' % (
        DPRAMFWTTransferBlockSize, regs.DWP_DPRAM.FirmwareTransferBufferSize))

    statinfo = os.stat(filePath)
    fileSize = statinfo.st_size
    # sizeHI = (fileSize >> 16) & 0xFFFF
    # sizeLO = fileSize & 0xFFFF

    commandStr = '#------ Start Firmware DWN\n'
    commandStr += DPRAM_GenerateCmd(WSSobj=WSSobj, Command='STARTFWD ' + str(fileSize), TestInfo=TestInfo,
                                    expectFailure=None)

    commandStr += DPRAMPrepareFWTransfer(WSSobj, TestInfo, filePath=filePath, size=fileSize, offset=0,
                                         DPRAMFWTTransferBlockSize=DPRAMFWTTransferBlockSize)

    return DPRAM_SendRunTextFile(WSSobj, TestInfo, 'FirmwareTransfer', commandStr, 60)


def DPRAMPrepareFWTransfer(WSSobj, TestInfo, filePath, size, offset=0, DPRAMFWTTransferBlockSize=None):
    if DPRAMFWTTransferBlockSize is None:
        DPRAMFWTTransferBlockSize = regs.DWP_DPRAM.DPRAMFWTTransferBlockSize

    fileCRC = calculateFileCRC(filePath)
    fileLength = Internal_GetFileLength(filePath)
    totalLen = 0
    offset = 0
    length = 0
    result = ''
    for chunk in Internal_readFileByChunks(filePath, regs.DWP_DPRAM.FirmwareTransferBufferSize * 2):
        length = len(chunk)
        result += '#-------------D>WMX 0x%X 1 %d %d\n' % (regs.DWP_DPRAM.FirmwareTransferBufferOffset, offset, length)
        result += 'D>WMX 0x%X 1 %d %d\n' % (regs.DWP_DPRAM.FirmwareTransferBufferOffset, offset, length)
        # -- If length is odd then add 1
        if (length % 2 == 1):
            length += 1
        result += DPRAMTransferBlock(WSSobj, TestInfo, length / 2)
        result += '#--------T>FLUSH\n'
        result += 'T>FLUSH\n'
        offset += length
        totalLen += length

    result += '#--------T>FLUSH\n'
    result += 'T>FLUSH\n'
    result += '#--------' + DPRAMVerifyMemory(regs.DWP_DPRAM.OverAllFileCRCHI, [(fileCRC & 0xFFFF0000) >> 16])
    result += DPRAMVerifyMemory(regs.DWP_DPRAM.OverAllFileCRCHI, [(fileCRC & 0xFFFF0000) >> 16])
    result += '#--------' + DPRAMVerifyMemory(regs.DWP_DPRAM.OverAllFileCRCLO, [(fileCRC & 0xFFFF)])
    result += DPRAMVerifyMemory(regs.DWP_DPRAM.OverAllFileCRCLO, [(fileCRC & 0xFFFF)])
    return result


def DPRAMVerifyMemory(offset, values):
    result = 'D>VM 0x%04X' % offset
    for aValue in values:
        result += ' 0x%04X' % (int(aValue) & 0xFFFF)
    result += '\n'
    return result


def DPRAMTransferBlock(WSSobj, TestInfo, XBytes):
    result = '#-- Xfer\n'
    result += DPRAM_GenerateCmd(WSSobj=WSSobj, Command='FWT ' + str(XBytes), TestInfo=TestInfo, expectFailure=None)
    return result


def Internal_readFileByChunks(filePath, chunkSize):
    fileObject = open(filePath, 'rb')
    while True:
        chunk = fileObject.read(chunkSize)
        if not chunk:
            break
        yield chunk
    fileObject.close()


def WSSFirmwareTransfer(WSSobj, TestInfo, filePath, offset=0, offsetInFile=None, transferBlockSize=None, DWN=None):
    if TestInfo.Variables['Interface'] == 'Serial':
        return Serial_FirmwareTransfer(WSSobj=WSSobj, TestInfo=TestInfo, filePath=filePath,
                                       serialFWTTransferBlockSize=transferBlockSize, DWN=DWN)
    elif TestInfo.Variables['Interface'] == 'Huawei_HD':
        return HuaweiFwUpgradePrepareAndTransfer(WSSobj=WSSobj, TestInfo=TestInfo, filePath=filePath)
    elif TestInfo.Variables['Interface'] == 'SPI':
        return SPI_FirmwareTransfer(WSSobj=WSSobj, TestInfo=TestInfo, filePath=filePath, offset=offset,
                                    offsetInFile=offsetInFile, spiFWTTransferBlockSize=transferBlockSize)
    elif TestInfo.Variables['Interface'] == 'DPRAM':
        return DPRAM_FirmwareTransfer(WSSobj=WSSobj, TestInfo=TestInfo, filePath=filePath,
                                      DPRAMFWTTransferBlockSize=transferBlockSize)
    else:
        raise Exception('Error - interface ' + TestInfo.Variables['Interface'] + ' not supported!')


def WSSVerifyFirmwareVersion(WSSobj, TestInfo, fwVersion):
    if TestInfo.Variables['Interface'] == 'Serial':
        return Serial_VerifyFirmwareVersion(WSSobj=WSSobj, TestInfo=TestInfo, fwVersion=fwVersion)
    if TestInfo.Variables['Interface'] == 'Huawei_HD':
        return Huawei_VerifyFirmwareVersion(WSSobj=WSSobj, TestInfo=TestInfo, fwVersion=fwVersion)
    elif TestInfo.Variables['Interface'] == 'SPI':
        return SPI_VerifyFirmwareVersion(WSSobj=WSSobj, TestInfo=TestInfo, fwVersion=fwVersion)
    elif TestInfo.Variables['Interface'] == 'DPRAM':
        return DPRAM_VerifyFirmwareVersion(WSSobj=WSSobj, TestInfo=TestInfo, fwVersion=fwVersion)
    elif TestInfo.Variables['Interface'] == 'Nokia_HD':
        return Nokia_VerifyFirmwareVersion(WSSobj=WSSobj, TestInfo=TestInfo, fwVersion=fwVersion)
    else:
        raise Exception('Error - interface ' + TestInfo.Variables['Interface'] + ' not supported!')


def Serial_VerifyFirmwareVersion(WSSobj, TestInfo, fwVersion):
    return Serial_GenerateCmd(WSSobj=WSSobj, TestInfo=TestInfo, Command='FWR?', response=fwVersion)


def SPI_VerifyFirmwareVersion(WSSobj, TestInfo, fwVersion):
    print 'Verify Firmware Version ' + fwVersion
    result = SPI_GenerateCmd(WSSobj=WSSobj, Cmd='FWR?', TestInfo=TestInfo)

    x, y, z, rc = Parse_VersionString(fwVersion)

    if x is None:
        x = 0
    if y is None:
        y = 0
    if z is None:
        z = 0
    if rc is None:
        rc = 0

    result = VerifyMemory(offset=ReplyReg.SPIDATA, wordsList=[x, y, z, rc], wordLengthInBytes=1) and result
    return result


def DPRAM_VerifyFirmwareVersion(WSSobj, TestInfo, fwVersion):
    print 'Verify Firmware Version ' + fwVersion
    [major, minor, patch, rc] = Parse_VersionString(fwVersion)
    if major is None:
        major = 0
    if minor is None:
        minor = 0
    if patch is None:
        patch = 0
    if rc is None:
        rc = 0
    HighWord = ((major << 8) | minor)
    LowWord = ((patch << 8) | rc)
    result = '#------ VerifyFirmwareVersion\n'
    result += '#------ D>VM 0x%04X 0x%04X\n' % (regs.DWP_DPRAM.FirmwareVersionHigh, HighWord)
    result += 'D>VM 0x%04X 0x%04X\n' % (regs.DWP_DPRAM.FirmwareVersionHigh, HighWord)
    result += '#------ D>VM 0x%04X 0x%04X\n' % (regs.DWP_DPRAM.FirmwareVersionLow, LowWord)
    result += 'D>VM 0x%04X 0x%04X\n' % (regs.DWP_DPRAM.FirmwareVersionLow, LowWord)
    return DPRAM_SendRunTextFile(WSSobj, TestInfo, 'VerifyFWVer', result)


def Parse_VersionString(version):
    """
    Parse version string
    expected format x.y.z where x,y,z are numbers
    all components are optional

    Returns:
        tupple - (x,y,z,rc)
    """
    x = y = z = rc = None
    r1 = re.compile('(\d+)\.*(\d*)\.*(\d*)(_rc)*(\d*)')
    m = r1.match(version)
    if m:
        if (len(m.groups())) > 0:
            try:
                x = int(m.groups()[0])
                y = int(m.groups()[1])
                z = int(m.groups()[2])
                rc = int(m.groups()[4])
            except ValueError:
                pass
    return (x, y, z, rc)


def UploadFirmware(WSSobj, filePath):
    result = False
    statinfo = os.stat(filePath)
    size = statinfo.st_size
    retString = WSSobj.SerialQuery('\rupload firmware\r' + str(size))
    print retString
    expectRet = 'Transfer Firmware 1 in Binary'
    if retString.find(expectRet) > 0:
        print 'We are ready to send the file now!!!'

    temp = 0
    flag = False
    while temp < 50:
        temp = temp + 1
        print temp
        retString = WSSobj.SerialRead()
        if retString.find('File Loaded successfully') >= 0:
            result = True
            print retString
            break
        elif flag == False:
            fileObject = open(filePath, 'rb')
            print 'START TRANSFER BLOCK...'
            i = 0
            while i < size:
                nextstr = fileObject.read(1)
                if not nextstr:
                    break
                testarray = array.array('B', nextstr)
                y = Array[Byte](testarray)
                WSSobj.SerialWrite(y)
                i = i + 1
            fileObject.close()
            flag = True
    return result


# Huawei Related Functions

# Huawei HDSP Variables
FMax = 4194304
FwUpgradePackeNumber = 0
bufferCount = 0
Firmwares = []
ReadyTimeout = 3
# CentralFrequency = [192100.00, 192300.00,192400.00,192500.00,193000.00,193100.00,193200.00,193300.00,193400.00,193500.00,193800.00,194200.00,194300.00,194500.00,194700.00,194900.00,195200.00,195300.00,195500.00,195800.00]
# SOURCEFREQUENCY = [192100.00, 192300.00,192400.00,192500.00,193000.00,193100.00,193200.00,193300.00,193400.00,193500.00,193800.00,194200.00,194300.00,194500.00,194700.00,194900.00,195200.00,195300.00,195500.00,195800.00]
IGNORE_BIT = 99


# WSSQuery - Interface: Huawei_HD
def Huawei_GenerateCheckSum(Command):
    # xor all bytes and subtract 1
    val = reduce(lambda a, b: a ^ b, map(ord, Command), 0) - 1
    val &= 0xFF
    CHK = ':CHK=' + str(val).zfill(5)
    return CHK


def Huawei_GenerateRetCheckSum(ret):
    RetCHK = ''
    if ret.find('{') > 0 or ret.find('.*') > 0:
        RetCHK = '{x}'
    else:
        RetCHK = Huawei_GenerateCheckSum(ret)
    return RetCHK


def Huawei_GenerateCmd_WithTXT(WSSobj, Command, TestInfo, ret=None, checkResponse=True):
    CmdSet = {'Serial': {'SEND': 'E>SEND', 'RECV': 'E<RECV', 'RECVREX': 'E<RECVREX', 'RECVMATCHANY': 'E<RECVMATCHANY'},
              'SPI': {'SEND': 'J>SEND', 'RECV': 'J<RECV', 'RECVREX': 'J<RECVREX', 'RECVMATCHANY': 'J<RECVMATCHANY'}
              }

    Mode = 'Serial'
    CmdCHK = RetCHK = ''
    if 'SPIMessage' in TestInfo.Variables and TestInfo.Variables['SPIMessage'] == 1:
        Mode = 'SPI'
    if 'CHK' in TestInfo.Variables and TestInfo.Variables['CHK'] == 1:
        CmdCHK = ':CHK=' + Huawei_GenerateCheckSum(Command + ':CHK=')
        # use '\n' when calculating checkSum, use '\\n' to output as string
        RetCHK = '\\nchk=' + Huawei_GenerateRetCheckSum(Ret + '\nchk')

    req = CmdSet[Mode]['SEND'] + Command + CmdCHK
    expectedResponse = ''
    result = True

    # Wait until WSS is ready
    if not checkResponse:
        return SendResult

    if ret is None:
        ret = 'OK'
    if ret == '':
        ret = 'OK'

    if ret is not None:
        if (type(ret).__name__ == 'str'):
            if ret == 'DISCARD_RESPONSE_PACKET':
                expectedResponse += CmdSet[Mode]['RECV'] + ' ' + '*'
            elif ret.find('{') > 0 or ret.find('.*') > 0:
                expectedResponse += CmdSet[Mode]['RECVREX'] + ' ' + ret + RetCHK
            else:
                expectedResponse += CmdSet[Mode]['RECV'] + ' ' + ret + RetCHK
        else:
            if (type(ret).__name__ == 'list'):
                expectedResponse += CmdSet[Mode]['RECVMATCHANY'] + ' '
                for s in ret:
                    expectedResponse += ' ' + s

    print req
    print expectedResponse

    libpath = os.path.dirname(os.path.abspath(__file__))
    txtTemplateFile = libpath + '\\..\\template\\Textfile\\tempcmd.txt'
    txtPath = TestInfo.Variables['TxtPath']
    txtName = 'Huawei_tempcmd' + '.txt'
    filePath = txtPath + '\\' + txtName

    if not os.path.exists(txtPath):
        os.makedirs(txtPath)
    txtRun = open(txtPath + '\\' + txtName, 'w')

    with open(txtTemplateFile) as openfileobject:
        for line in openfileobject:
            if line.find('key_TestData') >= 0:
                statinfo = os.stat(filePath)
                filesize = statinfo.st_size
                txtRun.write('#--------' + req)
                txtRun.write('\n')
                txtRun.write(req)
                txtRun.write('\n')
                txtRun.write('#--------' + expectedResponse)
                txtRun.write('\n')
                txtRun.write(expectedResponse)
                txtRun.write('\n')
            else:
                txtRun.write(line)

    openfileobject.close()
    txtRun.close()
    result = SendRunTestFile_HuaweiHD(WSSobj=WSSobj, TestInfo=TestInfo, fileToTransfer=txtPath + '\\' + txtName,
                                      waitExeTimeInS=1)

    if not result:
        msg = 'ERROR - WSS error, command ' + Command + ' expecting return ' + ret
        print msg
        TestInfo.ResultMessage += msg
        TestInfo.IsResultPass = False
    return result


def Huawei_GenerateCmd_WithRECV(WSSobj, Command, TestInfo, ret=None, checkResponse=True):
    req = 'E>SEND ' + Command
    expectedResponse = ''
    SendResult = True
    RecvResult = True

    retString = WSSobj.SerialQuery(req)
    print retString
    # Wait until WSS is ready
    if not checkResponse:
        return SendResult

    if retString.find('ms S') == -1:
        SendResult = False

    if ret is None:
        ret = 'OK'

    if ret is not None:
        if (type(ret).__name__ == 'str'):
            if ret == 'DISCARD_RESPONSE_PACKET':
                expectedResponse += 'E<RECV *'
            elif ret.find('{') > 0 or ret.find('.*') > 0:
                expectedResponse += 'E<RECVREX ' + ret
            else:
                expectedResponse += 'E<RECV ' + ret
        else:
            if (type(ret).__name__ == 'list'):
                expectedResponse += 'E<RECVMATCHANY'
                for s in expectedResponse:
                    expectedResponse += ' ' + s

    retString = WSSobj.SerialQuery(expectedResponse)
    print retString
    if retString.find('ms S') == -1:
        RecvResult = False

    result = SendResult & RecvResult
    if not result:
        msg = 'ERROR - WSS error, command ' + Command + ' expecting return ' + ret
        print msg
        TestInfo.ResultMessage += msg
        TestInfo.IsResultPass = False
    return result


def Huawei_GenerateCmd(WSSobj, Command, TestInfo, ret=None, checkResponse=True, ERECV=False, ETXT=False):
    if ERECV:
        return Huawei_GenerateCmd_WithRECV(WSSobj=WSSobj, Command=Command, TestInfo=TestInfo, ret=ret,
                                           checkResponse=checkResponse)
    if ETXT:
        return Huawei_GenerateCmd_WithTXT(WSSobj=WSSobj, Command=Command, TestInfo=TestInfo, ret=ret,
                                          checkResponse=checkResponse)

    req = 'E>SEND ' + Command
    expectedResponse = ''
    SendResult = True

    retString = WSSobj.SerialQuery(req)
    # Wait until WSS is ready
    if not checkResponse:
        return SendResult

    if retString.find('ms S') == -1:
        SendResult = False

    if ret is None:
        ret = 'OK'

    if retString.find(ret) == -1:
        SendResult = False

    print retString

    result = SendResult
    if not result:
        msg = 'ERROR - WSS error, command ' + Command + ' expecting return ' + ret
        print msg
        TestInfo.ResultMessage += msg
        TestInfo.IsResultPass = False
    return result


def Huawei_VerifyErrorCode(WSSobj, TestInfo, errorCodeID, bitsStr=None, objectValue=1):
    if bitsStr == None:
        bitsStr = ''
    mask = GetErrorCodeRegisterMask(errorCodeID)
    reg = GetErrorCodeRegisterForID(errorCodeID)
    bitPattern = GenerateBitPatternForRegister(mask, reg, bitsStr)
    cmdToSend = 'GET:ERRCODE.%s:ERRCODEID=%s' % (objectValue, errorCodeID)
    expectedResponse = 'errcodeid=%s\\nerrcode={%s}' % (errorCodeID, bitPattern)
    result = WSSQuery(WSSobj=WSSobj, WSScommand=cmdToSend, TestInfo=TestInfo, expectedRet=expectedResponse, ETXT=True)
    return result


def HuaweiVerifyStatus(WSSobj, TestInfo, bitsStr1='', bitsStr2='', bitsStr3='', bitsStr4=''):
    # Current recoverable error code register
    result = Huawei_VerifyErrorCode(WSSobj=WSSobj, TestInfo=TestInfo, errorCodeID=1, bitsStr=bitsStr1)
    # Latched recoverable error code register
    result = Huawei_VerifyErrorCode(WSSobj=WSSobj, TestInfo=TestInfo, errorCodeID=2, bitsStr=bitsStr2) and result
    # Current unrecoverable error code register
    result = Huawei_VerifyErrorCode(WSSobj=WSSobj, TestInfo=TestInfo, errorCodeID=3, bitsStr=bitsStr3) and result
    # Latched unrecoverable error code register
    result = Huawei_VerifyErrorCode(WSSobj=WSSobj, TestInfo=TestInfo, errorCodeID=4, bitsStr=bitsStr4) and result
    return result


def HuaweiVerifyOpticsReady(WSSobj, TestInfo, bitsStr='OpticsNotReadyBit:0'):
    result = True
    result = Huawei_VerifyErrorCode(WSSobj=WSSobj, TestInfo=TestInfo, errorCodeID=3, bitsStr=bitsStr) & result
    return result


def HuaweiWaitForOpticsReady(WSSobj, TestInfo, serialPollingTimeInMS=2000, timeoutInMS=20000):
    result = HuaweiVerifyOpticsReady(WSSobj=WSSobj, TestInfo=TestInfo)
    while (not result) and timeoutInMS > 0:
        time.sleep(serialPollingTimeInMS / 1000)
        timeoutInMS -= serialPollingTimeInMS
        result = HuaweiVerifyOpticsReady(WSSobj, TestInfo)
    if timeoutInMS <= 0:
        result = False
        msg = 'ERROR - Serial Wait for  Huawei HDSP optitcs ready status 0x00000000000000000000000000000000 + failed!'
        print msg
        TestInfo.ResultMessage += msg
    return result


# Firmware Related
def GetFwUpgradeState(WSSobj, TestInfo, state=None, expectFailure=None):
    if state is None and expectFailure is None:
        raise RuntimeError('Either state or expectFailure must be provided')

    cmdToSend = 'GET:FwUpgrade.1:STATE'
    expectedResponse = 'state:%s' % (state)
    if expectFailure is not None:
        expectedResponse = expectFailure
    result = WSSQuery(WSSobj=WSSobj, WSScommand=cmdToSend, TestInfo=TestInfo, expectedRet=expectedResponse,
                      checkResponse=True)
    return result


def GetFwUpgradeActiveBank(WSSobj, TestInfo, activeBank=None, expectFailure=None):
    if activeBank is None and expectFailure is None:
        raise RuntimeError('Either activeBank or expect Failure must be provided')

    cmdToSend = 'GET:FwUpgrade.1:ACTIVEBANK'
    expectedResponse = 'activebank:%s' % (activeBank)
    if expectFailure is not None:
        expectedResponse = expectFailure
    result = WSSQuery(WSSobj=WSSobj, WSScommand=cmdToSend, TestInfo=TestInfo, expectedRet=expectedResponse,
                      checkResponse=True)
    return result


def HuaweiFwUpgradePrepare(WSSobj, TestInfo, size, expectFailure=None):
    cmdToSend = 'E>SEND ACTION:FWUPGRADE.1:PREPARE:%s' % (str(size))
    expectedResponse = 'E>RECV OK'
    if expectFailure is not None:
        expectedResponse = 'R<RECV ' + expectFailure
    # result = WSSQuery(WSSobj = WSSobj, WSScommand = cmdToSend, TestInfo = TestInfo, expectedRet = expectedResponse, checkResponse = True)
    result = cmdToSend + '\n'
    result += expectedResponse + '\n'
    return result


def HuaweiFwUpgradeTransferBlocksFromFile(WSSobj, TestInfo, filePath, startingPacketNumber=None, offsetInFile=None,
                                          size=None, expectFailure=None, blockSize=None, sendBlocksInReverseOrder=False,
                                          forceSameIntermediateExpectFailure=False):
    global Firmwares
    if not (os.path.isfile(filePath)):
        print 'FwUpgradeTransferBlockFromFirmware: Error: File does not exist -', filePath
        sys.exit(1)

    def IndexOf(Firmwares, aFile):
        for i in range(0, len(Firmwares)):
            if Firmwares[i] == aFile:
                return i
        return -1

    index = IndexOf(Firmwares, filePath)
    if index == -1:
        Firmwares.append(filePath)
        index = len(Firmwares) - 1

    if blockSize is None:
        blockSize = 2 * 1024

    if startingPacketNumber is None:
        startingPacketNumber = 0

    if offsetInFile is None:
        offsetInFile = 0

    actualFileSize = GetFileSize(filePath)
    if size is None:
        size = actualFileSize
    else:
        if size > actualFileSize:
            raise RuntimeError('size - %s should be less than or equal to actualFileSize - %s' % (size, actualFileSize))

    global FwUpgradePackeNumber
    FwUpgradePackeNumber = startingPacketNumber
    cmdtxt = HuaweiFwUpgradeTransferBlocksFromFile_Internal(WSSobj=WSSobj, TestInfo=TestInfo, filePath=filePath,
                                                            size=size, offsetInFile=offsetInFile,
                                                            expectFailure=expectFailure, blockSize=blockSize,
                                                            sendBlocksInReverseOrder=sendBlocksInReverseOrder,
                                                            forceSameIntermediateExpectFailure=forceSameIntermediateExpectFailure)

    libpath = os.path.dirname(os.path.abspath(__file__))
    txtTemplateFile = libpath + '\\..\\template\\Textfile\\texttplHuawei_HDSP.txt'
    txtPath = TestInfo.Variables['TxtPath']
    txtName = TestInfo.Variables['TCName'] + '_HuaweiFWT_' + str(datetime.now().hour) + '_' + str(
        datetime.now().minute) + '_' + str(datetime.now().second) + '.txt'

    print 'text path: ' + txtPath
    if not os.path.exists(txtPath):
        os.makedirs(txtPath)
    txtRun = open(txtPath + '\\' + txtName, 'w')

    with open(txtTemplateFile) as openfileobject:
        for line in openfileobject:
            if line.find('key_TestData') >= 0:
                statinfo = os.stat(filePath)
                filesize = statinfo.st_size
                prepareString = HuaweiFwUpgradePrepare(WSSobj=WSSobj, TestInfo=TestInfo, size=size)
                txtRun.write(prepareString)
                txtRun.write(cmdtxt)
            else:
                txtRun.write(line)

    openfileobject.close()
    txtRun.close()
    result = SendRunTestFile(WSSobj=WSSobj, TestInfo=TestInfo, fileToTransfer=txtPath + '\\' + txtName,
                             waitExeTimeInS=30)
    return result


def HuaweiFwUpgradeTransferBlocksFromFile_Internal(WSSobj, TestInfo, filePath, size, offsetInFile, blockSize,
                                                   expectFailure=None, sendBlocksInReverseOrder=False,
                                                   forceSameIntermediateExpectFailure=False):
    msg = ''
    cmdtxt = ''
    result = True
    global FwUpgradePackeNumber
    if size <= 20 and blockSize <= 0:
        """
        IF is a small block and blockSize is zero then
        send it inline using T>SEND
        """
        msg += '#------ FwUpgradeTransferBlocksFromFile--Alpha offsetInFile=%s, size=%s\n' % (offsetInFile, size)
        cmdtxt += msg
        with open(filePath, 'rb') as fin:
            fin.seek(offsetInFile)
            fileData = fin.read(size)

        fin.close()
        startByte = 0x3
        endByte = 0x4
        dataToSend = [startByte]

        # Packet format - 0x3 <2 bytes packet_no> <FWBytes> 0x4
        # packetNumber - 2 byte binary number
        packetNumber = FwUpgradePackeNumber
        tempBytesList = WordsToBytes(wordsList=[packetNumber], littleEndian=False, wordLengthInBits=16)
        dataToSend.extend(tempBytesList)
        FwUpgradePackeNumber += 1

        # FWBytes - represents the bytes of the firmware image.
        bytesListFromFile = []
        for ch in fileData:
            bytesListFromFile.append(ord(ch))
        dataToSend.extend(bytesListFromFile)
        dataToSend.append(endByte)

        packet_string = BytesListToString(dataToSend)
        cmdToSend = SendBinaryData(packet_string)
        expectedResponse = 'OK'
        if expectFailure is not None:
            expectedResponse = '%s' % (expectFailure)
        cmdtxt += cmdToSend + '\n' + expectedResponse + '\n'
        # result = Serial_GenerateCmd(WSSobj = WSSobj, Command = cmdToSend, ret = expectedResponse, TestInfo = TestInfo, checkResponse = True) & result
    else:
        if blockSize > 0:
            if size <= blockSize:
                """
                This can be send in one shot because size <= blockSize
                Either directly using T>SEND if its a small packet or using User Defined Buffer in Test Driver
                """
                offsetInFileX = offsetInFile
                lengthX = size
                msg = '#------ FwUpgradeTransferBlocksFromFile--Omega offsetInFile=%s, size=%s, blockSize=%s\n' % (
                offsetInFile, size, blockSize)
                # print msg
                cmdtxt += msg
                msg = HuaweiFwUpgradeTransferBlocksFromFile_Internal(WSSobj=WSSobj, TestInfo=TestInfo,
                                                                     filePath=filePath, size=lengthX,
                                                                     offsetInFile=offsetInFileX, blockSize=0,
                                                                     expectFailure=expectFailure)
                cmdtxt += msg
            else:
                """
                We are sending firmware in multiple parts - with multiple download commands!
                For each chunk of firmware file:
                    Call this function with blockSize = 0
                    All intermediate packets will be send using User Defined Buffer in Test Driver (it's a recursive call to Algorithm Firmware Download 1.1)
                    and last packet might be send directly using T>SEND if its a small packet
                """
                msg = '#------ FwUpgradeTransferBlocksFromFile--Recurse offsetInFile=%s, size=%s, blockSize=%s\n' % (
                offsetInFile, size, blockSize)
                dx = int(size / blockSize)
                lastBlockSize = size % blockSize

                msg += '# Total blocks to transfer - %s of size(%s)' % (dx, blockSize)

                if lastBlockSize > 0:
                    msg += ', 1 of size(%s)' % (lastBlockSize)
                msg += '\n'
                # print msg
                cmdtxt += msg

                offsetInFileX = offsetInFile
                lengthX = blockSize
                fwtBlocksQueue = []

                for i in range(dx):
                    args = {
                        'lengthX': lengthX,
                        'offsetInFileX': offsetInFileX,
                    }
                    fwtBlocksQueue.append(args)
                    offsetInFileX += lengthX

                if lastBlockSize > 0:
                    args = {
                        'lengthX': lastBlockSize,
                        'offsetInFileX': offsetInFileX,
                    }
                    fwtBlocksQueue.append(args)

                if sendBlocksInReverseOrder:
                    fwtBlocksQueue.reverse()

                # Send FWT blocks one by one from the queue - actual calls to FirmwareTransfer() algorithm 1.1
                while len(fwtBlocksQueue) > 0:
                    args = fwtBlocksQueue.pop(0)

                    """
                    Intermediate blocks vs Last block:
                    expectFailure:           for all intermediate blocks check OK, last block will have expectFailure as specified e.g. AER
                    """
                    if forceSameIntermediateExpectFailure is True:
                        tempExpectFailure = expectFailure
                    else:
                        tempExpectFailure = None

                    # this is last block
                    if len(fwtBlocksQueue) == 0:
                        tempExpectFailure = expectFailure

                    msg = HuaweiFwUpgradeTransferBlocksFromFile_Internal(WSSobj=WSSobj, TestInfo=TestInfo,
                                                                         filePath=filePath, size=args['lengthX'],
                                                                         offsetInFile=args['offsetInFileX'],
                                                                         blockSize=0, expectFailure=tempExpectFailure,
                                                                         forceSameIntermediateExpectFailure=forceSameIntermediateExpectFailure)
                    cmdtxt += msg
        else:  # if blockSize > 0:
            """
            Algorithm FirmwareTransfer 1.1

            We are sending the whole firmware in one go!
            For optimization reasons we will use a temp buffer in Test Driver memory and construct SPI packet in that buffer
            We need to do here everything here...

            Create packet in a user defined buffer in Test Driver memory

            IF there are no user defined buffers THEN
                Create a new buffer

            Write header to buffer
            Copy firmware data from firmware file to user buffer
            Write endByte to buffer
            """
            msg = '#------ FwUpgradeTransferBlocksFromFile--Bottom offsetInFile=%s, size=%s\n' % (offsetInFile, size)
            # print msg
            cmdtxt += msg
            if expectFailure is None:
                expectFailure = 'OK'
            global bufferCount
            if bufferCount == 0:
                cmdToSend = CreateBuffer(
                    (FMax * 2) + 1000)  # allocate a large enough buffer for FWT test cases to play with boundary values
                cmdtxt += cmdToSend + '\n'
                # result = Serial_GenerateCmd(WSSobj = WSSobj, Command = cmdToSend, ret = 'ms S', TestInfo = TestInfo, checkResponse = True) & result
            """
            Assemble packet
            Packet format - 0x3 + <2 bytes packet_no> + ...<FWBytes>... + 0x4
            packetNumber - 2 byte binary number
            """
            startByte = 0x3
            endByte = 0x4

            """
            Prepare and write firmware download packet PART 1 to user defined buffer
            """
            dataToSend = [startByte]
            packetNumber = FwUpgradePackeNumber
            tempBytesList = WordsToBytes(wordsList=[packetNumber], littleEndian=False, wordLengthInBits=16)
            dataToSend.extend(tempBytesList)
            FwUpgradePackeNumber += 1

            fwtPacketPart1 = dataToSend
            cmdToSend = WriteToBuffer(0, BytesListToString(fwtPacketPart1))  # write part 1
            cmdtxt += cmdToSend + '\n'
            # result = Serial_GenerateCmd(WSSobj = WSSobj, Command = cmdToSend, ret = 'ms S', TestInfo = TestInfo, checkResponse = True) & result
            """
            Prepare and write <FWBytes> PART 2 - Copy firmware data from firmware buffer to user defined buffer
            """

            userBufferNumber = 1
            userBufferOffset = 3
            if size > 0:
                cmdToSend = CopyBinaryDataFromFirmware2Buffer(filePath, offsetInFile, userBufferNumber,
                                                              userBufferOffset, size)  # write part 2
                cmdtxt += cmdToSend + '\n'
                # result = Serial_GenerateCmd(WSSobj = WSSobj, Command = cmdToSend, ret = 'ms S', TestInfo = TestInfo, checkResponse = True) & result
                userBufferOffset += size

            cmdToSend = WriteToBuffer(userBufferOffset, BytesListToString([endByte]))  # write part 3
            cmdtxt += cmdToSend + '\n'
            # result = Serial_GenerateCmd(WSSobj = WSSobj, Command = cmdToSend, ret = 'ms S', TestInfo = TestInfo, checkResponse = True) & result
            """
            User buffer now contains a valid firmware download packet containing - part 1 + firmware image +  part 3
            Send packet from user buffer to UUT over Serial
            """
            totalLength = userBufferOffset + 1
            cmdToSend = SendBinaryDataFromBuffer(bufferNumber=userBufferNumber, offset=0, length=totalLength)
            expectedResponse = 'E<RECV OK'
            if expectFailure is not None and expectFailure != 'OK':
                expectedResponse = 'E<RECV %s' % (expectFailure)
            cmdtxt += cmdToSend + '\n' + expectedResponse + '\n'
            # result = Serial_GenerateCmd(WSSobj = WSSobj, Command = cmdToSend, ret = expectedResponse, TestInfo = TestInfo, checkResponse = True) & result

    return cmdtxt


def HuaweiFwUpgradeActivate(WSSobj, TestInfo, expectFailure=None):
    result = True
    cmdToSend = 'ACTION:FWUPGRADE.1:ACTIVATE'
    expectedResponse = 'OK'
    if expectFailure is not None:
        expectedResponse = expectFailure
    result = WSSQuery(WSSobj=WSSobj, WSScommand=cmdToSend, TestInfo=TestInfo, expectedRet=expectedResponse,
                      checkResponse=True) & result
    return result


def HuaweiFwUpgradeCommit(WSSobj, TestInfo, expectFailure=None):
    result = True
    cmdToSend = 'ACTION:FWUPGRADE.1:COMMIT'
    expectedResponse = 'OK'
    if expectFailure is not None:
        expectedResponse = expectFailure
    result = WSSQuery(WSSobj=WSSobj, WSScommand=cmdToSend, TestInfo=TestInfo, expectedRet=expectedResponse,
                      checkResponse=True) & result
    return result


def HuaweiFwUpgradeRevert(WSSobj, TestInfo, expectFailure=None):
    result = True
    cmdToSend = 'ACTION:FWUPGRADE.1:REVERT'
    expectedResponse = 'OK'
    if expectFailure is not None:
        expectedResponse = expectFailure
    result = WSSQuery(WSSobj=WSSobj, WSScommand=cmdToSend, TestInfo=TestInfo, expectedRet=expectedResponse,
                      checkResponse=True) & result
    return result


def HuaweiFwUpgradePrepareAndTransfer(WSSobj, TestInfo, filePath):
    result = True
    #   result = HuaweiFwUpgradePrepare(WSSobj = WSSobj, TestInfo= TestInfo,size = GetFileSize(filePath = filePath)) & result
    result = HuaweiFwUpgradeTransferBlocksFromFile(WSSobj=WSSobj, TestInfo=TestInfo, filePath=filePath) & result
    global bufferCount
    bufferCount = 0
    return result


def FwUpgradePrepareTransferActivateAndCommit(WSSobj, TestInfo, filePath):
    result = True
    result = HuaweiFwUpgradePrepare(WSSobj=WSSobj, TestInfo=TestInfo, size=GetFileSize(filePath=filePath)) & result
    result = HuaweiFwUpgradeTransferBlocksFromFile(WSSobj=WSSobj, TestInfo=TestInfo, filePath=filePath) & result
    result = HuaweiFwUpgradeActivate(WSSobj=WSSobj, TestInfo=TestInfo) & result
    # wait for ready
    Sleep(ReadyTimeout * 1000)
    result = HuaweiFwUpgradeCommit(WSSobj=WSSobj, TestInfo=TestInfo) & result
    return result


def Huawei_VerifyFirmwareVersion(WSSobj, TestInfo, fwVersion, idnID=1, expectFailure=None):
    result = True
    cmdToSend = 'GET:IDN.%s:FirmwareRelease' % (idnID)
    expectedResponse = 'firmwarerelease:%s' % (fwVersion)
    if expectFailure is not None:
        expectedResponse = expectFailure
    result = WSSQuery(WSSobj=WSSobj, WSScommand=cmdToSend, TestInfo=TestInfo, expectedRet=expectedResponse,
                      checkResponse=True) & result
    return result


# Switching ADD:CH
def AddChannel(channelRecords, randomAttributeOrder=True, randomUpperLowerCase=True, expectFailure=None):
    return AddChannel_Internal(channelRecords=channelRecords, randomAttributeOrder=randomAttributeOrder,
                               randomUpperLowerCase=randomUpperLowerCase, expectFailure=expectFailure,
                               randomlyCorruptAttributeLabels=False, randomlyCorruptAttributeValues=False,
                               randomlyCorruptDelimiters=False)


def AddChannel_Internal(channelRecords, randomAttributeOrder=True, randomUpperLowerCase=True, expectFailure=None,
                        randomlyCorruptAttributeLabels=False, randomlyCorruptAttributeValues=False,
                        randomlyCorruptDelimiters=False):
    """
    Generates the ADD:CH low level protocol text as per the channelRecord specified

    Arguments:
    channelRecord - channel Record is list of channel Record values with optional attributes in following format:
    [{'Module':module, 'Channel':c, 'CommonPort':cmp, 'AddDropPort':adp, 'FrequencyCenter':fc, 'Bandwidth':bw, 'Attenuation':att, 'Frequency1':f1, 'Frequency2':f2, 'SlotSize':currentSlotSize}, ...]

    example - [{'Attenuation': 3.133, 'AddDropPort': 1, 'Bandwidth': 18.750, 'Module': '2', 'Frequency': 192065.625, 'CommonPort': 2, 'Channel': 608}, ...]
    Note that frequency and bandwidth are in GHz

    Optional Arguments:
    randomAttributeOrder - default True, generates attributes in random order
    randomUpperLowerCase - default True, case labels for attributes will be picked randomly
    """
    attributeOrder = [
        'AddDropPort',
        'FrequencyCenter',
        'Bandwidth',
        'CommonPort',
        'Attenuation',
    ]
    attributeNameToLabel = {
        'AddDropPort': 'ADP',
        'FrequencyCenter': 'FC',
        'Bandwidth': 'BW',
        'CommonPort': 'CMP',
        'Attenuation': 'ATT',
    }
    attributeNameToFormatString = {
        'Module': '%s',
        'Channel': '%s',
        'AddDropPort': '%s',
        'FrequencyCenter': '%.7f',
        'Bandwidth': '%.7f',
        'CommonPort': '%s',
        'Attenuation': '%.7f',
    }

    if type(channelRecords).__name__ != 'list':
        raise RuntimeError('channelRecords should be a list of dictionaries (records), instead it is a %s' % (
        type(channelRecords).__name__))

    commandLABEL = 'ADD'
    if randomUpperLowerCase and self.FlipCoin():
        commandLABEL = commandLABEL.lower()
    result = ['%s:' % (commandLABEL)]

    # Generate attributes in random order
    if randomAttributeOrder:
        random.shuffle(attributeOrder)

    for aChnl in channelRecords:
        channelLABEL = 'CH'
        if randomUpperLowerCase and self.FlipCoin():
            channelLABEL = channelLABEL.lower()

        result.append('%s.%s.%s' % (channelLABEL, aChnl['Module'], aChnl['Channel']))
        for anAttribute in attributeOrder:
            if anAttribute in aChnl and aChnl[anAttribute] is not None:
                delimiterColon = ':'
                if randomlyCorruptDelimiters:
                    delimiterColon = self.MutateDelimiter(delimiterColon)

                attFormatStr = attributeNameToFormatString[anAttribute]
                if attFormatStr.find('f') > 0 and type(aChnl[anAttribute]).__name__ == 'str':
                    attFormatStr = '%s'
                formatString = delimiterColon + '%s=' + attFormatStr

                attributeLABEL = attributeNameToLabel[anAttribute]
                if randomUpperLowerCase and self.FlipCoin():
                    attributeLABEL = attributeLABEL.lower()
                if randomlyCorruptAttributeLabels:
                    attributeLABEL = self.MutateAttributeLabel(attributeLABEL)

                attributeLABELAndValue = formatString % (attributeLABEL, aChnl[anAttribute])

                if randomlyCorruptAttributeValues:
                    attributeLABELAndValue = self.MutateAttributeValue(attributeLABELAndValue)

                result.append(attributeLABELAndValue)

        delimiterSemiColon = ';'
        if randomlyCorruptDelimiters:
            delimiterSemiColon = self.MutateDelimiter(delimiterSemiColon)
        result.append(delimiterSemiColon)

    result = result[:-1]
    cmdToSend = ''.join(result)
    if expectFailure is None:
        response = 'OK'
    else:
        response = expectFailure
    result = WSSQuery(WSSobj=WSSobj, WSScommand=cmdToSend, TestInfo=TestInfo, expectedRet=expectedResponse,
                      checkResponse=True) & result
    return result


# Utils
def SwapBits8b(b):
    """
    Swap bits in a bytes
    e.g. 0x5C (0101 1100) will become 0x3A (0011 1010)

    Arguments:
        an 8-bit byte

    Returns:
        byte
    """
    r = 0
    for m1, m2 in (
    (0x80, 0x01), (0x40, 0x02), (0x20, 0x04), (0x10, 0x08), (0x01, 0x80), (0x02, 0x40), (0x04, 0x20), (0x08, 0x10)):
        if b & m1:
            r |= m2
    return r


def SendRunTestCmdFile(WSSobj, TestInfo, fileToTransfer, waitExeTimeInS=1):
    totalTimeOutInS = 10
    result = True
    if TestInfo.Variables['Interface'] == 'Serial':
        exitMsg = WSSobj.ExitUUT()
        if exitMsg.find('Error') >= 0:
            exitMsg = WSSobj.ExitUUT()
            if exitMsg.find('Error') >= 0:
                result = False
                msg = 'Error - exit uut mode failed!'
                print msg
                TestInfo.ResultMessage += msg
                return result

    statinfo = os.stat(fileToTransfer)
    filesize = statinfo.st_size
    retMsg = WSSobj.SerialQuery('\rupload testdata\r' + str(filesize))

    if retMsg.find('Transfer Test Data File in Binary') == -1:
        result = False
        msg = 'Error - transfer file error'
        print msg
        TestInfo.ResultMessage += msg
        return result

    TransferBinaryFile(WSSobj=WSSobj, TestInfo=TestInfo, fileToTransfer=fileToTransfer, printMsg=True)

    retMsg = WSSobj.SerialQuery('run')
    print retMsg
    time.sleep(waitExeTimeInS)
    resultMsg = ''
    totalTimeOutInS -= waitExeTimeInS
    readFlag = False
    while totalTimeOutInS > 0:
        resultMsg = WSSobj.SerialRead()
        while resultMsg.find('No Reading') == -1:
            retMsg += resultMsg
            resultMsg = WSSobj.SerialRead()
            print resultMsg
            retMsg += resultMsg
            readFlag = True
        if readFlag:
            break
        time.sleep(1)
        totalTimeOutInS -= 1

    if retMsg.find('Pass = 1') == -1:
        result = False
        msg = 'Error - running test file ' + fileToTransfer + ' failed! '
        print msg
        TestInfo.ResultMessage += msg

    return result


def GetFileSize(filePath):
    """
    Returns file size in bytes.

    Arguments:

    * filePath: file path on file system.
    """
    length = 0;
    fileObject = open(filePath, 'rb')
    allData = fileObject.read()
    length = len(allData)
    fileObject.close()
    return length;


def HuaweiAddChannel(WSSobj, channelList, TestInfo, HuaweiTestInfo, expectedRet=None, checkResponse=True, ERECV=False,
                     ETXT=True):
    """
    Send Huawei ADD:CH command
    Arguments:
        WSSobj : WSS object
        channelList : List of Dictionary of each channel.
            FC: channel center frequency in GHz, float
            BW: channel bandwidth in GHz, float
            MO: channel module number ,int
            CH: channel number, int
            ADP: channel add drop port, int
            CMP: channel common port, int
            ATT: channel attenuation, float
        TestInfo : OFT session info
            startF: Dictionary of WSS slot start frequency
            mode: WSS current session slot mode
            maxSlot: Dictionary of WSS max slot number
        expectedRet: expected return of add channel command
        checkResponse: whether need to check response of this command
        ERECV: send cmd and receive
        ETXT: send cmd in text
    Returns:
        Add Channel command execution status: true/false
    """
    addChnlStr = 'ADD:'
    for cp in channelList:
        cFC = AdjustFC(cp['FC'], cp['BW'], HuaweiTestInfo['startF'][HuaweiTestInfo['mode']], HuaweiTestInfo['mode'],
                       HuaweiTestInfo['maxSlot'][HuaweiTestInfo['mode']])
        addChnlStr += 'CH.%d.%d:ADP=%d:FC=%.7f:BW=%.7f' % (cp['MO'], cp['CH'], cp['ADP'], cFC, cp['BW'])
        if 'CMP' in cp:
            addChnlStr += ':CMP=%d' % cp['CMP']
        if 'ATT' in cp:
            addChnlStr += ':ATT=%.7f' % cp['ATT']
        addChnlStr += ';'
    addChnlStr = addChnlStr.rstrip(';')
    return WSSQuery(WSSobj=WSSobj, WSScommand=addChnlStr, TestInfo=TestInfo, expectedRet=expectedRet,
                    checkResponse=checkResponse, ERECV=ERECV, ETXT=ETXT)


def HuaweiSetChannel(WSSobj, channelList, TestInfo, HuaweiTestInfo, expectedRet=None, checkResponse=True, ERECV=False,
                     ETXT=True):
    """
    Send Huawei SET:CH command
    Arguments:
        WSSobj : WSS object
        channelList : List of Dictionary of each channel.
            MO: channel module number int
            CH: channel number int
            ADP: channel add drop port (optional) int
            CMP: channel common port (optional) int
            ATT: channel attenuation (optional) float
            F1: channel start frequency (optional) float
            F2: channel end frequency (optional) float
        TestInfo : OFT session info
            startF: Dictionary of WSS slot start frequency
            mode: WSS current session slot mode
            maxSlot: Dictionary of WSS max slot number
        expectedRet: expected return of add channel command
        checkResponse: whether need to check response of this command
        ERECV: send cmd and receive
        ETXT: send cmd in text
    Returns:
        set channel command execution status : true/false
    """
    setChnlStr = 'SET:'
    for cp in channelList:
        setChnlStr += 'CH.%d.%d' % (cp['MO'], cp['CH'])
        if 'CMP' in cp:
            setChnlStr += ':CMP=%d' % cp['CMP']
        if 'ADP' in cp:
            setChnlStr += ':ADP=%d' % cp['ADP']
        if 'ATT' in cp:
            setChnlStr += ':ATT=%.7f' % cp['ATT']
        if 'F1' in cp and 'F2' in cp:
            cF1, cF2 = AdjustF1F2(cp['F1'], cp['F2'], HuaweiTestInfo['startF'][HuaweiTestInfo['mode']],
                                  HuaweiTestInfo['mode'], HuaweiTestInfo['maxSlot'][HuaweiTestInfo['mode']])
            setChnlStr += ':F1=%.7f:F2=%.7f' % (cF1, cF2)
        setChnlStr += ';'
    setChnlStr = setChnlStr.rstrip(';')
    return WSSQuery(WSSobj=WSSobj, WSScommand=setChnlStr, TestInfo=TestInfo, expectedRet=expectedRet,
                    checkResponse=checkResponse, ERECV=ERECV, ETXT=ETXT)


def AdjustFC(mFC, cBW, startF, mode, maxSlot):
    """
    Round module frequency to the nearest slot frequency of given bandwidth
    Arguments:
        mFC: module frequency, in GHz
        cBW: channel bandwidth, in GHz
        startF: start frequency of current slot mode, in Hz
        mode: current slot mode, in GHz
    Returns:
        Adjusted channel central frequency.
    """

    cF1, cF2 = AdjustF1F2(mFC - cBW / 2.0, mFC + cBW / 2.0, startF, mode, maxSlot)
    return (cF1 + cF2) / 2


def AdjustF1F2(cF1, cF2, startF, mode, maxSlot):
    """
    Round channel start and end frequency to the nearest slot edges
    Arguments:
        cF1: channel start frequency, in GHz
        cF2: channel end frequency, in GHz
        startF: start frequency of current slot mode, in Hz
        mode: current slot mode, in GHz
        maxSlot: max slot number in current slot mode.
    Returns:
        A tuple of adjusted channel start and end frequency.
    """
    cF1 *= int(pow(10, 9))  # convert from GHz to Hz
    cF2 *= int(pow(10, 9))  # convert from GHz to Hz
    cBW = cF2 - cF1  # convert from GHz to Hz
    mode *= pow(10, 9)  # convert from GHz to Hz
    startF -= mode / 2  # change from center to edge frequency
    # Case 1: invalid bandwidth - not multiples of mode
    if cBW % mode != 0:
        raise ValueError('Invalid bandwidth: %d for F1 %d and F2 %d' % (cBW, cF1 / pow(10, 9), cF2 / pow(10, 9)))

    diff = (cF1 - startF) % mode

    # Case 2: F1, F2 already on the edge
    if diff == 0: return (cF1 / float(pow(10, 9)), cF2 / float(pow(10, 9)))

    # Case 3: input frequency range smaller than slot range
    if cF1 < startF:
        if (cF2 - cF1) / 2 + cF1 < startF:
            raise ValueError('Invalid frequency: F1 %d and F2 %d out of WSS slots boundary' % (cF1, cF2))
        return (startF / float(pow(10, 9)), (startF + cBW) / float(pow(10, 9)))

    # Case 4: input frequency range greater than slot range
    if cF2 > startF + maxSlot * mode:
        if (cF2 - cF1) / 2 + cF1 > startF + maxSlot * mode:
            raise ValueError('Invalid frequency: F1 %d and F2 %d out of WSS slots boundary' % (cF1, cF2))
        return ((startF + maxSlot * mode - cBW) / float(pow(10, 9)), (startF + maxSlot * mode) / float(pow(10, 9)))

    # Case 5: round to nearest f
    cF1 = startF + mode * round((cF1 - startF) / mode)
    cF2 = startF + mode * round((cF2 - startF) / mode)

    return (cF1 / float(pow(10, 9)), cF2 / float(pow(10, 9)))


def GetErrorCodeRegisterMask(errorCodeID):
    errCodeRegMasks = [
        0xFFFFFFFF,
        0xFFFFFFFF,
        0xFFFFFFFF,
        0xFFFFFFFF
    ]
    return errCodeRegMasks[errorCodeID - 1]


def GetErrorCodeRegisterForID(errorCodeID):
    errRegs = [
        regs.Huawei_HDSP.ErrorCodeRegisterHardResetRecoverableCurrent,
        regs.Huawei_HDSP.ErrorCodeRegisterHardResetRecoverableLatch,
        regs.Huawei_HDSP.ErrorCodeRegisterHardResetUnrecoverableCurrent,
        regs.Huawei_HDSP.ErrorCodeRegisterHardResetUnrecoverableLatch
    ]
    return errRegs[errorCodeID - 1]


def GenerateBitPatternForRegister(regMask, register, bitsStr=None, wordLengthInBits=32):
    if bitsStr is None or len(bitsStr) <= 0:
        finalStr = CombineMaskWithBits(regMask, GenerateStatusBits(wordLengthInBits=wordLengthInBits),
                                       wordLengthInBits=wordLengthInBits)
    else:
        tempSym = ParseStatusBitSymbols(bitsStr)
        symBitsDict = SymbolicNamesToBitPos(register, tempSym)
        finalStr = CombineMaskWithBits(regMask, symBitsDict, wordLengthInBits=wordLengthInBits)
    return finalStr


def CombineMaskWithBits(mask, bitValues, wordLengthInBits=32):
    """
    Combines the bit mask with the actual bit values required

    Arguments:

    mask - a 16/32 bit mask e.g. 0x03CF
    bitValues - a dictionary with bit position and a value of 0 or 1 for that bit position, bit position range from 0-15 or 0-31

    Returns:

    a 16/32 character string with 0, 1 or x e.g. 'xxxxxx11x0001101'
    """
    result = ''

    if mask > (0xFFFF):
        wordLengthInBits = 32

    for i in range(0, wordLengthInBits):
        if not (mask & (1 << i)):
            result = 'x' + result
        else:
            try:
                if bitValues[i] == IGNORE_BIT:
                    result = 'x' + result
                elif bitValues[i] == 1:
                    result = '1' + result
                elif bitValues[i] == 0:
                    result = '0' + result
                else:
                    raise SyntaxError('Unknown bit value - %d for bitPos - %d' % (bitValues[i], i))
            except KeyError:
                result = '0' + result
    return result


def GenerateStatusBits(allOnes=False, wordLengthInBits=32):
    """
    Generate all zero or ones values for all 16/32 bits

    Returns:

    a dictionary with bit position and a value of 0 or 1 for all bit position, bit position range from 0-15 or 0-31
    """
    val = 0
    if allOnes:
        val = 1
    result = {}
    for i in range(0, wordLengthInBits):
        result[i] = val
    return result


def ParseStatusBitSymbols(bitsStr):
    """
    Parse the symbolic status bit names and return
    a dictionary containing key value pairs for each bit

    Arguments:

    bitsStr - a string containing bit names and values

    Example::

        ParseStatusBitSymbols('ReadyBit:1')
        ParseStatusBitSymbols('ReadyBit:1,StartBit:0')
    """
    rePattern = '([\w]*):(.*)'

    if not bitsStr or len(bitsStr) < 0:
        return None

    syms = bitsStr.split(',')
    result = {}
    for aSym in syms:
        match = re.search(rePattern, aSym.strip())
        if not match:
            raise ValueError(
                'ParseStatusBitSymbols - incorrect format, bitsStr = %s, Symbol mismatch = %s' % (bitsStr, aSym))
        bitKey = match.groups()[0].strip()
        try:
            if match.groups()[1].strip() == 'x':
                bitVal = IGNORE_BIT
            else:
                bitVal = int(match.groups()[1].strip())
                if bitVal < 0 or bitVal > 1:
                    raise ValueError(
                        'ParseStatusBitSymbols - incorrect format (bit value is incorrect expected values 0, 1 or x), "%s", actual value = %d' % (
                        bitsStr, bitVal))
        except ValueError:
            raise ValueError(
                'ParseStatusBitSymbols - incorrect format (bit value is incorrect expected values 0, 1 or x), "%s", actual value = %s' % (
                bitsStr, match.groups()[1].strip()))
        result[bitKey] = bitVal
    return result


def SymbolicNamesToBitPos(register, symDict):
    """
    Converts the symbolic names to actual bit positions number

    Arguments:

    register - register section in the INI file to look the definitions for e.g. StatusRegister (for DPRAM), OSSRegister (for serial)
    symDict - a dictionary with bit name (e.g. ReadyBit, VCOMControlBit) and a value of 0 or 1 for that bit

    Returns:

    a dictionary with bit position and a value of 0 or 1 for that bit position, bit position range from 0-15
    """
    result = {}
    for aSym in symDict.keys():
        keyPos = getattr(register, aSym)
        key = aSym
        val = symDict[aSym]
        result[keyPos] = val
    return result


def CreateBuffer(size, bufferNumber=1):
    """
    Creates a new user defined buffer in Test Driver memory.
    Buffer numbers start from 1.

    Arguments:
        size - size of buffer

    Optional Arguments:
        bufferNumber - buffer to write into, default is 1

    """
    result = 'T>NEWBFR %d %d' % (bufferNumber, size)
    global bufferCount
    bufferCount = bufferCount + 1

    return result


def WriteToBuffer(offset, dataString, bufferNumber=1):
    """
    Writes binary data into user defined buffer in Test Driver memory.
    Buffer numbers start from 1.

    Arguments:
        offset - offset in data buffer
        dataString - data values in hex or decimal format e.g. '0x0A 15 255 13 10'

    Optional Arguments:
        bufferNumber - buffer to write into, default is 1

    """
    global bufferCount
    if bufferNumber > bufferCount:
        raise RuntimeError('Invalid buffer number - %d, current bufferCount=%d' % (bufferNumber, bufferCount))
    result = 'T>WBFR %d 0x%X %s' % (bufferNumber, offset, dataString)
    return result


def CopyBinaryDataFromFirmware2Buffer(filePath, offsetInFirmware, bufferNumber, offsetInBuffer, length):
    """
    Copy binary data from a firmware file to a user defined buffer
    Use CreateBuffer() API to create a user defined buffer in Test Driver memory.
    Buffer numbers start from 1.

    Arguments:
        filePath - path to firmware file on PC
        offsetInFirmware - offset in firmware
        bufferNumber - which buffer to copy to
        offsetInBuffer - where to copy
        length - how many bytes to copy

    """
    global Firmwares

    def IndexOf(Firmwares, aFile):
        for i in range(0, len(Firmwares)):
            if Firmwares[i] == aFile:
                return i
        return -1

    index = IndexOf(Firmwares, filePath)
    if index == -1:
        Firmwares.append(filePath)
        index = len(Firmwares) - 1

    header = UploadFileToTestDriver(filePath, index + 1)
    cmd = header
    cmd += 'T>COPYF2X 1 %d %d %d %d' % (offsetInFirmware, bufferNumber, offsetInBuffer, length)
    return cmd


def SendBinaryDataFromBuffer(bufferNumber, offset, length, downloadViaSPI=False):
    """
    Send binary data from a user defined buffer to UUT via serial or SPI interface.
    Use CreateBuffer() API to create a user defined buffer in Test Driver memory.
    WriteToBuffer(), CopyBinaryDataFromFirmware2Buffer or CopyBinaryDataFromBuffer2Buffer() APIs to write
    data into user defined buffer.

    Buffer numbers start from 1.

    Arguments:
        bufferNumber - which buffer to send data from
        offset - where to send data from
        length - how many bytes to send

    Optional Arguments:
        downloadViaSPI - if true send data on SPI, default via serial

    """
    cmd = 'T>SENDX 1 '
    if downloadViaSPI:
        cmd = 'T>SENDX 2 '
    result = cmd + '%d 0x%04X 0x%04X' % (bufferNumber, offset, length)
    return result


def UploadFileToTestDriver(filePath, firmwareFileNumber):
    if not (os.path.isfile(filePath)):
        print 'DownloadFirmware: Error: File does not exist -', filePath
        sys.exit(1)
    result = '# DownloadFirmware FileOnPC="%s" FirmwareFileNumber=%s\n' % (filePath, firmwareFileNumber)
    return result


# NOKIA Related
def NokiaSerial_GenerateCmd(WSSobj, Command, TestInfo, Status=None, response=None, checkResponse=True, sendRECV=True,
                            byTXT=True, processCmd=True):
    if processCmd:
        # get command and data
        Cmd = Command.strip(' ')
        if Cmd.find(' ') >= 0:
            opIndex = Cmd.index(' ')
        else:
            opIndex = len(Cmd)

        opCodeStr = 'Nokia' + Cmd[:opIndex]
        # opCodeStr = opCodeStr.replace('?', '_Q')

        try:
            NokiaSerial_opCode = getattr(NokiaCmdCode, opCodeStr)
        except:
            NokiaSerial_opCode = 0xFF

        bytesToSend = [NokiaSerial_opCode]
        data = Cmd[opIndex:].strip(' ')

        print 'CMD sent: ' + Cmd
        if NokiaSerial_opCode == NokiaCmdCode.NokiaModifyChBW:
            # CH BW Data Format: ChangeChBW CH LowFrequencyInHz HighFrequencyInHz
            bytesToSend.extend(NokiaSerial_ParseChangeChBandwidthStr(data, TestInfo))
        elif NokiaSerial_opCode == NokiaCmdCode.NokiaUCA:
            # UCA Format: UCA C,P(1-20,51-70),A(0-255,>=250 is blk);C,P,A;
            bytesToSend.extend(NokiaSerial_ParseUCAStr(data, TestInfo))
        elif NokiaSerial_opCode == NokiaCmdCode.NokiaDCC:
            # DCC Format: DCC testPortBit(CP) C=LF:HF;C=LF:HF;
            bytesToSend.extend(NokiaSerial_ParseDCCStr(data, TestInfo))
        elif NokiaSerial_opCode in [NokiaCmdCode.Nokia0x13, NokiaCmdCode.Nokia0x21]:
            testPortBit = TestInfo.Variables['HDTestPort']
            DeviceID = TestInfo.Variables['DeviceID']
            WSSByte = (testPortBit << 7) + DeviceID
            bytesToSend.extend([0x00, 0x01, WSSByte])
        else:
            # testPortBit = TestInfo.Variables['HDTestPort']
            # DeviceID = TestInfo.Variables['DeviceID']
            # WSSByte = (testPortBit<<7) + DeviceID
            bytesToSend.extend([0x00, 0x00])

        cmdStrToSend = 'N>SEND ' + NokiaSerial_PrepareCMDStr(bytesToSend)
    else:
        cmdStrToSend = Command

    verifyStr = 'N<RECVSB '
    if Status is None or Status == 'Success':
        verifyStr += '00000000'
    # CRC16 Error
    elif Status == 'CRC-16 error':
        verifyStr += '00000001'
    # Syntax Error
    elif Status == 'syntax error':
        verifyStr += '00000010'
    if byTXT:
        PrepareTextFile(cmdStrToSend, verifyStr, TestInfo)
        result = SendRunTestFile(WSSobj=WSSobj, TestInfo=TestInfo,
                                 fileToTransfer=TestInfo.Variables['TxtPath'] + '\\tempcmd.txt', waitExeTimeInS=5)

        if not result:
            msg = 'ERROR - WSS error, command ' + Cmd + ' failed! '
            print msg
            TestInfo.ResultMessage += msg
            TestInfo.IsResultPass = False
        return result

    else:
        NokiaRet = WSSobj.SerialQuery(cmdStrToSend)
        print NokiaRet
        TestInfo.ResultMessage += NokiaRet
        if checkResponse and NokiaRet.find('ms S') == -1:
            result = False
            msg = 'ERROR - Nokia_HD command ' + str(hex(NokiaSerial_opCode)) + ' failed'
            print msg
            TestInfo.ResultMessage += msg
            return result

        if sendRECV:
            NokiaRet = WSSobj.SerialQuery(verifyStr)
            print NokiaRet
            if NokiaRet.find('ms S') == -1:
                result = False
                msg = 'ERROR - Nokia_HD command ' + str(hex(OpCode)) + ' verification failed'
                print msg
                TestInfo.ResultMessage += msg
                return result

    return True


def NokiaSerial_PrepareCMDStr(bytesToSend):
    crc16 = CalculateCRC16(bytesList=bytesToSend)
    bytesToSend.extend(WordsToBytes(wordsList=[crc16 & 0xFFFF], littleEndian=False, wordLengthInBits=16))
    return BytesListToString(bytesList=bytesToSend)


def NokiaSerial_ParseChangeChBandwidthStr(strChangeChBW, TestInfo):
    DataLength_High = 0x00
    DataLength_Low = 0x05
    OptionalData = strChangeChBW.split(' ')
    CH = int(OptionalData[0])
    bytesToSend = [DataLength_High, DataLength_Low, CH]
    bytesToSend.extend(
        WordsToBytes(wordsList=[int(OptionalData[1], 0) & 0xFFFF, int(OptionalData[2], 0) & 0xFFFF], littleEndian=False,
                     wordLengthInBits=16))
    testPortBit = TestInfo.Variables['HDTestPort']
    DeviceID = TestInfo.Variables['DeviceID']
    WSS = (testPortBit << 7) + DeviceID
    bytesToSend.extend([WSS])
    return bytesToSend


def NokiaSerial_ParseUCAStr(strUCA, TestInfo):
    testPortBit = TestInfo.Variables['HDTestPort']

    if not strUCA:
        raise Exception('Error : strUCA cannot be empty or None - %s')

    # remove last ';'
    if strUCA[-1] == ';':
        strUCA = strUCA[:-1]

    elements = strUCA.strip().split(';')
    dataLength = len(elements) * 3 + 1

    optionalData = WordsToBytes(wordsList=[dataLength & 0xFFFF], littleEndian=False, wordLengthInBits=16, )
    # fill in the port and attenuation arrays
    for anElement in elements:
        innerElements = anElement.strip().split(',')
        chnlNo = int(innerElements[0])
        port = int(innerElements[1])
        if TestInfo.Variables['HDTestPort']:
            port += 50
        attn = int(float(innerElements[2]) * 10)
        optionalData.extend([chnlNo, port, attn])

    DeviceID = TestInfo.Variables['DeviceID']
    WSS = (testPortBit << 7) + DeviceID
    optionalData.extend([WSS])

    return optionalData


def NokiaSerial_ParseDCCStr(strDCC, TestInfo):
    channelPlan = []

    if not strDCC:
        raise Exception('Error : strDCC cannot be empty or None - %s')

    # remove last ';'
    if strDCC[-1] == ';':
        strDCC = strDCC[:-1]

    elements = strDCC.strip().split(' ')
    testPortBit = TestInfo.Variables['HDTestPort']

    channelPlanStr = strDCC.strip().split(';')
    # dataLength = len(channelPlanStr)*4 +1

    # optionalData = WordsToBytes(wordsList=[dataLength & 0xFFFF], littleEndian = False, wordLengthInBits = 16)
    portFormatCheckCount = 0
    # generate channelPlan = [[chnlNo, HighFrequency in word,LowFrequency in word ],[]]

    for anElement in channelPlanStr:
        innerElements = anElement.strip().split('=')
        chnlNo = int(innerElements[0])
        FrequencyList = innerElements[1].strip().split(':')
        HighFrequency = int(round(int(FrequencyList[1]) * 62.5))
        LowFrequency = int(round((int(FrequencyList[0]) - 1) * 62.5))
        channelPlan.append([chnlNo, HighFrequency, LowFrequency])
    channelPlan.sort(key=lambda x: x[0])

    channelPlanByteList = []
    channelCount = 0
    for eachItem in channelPlan:
        channelNo = eachItem[0]
        for i in range(channelNo - channelCount - 1):
            channelPlanByteList.extend([0xFF] * 4)
        channelCount = channelNo
        frequencyByteList = WordsToBytes(wordsList=[eachItem[1] & 0xFFFF, eachItem[2] & 0xFFFF], littleEndian=False,
                                         wordLengthInBits=16)
        channelPlanByteList.extend(frequencyByteList)

    dataLength = len(channelPlanByteList) + 1
    optionalData = WordsToBytes(wordsList=[dataLength & 0xFFFF], littleEndian=False, wordLengthInBits=16)
    optionalData.extend(channelPlanByteList)

    DeviceID = TestInfo.Variables['DeviceID']
    WSSByte = (testPortBit << 7) + DeviceID
    optionalData.extend([WSSByte])

    return optionalData


def PrepareTextFile(cmdStrToSend, verifyStr, TestInfo):
    libpath = os.path.dirname(os.path.abspath(__file__))
    txtTemplateFile = libpath + '\\..\\template\\Textfile\\tempcmd.txt'
    txtPath = TestInfo.Variables['TxtPath']
    txtName = 'tempcmd.txt'
    filePath = txtPath + '\\' + txtName

    if not os.path.exists(txtPath):
        os.makedirs(txtPath)

    txtRun = open(txtPath + '\\' + txtName, 'w')

    with open(txtTemplateFile) as openfileobject:
        for line in openfileobject:
            if line.find('key_TestData') >= 0:
                statinfo = os.stat(filePath)
                filesize = statinfo.st_size
                txtRun.write('#--------' + cmdStrToSend)
                txtRun.write('\n')
                txtRun.write(cmdStrToSend)
                txtRun.write('\n')
                txtRun.write('#--------' + verifyStr)
                txtRun.write('\n')
                txtRun.write(verifyStr)
                txtRun.write('\n')
            else:
                txtRun.write(line)

    openfileobject.close()
    txtRun.close()


def NokiaSerialVerifyStatus(WSSobj, TestInfo, bitsStrOSS=0x001, bitsStrHSS=0x0000):
    result = True
    bitsStr1 = str(bin(bitsStrOSS))[2:]
    bitsStr1 = '0' * (8 - len(bitsStr1)) + bitsStr1
    bitsStr2 = str(bin(bitsStrHSS))[2:]
    bitsStr2 = '0' * (16 - len(bitsStr2)) + bitsStr2

    cmdStrToSend = 'N>SEND 0x22 0x0 0x0 0xA 0xA0'
    verifyStr = 'N<VBS 3 00000000' + bitsStr1 + bitsStr2

    PrepareTextFile(cmdStrToSend, verifyStr, TestInfo)
    result = SendRunTestFile(WSSobj=WSSobj, TestInfo=TestInfo,
                             fileToTransfer=TestInfo.Variables['TxtPath'] + '\\tempcmd.txt', waitExeTimeInS=5)

    if not result:
        msg = 'ERROR - WSS verify status failed! '
        print msg
        TestInfo.ResultMessage += msg
        TestInfo.IsResultPass = False
    return result


def NokiaSerialWaitForOSSReady(WSSobj, TestInfo, bitsStr=0x0001, NokiaserialPollingTimeInMS=2000, timeoutInMS=20000):
    result = True
    retString = WSSobj.SerialQuery(
        'N<WBS 0x22 3 00000000000000010000000000000000 ' + str(NokiaserialPollingTimeInMS) + ' ' + str(timeoutInMS))
    print retString
    if retString.find('ms S') == -1:
        result = False
        msg = 'Error - WSS command 0x22 wait for OSS ready failed.'
        print msg
        TestInfo.ResultMessage += msg
        return result
    return result


def CalculateCRC16(bytesList=None, binaryString=None):
    """
    CRC16 polynomial: 0x18005, bit reverse algorithm
    """
    table = [0x0000, 0xC0C1, 0xC181, 0x0140, 0xC301, 0x03C0, 0x0280, 0xC241, 0xC601, 0x06C0, 0x0780, 0xC741, 0x0500,
             0xC5C1, 0xC481, 0x0440, 0xCC01, 0x0CC0, 0x0D80, 0xCD41, 0x0F00, 0xCFC1, 0xCE81, 0x0E40, 0x0A00, 0xCAC1,
             0xCB81, 0x0B40, 0xC901, 0x09C0, 0x0880, 0xC841, 0xD801, 0x18C0, 0x1980, 0xD941, 0x1B00, 0xDBC1, 0xDA81,
             0x1A40, 0x1E00, 0xDEC1, 0xDF81, 0x1F40, 0xDD01, 0x1DC0, 0x1C80, 0xDC41, 0x1400, 0xD4C1, 0xD581, 0x1540,
             0xD701, 0x17C0, 0x1680, 0xD641, 0xD201, 0x12C0, 0x1380, 0xD341, 0x1100, 0xD1C1, 0xD081, 0x1040, 0xF001,
             0x30C0, 0x3180, 0xF141, 0x3300, 0xF3C1, 0xF281, 0x3240, 0x3600, 0xF6C1, 0xF781, 0x3740, 0xF501, 0x35C0,
             0x3480, 0xF441, 0x3C00, 0xFCC1, 0xFD81, 0x3D40, 0xFF01, 0x3FC0, 0x3E80, 0xFE41, 0xFA01, 0x3AC0, 0x3B80,
             0xFB41, 0x3900, 0xF9C1, 0xF881, 0x3840, 0x2800, 0xE8C1, 0xE981, 0x2940, 0xEB01, 0x2BC0, 0x2A80, 0xEA41,
             0xEE01, 0x2EC0, 0x2F80, 0xEF41, 0x2D00, 0xEDC1, 0xEC81, 0x2C40, 0xE401, 0x24C0, 0x2580, 0xE541, 0x2700,
             0xE7C1, 0xE681, 0x2640, 0x2200, 0xE2C1, 0xE381, 0x2340, 0xE101, 0x21C0, 0x2080, 0xE041, 0xA001, 0x60C0,
             0x6180, 0xA141, 0x6300, 0xA3C1, 0xA281, 0x6240, 0x6600, 0xA6C1, 0xA781, 0x6740, 0xA501, 0x65C0, 0x6480,
             0xA441, 0x6C00, 0xACC1, 0xAD81, 0x6D40, 0xAF01, 0x6FC0, 0x6E80, 0xAE41, 0xAA01, 0x6AC0, 0x6B80, 0xAB41,
             0x6900, 0xA9C1, 0xA881, 0x6840, 0x7800, 0xB8C1, 0xB981, 0x7940, 0xBB01, 0x7BC0, 0x7A80, 0xBA41, 0xBE01,
             0x7EC0, 0x7F80, 0xBF41, 0x7D00, 0xBDC1, 0xBC81, 0x7C40, 0xB401, 0x74C0, 0x7580, 0xB541, 0x7700, 0xB7C1,
             0xB681, 0x7640, 0x7200, 0xB2C1, 0xB381, 0x7340, 0xB101, 0x71C0, 0x7080, 0xB041, 0x5000, 0x90C1, 0x9181,
             0x5140, 0x9301, 0x53C0, 0x5280, 0x9241, 0x9601, 0x56C0, 0x5780, 0x9741, 0x5500, 0x95C1, 0x9481, 0x5440,
             0x9C01, 0x5CC0, 0x5D80, 0x9D41, 0x5F00, 0x9FC1, 0x9E81, 0x5E40, 0x5A00, 0x9AC1, 0x9B81, 0x5B40, 0x9901,
             0x59C0, 0x5880, 0x9841, 0x8801, 0x48C0, 0x4980, 0x8941, 0x4B00, 0x8BC1, 0x8A81, 0x4A40, 0x4E00, 0x8EC1,
             0x8F81, 0x4F40, 0x8D01, 0x4DC0, 0x4C80, 0x8C41, 0x4400, 0x84C1, 0x8581, 0x4540, 0x8701, 0x47C0, 0x4680,
             0x8641, 0x8201, 0x42C0, 0x4380, 0x8341, 0x4100, 0x81C1, 0x8081, 0x4040]

    if bytesList:
        pass
    elif binaryString:
        bytesList = map(ord, binaryString)
    else:
        raise RuntimeError("either bytesList or binaryString must be provided")

    crc = 0
    for abyte in bytesList:
        crc = table[abyte ^ (crc & 0xFF)] ^ (crc >> 8)

    return crc


def NokiaStartFirmwareLoading(WSSobj, TestInfo):
    print 'Nokia start firmware loading'
    cmdStrToSend = 'N>SEND 0x0C 0x00 0x00 0x03 0xC0'
    verifyStr = 'N<RECV 0x00 0x00 0x02 0x08 0x00 0x00 0xA6'
    PrepareTextFile(cmdStrToSend, verifyStr, TestInfo)
    result = SendRunTestFile(WSSobj=WSSobj, TestInfo=TestInfo,
                             fileToTransfer=TestInfo.Variables['TxtPath'] + '\\tempcmd.txt', waitExeTimeInS=5)
    if not result:
        msg = 'ERROR - WSS start firmware loading failed! '
        print msg
        TestInfo.ResultMessage += msg
        TestInfo.IsResultPass = False
    return result


def NokiaLoadNewFirmware(WSSobj, TestInfo, filePath):
    print 'Nokia load new firmware'
    # step 1 - upload file to test driver
    if not UploadFirmware(WSSobj, filePath):
        return False

    # step 2 - write firmware upload to txt
    libpath = os.path.dirname(os.path.abspath(__file__))
    txtTemplateFile = libpath + '\\..\\template\\Textfile\\tempcmd.txt'
    txtPath = TestInfo.Variables['TxtPath']
    txtName = TestInfo.Variables['TCName'] + '_NokiaFWUpgrade_' + str(datetime.now().hour) + '_' + str(
        datetime.now().minute) + '_' + str(datetime.now().second) + '.txt'
    print 'text path: ' + txtPath
    if not os.path.exists(txtPath):
        os.makedirs(txtPath)

    statinfo = os.stat(filePath)
    filesize = statinfo.st_size
    length = filesize
    offset = 0
    n = 1
    blocksize = 0x0800
    txt = "#------ LoadNewFirmware\n"
    while offset < length:
        txt += "#------ Sending block [%d] - offsetInFile = %d, size = %d\n" % (n, offset, blocksize)
        # print "Block:" + str(n)
        if offset + blocksize >= length:
            lastBlock = True
        txt += '#----------T>NEWBFR 1 %d\n' % (blocksize + 10)
        txt += 'T>NEWBFR 1 %d\n' % (blocksize + 10)
        packetP1 = [NokiaCmdCode.NokiaLoadNewFirmware]
        packetP1.extend(WordsToBytes(wordsList=[blocksize & 0xFFFF], wordLengthInBits=16, littleEndian=0))
        txt += '#----------T>WBFR 1 0x%X %s\n' % (0, BytesListToString(packetP1))
        txt += 'T>WBFR 1 0x%X %s\n' % (0, BytesListToString(packetP1))
        userBufferOffset = 3
        tempPacketBytesString = BytesListToBinaryString(bytesList=packetP1)
        zeros = []
        if length > 0:
            with open(filePath, "rb") as fin:
                fin.seek(offset)
                fileData = fin.read(blocksize)
                tempPacketBytesString += fileData
                blockLengthFromFile = len(fileData)

                if blockLengthFromFile > 0:
                    txt += '#----------T>COPYF2X 1 %d 1 %d %d\n' % (offset, userBufferOffset, blockLengthFromFile)
                    txt += 'T>COPYF2X 1 %d 1 %d %d\n' % (offset, userBufferOffset, blockLengthFromFile)
                    userBufferOffset += blockLengthFromFile

                if blockLengthFromFile < blocksize:
                    padCount = blocksize - blockLengthFromFile
                    tempStr = "s" if padCount > 1 else ""
                    txt += "# this is partial block padded with {0} zero{1}\n".format(padCount, tempStr)
                    zeros = [0] * (padCount)
                    txt += '#----------T>WBFR 1 0x%X %s\n' % (userBufferOffset, BytesListToString(zeros))
                    txt += 'T>WBFR 1 0x%X %s\n' % (userBufferOffset, BytesListToString(zeros))
                    tempPacketBytesString += BytesListToBinaryString(bytesList=zeros)
                    userBufferOffset += padCount

        tempCrc = CalculateCRC16(binaryString=tempPacketBytesString)
        packetP3 = WordsToBytes(wordsList=[tempCrc & 0xFFFF], wordLengthInBits=16, littleEndian=0)
        txt += '#----------T>WBFR 1 0x%X %s\n' % (userBufferOffset, BytesListToString(packetP3))
        txt += 'T>WBFR 1 0x%X %s\n' % (userBufferOffset, BytesListToString(packetP3))

        totalLength = userBufferOffset + 2
        txt += '#----------T>SENDX 1 1 0x%04X 0x%04X\n' % (0, totalLength)
        txt += 'T>SENDX 1 1 0x%04X 0x%04X\n' % (0, totalLength)

        # Verify Block by Block Transfer Result Here
        txt += 'N<RECV 0x00 0x00 0x00 0x00 0x00\n'

        n += 1
        offset += blocksize

    txtRun = open(txtPath + '\\' + txtName, 'w')
    # step 3 - run txt
    with open(txtTemplateFile) as openfileobject:
        for line in openfileobject:
            if line.find('key_TestData') >= 0:
                statinfo = os.stat(filePath)
                filesize = statinfo.st_size
                txtRun.write(txt)
            else:
                txtRun.write(line)

    openfileobject.close()
    txtRun.close()
    return SendRunTestFile(WSSobj=WSSobj, TestInfo=TestInfo, fileToTransfer=txtPath + '\\' + txtName, waitExeTimeInS=30,
                           spiFwtFlag=True)


def NokiaInstallFirmware(WSSobj, TestInfo):
    print 'Nokia Install Firmware'
    cmdStrToSend = 'N>SEND 0x0E 0x00 0x00 0xC3 0x61'
    verifyStr = 'N<RECVSB 00000000'
    PrepareTextFile(cmdStrToSend, verifyStr, TestInfo)
    return SendRunTestFile(WSSobj=WSSobj, TestInfo=TestInfo,
                           fileToTransfer=TestInfo.Variables['TxtPath'] + '\\tempcmd.txt', waitExeTimeInS=5)


def Nokia_VerifyFirmwareVersion(WSSobj, TestInfo, fwVersion):
    print 'Verify Firmware Version'
    cmdStrToSend = 'N>SEND 0x02 0x0 0x0 0xC0 0xA1'

    x, y, z, rc = Parse_VersionString(fwVersion)
    if x is None:
        x = 0
    if y is None:
        y = 0
    fwr = ((x << 4) & 0xF0) | (y & 0xF)

    verifyStr = 'N<VBS 4 ' + bin(fwr)[2:].zfill(8)

    PrepareTextFile(cmdStrToSend, verifyStr, TestInfo)
    return SendRunTestFile(WSSobj=WSSobj, TestInfo=TestInfo,
                           fileToTransfer=TestInfo.Variables['TxtPath'] + '\\tempcmd.txt', waitExeTimeInS=5)


def CalculateChecksum(data):
    # xor all bytes and subtract 1
    chk = reduce(lambda a, b: a ^ b, map(ord, data), 0) - 1
    chk &= 0xFF
    return chk


print Huawei_GenerateCheckSum("GET:PANEL.1:READY:CHK=")
print CalculateChecksum("GET:PANEL.1:READY:CHK=")