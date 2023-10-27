import pandas as pd
import time
from clickhouse_driver import Client

host = '172.19.11.188'
port = 9000
user = 'default'
password = 'akvorado@123'
database = 'akvorado'

sql_query = '''
SELECT *
FROM
(
    SELECT
        toStartOfMinute(TimeReceived) AS TimeReceived,
        DstAddr,
        SrcPort,
        dictGetOrDefault('protocols', 'name', Proto, '???') AS Proto,
        SUM(((((Bytes * SamplingRate) * 8) / 1000) / 1000) / 1000) / 60 AS Gbps,
        uniq(SrcAddr) AS sources,
        uniq(SrcCountry) AS countries
    FROM flows
    WHERE TimeReceived > (now() - toIntervalMinute(120))
    GROUP BY
        TimeReceived,
        DstAddr,
        SrcPort,
        Proto
)
WHERE (Gbps > 3.4) OR ((sources > 20) AND (Gbps > 2.5)) OR ((countries > 10) AND (Gbps > 2.5))
ORDER BY
    TimeReceived DESC,
    Gbps DESC
'''
client = Client(host=host, port=port, user=user, password=password, database=database)

while True:
    results = client.execute(sql_query)
    df = pd.DataFrame(results,columns =['Date and time' , 'IPadd' , 'Port' , 'Proto' , 'Gbps' , 'Sources' , 'Country' ])
    print(df)
    time.sleep(300)
    
