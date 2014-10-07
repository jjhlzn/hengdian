# coding:UTF-8
from __future__ import division
from ..dbutils import *

AREA_TYPE_PROVINCE = 'province'
AREA_TYPE_CITY = 'city'

class NetworkOrderAreaReport:
    def __init__(self):
        pass
    def get_report(self, year, area_type, indicator,
                   is_real_sell_info = False, is_consider_return = False, topN = 9):
        filed_name = 'province'
        database = 'iccard14'
        if area_type == AREA_TYPE_CITY:
            filed_name = 'city'
        if year == '2013':
            database = 'iccard13'
        sql = """SELECT %s, COUNT(*) as order_count, SUM(DDjNumber) as people_count, cast(SUM(DAmount) as int) as total_money FROM (
                SELECT a.Sellid, DTel, a.DDjNumber, a.DAmount, (SELECT %s FROM report.dbo.t_phonenumber where phonenumber = SUBSTRING(DTel,0,8)) as %s
                FROM %s.dbo.v_tbdTravelOk a inner join %s.dbo.v_tbdTravelOkCustomer b on a.SellID = b.SellID
                WHERE a. Flag in (0,1) and
                exists(select * from %s.dbo.tbdGroupType b where a.DGroupType = b.DName and a.DGroupTypeAssort = b.sType and DGroupRoomType = '网络用房')
                and DComeDate >= '%s-1-1' and DComeDate <= '%s-12-31') as a
                GROUP BY %s
                order by total_money desc""" % (filed_name, filed_name, filed_name, database, database, database,  year, year, filed_name)
        print sql
        rows = get_rows_from_orders(sql)
        total = reduce(lambda x, y: x + y, map(lambda item: item[indicator], rows) )
        for row in rows:
            row['percent'] = "{0:.3f}".format(row[indicator] / total * 100) + '%'
            row['label'] = row[filed_name]
            row['value'] = row[indicator]
            if row['label'] is None:
                row['label'] = u'未知'

        colors = ['#659AC9', '#A0BFBE', '#ADC896', '#B58371', '#DA917A', '#BE98B7', '#8B814C', '#CD69C9', '#CDC673', '#EEE8CD',
                  '#CD919E', '#C1CDC1', '#8B8878', '#7F7F7F', '#607B8B', '#4682B4', '#8C8C8C']
        datasets = []
        other = {filed_name: '其他', 'order_count': 0, 'people_count': 0, 'total_money': 0, 'color': colors[-1]}

        index = 1

        for row in rows:
            province = row[filed_name]
            if index >  topN:
                other['order_count'] += row['order_count']
                other['people_count'] += row['people_count']
                other['total_money'] += row['total_money']
            else:
                row['color'] = colors[index-1]
                datasets.append(row)
            index += 1
        datasets.append(other)
        datasets = map(lambda(item): {  \
                        'value':  int(item[indicator]), \
                        'color':  item['color'], \
                        'highlight': item['color'], \
                        'label': item[filed_name] if  item[filed_name] is not None else u'未知'\
                     }, datasets)

        return [datasets, rows]