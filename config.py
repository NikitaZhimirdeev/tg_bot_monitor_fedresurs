from parser_web import PARSER

parser = PARSER()

URL = 'https://old.bankrot.fedresurs.ru/Messages.aspx'

COOKIE = [{
    '45': 'Messages=MessageNumber=&MessageType=AssessmentReport&IdRegion=',
    '46': 'Messages=MessageNumber=&MessageType=AssessmentReport&IdRegion=',
    },
    {
    '45': 'Messages=MessageNumber=&MessageType=Auction&IdRegion=',
    '46': 'Messages=MessageNumber=&MessageType=Auction&IdRegion=',
    },
    {
    '45': 'Messages=MessageNumber=&MessageType=SaleOrderPledgedProperty&IdRegion=',
    '46': 'Messages=MessageNumber=&MessageType=SaleOrderPledgedProperty&IdRegion=',
    }]

def HEADERS_def(bankrotcookie):
    HEADERS_defaulter = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
               'Cookie': f'bankrotcookie={bankrotcookie}'}

    return HEADERS_defaulter

def HEAD(mes, reg, bankrotcookie):
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
               'Cookie': '_ym_uid=1637760967890989625;'
                         '_ym_d=1637760967;'
                         'ASP.NET_SessionId=wla5f454rt1kwldtof3qljze;'
                         '_ym_isad=2;'
                         f'{mes}{reg};'
                         f'bankrotcookie={bankrotcookie};'
                         '_ym_visorc=w'}
    return HEADERS