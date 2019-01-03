CREATE TABLE public.sessions
(
    session_id varchar NOT NULL,
    username varchar,
    create_date timestamp DEFAULT now()
);