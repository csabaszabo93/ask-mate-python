CREATE TABLE public.users
(
    id serial PRIMARY KEY NOT NULL,
    user_name varchar NOT NULL,
    password_hash varchar NOT NULL,
    salt varchar NOT NULL,
    date_of_registration timestamp DEFAULT now(),
    role varchar DEFAULT 'user' NOT NULL
);