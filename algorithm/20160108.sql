CREATE TABLE commits (
    id bigint,
    repository_id bigint,
    blamed_commit_id bigint,
    type text,
    sha text,
    url text,
    author_email text,
    author_name text,
    author_when timestamp,
    committer_email text,
    committer_name text,
    committer_when timestamp,
    additions bigint,
    deletions bigint,
    total_changes bigint,
    past_changes bigint,
    future_changes bigint,
    past_different_authors bigint,
    future_different_authors bigint,
    author_contributions_percent double precision,
    message text,
    patch text,
    hunk_count bigint,
    cve text,
    files_changed bigint,
    patch_keywords text
);

CREATE TABLE repositories (
    id integer,
    name text,
    description text,
    pushed_at timestamp,
    created_at timestamp,
    updated_at timestamp,
    forks_count integer,
    stargazers_count integer,
    watchers_count integer,
    subscribers_count integer,
    open_issues_count integer,
    size integer,
    language text,
    default_branch text,
    git_url text,
    distinct_authors_count integer,
    commits_count integer
);


CREATE TABLE cves (
    id text,
    type text,
    published date,
    updated date,
    score real,
    gained_access_level text,
    access text,
    complexity text,
    authentication text,
    conf text,
    integ text,
    avail text,
    description text,
    vendor text
);

create table issues (
	id int,
	issue_id bigint,
	title varchar(255),
	name varchar(45),
	time datetime,
	content mediumtext,
	tag varchar(255),
	project varchar(45));
	
truncate table issues

select count(*) from issues

select comment from commits where changed_files != 'CHANGELOG.md'

git log --stat -U1 -w >/home/wangyu/code-mine/data/node_gitlog



