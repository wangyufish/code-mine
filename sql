select count(*) from projects;
select count(*) from projects where forked_from is null;
select count(*) from users where location is not null;
select count(distinct name) from projects;
select * from projects where forked_from is null;
select * from (select forked_from, count(*) as count from ( select * from projects where forked_from is not null) as projectnotnull group by forked_from) as origin order by count desc; 
select * from projects where id = 79163;

select count(*) from users;
