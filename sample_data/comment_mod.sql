ALTER TABLE public.comment ALTER COLUMN edited_count SET DEFAULT 0;
ALTER TABLE public.comment ALTER COLUMN submission_time SET DEFAULT NOW();
ALTER TABLE public.comment ALTER COLUMN question_id SET DEFAULT NULL;
ALTER TABLE public.comment ALTER COLUMN answer_id SET DEFAULT NULL;