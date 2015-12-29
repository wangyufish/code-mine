create table commits(commit_id int ,name varchar(20),email varchar(30),comment tinytext, changed_files tinytext)

insert into commits values('7c9cdb0882058924e9066a8f943109009d8b3bfc','Rod Vagg','rod@vagg.org','Thu Dec 24 13:34:59 2015','test: test each block in addon.md contains js & cc','tools/doc/addon-verify.js')

insert into commits values('7c9cdb0882058924e9066a8f943109009d8b3bfc', 'Rod Vagg', 'rod@vagg.org', 'Thu Dec 24 13:34:59 2015 +1100', 'test: test each block in addon.md contains js & cc  Allows more freedom in adding additional headings to addon.markdown, otherwise itll try and convert each block under a heading to a test case. We need to have at least a .js and a .cc in order to have something to test.  Fixes regression caused by adding a new 3rd-level heading in d5863bc0f43a3778aa773d5f5f4ad08e1d7d7497  PR-URL: https://github.com/nodejs/node/pull/4411 Reviewed-By: Myles Borins <myles.borins@gmail.com> ', 'tools/doc/addon-verify.js ')

insert into commits values('6f1d0a8a2f1514823cd856812407c87383aedee7', 'Kevin O Hara', 'kevinohara80@gmail.com', 'Tue Dec 2 22:17:17 2014 -0500', 'docs: reword project messaging  Rewords project messaging in README to make the overall project messaging a bit clearer. More discussion to be found in iojs/io.js#24.  PR-URL: https://github.com/iojs/io.js/pull/36 Reviewed-By: Ben Noordhuis <info@bnoordhuis.nl> Reviewed-By: Jeremiah Senkpiel <fishrock123@rocketmail.com> Reviewed-By: Rod Vagg <rod@vagg.org> ', 'README.md ')

select * from commits

truncate table commits

select * from commits where locate('error', comment)>0 or locate('bug', comment)>0 or locate('fix', comment)>0 or locate('issue', comment)>0 or locate('mistake', comment)>0 or locate('incorrent', comment)>0 or locate('fault', comment)>0 or locate('defect', comment)>0 or locate('flow', comment)>0