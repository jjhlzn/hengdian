# coding:UTF-8
from __future__ import division
from ..dbutils import *


colors = ['#659AC9', '#A0BFBE', '#ADC896', '#B58371', '#DA917A', '#BE98B7', '#8B814C', '#CD69C9', '#CDC673', '#EEE8CD',  #10
          '#CD919E', '#C1CDC1', '#8B8878', '#7F7F7F', '#607B8B', '#4682B4', '#C67171', '#C0FF3E', '#C5C1AA', '#B9D3EE'
        , '#8C8C8C']

class NetworkOrderAreaReport:
    AREA_TYPE_PROVINCE = 'province'
    AREA_TYPE_CITY = 'city'

    def __init__(self):
        pass
    def get_report(self, year, area_type, indicator,
                   is_real_sell_info = False, is_consider_return = False, topN = 9):

        field_name = 'province'
        database = "%s.iccard14" % ticket_server
        if area_type == self.AREA_TYPE_CITY:
            field_name = 'city'
        if year == '2013':
            database = "%s.iccard13" % ticket_server
        elif year == '2012':
            database = "%s.iccard12" % ticket_server

        sql = self.get_sql(year, field_name, database, indicator, is_real_sell_info, is_consider_return)

        rows = get_rows_from_orders(sql)
        total = reduce(lambda x, y: x + y, map(lambda item: item[indicator], rows) )

        for row in rows:
            row['percent'] = "{0:.3f}".format(row[indicator] / total * 100) + '%'
            row['label'] = row[field_name]
            row['value'] = row[indicator]
            if row['label'] is None:
                row['label'] = u'未知'

        datasets = []
        other = {field_name: '其他', 'order_count': 0, 'people_count': 0, 'total_money': 0, 'color': colors[-1]}
        index = 1

        for row in rows:
            province = row[field_name]
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
                        'label': item[field_name] if  item[field_name] is not None else u'未知'\
                     }, datasets)
        rows.append({'percent': '100%', 'label': '总和', 'value': total})
        return [datasets, rows]

    def get_sql(self, year, field_name, database, indicator, is_real_sell_info = False, is_consider_return  = False):
        if is_real_sell_info:
            sql = """SELECT %s, COUNT(*) as order_count, SUM(DDjNumber) as people_count, cast(SUM(DAmount) as int) as total_money FROM (
                    SELECT a.Sellid, DTel, c.DSjNumber as DDjNumber, (c.DSjAmount - c.DSjYhAmount) as DAmount, (SELECT %s FROM report.dbo.t_phonenumber where phonenumber = SUBSTRING(DTel,0,8)) as %s
                    FROM %s.dbo.v_tbdTravelOk a inner join %s.dbo.v_tbdTravelOkCustomer b on a.SellID = b.SellID
                    inner join %s.dbo.v_tbdTravelOkOther c on a.SellID = c.SellID
                    WHERE a. Flag = 1 and
                    exists(select * from %s.dbo.tbdGroupType b where a.DGroupType = b.DName and a.DGroupTypeAssort = b.sType and DGroupRoomType = '网络用房')
                    and DComeDate >= '%s-1-1' and DComeDate <= '%s-12-31') as a
                    GROUP BY %s
                    order by %s desc""" % (field_name, field_name, field_name, database, database, database, database,  year, year, field_name, indicator)
        else:
            sql = """SELECT %s, COUNT(*) as order_count, SUM(DDjNumber) as people_count, cast(SUM(DAmount) as int) as total_money FROM (
                    SELECT a.Sellid, DTel, a.DDjNumber, a.DAmount, (SELECT %s FROM report.dbo.t_phonenumber where phonenumber = SUBSTRING(DTel,0,8)) as %s
                    FROM %s.dbo.v_tbdTravelOk a inner join %s.dbo.v_tbdTravelOkCustomer b on a.SellID = b.SellID
                    WHERE a. Flag = 1 and
                    exists(select * from %s.dbo.tbdGroupType b where a.DGroupType = b.DName and a.DGroupTypeAssort = b.sType and DGroupRoomType = '网络用房')
                    and DComeDate >= '%s-1-1' and DComeDate <= '%s-12-31') as a
                    GROUP BY %s
                    order by %s desc""" % (field_name, field_name, field_name, database, database, database,  year, year, field_name, indicator)
        print sql
        return sql