create database ask_mate_db
	with owner csaba
;

create table if not exists question
(
	id serial not null
		constraint pk_question_id
			primary key,
	submission_time timestamp default now(),
	view_number integer default 0,
	vote_number integer default 0,
	title text,
	message text,
	image text
)
;

alter table question owner to csaba
;

create table if not exists answer
(
	id serial not null
		constraint pk_answer_id
			primary key,
	submission_time timestamp default now(),
	vote_number integer default 0,
	question_id integer
		constraint fk_question_id
			references question
				on delete cascade,
	message text,
	image text
)
;

alter table answer owner to csaba
;

create table if not exists comment
(
	id serial not null
		constraint pk_comment_id
			primary key,
	question_id integer
		constraint fk_question_id
			references question,
	answer_id integer
		constraint fk_answer_id
			references answer,
	message text,
	submission_time timestamp,
	edited_count integer
)
;

alter table comment owner to csaba
;

create table if not exists tag
(
	id serial not null
		constraint pk_tag_id
			primary key,
	name text
)
;

alter table tag owner to csaba
;

create table if not exists question_tag
(
	question_id integer not null
		constraint fk_question_id
			references question,
	tag_id integer not null
		constraint fk_tag_id
			references tag,
	constraint pk_question_tag_id
		primary key (question_id, tag_id)
)
;

alter table question_tag owner to csaba
;

