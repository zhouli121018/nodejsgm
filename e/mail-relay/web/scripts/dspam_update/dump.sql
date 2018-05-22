COPY (select * from dspam_token_data where last_hit='datetime')
TO '/tmp/dspam.csv'
WITH csv;
