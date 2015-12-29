select repo_id, count(*) as count from project_members group by repo_id order by count desc

select language, count(*) from projects where forked_from is null group by language

select * from projects where forked_from is null

select * from projects where language='C++' and forked_from is null

select * from (select forked_from, count(*) as count from ( select * from projects where forked_from is not null and language = 'C') as projectnotnull group by forked_from) as origin order by count desc; 

select * from projects order by created_at desc

select count(*) from commits

select * from projects where name='android' and forked_from is null

select * from commit_comments where ext_ref_id='4da86be29a349ab2c34052d4972ebb789117e09b'

select * from users where name='Jonathan Abrahams'

select * from commit_comments where locate('error', body)>0 or locate('bug', body)>0 or locate('fix', body)>0 or locate('issue', body)>0 or locate('mistake', body)>0 or locate('incorrent', body)>0 or locate('fault', body)>0 or locate('defect', body)>0 or locate('flow', body)>0
